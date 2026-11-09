from app.domains.audit.service import redact_metadata


def test_audit_metadata_redacts_sensitive_keys_recursively():
    result = redact_metadata({
        "action": "booking.created",
        "phone": "+251900000000",
        "nested": {"token": "synthetic-secret", "count": 2},
    })
    assert result["action"] == "booking.created"
    assert result["phone"] == "[REDACTED]"
    assert result["nested"]["token"] == "[REDACTED]"
    assert result["nested"]["count"] == 2


def test_audit_metadata_redacts_sensitive_keys_inside_arrays_of_objects():
    result = redact_metadata({
        "events": [
            {"type": "registration", "email": "person@example.test"},
            {"type": "verification", "verification_token": "one-time-secret"},
        ],
    })

    assert result == {
        "events": [
            {"type": "registration", "email": "[REDACTED]"},
            {"type": "verification", "verification_token": "[REDACTED]"},
        ],
    }


def test_audit_metadata_redacts_nested_arrays_and_mixed_values():
    result = redact_metadata({
        "payload": [
            "safe-label",
            7,
            None,
            {
                "authorization": "Bearer synthetic-token",
                "children": [
                    {"phone": "+251911111111", "label": "contact"},
                    ["safe-nested-value", {"credential_id": "credential-secret"}],
                ],
            },
        ],
    })

    assert result == {
        "payload": [
            "safe-label",
            7,
            None,
            {
                "authorization": "[REDACTED]",
                "children": [
                    {"phone": "[REDACTED]", "label": "contact"},
                    ["safe-nested-value", {"credential_id": "[REDACTED]"}],
                ],
            },
        ],
    }


def test_audit_metadata_preserves_safe_array_structure_and_values():
    source = {
        "attempts": [1, 2, 3],
        "labels": ["created", "verified"],
        "nested": {"flags": [True, False, None]},
    }

    assert redact_metadata(source) == source
