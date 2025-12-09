from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

@shared_task
def enviar_credenciales_empleado(usuario_id, password_temporal):
    """
    Envía un correo con las credenciales temporales al nuevo empleado.
    """
    try:
        from .models import Usuario
        from django.core.mail import EmailMultiAlternatives
        from django.template.loader import render_to_string
        from django.utils.html import strip_tags
        
        usuario = Usuario.objects.get(id=usuario_id)
        
        asunto = f"Bienvenido a CotizApp - Tus Credenciales"
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
        login_url = f"{frontend_url}/login"
        
        # Mensaje HTML
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px; }}
                .header {{ background-color: #f8f9fa; padding: 15px; text-align: center; border-bottom: 1px solid #ddd; }}
                .content {{ padding: 20px; }}
                .credentials {{ background-color: #e9ecef; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .btn {{ display: inline-block; padding: 10px 20px; background-color: #007bff; color: white; text-decoration: none; border-radius: 5px; font-weight: bold; }}
                .footer {{ margin-top: 20px; font-size: 12px; color: #777; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Bienvenido a CotizApp</h2>
                </div>
                <div class="content">
                    <p>Hola <strong>{usuario.first_name}</strong>,</p>
                    <p>Has sido registrado exitosamente como colaborador en CotizApp.</p>
                    
                    <p>Para acceder a tu cuenta, utiliza las siguientes credenciales temporales:</p>
                    
                    <div class="credentials">
                        <p><strong>Usuario/Correo:</strong> {usuario.email}</p>
                        <p><strong>Contraseña Temporal:</strong> {password_temporal}</p>
                    </div>
                    
                    <p>Por seguridad, se te pedirá cambiar esta contraseña la primera vez que inicies sesión.</p>
                    
                    <div style="text-align: center; margin-top: 30px;">
                        <a href="{login_url}" class="btn">Iniciar Sesión Ahora</a>
                    </div>
                </div>
                <div class="footer">
                    <p>Si el botón no funciona, copia y pega este enlace en tu navegador:<br>
                    {login_url}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Versión texto plano
        text_content = strip_tags(html_content)
        
        msg = EmailMultiAlternatives(asunto, text_content, settings.DEFAULT_FROM_EMAIL, [usuario.email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        
        logger.info(f"Correo de credenciales enviado a {usuario.email}")
        
    except Exception as e:
        logger.error(f"Error enviando credenciales a usuario {usuario_id}: {str(e)}")
