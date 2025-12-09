from celery import shared_task
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

@shared_task
def enviar_correo_cotizacion(cotizacion_id):
    """
    Tarea asincrónica para enviar correos de cotización.
    Recibe solo el ID, obtiene los datos frescos de la BD y genera el PDF al vuelo.
    """
    try:
        from .models import Cotizacion
        from django.utils.html import escape
        from django.core.mail import EmailMultiAlternatives
        from email.mime.image import MIMEImage
        import os
        
        cotizacion = Cotizacion.objects.get(id=cotizacion_id)
        empresa = cotizacion.empresa
        cliente = cotizacion.cliente
        
        logger.info(f"Iniciando tarea de correo para Cotización #{cotizacion.numero}")
        
        # 1. Generar contenido del correo
        asunto = f"Cotización #{cotizacion.numero} - {empresa.nombre}"
        
        # Construir referencia al logo para usar en el HTML
        logo_cid = "empresa_logo"
        logo_html = ""
        if empresa.logo:
            logo_html = f'<img src="cid:{logo_cid}" alt="{escape(empresa.nombre)}" style="max-width: 200px; height: auto;" />'
        
        # Construir link al portal de revisión
        base_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000').rstrip('/')
        public_link = f"{base_url}/cotizacion/{cotizacion.uuid}"

        if empresa.mensaje_correo_cotizacion:
            # Reemplazar variables básicas si existen en el texto
            mensaje_texto = empresa.mensaje_correo_cotizacion.format(
                cliente_nombre=cliente.nombre,
                cotizacion_numero=cotizacion.numero,
                empresa_nombre=empresa.nombre,
                total=f"${cotizacion.total:,.0f}",
                empresa_logo=logo_html,
                link_revision=f'<a href="{public_link}">Revisar y Aceptar Cotización</a>'
            )
            # Convertir saltos de línea a <br> para HTML
            mensaje_html = mensaje_texto.replace('\n', '<br>')
            
            # Si el usuario no usó la variable {link_revision}, lo agregamos al final por seguridad
            if '{link_revision}' not in empresa.mensaje_correo_cotizacion:
                 mensaje_html += f'<br><br><p>Puede revisar, descargar y aceptar su cotización en el siguiente enlace:<br><a href="{public_link}">{public_link}</a></p>'

        else:
            # Mensaje por defecto (sin logo, el usuario puede agregarlo con {empresa_logo})
            mensaje_html = f"""
            <p>Estimado/a <strong>{escape(cliente.nombre)}</strong>,</p>
            <p>Adjunto encontrará la cotización <strong>#{cotizacion.numero}</strong> solicitada.</p>
            <p><strong>Detalles:</strong><br>
            Total: ${cotizacion.total:,.0f}</p>
            
            <p>Puede revisar y aceptar esta cotización online aquí:<br>
            <a href="{public_link}" style="display:inline-block; background-color:#F97316; color:white; padding:10px 20px; text-decoration:none; border-radius:5px; font-weight:bold;">Revisar Cotización</a>
            </p>
            
            <p>Atte,<br>
            {escape(empresa.nombre)}<br>
            {escape(empresa.direccion)}<br>
            {escape(empresa.telefono)}</p>
            """
        
        # Envolver en HTML básico
        mensaje_completo = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            {mensaje_html}
        </body>
        </html>
        """
        
        # 2. Configurar destinatarios y reply-to
        destinatarios = [cliente.email]
        reply_to = [empresa.email] if empresa.email else None
        
        # Usar EmailMultiAlternatives para poder adjuntar imágenes inline
        email = EmailMultiAlternatives(
            subject=asunto,
            body="Por favor, visualice este correo en un cliente que soporte HTML.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=destinatarios,
            reply_to=reply_to
        )
        email.attach_alternative(mensaje_completo, "text/html")
        
        # Adjuntar logo como imagen inline SOLO si el usuario lo usa en su mensaje
        logo_adjuntado = False
        if empresa.logo and empresa.mensaje_correo_cotizacion and '{empresa_logo}' in empresa.mensaje_correo_cotizacion:
            try:
                logger.info(f"Detectado {{empresa_logo}} en mensaje personalizado. Adjuntando logo...")
                logo_path = empresa.logo.path
                with open(logo_path, 'rb') as logo_file:
                    logo_data = logo_file.read()
                    # Determinar el tipo MIME basado en la extensión
                    ext = os.path.splitext(logo_path)[1].lower()
                    mime_type = 'image/jpeg' if ext in ['.jpg', '.jpeg'] else 'image/png'
                    
                    img = MIMEImage(logo_data, _subtype=mime_type.split('/')[1])
                    img.add_header('Content-ID', f'<{logo_cid}>')
                    # NO agregar Content-Disposition para evitar que aparezca como adjunto descargable
                    email.attach(img)
                    logo_adjuntado = True
                    logger.info(f"Logo adjuntado como imagen inline con CID: {logo_cid}")
            except Exception as e:
                logger.warning(f"No se pudo adjuntar el logo: {e}")
        else:
            logger.info(f"Logo NO adjuntado. Condiciones: logo={bool(empresa.logo)}, mensaje_personalizado={bool(empresa.mensaje_correo_cotizacion)}, contiene_variable={'{empresa_logo}' in (empresa.mensaje_correo_cotizacion or '')}")
        
        # 3. Generar PDF (Opcional - Deshabilitado por configuración)
        # El usuario solicitó no adjuntar PDF, solo enviar el link.
        # pdf_content = cotizacion.generar_pdf()
        # filename = f"Cotizacion_{cotizacion.numero}.pdf"
        # email.attach(filename, pdf_content, 'application/pdf')
        logger.info("PDF no adjuntado por configuración (solo link)")
            
        # 4. Enviar
        email.send()
        
        logger.info(f"Correo enviado exitosamente a {destinatarios}")
        return f"Correo enviado a {cliente.email} con PDF"
        
    except Cotizacion.DoesNotExist:
        logger.error(f"Cotización ID {cotizacion_id} no encontrada")
        return "Error: Cotización no encontrada"
    except Exception as e:
        logger.error(f"Error crítico en tarea de correo: {str(e)}")
        return f"Error: {str(e)}"

@shared_task
def notificar_solicitud_cambio(cotizacion_id, user_id, mensaje):
    """Notifica al admin que un empleado solicita cambios"""
    try:
        from .models import Cotizacion
        from usuarios.models import CustomUser
        from django.core.mail import send_mail
        from django.conf import settings
        
        cotizacion = Cotizacion.objects.get(id=cotizacion_id)
        empleado = CustomUser.objects.get(id=user_id)
        empresa = cotizacion.empresa
        
        if not empresa.email:
            return "No hay email de empresa configurado"
            
        subject = f"Solicitud de Cambio - Cotización #{cotizacion.numero}"
        body = f"""
        El empleado {empleado.first_name} {empleado.last_name} ha solicitado cambios en la cotización #{cotizacion.numero}.
        
        Mensaje del empleado:
        "{mensaje}"
        
        Por favor, revise la cotización en el sistema.
        """
        
        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [empresa.email],
            fail_silently=False,
        )
        return "Notificación de solicitud de cambio enviada"
    except Exception as e:
        return f"Error notificando solicitud de cambio: {e}"

@shared_task
def notificar_rechazo_cliente(cotizacion_id):
    """
    Notifica a la EMPRESA que un CLIENTE rechazó la cotización.
    """
    try:
        from .models import Cotizacion
        from django.core.mail import EmailMultiAlternatives
        from email.mime.image import MIMEImage
        import os
        from django.conf import settings
        
        cotizacion = Cotizacion.objects.get(id=cotizacion_id)
        empresa = cotizacion.empresa
        cliente = cotizacion.cliente
        
        # Destinatarios
        # Destinatarios: Empresa (Admin) + Empleado que autorizó (si existe)
        destinatarios = []
        
        # 1. Empresa siempre recibe copia
        if empresa.email:
            destinatarios.append(empresa.email)
            
        # 2. Empleado que autorizó el envío (Usuario Decision)
        if cotizacion.usuario_decision and cotizacion.usuario_decision.email:
            destinatarios.append(cotizacion.usuario_decision.email)
            
        # 3. Fallback: Si no hay nadie, intentar usuario creador
        if not destinatarios and cotizacion.usuario_creador and cotizacion.usuario_creador.email:
             destinatarios.append(cotizacion.usuario_creador.email)
             
        # Eliminar duplicados
        destinatarios = list(set(destinatarios))
            
        if not destinatarios:
            return "No hay destinatarios"

        asunto = f"Cotización Rechazada por Cliente - #{cotizacion.numero}"
        motivo_texto = f"<p><strong>Motivo indicado:</strong> {cotizacion.motivo_rechazo}</p>" if cotizacion.motivo_rechazo else "<p><em>Sin motivo especificado.</em></p>"
        
        # CotizApp Logo Logic (System Logo)
        logo_cid = "cotizapp_logo"
        logo_html = '<h1 style="color: #F97316;">CotizApp</h1>' # Fallback text
        
        # Try to find system logo
        system_logo_path = os.path.join(settings.MEDIA_ROOT, 'logos', 'logo.png')
        logo_exists = os.path.exists(system_logo_path)
        
        if logo_exists:
            logo_html = f'<div style="text-align:center; margin-bottom: 20px;"><img src="cid:{logo_cid}" alt="CotizApp" style="max-height: 60px; width: auto;" /></div>'

        mensaje_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto;">
            {logo_html}
            <div style="background-color: #ffffff; padding: 20px; border-radius: 8px; border: 1px solid #e5e7eb;">
                <h2 style="color: #ef4444; margin-top: 0; text-align: center;">Cotización Rechazada</h2>
                <p>Estimado equipo,</p>
                <p>El cliente <strong>{cliente.nombre}</strong> ha RECHAZADO la cotización <strong>#{cotizacion.numero}</strong>.</p>
                
                <div style="background-color: #fef2f2; padding: 15px; border-radius: 5px; border-left: 4px solid #ef4444; margin: 15px 0;">
                    {motivo_texto}
                </div>
                
                <p style="text-align: right;"><strong>Monto:</strong> ${cotizacion.total:,.0f}</p>
                
                <p style="text-align: center; margin-top: 30px;">
                    <a href="{settings.FRONTEND_URL}/cotizaciones/editar/{cotizacion.id}" style="background-color: #333; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Ver Cotización</a>
                </p>
            </div>
            <p style="text-align: center; color: #9ca3af; font-size: 12px; margin-top: 20px;">
                Enviado automáticamente por CotizApp
            </p>
        </body>
        </html>
        """
        
        email = EmailMultiAlternatives(
            subject=asunto,
            body="El cliente ha rechazado la cotización. Motivo: " + (cotizacion.motivo_rechazo or "No especificado"),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=destinatarios
        )
        email.attach_alternative(mensaje_html, "text/html")

        # Adjuntar logo systema si existe
        if logo_exists:
            try:
                with open(system_logo_path, 'rb') as logo_file:
                    logo_data = logo_file.read()
                    img = MIMEImage(logo_data, _subtype="png") # Asumimos png para logo.png
                    img.add_header('Content-ID', f'<{logo_cid}>')
                    email.attach(img)
            except Exception as e:
                logger.warning(f"Error adjuntando logo sistema: {e}")

        email.send()
        logger.info(f"Notificación de rechazo cliente enviada a {destinatarios}")
        return "Notificación enviada"

    except Exception as e:
        logger.error(f"Error en notificar_rechazo_cliente: {e}")
        return f"Error: {e}"

@shared_task
def notificar_rechazo_empresa(cotizacion_id):
    """
    Notifica al CLIENTE que la EMPRESA ha rechazado/anulado la cotización.
    """
    try:
        from .models import Cotizacion
        from django.core.mail import EmailMultiAlternatives
        from email.mime.image import MIMEImage
        import os
        from django.conf import settings
        
        cotizacion = Cotizacion.objects.get(id=cotizacion_id)
        empresa = cotizacion.empresa
        cliente = cotizacion.cliente
        
        if not cliente.email:
            return "Cliente sin email"

        asunto = f"Actualización de Cotización #{cotizacion.numero} - {empresa.nombre}"
        motivo_texto = f"<p><strong>Razón:</strong> {cotizacion.motivo_rechazo}</p>" if cotizacion.motivo_rechazo else ""
        
        # Logo Logic
        logo_cid = "empresa_logo"
        logo_html = ""
        if empresa.logo:
            logo_html = f'<div style="text-align:center; margin-bottom: 20px;"><img src="cid:{logo_cid}" alt="{empresa.nombre}" style="max-height: 80px; width: auto;" /></div>'
        
        mensaje_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto;">
            {logo_html}
            <div style="background-color: #ffffff; padding: 20px; border-radius: 8px; border: 1px solid #e5e7eb;">
                <h2 style="color: #ef4444; margin-top: 0;">Cotización Rechazada/Cerrada</h2>
                <p>Estimado/a <strong>{cliente.nombre}</strong>,</p>
                <p>Le informamos que su cotización <strong>#{cotizacion.numero}</strong> ha sido cerrada o rechazada por la empresa.</p>
                
                {motivo_texto}
                
                <p>Si tiene dudas, por favor contacte directamente con nosotros.</p>
                
                <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                
                <p style="color: #666; font-size: 0.9em;">
                Atte,<br>
                <strong>{empresa.nombre}</strong>
                </p>
            </div>
        </body>
        </html>
        """
        
        email = EmailMultiAlternatives(
            subject=asunto,
            body="Su cotización ha sido rechazada por la empresa. Por favor habilite HTML para ver los detalles.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[cliente.email],
            reply_to=[empresa.email] if empresa.email else None
        )
        email.attach_alternative(mensaje_html, "text/html")

        # Adjuntar logo
        if empresa.logo:
            try:
                logo_path = empresa.logo.path
                with open(logo_path, 'rb') as logo_file:
                    logo_data = logo_file.read()
                    ext = os.path.splitext(logo_path)[1].lower()
                    mime_type = 'image/jpeg' if ext in ['.jpg', '.jpeg'] else 'image/png'
                    img = MIMEImage(logo_data, _subtype=mime_type.split('/')[1])
                    img.add_header('Content-ID', f'<{logo_cid}>')
                    email.attach(img)
            except Exception as e:
                logger.warning(f"No se pudo adjuntar logo: {e}")
        
        email.send()
        logger.info(f"Notificación de rechazo empresa enviada a {cliente.email}")
        return "Notificación enviada"

    except Exception as e:
        logger.error(f"Error en notificar_rechazo_empresa: {e}")
        return f"Error: {e}"

@shared_task
def notificar_decision_empleado(cotizacion_id, decision_tipo, usuario_id):
    """
    Notifica a la empresa cuando un EMPLEADO toma una decisión (Aprobar/Rechazar)
    sobre una cotización.
    """
    try:
        from .models import Cotizacion
        from usuarios.models import Usuario
        
        cotizacion = Cotizacion.objects.get(id=cotizacion_id)
        empleado = Usuario.objects.get(id=usuario_id)
        empresa = cotizacion.empresa
        
        if not empresa.email:
            logger.warning(f"Empresa {empresa.nombre} no tiene email para notificar decisión de empleado.")
            return

        subject = f"Decisión de Empleado - Cotización #{cotizacion.numero}"
        
        mensaje = f'''
        Hola Administrador,
        
        El empleado {empleado.get_full_name()} ha tomado una decisión sobre la siguiente cotización:
        
        Cotización: #{cotizacion.numero}
        Cliente: {cotizacion.cliente.nombre}
        Decisión: {decision_tipo}
        Fecha: {cotizacion.fecha_decision.strftime('%d/%m/%Y %H:%M') if cotizacion.fecha_decision else 'Reciente'}
        
        Estado resultante: {cotizacion.get_estado_display()}
        '''
        
        if decision_tipo == 'RECHAZADA' and cotizacion.motivo_rechazo:
            mensaje += f"\\nMotivo del rechazo: {cotizacion.motivo_rechazo}"
            
        mensaje += "\\n\\nAtentamente,\\nSistema CotizApp"
        
        send_mail(
            subject,
            mensaje,
            settings.DEFAULT_FROM_EMAIL,
            [empresa.email],
            fail_silently=False,
        )
        logger.info(f"Notificación de decisión de empleado enviada a {empresa.email}")
        
    except Exception as e:
        logger.error(f"Error enviando notificación decisión empleado: {e}")

@shared_task
def procesar_ofertas_automaticas():
    """
    Tarea periódica para procesar reglas de ofertas automáticas.
    Revisa cotizaciones ENVIADA y genera ofertas si se cumplen los tiempos de espera.
    """
    from .models import Cotizacion, OfertaCotizacion, ReglaOfertaAutomatica
    from empresas.models import Empresa
    from django.utils import timezone
    from datetime import timedelta
    
    logger.info("Iniciando procesamiento de ofertas automáticas...")
    
    # 1. Obtener empresas con el sistema activo
    empresas = Empresa.objects.filter(mensajeria_automatica_activa=True)
    
    count_ofertas = 0
    
    for empresa in empresas:
        # Obtener reglas ordenadas
        reglas = list(empresa.reglas_oferta.all().order_by('orden'))
        if not reglas:
            continue
            
        # 2. Buscar cotizaciones elegibles (Enviadas, no aceptadas/rechazadas)
        # 2. Buscar cotizaciones elegibles (Enviadas O Rechazadas por Cliente)
        # "En caso de que la cotización original sea rechazada, las ofertas se continuan mandando"
        cotizaciones = Cotizacion.objects.filter(
            empresa=empresa, 
            estado__in=[Cotizacion.Estado.ENVIADA, Cotizacion.Estado.RECHAZADA]
        )
        
        for cotizacion in cotizaciones:
            try:
                # Si está rechazada, verificar que NO haya sido rechazada por la empresa (Usuario interno)
                # Si usuario_decision es None, asumimos rechazo público (Cliente).
                if cotizacion.estado == 'RECHAZADA' and cotizacion.usuario_decision:
                     # Rechazada por admin/empleado -> Detener ofertas
                     continue
                
                # Obtener la última oferta generada (si existe)
                ultima_oferta = cotizacion.ofertas_automaticas.order_by('-fecha_generacion').first()
                
                siguiente_regla = None
                base_tiempo = None
                
                if not ultima_oferta:
                    # Caso 1: No hay ofertas previas, buscar Regla #1 (o la primera disponible)
                    siguiente_regla = reglas[0]
                    # La base de tiempo es cuando se decidió enviar la cotización
                    base_tiempo = cotizacion.fecha_decision or cotizacion.fecha_creacion
                else:
                    # Caso 2: Ya hay oferta, buscar la siguiente regla
                    try:
                        idx_actual = reglas.index(ultima_oferta.regla)
                        if idx_actual + 1 < len(reglas):
                            siguiente_regla = reglas[idx_actual + 1]
                            # La base de tiempo es cuando VENCIÓ la última oferta (según requerimiento de flujo secuencial)
                            # "el tiempo que se pone al rellenar la tabla es el tiempo que va a pasar entre que expira una oferta y se lanza la otra"
                            base_tiempo = ultima_oferta.fecha_vencimiento
                        else:
                            # Ya se aplicaron todas las reglas
                            continue
                    except ValueError:
                        # La regla antigua quizás fue borrada, reiniciamos o saltamos?
                        # Por seguridad, si no machea, no hacemos nada para evitar spam
                        continue
                
                if not siguiente_regla or not base_tiempo:
                    continue
                
                tiempo_actual = timezone.now()

                # --- VALIDACIÓN DE TRASLAPE ---
                # Si la última oferta está ACTIVA y VIGENTE, no generar nueva oferta
                if ultima_oferta and ultima_oferta.estado == 'ACTIVA':
                    if ultima_oferta.fecha_vencimiento > tiempo_actual:
                        # Todavía vigente, esperar terminar
                        continue
                    else:
                        # Expired but status says ACTIVE. Mark as VENCIDA.
                        ultima_oferta.estado = 'VENCIDA'
                        ultima_oferta.save()

                # 3. Verificar si cumplió el tiempo de espera desde la base_tiempo (Generación anterior / Creación)
                delta_espera = timedelta(hours=siguiente_regla.tiempo_espera_valor)
                if siguiente_regla.tiempo_espera_unidad == 'DIAS':
                    delta_espera = timedelta(days=siguiente_regla.tiempo_espera_valor)
                elif siguiente_regla.tiempo_espera_unidad == 'MINUTOS':
                    delta_espera = timedelta(minutes=siguiente_regla.tiempo_espera_valor)
                    
                tiempo_actual = timezone.now()
                
                if tiempo_actual >= base_tiempo + delta_espera:
                    # CUMPLIÓ LA REGLA -> GENERAR OFERTA
                    
                    # A. Invalidar oferta anterior si existe
                    if ultima_oferta and ultima_oferta.estado == 'ACTIVA':
                        ultima_oferta.estado = 'VENCIDA'
                        ultima_oferta.save()
                        
                    # B. Calcular validez de nueva oferta
                    delta_validez = timedelta(hours=siguiente_regla.tiempo_validez_valor)
                    if siguiente_regla.tiempo_validez_unidad == 'DIAS':
                        delta_validez = timedelta(days=siguiente_regla.tiempo_validez_valor)
                    elif siguiente_regla.tiempo_validez_unidad == 'MINUTOS':
                        delta_validez = timedelta(minutes=siguiente_regla.tiempo_validez_valor)
                        
                    fecha_vencimiento = tiempo_actual + delta_validez
                    
                    # C. Crear nueva oferta
                    nueva_oferta = OfertaCotizacion.objects.create(
                        cotizacion=cotizacion,
                        regla=siguiente_regla,
                        descuento_porcentaje=siguiente_regla.descuento_porcentaje,
                        fecha_vencimiento=fecha_vencimiento,
                        estado='ACTIVA'
                    )
                    
                    # D. Enviar correo de notificación de oferta
                    enviar_notificacion_oferta.delay(nueva_oferta.id)
                    count_ofertas += 1
                    logger.info(f"Oferta generada para Cotización {cotizacion.numero} (Regla {siguiente_regla.orden})")
                    
            except Exception as e:
                logger.error(f"Error procesando cotización {cotizacion.id} para ofertas: {e}")
                continue

    logger.info(f"Procesamiento finalizado. {count_ofertas} ofertas generadas.")
    return f"{count_ofertas} ofertas generadas"


@shared_task
def enviar_notificacion_oferta(oferta_id):
    """
    Envía el correo notificando la nueva oferta disponible.
    """
    try:
        from .models import OfertaCotizacion
        from django.core.mail import EmailMultiAlternatives
        from email.mime.image import MIMEImage
        import os
        from django.conf import settings
        from django.utils import timezone
        
        oferta = OfertaCotizacion.objects.get(id=oferta_id)
        cotizacion = oferta.cotizacion
        cliente = cotizacion.cliente
        empresa = cotizacion.empresa
        
        if not cliente.email:
            return "Cliente sin email"

        # Calcular nuevo total para mostrar "Antes/Ahora"
        from decimal import Decimal
        descuento_factor = Decimal(str(oferta.descuento_porcentaje)) / Decimal('100')
        monto_descuento = cotizacion.total * descuento_factor
        nuevo_total = cotizacion.total - monto_descuento
        
        asunto = f"¡Descuento Especial! {oferta.descuento_porcentaje}% OFF en tu Cotización #{cotizacion.numero}"
        
        # Logo Logic
        logo_cid = "empresa_logo"
        logo_html = ""
        if empresa.logo:
            logo_html = f'<div style="text-align:center; margin-bottom: 20px;"><img src="cid:{logo_cid}" alt="{empresa.nombre}" style="max-height: 80px; width: auto;" /></div>'
            
        # Link Público
        base_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000').rstrip('/')
        public_link = f"{base_url}/cotizacion/{cotizacion.uuid}"
        
        mensaje_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto;">
            {logo_html}
            <div style="background-color: #ffffff; padding: 20px; border-radius: 8px; border: 1px solid #e5e7eb; border-top: 5px solid #F97316;">
                <h2 style="color: #F97316; margin-top: 0; text-align: center;">¡Tenemos una oferta para ti!</h2>
                
                <p>Hola <strong>{cliente.nombre}</strong>,</p>
                <p>Queremos ayudarte a tomar la mejor decisión. Por tiempo limitado, te ofrecemos un descuento exclusivo sobre tu cotización <strong>#{cotizacion.numero}</strong>.</p>
                
                <div style="background-color: #fff7ed; border: 2px dashed #F97316; border-radius: 10px; padding: 20px; margin: 25px 0; text-align: center;">
                    <p style="margin: 0; color: #666; font-size: 14px;">Total Anterior</p>
                    <p style="margin: 0; text-decoration: line-through; color: #999; font-size: 18px;">${cotizacion.total:,.0f}</p>
                    
                    <h3 style="margin: 10px 0; color: #F97316; font-size: 32px; font-weight: bold;">
                        {oferta.descuento_porcentaje}% OFF
                    </h3>
                    
                    <p style="margin: 0; color: #666; font-size: 14px;">Nuevo Total</p>
                    <p style="margin: 0; color: #1f2937; font-size: 24px; font-weight: bold;">${nuevo_total:,.0f}</p>
                    
                    <p style="margin-top: 15px; font-size: 12px; color: #ef4444;">
                        ⏳ Oferta válida hasta el {timezone.localtime(oferta.fecha_vencimiento).strftime('%d/%m/%Y %H:%M')}
                    </p>
                </div>
                
                <p style="text-align: center;">
                    <a href="{public_link}" style="display:inline-block; background-color: #F97316; color: white; padding: 12px 25px; text-decoration: none; border-radius: 6px; font-weight: bold; font-size: 16px;">
                        Aprovechar Oferta Ahora
                    </a>
                </p>
                
                <p style="font-size: 13px; color: #666; text-align: center; margin-top: 30px;">
                    Al aceptar la oferta en el enlace, el descuento se aplicará automáticamente.
                </p>
            </div>
            
             <p style="text-align: center; color: #9ca3af; font-size: 12px; margin-top: 20px;">
                Enviado por {empresa.nombre} a través de CotizApp
            </p>
        </body>
        </html>
        """
        
        email = EmailMultiAlternatives(
            subject=asunto,
            body=f"Tienes un {oferta.descuento_porcentaje}% de descuento en tu cotización. Revisa el link: {public_link}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[cliente.email],
            reply_to=[empresa.email] if empresa.email else None
        )
        email.attach_alternative(mensaje_html, "text/html")

        if empresa.logo:
            try:
                logo_path = empresa.logo.path
                with open(logo_path, 'rb') as logo_file:
                    logo_data = logo_file.read()
                    ext = os.path.splitext(logo_path)[1].lower()
                    mime_type = 'image/jpeg' if ext in ['.jpg', '.jpeg'] else 'image/png'
                    img = MIMEImage(logo_data, _subtype=mime_type.split('/')[1])
                    img.add_header('Content-ID', f'<{logo_cid}>')
                    email.attach(img)
            except Exception as e:
                logger.warning(f"No se pudo adjuntar logo en oferta: {e}")
        
        email.send()
        logger.info(f"Notificación de oferta enviada a {cliente.email}")
        
    except Exception as e:
        logger.error(f"Error en enviar_notificacion_oferta: {e}")
