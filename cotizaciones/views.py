from rest_framework import viewsets, permissions, filters, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.http import HttpResponse
from .models import Cotizacion, DetalleCotizacion, ReglaOfertaAutomatica
from .serializers import CotizacionSerializer, CotizacionListSerializer, ReglaOfertaAutomaticaSerializer
from usuarios.permissions import IsAdministrador
from django.db.models import Q
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class CotizacionViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de cotizaciones.
    """
    
    def update(self, request, *args, **kwargs):
        """Restringe edición de cotizaciones finalizadas y valida cambios de estado"""
        cotizacion = self.get_object()
        user = request.user
        
        # 1. Validar permisos de edición si ya está finalizada o si usuario es empleado y ya envió
        if cotizacion.estado in ['ACEPTADA', 'RECHAZADA']:
            if not user.is_superuser and user.rol != 'ADMIN':
                 raise ValidationError("No puedes modificar una cotización finalizada.")
        
        # Restricción extra para Empleados: No editar si ya fue ENVIADA
        if user.rol == 'EMPLEADO' and cotizacion.estado == 'ENVIADA':
             raise ValidationError("No puedes modificar una cotización ya enviada. Debes solicitar cambios al administrador.")
        
        # 2. Preparar data (hacer mutable)
        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
        
        # 3. Validar restricción: No volver a BORRADOR si ya salió de allí
        nuevo_estado = data.get('estado')
        if cotizacion.estado != 'BORRADOR' and nuevo_estado == 'BORRADOR':
             raise ValidationError("No se puede revertir una cotización enviada/finalizada a Borrador.")

        # 4. Si ya estaba finalizada (Aceptada/Rechazada), proteger detalles para evitar re-creación
        # Esto permite que el Admin cambie el estado sin romper los items por validaciones
        if cotizacion.estado in ['ACEPTADA', 'RECHAZADA']:
             if 'detalles' in data:
                 del data['detalles']
             
             # Opcional: Proteger cliente/empresa también si se desea
        
        serializer = self.get_serializer(cotizacion, data=data, partial=kwargs.get('partial', False))
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(cotizacion, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            cotizacion._prefetched_objects_cache = {}

        return Response(serializer.data)
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
            user = self.request.user
            if user.empresa:
                queryset = queryset.filter(empresa=user.empresa)
                # Filtro para empleados: Sus cotizaciones O Autoatención (creador null/None)
                if user.rol == 'EMPLEADO':
                    # Empleados ven:
                    # 1. Sus propias creaciones
                    # 2. Cotizaciones que ellos gestionaron/decidieron (Aprobadas/Rechazadas)
                    # 3. Cotizaciones Públicas (sin creador) pero solo si están en BORRADOR (Bandeja de entrada)
                    queryset = queryset.filter(
                        Q(usuario_creador=user) | 
                        Q(usuario_decision=user) |
                        Q(usuario_creador__isnull=True, estado='BORRADOR')
                    )
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
        """Solo administradores pueden eliminar cotizaciones. Permitir acceso público a acciones específicas."""
        if self.action == 'destroy':
            return [permissions.IsAuthenticated(), IsAdministrador()]
        
        # Acciones públicas (Cliente)
        if self.action in ['download_public', 'public_detail', 'public_accept', 'public_reject']:
            return [permissions.AllowAny()]
            
        return [permissions.IsAuthenticated()]
    
    def create(self, request, *args, **kwargs):
        """Inyecta empresa y usuario_creador antes de la validación"""
        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
        user = request.user

        # Asignar empresa
        if 'empresa' not in data:
            if user.empresa:
                data['empresa'] = user.empresa.id
            elif user.is_superuser:
                 raise ValidationError({"empresa": "Superusuario debe especificar la empresa."})
        
        # Asignar usuario_creador
        data['usuario_creador'] = user.id
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        
        # --- Lógica de Auto-aprobación Interna ---
        # Si es creado por ADMIN o EMPLEADO, se auto-aprueba y envía
        rol_interno = user.rol in ['ADMIN', 'EMPLEADO']
        whatsapp_link = None
        
        if rol_interno:
            serializer.validated_data['estado'] = 'ENVIADA'
            # Trazabilidad
            serializer.validated_data['usuario_decision'] = user
            serializer.validated_data['fecha_decision'] = timezone.now()
            serializer.validated_data['es_decision_automatica'] = False
            
        cotizacion = serializer.save()
        
        # --- Post-Processing ---
        if rol_interno and cotizacion.estado == 'ENVIADA':
            
            # Caso Email: Enviar correo
            if cotizacion.canal_preferencia == 'EMAIL':
                from .tasks import enviar_correo_cotizacion
                enviar_correo_cotizacion.delay(cotizacion.id)
                
            # Caso WhatsApp: Generar Link
            elif cotizacion.canal_preferencia == 'WHATSAPP' and cotizacion.cliente.telefono:
                 # Generar link de WhatsApp
                 try:
                    telefono = ''.join(filter(str.isdigit, cotizacion.cliente.telefono))
                    mensaje_base = f"Hola {cotizacion.cliente.nombre}, le envío la cotización {cotizacion.numero}."
                    
                    if cotizacion.empresa.mensaje_whatsapp_cotizacion:
                        mensaje_base = cotizacion.empresa.mensaje_whatsapp_cotizacion.format(
                            cliente_nombre=cotizacion.cliente.nombre,
                            cotizacion_numero=cotizacion.numero,
                            empresa_nombre=cotizacion.empresa.nombre
                        )
                    
                    from django.conf import settings
                    from urllib.parse import quote
                    
                    # Link al portal público
                    base_url = getattr(settings, 'FRONTEND_URL', request.build_absolute_uri('/')).rstrip('/')
                    public_link = f"{base_url}/cotizacion/{cotizacion.uuid}"
                    
                    mensaje_final = f"{mensaje_base} Ver aquí: {public_link}"
                    whatsapp_link = f"https://wa.me/{telefono}?text={quote(mensaje_final)}"
                 except Exception as e:
                     logger.error(f"Error generando link wsp: {e}")

        # Construir respuesta
        response_data = serializer.data
        if whatsapp_link:
            response_data['whatsapp_link'] = whatsapp_link
            response_data['message'] = "Cotización creada y lista para enviar por WhatsApp"
            
            response_data['message'] = "Cotización creada y lista para enviar por WhatsApp"
            
        return Response(response_data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """
        Restricción: Empleados NO pueden editar cotizaciones (contenido/valores).
        Solo pueden cambiar estado a través de acciones específicas (no update directo).
        """
        if request.user.rol == 'EMPLEADO':
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("No tienes permiso para editar el contenido de la cotización. Solicita cambios al administrador.")
            
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Restricción: Empleados NO pueden eliminar cotizaciones en ningún momento.
        """
        if request.user.rol == 'EMPLEADO':
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("No tienes permiso para eliminar cotizaciones.")
            
        return super().destroy(request, *args, **kwargs)

    def perform_create(self, serializer):
        # Deprecado por el override de create completo arriba
        pass
    
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
                # Trazabilidad
                cotizacion.usuario_decision = request.user
                cotizacion.fecha_decision = timezone.now()
                cotizacion.es_decision_automatica = False
                cotizacion.save()

                # Notificar si es empleado
                if request.user.rol == 'EMPLEADO':
                    from .tasks import notificar_decision_empleado
                    notificar_decision_empleado.delay(cotizacion.id, 'ENVIADA', request.user.id)
            
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
            logger.error(f"Error al aprobar cotización {pk}: {e}", exc_info=True)
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
            
            # Trazabilidad
            cotizacion.usuario_decision = request.user
            cotizacion.fecha_decision = timezone.now()
            cotizacion.es_decision_automatica = False
            cotizacion.save()

            # Notificar si es empleado
            if request.user.rol == 'EMPLEADO':
                from .tasks import notificar_decision_empleado
                notificar_decision_empleado.delay(cotizacion.id, 'APROBADA', request.user.id)
            
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
        motivo = request.data.get('motivo', '')
        
        try:
            cotizacion.estado = Cotizacion.Estado.RECHAZADA
            if motivo:
                cotizacion.motivo_rechazo = motivo
            
            # Trazabilidad
            cotizacion.usuario_decision = request.user
            cotizacion.fecha_decision = timezone.now()
            cotizacion.es_decision_automatica = False
            cotizacion.save()
            
            # Notificar si es empleado (Rechazo interno)
            if request.user.rol == 'EMPLEADO':
                from .tasks import notificar_decision_empleado
                notificar_decision_empleado.delay(cotizacion.id, 'RECHAZADA', request.user.id)
            
            # Notificar al cliente
            from .tasks import notificar_rechazo_empresa
            notificar_rechazo_empresa.delay(cotizacion.id)

            return Response({'message': 'Cotización rechazada correctamente'})
        except Exception as e:
            return Response(
                {'error': f'Error al rechazar cotización: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def solicitar_cambio(self, request, pk=None):
        """
        Empleado solicita cambios sobre una cotización.
        """
        cotizacion = self.get_object()
        mensaje = request.data.get('mensaje', '')
        
        if not mensaje:
            return Response({'error': 'Debe especificar un mensaje.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            from .tasks import notificar_solicitud_cambio
            notificar_solicitud_cambio.delay(cotizacion.id, request.user.id, mensaje)
            return Response({'message': 'Solicitud de cambio enviada al administrador.'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
        data = serializer.data
        
        # Buscar oferta activa
        from .models import OfertaCotizacion
        from django.utils import timezone
        
        oferta_activa = cotizacion.ofertas_automaticas.filter(
            estado__in=['ACTIVA', 'ACEPTADA'], # Mostrar también si ya fue aceptada con oferta
            fecha_vencimiento__gte=timezone.now()
        ).order_by('-fecha_generacion').first()
        
        if oferta_activa and oferta_activa.estado == 'ACTIVA':
            from decimal import Decimal
            descuento_factor = Decimal(str(oferta_activa.descuento_porcentaje)) / Decimal('100')
            cotizacion_total = Decimal(str(cotizacion.total)) if not isinstance(cotizacion.total, Decimal) else cotizacion.total
            
            data['oferta_activa'] = {
                'id': oferta_activa.id,
                'descuento_porcentaje': oferta_activa.descuento_porcentaje,
                'fecha_vencimiento': oferta_activa.fecha_vencimiento,
                'nuevo_total': cotizacion_total * (Decimal('1') - descuento_factor)
            }
        
        return Response(data)

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def public_accept(self, request):
        """Cliente acepta la cotización públicamente por UUID"""
        uuid_str = request.data.get('uuid')
        if not uuid_str:
            return Response({'error': 'UUID requerido'}, status=status.HTTP_400_BAD_REQUEST)
            
        from django.shortcuts import get_object_or_404
        from django.utils import timezone
        cotizacion = get_object_or_404(Cotizacion, uuid=uuid_str)
        
        if cotizacion.estado == 'ACEPTADA':
              # Si ya fue aceptada, no permitir aceptar de nuevo salvo casos especiales
              return Response({'error': f'La cotización ya está {cotizacion.estado.lower()}'}, status=status.HTTP_400_BAD_REQUEST)

        # Verificar y aplicar oferta activa
        oferta_activa = cotizacion.ofertas_automaticas.filter(
            estado='ACTIVA',
            fecha_vencimiento__gte=timezone.now()
        ).order_by('-fecha_generacion').first()
        
        # Si está rechazada pero NO tiene oferta activa, entonces sí bloquear
        if cotizacion.estado == 'RECHAZADA' and not oferta_activa:
             return Response({'error': f'La cotización fue rechazada y no tiene ofertas vigentes.'}, status=status.HTTP_400_BAD_REQUEST)

        if oferta_activa:
            # Aplicar descuento
            from decimal import Decimal
            descuento_factor = Decimal(str(oferta_activa.descuento_porcentaje)) / Decimal('100')
            cotizacion_total = Decimal(str(cotizacion.total)) if not isinstance(cotizacion.total, Decimal) else cotizacion.total
            
            descuento_monto = cotizacion_total * descuento_factor
            cotizacion.total = cotizacion_total - descuento_monto
            
            # Marcar oferta como aceptada
            oferta_activa.estado = 'ACEPTADA'
            oferta_activa.save()
            
            # Podríamos guardar una nota o campo extra
            cotizacion.notas += f"\n[AUTO] Oferta {oferta_activa.descuento_porcentaje}% aplicada. Descuento: ${descuento_monto:,.0f}"

        cotizacion.estado = 'ACEPTADA'
        # cotizacion.usuario_decision = None # COMENTADO: Mantener al empleado que aprobó el envío como responsable/visible
        cotizacion.es_decision_automatica = False
        cotizacion.save()
        
        # Opcional: Notificar a la empresa de la aceptación (pendiente en HU)
        
        return Response({'message': 'Cotización aceptada exitosamente'})

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def public_reject(self, request):
        """Cliente rechaza la cotización públicamente por UUID"""
        uuid_str = request.data.get('uuid')
        motivo = request.data.get('motivo', '') # Obtener motivo opcional
        
        if not uuid_str:
            return Response({'error': 'UUID requerido'}, status=status.HTTP_400_BAD_REQUEST)
            
        from django.shortcuts import get_object_or_404
        cotizacion = get_object_or_404(Cotizacion, uuid=uuid_str)
        
        # Permitir rechazar SI es aceptada (caso raro) o SI ya está rechazada pero queremos rechazar la oferta
        if cotizacion.estado == 'ACEPTADA':
             return Response({'error': f'La cotización ya está aceptada.'}, status=status.HTTP_400_BAD_REQUEST)
             
        # Si ya está RECHAZADA, validamos si tiene oferta activa para permitir "rechazar la oferta"
        # Si no tiene oferta, entonces sí es redundante.
        from django.utils import timezone
        oferta_activa = cotizacion.ofertas_automaticas.filter(
            estado='ACTIVA',
            fecha_vencimiento__gte=timezone.now()
        ).first()
        
        if cotizacion.estado == 'RECHAZADA' and not oferta_activa:
            return Response({'error': 'La cotización ya está rechazada.'}, status=status.HTTP_400_BAD_REQUEST)

        cotizacion.estado = 'RECHAZADA'
        # IMPORTANTE: Marcar que fue decisión del CLIENTE (None) para que el bot siga enviando ofertas
        # cotizacion.usuario_decision = None # COMENTADO: Mantener al empleado que aprobó el envío como responsable/visible
        cotizacion.es_decision_automatica = False # Fue manual por el cliente
        
        if motivo:
            cotizacion.motivo_rechazo = motivo
        cotizacion.save()
        
        # Invalidar/Rechazar oferta activa si existe
        from django.utils import timezone
        oferta_activa = cotizacion.ofertas_automaticas.filter(
            estado='ACTIVA',
            fecha_vencimiento__gte=timezone.now()
        ).first()
        
        if oferta_activa:
            oferta_activa.estado = 'RECHAZADA'
            oferta_activa.save()
        
        # Notificar a la empresa
        from .tasks import notificar_rechazo_cliente
        notificar_rechazo_cliente.delay(cotizacion.id)

        return Response({'message': 'Cotización rechazada'})

class ReporteViewSet(viewsets.ViewSet):
    """
    ViewSet para generar reportes y estadísticas (Solo Admin/Empresa)
    """
    permission_classes = [permissions.IsAuthenticated, IsAdministrador]

    def _get_stats(self, empresa, user=None):
        """Helper para calcular estadísticas. Si viene user (empleado), filtra por él o autoatención."""
        qs = Cotizacion.objects.filter(empresa=empresa)
        
        if user and user.rol == 'EMPLEADO':
            qs = qs.filter(Q(usuario_creador=user) | Q(usuario_creador__isnull=True))
        
        # 1. Totales Generales
        total_cotizaciones = qs.count()
        total_aprobadas = qs.filter(estado='ACEPTADA').count()
        monto_total_aprobado = sum(c.total for c in qs.filter(estado='ACEPTADA'))

        monto_total_aprobado = sum(c.total for c in qs.filter(estado='ACEPTADA'))

        # 2. Ventas por Mes
        # 2. Ventas por Mes (Agregación en Python para evitar error de zonas horarias en SQLite)
        from django.db.models import Sum
        ventas_aprobadas = qs.filter(estado='ACEPTADA').order_by('fecha_creacion')
        
        ventas_dict = {}
        for venta in ventas_aprobadas:
            # Asegurarse que es fecha local o UTC
            fecha = venta.fecha_creacion
            mes_key = fecha.strftime('%Y-%m')
            
            if mes_key not in ventas_dict:
                ventas_dict[mes_key] = {'total': 0, 'cantidad': 0}
            
            ventas_dict[mes_key]['total'] += float(venta.total)
            ventas_dict[mes_key]['cantidad'] += 1
            
        data_ventas = []
        for mes, data in ventas_dict.items():
            data_ventas.append({
                'mes': mes,
                'total': data['total'],
                'cantidad': data['cantidad']
            })
        
        # Ordenar por mes
        data_ventas.sort(key=lambda x: x['mes'])

        # 3. Top Productos
        top_productos = (
            DetalleCotizacion.objects.filter(cotizacion__empresa=empresa)
            .values('producto__nombre')
            .annotate(cantidad_total=Sum('cantidad'))
            .order_by('-cantidad_total')[:5]
        )
        
        data_productos = [
            {'nombre': item['producto__nombre'], 'cantidad': item['cantidad_total']}
            for item in top_productos
        ]

        # 4. Métricas de Mensajería Automática
        from .models import OfertaCotizacion
        from django.db.models import Count, Avg, Sum, F
        from decimal import Decimal

        qs_ofertas = OfertaCotizacion.objects.filter(cotizacion__empresa=empresa)
        
        total_ofertas = qs_ofertas.count()
        ofertas_aceptadas = qs_ofertas.filter(estado='ACEPTADA').count()
        ofertas_rechazadas = qs_ofertas.filter(estado='RECHAZADA').count()
        tasa_conversion_ofertas = round((ofertas_aceptadas / total_ofertas * 100), 1) if total_ofertas > 0 else 0
        
        # Análisis de Eficiencia por Porcentaje de Descuento
        # Agrupar por 'descuento_porcentaje' y contar total vs aceptadas
        eficiencia_por_descuento = []
        descuentos_distinct = qs_ofertas.values_list('descuento_porcentaje', flat=True).distinct().order_by('descuento_porcentaje')
        
        for pct in descuentos_distinct:
            total_pct = qs_ofertas.filter(descuento_porcentaje=pct).count()
            aceptadas_pct = qs_ofertas.filter(descuento_porcentaje=pct, estado='ACEPTADA').count()
            tasa_pct = round((aceptadas_pct / total_pct * 100), 1) if total_pct > 0 else 0
            eficiencia_por_descuento.append({
                'porcentaje': f"{pct}%",
                'enviadas': total_pct,
                'aceptadas': aceptadas_pct,
                'tasa': tasa_pct
            })
        
        # Ingresos Recuperados y Dinero Descontado
        # Iterar para calcular montos exactos (dado que total ya tiene descuento aplicado en cotizacion)
        ingresos_recuperados = 0
        total_descontado = 0
        
        ofertas_aceptadas_objs = qs_ofertas.filter(estado='ACEPTADA').select_related('cotizacion')
        for oferta in ofertas_aceptadas_objs:
            final_total = Decimal(oferta.cotizacion.total)
            pct = Decimal(oferta.descuento_porcentaje) / Decimal(100)
            
            # Revertir cálculo para obtener original: Final = Original * (1 - pct)  => Original = Final / (1 - pct)
            if pct < 1:
                original_total = final_total / (1 - pct)
                monto_descuento = original_total - final_total
                
                ingresos_recuperados += final_total
                total_descontado += monto_descuento

        promedio_descuento = round(total_descontado / ofertas_aceptadas) if ofertas_aceptadas > 0 else 0
        
        # Estado de Ofertas (Para Gráfico Torta)
        estado_counts = qs_ofertas.values('estado').annotate(cantidad=Count('estado'))
        data_estado_ofertas = [
            {'nombre': item['estado'], 'cantidad': item['cantidad']}
            for item in estado_counts
        ]

        return {
            'resumen': {
                'total_cotizaciones': total_cotizaciones,
                'tasa_aprobacion': round((total_aprobadas / total_cotizaciones * 100), 1) if total_cotizaciones > 0 else 0,
                'monto_total_aprobado': monto_total_aprobado
            },
            'ventas_mensuales': data_ventas,
            'top_productos': data_productos,
            'automatizacion': {
                'total_ofertas': total_ofertas,
                'ofertas_aceptadas': ofertas_aceptadas,
                'ofertas_rechazadas': ofertas_rechazadas,
                'tasa_conversion': tasa_conversion_ofertas,
                'ingresos_recuperados': ingresos_recuperados,
                'total_descontado': total_descontado,
                'promedio_descuento': promedio_descuento,
                'eficiencia_por_descuento': eficiencia_por_descuento, # Lista para Gráfico Barras
                'estado_ofertas': data_estado_ofertas
            }
        }

    def list(self, request):
        """Retorna estadísticas generales para el dashboard en JSON"""
        empresa = request.user.empresa
        if not empresa:
            return Response({'error': 'Usuario no tiene empresa asignada'}, status=400)
            
        # Pasar usuario para filtrar si es empleado
        stats = self._get_stats(empresa, request.user)
        return Response(stats)

    @action(detail=False, methods=['get'])
    def download_pdf(self, request):
        """Descarga el reporte en PDF"""
        empresa = request.user.empresa
        if not empresa:
             return Response({'error': 'Usuario no tiene empresa'}, status=400)
        
        stats = self._get_stats(empresa, request.user)
        
        from .utils.report_generator import generar_reporte_pdf
        return generar_reporte_pdf(empresa, stats)


class ReglaOfertaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para administrar las reglas de oferta automática de la empresa.
    """
    serializer_class = ReglaOfertaAutomaticaSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdministrador]

    def get_queryset(self):
        # Retorna solo las reglas de la empresa del usuario
        return ReglaOfertaAutomatica.objects.filter(empresa=self.request.user.empresa).order_by('orden')

    def perform_create(self, serializer):
        # Asigna automáticamente la empresa al crear
        serializer.save(empresa=self.request.user.empresa)
