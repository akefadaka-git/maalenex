#!/usr/bin/env python3
"""Offline validator for synthetic F-04 acceptance fixtures; never probes live systems."""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

GATE_IDS = tuple(f"F04-{number:02d}" for number in range(1, 13))
LOCAL_DB_HOSTS = {"localhost", "127.0.0.1", "::1"}
ALLOWED_METHODS = {"GET", "HEAD", "POST", "DELETE", "OPTIONS"}


def _is_sha(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{40}", value) is not None


def _timestamp_is_valid(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return True


def _gate_assertions(gates: dict[str, Any]) -> dict[str, list[str]]:
    gates = {gate: value if isinstance(value, dict) else {} for gate, value in gates.items()}
    issues: dict[str, list[str]] = {gate: [] for gate in GATE_IDS}

    def expect(gate: str, key: str, expected: Any) -> None:
        actual = gates.get(gate, {}).get(key)
        if actual != expected:
            issues[gate].append(f"{key}: expected {expected!r}, got {actual!r}")

    def truthy_text(gate: str, key: str) -> None:
        value = gates.get(gate, {}).get(key)
        if not isinstance(value, str) or not value.strip():
            issues[gate].append(f"{key}: expected a non-empty synthetic reference")

    # F04-01: the public edge is the only HSTS/CSP policy owner.
    expect("F04-01", "hsts_owner", "edge")
    expect("F04-01", "csp_owner", "edge")
    expect("F04-01", "app_emits_hsts", False)
    expect("F04-01", "app_emits_csp", False)
    expect("F04-01", "duplicate_policy_headers", False)

    # F04-02: TLS profile assertions; the fixture is not an actual TLS scan.
    versions = gates.get("F04-02", {}).get("tls_versions")
    if not isinstance(versions, list) or "1.2" not in versions or any(
        version not in {"1.2", "1.3"} for version in versions
    ):
        issues["F04-02"].append("tls_versions: expected only TLS 1.2/1.3 and must include 1.2")
    for key in ("certificate_chain_valid", "hostname_san_matches"):
        expect("F04-02", key, True)
    for key in ("weak_protocols_enabled", "weak_ciphers_enabled"):
        expect("F04-02", key, False)

    # F04-03: canonical HTTPS redirects without host reflection or loops.
    expect("F04-03", "canonical_https_redirect", True)
    expect("F04-03", "open_redirect", False)
    expect("F04-03", "host_reflection", False)
    expect("F04-03", "redirect_loop", False)

    # F04-04: one staged HSTS value on HTTPS and none on HTTP.
    expect("F04-04", "http_has_hsts", False)
    expect("F04-04", "https_hsts_header_count", 1)
    if gates.get("F04-04", {}).get("max_age_seconds") not in {300, 86400, 31536000}:
        issues["F04-04"].append("max_age_seconds: expected an approved H0-H3 staged value")
    expect("F04-04", "include_subdomains", False)
    expect("F04-04", "preload", False)

    # F04-05: report-only observation must cover at least seven representative days.
    expect("F04-05", "csp_mode", "report-only")
    days = gates.get("F04-05", {}).get("observation_days")
    if not isinstance(days, int) or isinstance(days, bool) or days < 7:
        issues["F04-05"].append("observation_days: expected an integer >= 7")
    expect("F04-05", "unexplained_first_party_violations", 0)
    expect("F04-05", "representative_workflows_exercised", True)

    # F04-06: enforcement and browser regression; no unsafe policy escape hatches.
    expect("F04-06", "csp_mode", "enforce")
    expect("F04-06", "browser_regression_passed", True)
    expect("F04-06", "unsafe_eval", False)
    expect("F04-06", "unsafe_inline", False)

    # F04-07: origin must not be publicly reachable around the edge.
    expect("F04-07", "origin_publicly_reachable", False)
    expect("F04-07", "origin_access_limited_to_edge", True)

    # F04-08: exact immediate-peer and one-hop forwarding contract.
    for key in (
        "immediate_peer_allowlist_enforced",
        "forwarding_headers_overwritten",
        "single_hop_only",
        "malformed_metadata_rejected",
        "client_ip_single_value",
    ):
        expect("F04-08", key, True)

    # F04-09: bounded ingress controls and no shared cache for private responses.
    methods = gates.get("F04-09", {}).get("allowed_methods")
    if (
        not isinstance(methods, list)
        or not methods
        or any(not isinstance(method, str) or method.upper() not in ALLOWED_METHODS for method in methods)
        or len({method.upper() for method in methods}) != len(methods)
    ):
        issues["F04-09"].append("allowed_methods: expected a unique non-empty subset of GET/HEAD/POST/DELETE/OPTIONS")
    for key in (
        "request_limits_bounded",
        "timeouts_bounded",
        "rate_controls_enabled",
        "private_response_shared_cache_disabled",
        "unknown_hosts_denied",
    ):
        expect("F04-09", key, True)

    # F04-10: redaction and alert routing are asserted, not actually exercised.
    expect("F04-10", "sensitive_log_fields_redacted", True)
    expect("F04-10", "alert_delivery_tested", True)
    truthy_text("F04-10", "synthetic_oncall_reference")

    # F04-11: rollback meets an explicitly recorded synthetic RTO and preserves controls.
    expect("F04-11", "rollback_rehearsed", True)
    rto = gates.get("F04-11", {}).get("approved_rto_minutes")
    observed = gates.get("F04-11", {}).get("observed_recovery_minutes")
    if not isinstance(rto, int) or isinstance(rto, bool) or rto <= 0:
        issues["F04-11"].append("approved_rto_minutes: expected a positive integer")
    if not isinstance(observed, int) or isinstance(observed, bool) or observed < 0:
        issues["F04-11"].append("observed_recovery_minutes: expected a non-negative integer")
    elif isinstance(rto, int) and not isinstance(rto, bool) and rto > 0 and observed > rto:
        issues["F04-11"].append("observed_recovery_minutes: exceeds approved_rto_minutes")
    expect("F04-11", "authentication_preserved", True)
    expect("F04-11", "csrf_preserved", True)
    expect("F04-11", "runtime_guards_preserved", True)

    # F04-12 is deliberately not attestable by synthetic data.
    expect("F04-12", "owner_approval", False)
    expect("F04-12", "deployment_authorized", False)
    return issues


def validate_manifest(manifest: Any) -> dict[str, Any]:
    errors: list[str] = []
    gate_issues: dict[str, list[str]] = {gate: [] for gate in GATE_IDS}

    if not isinstance(manifest, dict):
        return {
            "valid": False,
            "production_acceptance": "NOT_EVALUATED_NO_LIVE_EDGE_EVIDENCE",
            "gate_results": [],
            "errors": ["manifest must be a JSON object"],
        }

    meta = manifest.get("meta")
    gates = manifest.get("gates")
    if manifest.get("schema_version") != 1:
        errors.append("schema_version must equal 1")
    if not isinstance(meta, dict):
        errors.append("meta must be an object")
        meta = {}
    if not isinstance(gates, dict):
        errors.append("gates must be an object")
        gates = {}

    if meta.get("evidence_mode") != "synthetic-fixture":
        errors.append("evidence_mode must be synthetic-fixture")
    if meta.get("environment") not in {"development", "test"}:
        errors.append("environment must be development or test")
    hostname = meta.get("hostname")
    if not isinstance(hostname, str) or not hostname.endswith(".invalid"):
        errors.append("hostname must use the reserved .invalid suffix")
    if not _is_sha(meta.get("source_commit")):
        errors.append("source_commit must be a 40-character lowercase Git SHA")
    revision = meta.get("config_revision")
    if not isinstance(revision, str) or not revision.startswith("synthetic-"):
        errors.append("config_revision must start with synthetic-")
    if not _timestamp_is_valid(meta.get("captured_at")):
        errors.append("captured_at must be an ISO-8601 timestamp")
    for key in ("endpoint_contacted", "production_data_present", "secret_values_included"):
        if meta.get(key) is not False:
            errors.append(f"{key} must be false in a synthetic fixture")
    if meta.get("app_env") not in {"development", "test"}:
        errors.append("app_env must remain development or test")
    if meta.get("synthetic_data_only") is not True:
        errors.append("synthetic_data_only must be true")
    if meta.get("database_host") not in LOCAL_DB_HOSTS:
        errors.append("database_host must be loopback-only")
    if meta.get("database_name") != "maalenex_dev":
        errors.append("database_name must remain maalenex_dev")

    missing = sorted(set(GATE_IDS) - set(gates))
    extra = sorted(set(gates) - set(GATE_IDS))
    if missing:
        errors.append("missing gates: " + ", ".join(missing))
    if extra:
        errors.append("unexpected gates: " + ", ".join(extra))

    for gate in GATE_IDS:
        if not isinstance(gates.get(gate), dict):
            gate_issues[gate].append("gate assertion must be an object")

    if not errors and all(not gate_issues[gate] for gate in GATE_IDS):
        gate_issues = _gate_assertions(gates)
    elif not errors:
        # Preserve structural errors and still evaluate well-formed gate assertions.
        evaluated = _gate_assertions(gates)
        for gate in GATE_IDS:
            gate_issues[gate].extend(evaluated[gate])

    results = []
    for gate in GATE_IDS:
        if gate == "F04-12":
            status = "NOT_EVALUATED"
        else:
            status = "SYNTHETIC_PASS_NOT_LIVE" if not gate_issues[gate] and not errors else "SYNTHETIC_FAIL"
        results.append({"gate": gate, "status": status, "issues": gate_issues[gate]})

    return {
        "valid": not errors and all(not gate_issues[gate] for gate in GATE_IDS),
        "production_acceptance": "NOT_EVALUATED_NO_LIVE_EDGE_EVIDENCE",
        "gate_results": results,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path, help="path to a synthetic-only JSON fixture")
    args = parser.parse_args()
    try:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"valid": False, "errors": [str(exc)]}, indent=2))
        return 2

    result = validate_manifest(manifest)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
