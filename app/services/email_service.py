import logging
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Sends email notifications via SMTP using stdlib (no extra dependencies)."""

    def send_consent_notification(
        self, full_name: str, document_id: str, client_email: str, reference: str, submitted_at: str
    ) -> None:
        """Notify the studio when a new consent form is submitted.

        Fails silently — a broken SMTP config must never block the main flow.
        """
        if not settings.SMTP_USER or not settings.NOTIFICATION_EMAIL:
            return

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"[KameArt] Nuevo consentimiento \u2014 {full_name} [{reference}]"
            msg["From"] = settings.SMTP_USER
            msg["To"] = settings.NOTIFICATION_EMAIL

            html = f"""
            <html><body style="font-family:Arial,sans-serif;color:#222;max-width:520px;margin:auto;">
              <h2 style="background:#1a1a1a;color:#fff;padding:12px 16px;border-radius:4px;">
                KameArt \u2014 Nuevo Consentimiento Informado
              </h2>
              <table style="width:100%;border-collapse:collapse;font-size:14px;">
                <tr><td style="padding:6px 0;font-weight:bold;width:180px;">Referencia</td>
                    <td style="padding:6px 0;">{reference}</td></tr>
                <tr><td style="padding:6px 0;font-weight:bold;">Nombre</td>
                    <td style="padding:6px 0;">{full_name}</td></tr>
                <tr><td style="padding:6px 0;font-weight:bold;">Documento</td>
                    <td style="padding:6px 0;">{document_id}</td></tr>
                <tr><td style="padding:6px 0;font-weight:bold;">Email cliente</td>
                    <td style="padding:6px 0;">{client_email}</td></tr>
                <tr><td style="padding:6px 0;font-weight:bold;">Registrado</td>
                    <td style="padding:6px 0;">{submitted_at}</td></tr>
              </table>
              <p style="color:#666;font-size:12px;margin-top:24px;">
                El PDF del consentimiento y la firma est\u00e1n disponibles en Google Drive.
              </p>
            </body></html>
            """
            msg.attach(MIMEText(html, "html"))

            context = ssl.create_default_context()
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.ehlo()
                server.starttls(context=context)
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
        except Exception as exc:
            logger.error("Email notification failed: %s", exc)


email_service = EmailService()
