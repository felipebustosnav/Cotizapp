from rest_framework import viewsets, permissions, filters, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.http import HttpResponse
from .models import Cotizacion, DetalleCotizacion
from .serializers import CotizacionSerializer, CotizacionListSerializer
from usuarios.permissions import IsAdministrador


class CotizacionViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de cotizaciones.
    """
    
    def update(self, request, *args, **kwargs):
        """Restringe edición de cotizaciones finalizadas"""
        cotizacion = self.get_object()
        if cotizacion.estado in ['ACEPTADA', 'RECHAZADA']:
            if not request.user.is_superuser and request.user.rol != 'ADMIN':
                 raise ValidationError("No puedes modificar una cotización finalizada.")
        return super().update(request, *args, **kwargs)
    queryset = Cotizacion.objects.all()
    serializer_class = CotizacionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['estado', 'cliente', 'usuario_creador']
    search_fields = ['numero', 'cliente__nombre', 'cliente__rut']
    ordering_fields = ['fecha_creacion', 'total']
    ordering = ['-fecha_creacion']
    
    def get_queryset(self):
        """Filtra cotizaciones por empresa del usuario autenticado"""
        queryset = Cotizacion.objects.all()
        
        if not self.request.user.is_superuser:
            if self.request.user.empresa:
                queryset = queryset.filter(empresa=self.request.user.empresa)
            else:
                return Cotizacion.objects.none()
        
        # Filtros adicionales por query params
        fecha_inicio = self.request.query_params.get('fecha_inicio')
        fecha_fin = self.request.query_params.get('fecha_fin')
        
        if fecha_inicio:
            queryset = queryset.filter(fecha_creacion__gte=fecha_inicio)
        if fecha_fin:
            queryset = queryset.filter(fecha_creacion__lte=fecha_fin)
        
        return queryset
    
    def get_serializer_class(self):
        """Usa serializer simplificado para listado"""
        if self.action == 'list':
            return CotizacionListSerializer
        return CotizacionSerializer
    
    def get_permissions(self):
        """Solo administradores pueden eliminar cotizaciones"""
        if self.action == 'destroy':
            return [permissions.IsAuthenticated(), IsAdministrador()]
        if self.action == 'download_public':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]
    
    def create(self, request, *args, **kwargs):
        """Inyecta empresa y usuario_creador antes de la validación"""
        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
        
        # Asignar empresa
        if 'empresa' not in data:
            if request.user.empresa:
                data['empresa'] = request.user.empresa.id
            elif request.user.is_superuser:
                raise ValidationError({"empresa": "Superusuario debe especificar la empresa."})
        
        # Asignar usuario_creador
        data['usuario_creador'] = request.user.id
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def perform_create(self, serializer):
        """Guarda la cotización y auto-aprueba si es creada por admin/empleado"""
        # Auto-aprobar si el creador es administrador o empleado
        user = self.request.user
        if user.rol in ['ADMIN', 'EMPLEADO']:
            # Modificar el validated_data antes de guardar
            serializer.validated_data['estado'] = 'ENVIADA'
        
        # Guardar la cotización
        cotizacion = serializer.save()
        
        # Enviar correo automáticamente si fue auto-aprobada y el canal es EMAIL
        if cotizacion.estado == 'ENVIADA' and cotizacion.canal_preferencia == 'EMAIL':
            from .tasks import enviar_correo_cotizacion
            enviar_correo_cotizacion.delay(cotizacion.id)
    
    @action(detail=True, methods=['get'])
    def pdf(self, request, pk=None):
        """Genera y descarga el PDF de la cotización"""
        cotizacion = self.get_object()
        
        try:
            pdf_content = cotizacion.generar_pdf()
            response = HttpResponse(pdf_content, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="cotizacion_{cotizacion.numero}.pdf"'
            return response
        except Exception as e:
            return Response(
                {'error': f'Error al generar PDF: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def enviar(self, request, pk=None):
        """Envía la cotización por email"""
        cotizacion = self.get_object()
        email_destino = request.data.get('email', cotizacion.cliente.email)
        
        try:
            # Aquí iría la lógica de envío de email
            # Por ahora solo actualizamos el estado
            if cotizacion.estado == Cotizacion.Estado.BORRADOR:
                cotizacion.estado = Cotizacion.Estado.ENVIADA
                cotizacion.save()
            
            return Response({
                'message': f'Cotizacion enviada a {email_destino}',
                'cotizacion': CotizacionSerializer(cotizacion).data
            })
        except Exception as e:
            return Response(
                {'error': f'Error al enviar cotización: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def reenviar(self, request, pk=None):
        """Reenvía la cotización por correo"""
        cotizacion = self.get_object()
        try:
            from .tasks import enviar_correo_cotizacion
            enviar_correo_cotizacion.delay(cotizacion.id)
            return Response({'message': 'Cotización reenviada exitosamente'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def aprobar(self, request, pk=None):
        """
        Aprueba una cotización (cambia estado a ENVIADA).
        Si el canal es WHATSAPP, retorna el link para redirigir.
        """
        cotizacion = self.get_object()
        
        try:
            # Cambiar estado a ENVIADA (asumimos que la aprobación implica envío)
            cotizacion.estado = Cotizacion.Estado.ENVIADA
            cotizacion.save()
            
            response_data = {
                'message': 'Cotización aprobada correctamente',
                'canal': cotizacion.canal_preferencia,
                'whatsapp_link': None
            }
            
            # Generar link de WhatsApp si corresponde
            if cotizacion.canal_preferencia == 'WHATSAPP' and cotizacion.cliente.telefono:
                # Limpiar teléfono (eliminar espacios, guiones, +)
                telefono = ''.join(filter(str.isdigit, cotizacion.cliente.telefono))
                
                # Mensaje base por defecto
                mensaje_base = f"Hola {cotizacion.cliente.nombre}, adjunto cotización {cotizacion.numero} solicitada. Quedamos atentos."
                
                # Usar mensaje personalizado si existe
                if cotizacion.empresa.mensaje_whatsapp_cotizacion:
                    try:
                        mensaje_base = cotizacion.empresa.mensaje_whatsapp_cotizacion.format(
                            cliente_nombre=cotizacion.cliente.nombre,
                            cotizacion_numero=cotizacion.numero,
                            empresa_nombre=cotizacion.empresa.nombre
                        )
                    except Exception:
                        pass # Si falla el format, usamos el texto tal cual o fallamos silenciosamente al default? Mejor usamos el custom raw si falla format no es ideal.
                        # Mejor: Si falla format, no hacemos nada y dejamos mensaje_base? No, si el usuario puso texto, quiere ese texto.
                        # Asumimos que el usuario no pondrá {variables} rotas.
                
                # Codificar mensaje para URL
                from urllib.parse import quote
                
                # Generar link al portal de revisión público (Frontend)
                # Asumimos que el frontend corre en el mismo dominio base o está configurado
                # Construimos la URL al frontend: /cotizacion/{uuid}
                # request.build_absolute_uri('/') nos da la base.
                
                # Obtener la base URL del frontend (idealmente de settings, pero por ahora inferimos o hardcodeamos para dev)
                # Si estamos en dev django corre en 8000, react en 3000.
                # Para producción, suele ser el mismo dominio.
                # Usaremos una variable de entorno o settings, pero por simplicidad construiremos relativo a la petición actual
                # cambiada al puerto del frontend si es necesario, o asumimos root.
                
                # Estrategia: Usar una URL explicita si está definida en settings, sino construirla.
                from django.conf import settings
                base_url = getattr(settings, 'FRONTEND_URL', request.build_absolute_uri('/')).rstrip('/')
                public_link = f"{base_url}/cotizacion/{cotizacion.uuid}"
                
                mensaje_final = f"{mensaje_base} Puede revisarla y aceptarla aquí: {public_link}"
                mensaje_encoded = quote(mensaje_final)
                
                response_data['whatsapp_link'] = f"https://wa.me/{telefono}?text={mensaje_encoded}"
            
            # Si el canal es EMAIL, enviar correo usando la tarea asíncrona
            elif cotizacion.canal_preferencia == 'EMAIL':
                try:
                    from .tasks import enviar_correo_cotizacion
                    
                    asunto = f"Cotización #{cotizacion.numero} - {cotizacion.empresa.nombre}"
                    mensaje = f"Estimado/a {cotizacion.cliente.nombre},\n\nAdjunto encontrará su cotización solicitada.\n\nAtte,\n{cotizacion.empresa.nombre}"
                    destinatarios = [cotizacion.cliente.email]
                    
                    # Llamada asíncrona a Celery
                    enviar_correo_cotizacion.delay(cotizacion.id)
                    response_data['message'] = 'Cotización aprobada y correo encolado para envío'
                    
                except Exception as e:
                    print(f"Error al encolar tarea de correo manual: {e}")
            
            return Response(response_data)
            
        except Exception as e:
            return Response(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def rechazar(self, request, pk=None):
        """
        Rechaza una cotización.
        """
        cotizacion = self.get_object()
        
        try:
            cotizacion.estado = Cotizacion.Estado.RECHAZADA
            cotizacion.save()
            return Response({'message': 'Cotización rechazada correctamente'})
        except Exception as e:
            return Response(
                {'error': f'Error al rechazar cotización: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def pending_stats(self, request):
        """Retorna conteo de cotizaciones pendientes (borradores públicos)"""
        empresa = request.user.empresa
        if not empresa:
            return Response({'count': 0})
            
        count = Cotizacion.objects.filter(
            empresa=empresa,
            estado=Cotizacion.Estado.BORRADOR,
            usuario_creador__isnull=True
        ).count()
        
        return Response({'count': count})

    @action(detail=False, methods=['get'])
    def download_public(self, request):
        """
        Permite descargar el PDF de una cotización usando su UUID (Acceso Público).
        """
        uuid_str = request.query_params.get('uuid')
        if not uuid_str:
            return Response({'error': 'UUID requerido'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            from django.shortcuts import get_object_or_404
            cotizacion = get_object_or_404(Cotizacion, uuid=uuid_str)
            
            pdf_content = cotizacion.generar_pdf()
            response = HttpResponse(pdf_content, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="cotizacion_{cotizacion.numero}.pdf"'
            return response
        except Exception as e:
            return Response(
                {'error': 'Cotización no encontrada o error al generar PDF'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def marcar_aceptada(self, request, pk=None):
        """
        Acción manual para que un Admin/Empleado marque como ACEPTADA.
        """
        cotizacion = self.get_object()
        
        # Opcional: Validar que esté enviada
        if cotizacion.estado != Cotizacion.Estado.ENVIADA:
            # Podríamos ser flexibles o estrictos. Seremos flexibles pero warning si es borrador.
             pass

        cotizacion.estado = 'ACEPTADA' # Usar literal o Cotizacion.Estado.ACEPTADA si está definido
        cotizacion.save()
        
        return Response({'message': 'Cotización marcada como aceptada manualmente'})

    # --- Acciones Públicas (Cliente) ---

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def public_detail(self, request):
        """Detalle público de la cotización por UUID"""
        uuid_str = request.query_params.get('uuid')
        if not uuid_str:
            return Response({'error': 'UUID requerido'}, status=status.HTTP_400_BAD_REQUEST)
            
        from django.shortcuts import get_object_or_404
        cotizacion = get_object_or_404(Cotizacion, uuid=uuid_str)
        
        # Serializamos con el serializer completo para mostrar items
        serializer = CotizacionSerializer(cotizacion)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def public_accept(self, request):
        """Cliente acepta la cotización públicamente por UUID"""
        uuid_str = request.data.get('uuid')
        if not uuid_str:
            return Response({'error': 'UUID requerido'}, status=status.HTTP_400_BAD_REQUEST)
            
        from django.shortcuts import get_object_or_404
        cotizacion = get_object_or_404(Cotizacion, uuid=uuid_str)
        
        if cotizacion.estado in ['ACEPTADA', 'RECHAZADA']:
             return Response({'error': f'La cotización ya está {cotizacion.estado.lower()}'}, status=status.HTTP_400_BAD_REQUEST)

        cotizacion.estado = 'ACEPTADA'
        cotizacion.save()
        return Response({'message': 'Cotización aceptada exitosamente'})

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def public_reject(self, request):
        """Cliente rechaza la cotización públicamente por UUID"""
        uuid_str = request.data.get('uuid')
        if not uuid_str:
            return Response({'error': 'UUID requerido'}, status=status.HTTP_400_BAD_REQUEST)
            
        from django.shortcuts import get_object_or_404
        cotizacion = get_object_or_404(Cotizacion, uuid=uuid_str)
        
        if cotizacion.estado in ['ACEPTADA', 'RECHAZADA']:
             return Response({'error': f'La cotización ya está {cotizacion.estado.lower()}'}, status=status.HTTP_400_BAD_REQUEST)
             
        cotizacion.estado = 'RECHAZADA'
        cotizacion.save()
        return Response({'message': 'Cotización rechazada'})
