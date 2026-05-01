"""
SmtpEmailService — отправка транзакционных писем через SMTP (aiosmtplib).
Если SMTP не настроен (SMTP_HOST пуст), ссылка сброса пароля логируется в stdout.
"""
from __future__ import annotations

import logging

from src.infrastructure.config.settings import settings

logger = logging.getLogger(__name__)


async def send_password_reset_email(to_email: str, reset_token: str) -> None:
    """Отправляет письмо со ссылкой сброса пароля."""
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"

    if not settings.SMTP_HOST:
        logger.warning(
            "[DEV] SMTP не настроен. Ссылка сброса пароля: %s", reset_url
        )
        return

    try:
        import aiosmtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Сброс пароля — SalesPilot AI CRM"
        msg["From"] = settings.SMTP_FROM
        msg["To"] = to_email

        html_body = f"""
        <html><body>
          <p>Вы запросили сброс пароля для вашего аккаунта SalesPilot AI CRM.</p>
          <p>
            <a href="{reset_url}" style="
              display:inline-block;padding:10px 20px;
              background:#00A8E8;color:#fff;text-decoration:none;border-radius:6px;
            ">Сбросить пароль</a>
          </p>
          <p>Ссылка действительна {settings.PASSWORD_RESET_EXPIRE_MINUTES} минут.</p>
          <p>Если вы не запрашивали сброс пароля, проигнорируйте это письмо.</p>
        </body></html>
        """
        msg.attach(MIMEText(html_body, "html"))

        await aiosmtplib.send(
            msg,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER or None,
            password=settings.SMTP_PASSWORD or None,
            start_tls=True,
        )
    except Exception as exc:  # noqa: BLE001
        logger.error("Не удалось отправить письмо сброса пароля на %s: %s", to_email, exc)
