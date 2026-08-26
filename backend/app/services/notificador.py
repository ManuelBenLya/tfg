import requests
import smtplib
import logging
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings
from app.models.models import Usuario, Servidor

logger = logging.getLogger("uvicorn.error")

def enviar_notificaciones_alerta(db, servidor: Servidor, mensaje: str):
    """
    Envía notificaciones de alerta a todos los usuarios interesados:
    - Administradores de la misma empresa.
    - Técnicos asignados directamente a este servidor.
    Las notificaciones se envían por los canales que cada usuario tenga configurados:
    - Discord (Webhook)
    - Slack (Webhook)
    - Email (SMTP)
    """
    # 1. Obtener los administradores de la empresa del servidor
    admins = db.query(Usuario).filter(
        Usuario.empresa_id == servidor.empresa_id,
        Usuario.rol.in_(["admin", "superadmin"])
    ).all()

    # 2. Obtener los técnicos (usuarios) asignados a este servidor
    tecnicos = db.query(Usuario).join(Usuario.servidores_supervisados).filter(
        Usuario.empresa_id == servidor.empresa_id,
        Usuario.rol == "usuario",
        Servidor.id == servidor.id
    ).all()

    # Combinamos ambas listas sin duplicados
    usuarios_a_notificar = list({u.id: u for u in (admins + tecnicos)}.values())

    logger.info(f"Notificando alerta a {len(usuarios_a_notificar)} usuarios para el servidor {servidor.nombre}")

    for user in usuarios_a_notificar:
        # --- DISCORD WEBHOOK ---
        if user.discord_webhook and user.discord_webhook.strip():
            try:
                payload = {
                    "embeds": [
                        {
                            "title": "🚨 ALERTA DE INFRAESTRUCTURA (SITEM)",
                            "description": f"Se ha detectado una anomalía en el servidor **{servidor.nombre}**.",
                            "color": 15158332,  # Rojo
                            "fields": [
                                {"name": "Servidor", "value": servidor.nombre, "inline": True},
                                {"name": "Dirección IP", "value": servidor.ip_direccion, "inline": True},
                                {"name": "Detalle", "value": mensaje, "inline": False},
                                {"name": "Fecha", "value": datetime.now().strftime("%d/%m/%Y %H:%M:%S"), "inline": False}
                            ]
                        }
                    ]
                }
                res = requests.post(user.discord_webhook.strip(), json=payload, timeout=5)
                logger.info(f"Notificación de Discord enviada a {user.email} (Status: {res.status_code})")
            except Exception as e:
                logger.error(f"Error al enviar notificación a Discord para {user.email}: {e}")

        # --- SLACK WEBHOOK ---
        if user.slack_webhook and user.slack_webhook.strip():
            try:
                payload = {
                    "text": f"🚨 *ALERTA DE INFRAESTRUCTURA (SITEM)* 🚨\n*Servidor:* {servidor.nombre} (IP: {servidor.ip_direccion})\n*Detalle:* {mensaje}\n*Fecha:* {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
                }
                res = requests.post(user.slack_webhook.strip(), json=payload, timeout=5)
                logger.info(f"Notificación de Slack enviada a {user.email} (Status: {res.status_code})")
            except Exception as e:
                logger.error(f"Error al enviar notificación a Slack para {user.email}: {e}")

        # --- EMAIL (SMTP) ---
        if user.recibir_alertas_email is not False:
            # Intentamos obtener la configuración SMTP de la empresa del servidor
            empresa = servidor.empresa
            
            smtp_host = empresa.smtp_host if (empresa and empresa.smtp_host) else getattr(settings, "SMTP_HOST", None)
            smtp_port = empresa.smtp_port if (empresa and empresa.smtp_port) else getattr(settings, "SMTP_PORT", 587)
            smtp_user = empresa.smtp_user if (empresa and empresa.smtp_user) else getattr(settings, "SMTP_USER", None)
            smtp_password = empresa.smtp_password if (empresa and empresa.smtp_password) else getattr(settings, "SMTP_PASSWORD", None)
            smtp_from = empresa.smtp_from if (empresa and empresa.smtp_from) else getattr(settings, "SMTP_FROM", "alertas@sitem.com")

            # Si no hay credenciales configuradas (ni de empresa ni globales), mockeamos en logs
            if not smtp_user or not smtp_password or not smtp_host:
                logger.info(f"[EMAIL MOCK] Enviando alerta por correo a {user.email} -> {mensaje}")
            else:
                try:
                    msg = MIMEMultipart()
                    msg['From'] = smtp_from
                    msg['To'] = user.email
                    msg['Subject'] = f" ALERTA SMI: {servidor.nombre}"
                    
                    body = f"""
                    SMI - Sistema de Monitorización de Infraestructura
                    
                    Se ha generado una alerta en uno de tus servidores:
                    
                    Servidor: {servidor.nombre}
                    IP: {servidor.ip_direccion}
                    Alerta: {mensaje}
                    Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
                    
                    Por favor, accede al panel de control para más detalles.
                    """
                    msg.attach(MIMEText(body, 'plain'))
                    
                    # Soporte para SSL en puerto 465 (necesario en hosting como Render que bloquean el 587)
                    if smtp_port == 465:
                        with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
                            server.login(smtp_user, smtp_password)
                            server.send_message(msg)
                    else:
                        with smtplib.SMTP(smtp_host, smtp_port) as server:
                            server.starttls()
                            server.login(smtp_user, smtp_password)
                            server.send_message(msg)
                    logger.info(f"Correo de alerta enviado exitosamente a {user.email}")
                except Exception as e:
                    logger.error(f"Error al enviar correo electrónico a {user.email}: {e}")
