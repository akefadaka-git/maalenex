"""Provider-neutral delivery for account verification and recovery challenges.

SMTP is optional and uses only Python's standard library. No provider SDK or
paid service is required. SMS remains an explicit adapter contract until an
authorized, reachable provider is selected.
"""
from email.message import EmailMessage
import smtplib
import ssl
from typing import Protocol

from app.core.config import settings


class ChallengeDelivery(Protocol):
    def send(self, *, destination: str, purpose: str, token: str) -> None: ...


class SmsChallengeDelivery(Protocol):
    """Future SMS adapter contract; intentionally no provider is selected here."""

    def send(self, *, destination: str, purpose: str, token: str) -> None: ...


class DeliveryUnavailable(RuntimeError):
    pass


class SmtpEmailDelivery:
    def send(self, *, destination: str, purpose: str, token: str) -> None:
        if purpose == "identifier_verification":
            subject = "Verify your MaaleNex email address"
            instruction = "Use this one-time code to verify your email address."
            expiry = "15 minutes"
        elif purpose == "credential_enrollment":
            subject = "Complete your MaaleNex account setup"
            instruction = "Use this one-time code to finish setting your account password."
            expiry = "30 minutes"
        elif purpose == "password_recovery":
            subject = "Reset your MaaleNex account password"
            instruction = "Use this one-time code to reset your account password."
            expiry = "30 minutes"
        else:
            raise ValueError("Unsupported account challenge purpose.")

        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = f"{settings.identity_smtp_from_name} <{settings.identity_smtp_from_email}>"
        message["To"] = destination
        message.set_content(
            f"MaaleNex account security\n\n{instruction}\n\n"
            f"One-time code: {token}\n\n"
            f"This code expires in {expiry}. If you did not request this, "
            "you can ignore this message. Do not share this code with anyone.\n"
        )

        context = ssl.create_default_context()
        smtp_class = smtplib.SMTP_SSL if settings.identity_smtp_use_ssl else smtplib.SMTP
        with smtp_class(
            settings.identity_smtp_host,
            settings.identity_smtp_port,
            timeout=settings.identity_smtp_timeout_seconds,
            context=context if settings.identity_smtp_use_ssl else None,
        ) if settings.identity_smtp_use_ssl else smtp_class(
            settings.identity_smtp_host,
            settings.identity_smtp_port,
            timeout=settings.identity_smtp_timeout_seconds,
        ) as client:
            client.ehlo()
            if settings.identity_smtp_starttls and not settings.identity_smtp_use_ssl:
                client.starttls(context=context)
                client.ehlo()
            if settings.identity_smtp_username:
                client.login(settings.identity_smtp_username, settings.identity_smtp_password)
            refused = client.send_message(message)
            if refused:
                raise DeliveryUnavailable("SMTP server refused one or more recipients.")


def deliver_account_challenge(
    *, identifier_type: str, destination: str, purpose: str, token: str
) -> str:
    """Return sent, unsupported_channel, or not_configured; never log challenge data."""
    if identifier_type == "phone":
        return "unsupported_channel"
    if identifier_type != "email":
        return "unsupported_channel"
    if not settings.identity_email_delivery_enabled:
        return "not_configured"
    try:
        SmtpEmailDelivery().send(destination=destination, purpose=purpose, token=token)
    except (OSError, smtplib.SMTPException, DeliveryUnavailable, ValueError):
        return "failed"
    return "sent"



class SmtpConnectivityError(RuntimeError):
    """Sanitized SMTP connectivity failure with a safe stage identifier."""

    def __init__(self, stage: str, cause_type: str) -> None:
        self.stage = stage
        self.cause_type = cause_type
        super().__init__(f"SMTP check failed during {stage} ({cause_type}).")


def check_smtp_connection(
    *,
    host: str | None = None,
    port: int | None = None,
    use_ssl: bool | None = None,
    starttls: bool | None = None,
) -> None:
    """Validate TCP, TLS and optional authentication without sending an email.

    Optional transport overrides allow the diagnostic to check Gmail's two
    documented secure submission modes without changing application settings.
    Error details are reduced to a stage and exception class; credentials and
    provider response text are never returned.
    """
    smtp_host = host or settings.identity_smtp_host
    smtp_port = port or settings.identity_smtp_port
    ssl_enabled = settings.identity_smtp_use_ssl if use_ssl is None else use_ssl
    starttls_enabled = settings.identity_smtp_starttls if starttls is None else starttls

    if not settings.identity_email_delivery_enabled or not smtp_host:
        raise SmtpConnectivityError("configuration", "DeliveryUnavailable")

    context = ssl.create_default_context()
    client = None
    stage = "tcp_connect"
    try:
        if ssl_enabled:
            client = smtplib.SMTP_SSL(
                timeout=settings.identity_smtp_timeout_seconds,
                context=context,
            )
            client.connect(smtp_host, smtp_port)
        else:
            client = smtplib.SMTP(timeout=settings.identity_smtp_timeout_seconds)
            client.connect(smtp_host, smtp_port)

        stage = "smtp_greeting"
        client.ehlo()

        if starttls_enabled and not ssl_enabled:
            stage = "starttls"
            client.starttls(context=context)
            stage = "post_tls_ehlo"
            client.ehlo()

        if settings.identity_smtp_username:
            stage = "smtp_authentication"
            client.login(
                settings.identity_smtp_username,
                settings.identity_smtp_password,
            )
    except Exception as exc:
        raise SmtpConnectivityError(stage, type(exc).__name__) from None
    finally:
        if client is not None:
            try:
                client.quit()
            except Exception:
                try:
                    client.close()
                except Exception:
                    pass
