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
