# tests/test_hipaa_compliance.py
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import db_manager
from core.domain import (
    check_rbac_permission,
    generate_audit_checksum,
    generate_pure_hmac_token,
    mask_ephi,
    verify_pure_hmac_token,
)


class TestHIPAACompliance(unittest.TestCase):
    def test_ephi_safe_harbor_masking(self):
        # US Phone masking
        phone = "+1 (617) 555-0199"
        masked_phone = mask_ephi(phone, "phone")
        self.assertIn("***", masked_phone)
        self.assertTrue(masked_phone.endswith("0199"))
        self.assertFalse("555" in masked_phone)

        # US Insurance ID masking
        ins = "MC-99281-90"
        masked_ins = mask_ephi(ins, "insurance")
        self.assertIn("****", masked_ins)
        self.assertTrue(masked_ins.startswith("MC-"))
        self.assertTrue(masked_ins.endswith("90"))

        # US Address masking
        addr = "100 Healthcare Way, Suite 400, Boston, MA"
        masked_addr = mask_ephi(addr, "address")
        self.assertIn("[Restricted Address]", masked_addr)
        self.assertNotIn("100 Healthcare Way", masked_addr)

    def test_tamper_evident_audit_checksum(self):
        secret = "hipaa_test_secret_key_2026"
        ts = "2026-09-02 10:00:00"
        sig1 = generate_audit_checksum(secret, "doctor", "doctor", "VIEW_CHART", "patients", "G1-001", ts)
        sig2 = generate_audit_checksum(secret, "doctor", "doctor", "VIEW_CHART", "patients", "G1-001", ts)
        self.assertEqual(sig1, sig2)

        # Tampered action must produce different checksum
        sig_tampered = generate_audit_checksum(secret, "doctor", "doctor", "DELETE_CHART", "patients", "G1-001", ts)
        self.assertNotEqual(sig1, sig_tampered)

    def test_rbac_least_privilege_enforcement(self):
        # Admin has full access
        self.assertTrue(check_rbac_permission("admin", "patients", "delete"))
        self.assertTrue(check_rbac_permission("admin", "billing_invoices", "create"))

        # Doctor can read/write clinical, but cannot delete accounting vouchers
        self.assertTrue(check_rbac_permission("doctor", "prescriptions", "create"))
        self.assertTrue(check_rbac_permission("doctor", "lab_orders", "update"))
        self.assertFalse(check_rbac_permission("doctor", "accounting_vouchers", "create"))
        self.assertFalse(check_rbac_permission("doctor", "accounting_vouchers", "delete"))

        # Nurse can update beds and view patients, but cannot create billing invoices
        self.assertTrue(check_rbac_permission("nurse", "adt_beds", "update"))
        self.assertTrue(check_rbac_permission("nurse", "patients", "read"))
        self.assertFalse(check_rbac_permission("nurse", "billing_invoices", "create"))
        self.assertFalse(check_rbac_permission("nurse", "patients", "delete"))

        # Accountant can handle financial vouchers and invoices, but cannot prescribe medications
        self.assertTrue(check_rbac_permission("accountant", "accounting_vouchers", "create"))
        self.assertFalse(check_rbac_permission("accountant", "prescriptions", "create"))

    def test_audit_logs_db_integrity(self):
        db_manager.log_audit_event(
            user_id="audit_tester",
            action_name="TEST_HIPAA_EVENT",
            ip_address="127.0.0.1",
            status="SUCCESS",
            role="admin",
            entity="test_entity",
            record_id="REC-999",
            details="Automated compliance test"
        )
        logs = db_manager.get_all_audit_logs()
        self.assertTrue(len(logs) > 0)
        latest = logs[0]
        self.assertEqual(latest["user_id"], "audit_tester")
        self.assertEqual(latest["action_name"], "TEST_HIPAA_EVENT")
        self.assertTrue("checksum" in latest)
        self.assertTrue(len(latest["checksum"]) == 64) # SHA-256 length

    def test_session_inactivity_timeout_guardrail(self):
        # 15-Minute inactivity automatic logoff (§ 164.312(a)(2)(iii))
        secret = "hipaa_session_secret_2026"
        token = generate_pure_hmac_token(secret, "doctor_01", "doctor", timestamp=1000)

        # Valid within 15 minutes (900 seconds)
        valid = verify_pure_hmac_token(secret, token, max_age_seconds=900, current_time=1500)
        self.assertIsNotNone(valid)
        self.assertEqual(valid["username"], "doctor_01")

        # Expired after 15 minutes
        expired = verify_pure_hmac_token(secret, token, max_age_seconds=900, current_time=2000)
        self.assertIsNone(expired)

    def test_minimum_necessary_safe_harbor_query(self):
        # Non-clinical roles receive masked ePHI
        state = db_manager.get_full_emr_state(role="billing")
        patients = state.get("patients", [])
        if patients:
            sample = patients[0]
            if sample.get("address"):
                self.assertEqual(sample["address"], "[Restricted Address]")
            if sample.get("phone"):
                self.assertIn("***", sample["phone"])

if __name__ == "__main__":
    unittest.main()
