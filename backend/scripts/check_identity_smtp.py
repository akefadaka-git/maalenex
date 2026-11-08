"""Manually invoked, non-sending SMTP transport/TLS/authentication check."""
import sys

from app.domains.identity.email_delivery import DeliveryUnavailable, check_smtp_connection


def main() -> int:
    try:
        check_smtp_connection()
    except (DeliveryUnavailable, OSError, Exception) as exc:
        # Deliberately do not print exception strings: SMTP errors can expose
        # server details or provider responses in public workflow logs.
        print(f"SMTP connectivity check failed ({type(exc).__name__}).")
        return 1
    print("SMTP connectivity, TLS and configured authentication succeeded; no email was sent.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
