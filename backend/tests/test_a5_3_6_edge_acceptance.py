import copy
import json
import unittest
from pathlib import Path

from scripts.a5_3_6_edge_acceptance import validate_manifest


FIXTURE = Path(__file__).parent / "fixtures" / "a5_3_6_edge_acceptance.synthetic.json"


class SyntheticEdgeAcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_checked_in_fixture_passes_only_as_synthetic(self):
        result = validate_manifest(self.manifest)
        self.assertTrue(result["valid"], result["errors"])
        self.assertEqual(
            result["production_acceptance"],
            "NOT_EVALUATED_NO_LIVE_EDGE_EVIDENCE",
        )
        statuses = {item["gate"]: item["status"] for item in result["gate_results"]}
        for gate in (f"F04-{number:02d}" for number in range(1, 12)):
            self.assertEqual(statuses[gate], "SYNTHETIC_PASS_NOT_LIVE")
        self.assertEqual(statuses["F04-12"], "NOT_EVALUATED")

    def test_endpoint_contact_is_rejected(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["meta"]["endpoint_contacted"] = True
        result = validate_manifest(manifest)
        self.assertFalse(result["valid"])
        self.assertTrue(any("endpoint_contacted" in error for error in result["errors"]))

    def test_production_data_and_secret_values_are_rejected(self):
        for field in ("production_data_present", "secret_values_included"):
            with self.subTest(field=field):
                manifest = copy.deepcopy(self.manifest)
                manifest["meta"][field] = True
                self.assertFalse(validate_manifest(manifest)["valid"])

    def test_non_reserved_hostname_is_rejected(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["meta"]["hostname"] = "api.example.com"
        self.assertFalse(validate_manifest(manifest)["valid"])

    def test_runtime_guard_drift_is_rejected(self):
        cases = (
            ("app_env", "production"),
            ("synthetic_data_only", False),
            ("database_host", "db.example.invalid"),
            ("database_name", "maalenex_prod"),
        )
        for field, value in cases:
            with self.subTest(field=field):
                manifest = copy.deepcopy(self.manifest)
                manifest["meta"][field] = value
                self.assertFalse(validate_manifest(manifest)["valid"])

    def test_duplicate_hsts_header_fails_gate_four(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["gates"]["F04-04"]["https_hsts_header_count"] = 2
        result = validate_manifest(manifest)
        self.assertFalse(result["valid"])
        gate = next(item for item in result["gate_results"] if item["gate"] == "F04-04")
        self.assertEqual(gate["status"], "SYNTHETIC_FAIL")

    def test_csp_report_only_requires_seven_days(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["gates"]["F04-05"]["observation_days"] = 6
        self.assertFalse(validate_manifest(manifest)["valid"])

    def test_unsafe_csp_directive_fails_gate_six(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["gates"]["F04-06"]["unsafe_eval"] = True
        self.assertFalse(validate_manifest(manifest)["valid"])

    def test_trace_and_unapproved_methods_are_rejected(self):
        for methods in (["GET", "TRACE"], ["GET", "PUT"], ["*"], ["GET", "GET"]):
            with self.subTest(methods=methods):
                manifest = copy.deepcopy(self.manifest)
                manifest["gates"]["F04-09"]["allowed_methods"] = methods
                self.assertFalse(validate_manifest(manifest)["valid"])

    def test_recovery_must_meet_recorded_rto(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["gates"]["F04-11"]["observed_recovery_minutes"] = 61
        self.assertFalse(validate_manifest(manifest)["valid"])

    def test_synthetic_fixture_cannot_claim_owner_or_deployment_approval(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["gates"]["F04-12"]["owner_approval"] = True
        result = validate_manifest(manifest)
        self.assertFalse(result["valid"])
        gate = next(item for item in result["gate_results"] if item["gate"] == "F04-12")
        self.assertEqual(gate["status"], "NOT_EVALUATED")


    def test_non_object_gate_entry_fails_closed_without_crashing(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["gates"]["F04-03"] = "not-an-object"
        result = validate_manifest(manifest)
        self.assertFalse(result["valid"])
        gate = next(item for item in result["gate_results"] if item["gate"] == "F04-03")
        self.assertEqual(gate["status"], "SYNTHETIC_FAIL")

    def test_missing_gate_is_rejected(self):
        manifest = copy.deepcopy(self.manifest)
        del manifest["gates"]["F04-08"]
        result = validate_manifest(manifest)
        self.assertFalse(result["valid"])
        self.assertTrue(any("missing gates" in error for error in result["errors"]))


if __name__ == "__main__":
    unittest.main()
