"""Manually invoked Gmail SMTP connectivity check; never sends email."""
import sys

from app.domains.identity.email_delivery import SmtpConnectivityError, check_smtp_connection


def main() -> int:
    # Gmail supports STARTTLS on 587 and implicit TLS on 465. Try both
    # documented submission modes because some networks block one port.
    attempts = (
        ("smtp.gmail.com:587/STARTTLS", {"port": 587, "use_ssl": False, "starttls": True}),
        ("smtp.gmail.com:465/implicit-TLS", {"port": 465, "use_ssl": True, "starttls": False}),
    )
    failures = []
    for label, options in attempts:
        try:
            check_smtp_connection(host="smtp.gmail.com", **options)
        except SmtpConnectivityError as exc:
            # Stage and exception class are safe diagnostics; never emit provider
            # response text, credentials, or authentication payloads.
            failures.append(f"{label}: {exc.stage}/{exc.cause_type}")
            print(f"SMTP attempt failed: {failures[-1]}")
        except Exception as exc:
            failures.append(f"{label}: unexpected/{type(exc).__name__}")
            print(f"SMTP attempt failed: {failures[-1]}")
        else:
            print(f"PASS: {label}; TCP/TLS and configured authentication succeeded. No email was sent.")
            return 0

    print("All Gmail SMTP connection modes failed: " + "; ".join(failures))
    return 1


if __name__ == "__main__":
    sys.exit(main())
