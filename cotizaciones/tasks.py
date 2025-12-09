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
        
        if empresa.mensaje_correo_cotizacion:
            # Reemplazar variables básicas si existen en el texto
            mensaje_texto = empresa.mensaje_correo_cotizacion.format(
                cliente_nombre=cliente.nombre,
                cotizacion_numero=cotizacion.numero,
                empresa_nombre=empresa.nombre,
                total=f"${cotizacion.total:,.0f}",
                empresa_logo=logo_html
            )
            # Convertir saltos de línea a <br> para HTML
            mensaje_html = mensaje_texto.replace('\n', '<br>')
        else:
            # Mensaje por defecto (sin logo, el usuario puede agregarlo con {empresa_logo})
            mensaje_html = f"""
            <p>Estimado/a <strong>{escape(cliente.nombre)}</strong>,</p>
            <p>Adjunto encontrará la cotización <strong>#{cotizacion.numero}</strong> solicitada.</p>
            <p><strong>Detalles:</strong><br>
            Total: ${cotizacion.total:,.0f}</p>
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
        
        # 3. Generar y Adjuntar PDF
        try:
            pdf_content = cotizacion.generar_pdf()
            filename = f"Cotizacion_{cotizacion.numero}.pdf"
            email.attach(filename, pdf_content, 'application/pdf')
            logger.info("PDF generado y adjuntado correctamente")
        except Exception as e:
            logger.error(f"Error generando PDF: {e}")
            # Enviamos el correo igual, pero avisando en el log
            
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
