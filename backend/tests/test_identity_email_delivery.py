from email.message import EmailMessage

from app.core.config import settings
from app.domains.identity import email_delivery


class FakeSMTP:
    sent_messages = []

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def ehlo(self):
        return None

    def starttls(self, context=None):
        return None

    def login(self, username, password):
        return None

    def send_message(self, message):
        assert isinstance(message, EmailMessage)
        self.sent_messages.append(message)
        return {}


def _enable_smtp(monkeypatch):
    monkeypatch.setattr(settings, "identity_email_delivery_enabled", True)
    monkeypatch.setattr(settings, "identity_smtp_host", "smtp.example.invalid")
    monkeypatch.setattr(settings, "identity_smtp_port", 587)
    monkeypatch.setattr(settings, "identity_smtp_username", None)
    monkeypatch.setattr(settings, "identity_smtp_password", None)
    monkeypatch.setattr(settings, "identity_smtp_from_email", "no-reply@maalenex.invalid")
    monkeypatch.setattr(settings, "identity_smtp_from_name", "MaaleNex Test")
    monkeypatch.setattr(settings, "identity_smtp_starttls", True)
    monkeypatch.setattr(settings, "identity_smtp_use_ssl", False)
    monkeypatch.setattr(settings, "identity_smtp_timeout_seconds", 5)
    FakeSMTP.sent_messages = []
    monkeypatch.setattr(email_delivery.smtplib, "SMTP", FakeSMTP)


def test_email_challenge_uses_smtp_and_does_not_include_other_secrets(monkeypatch):
    _enable_smtp(monkeypatch)
    token = "synthetic-one-time-token"

    result = email_delivery.deliver_account_challenge(
        identifier_type="email",
        destination="person@example.invalid",
        purpose="identifier_verification",
        token=token,
    )

    assert result == "sent"
    message = FakeSMTP.sent_messages[0]
    assert message["To"] == "person@example.invalid"
    assert token in message.get_content()
    assert "expires in 15 minutes" in message.get_content()
    assert "SMTP_PASSWORD" not in message.get_content()


def test_delivery_is_disabled_by_default_and_sms_is_not_misrouted(monkeypatch):
    monkeypatch.setattr(settings, "identity_email_delivery_enabled", False)
    assert email_delivery.deliver_account_challenge(
        identifier_type="email", destination="person@example.invalid",
        purpose="password_recovery", token="synthetic-token",
    ) == "not_configured"
    assert email_delivery.deliver_account_challenge(
        identifier_type="phone", destination="+251911234567",
        purpose="password_recovery", token="synthetic-token",
    ) == "unsupported_channel"


def test_smtp_failure_is_reported_without_raising(monkeypatch):
    _enable_smtp(monkeypatch)

    class BrokenSMTP(FakeSMTP):
        def starttls(self, context=None):
            raise OSError("synthetic transport failure")

    monkeypatch.setattr(email_delivery.smtplib, "SMTP", BrokenSMTP)
    assert email_delivery.deliver_account_challenge(
        identifier_type="email", destination="person@example.invalid",
        purpose="password_recovery", token="synthetic-token",
    ) == "failed"
