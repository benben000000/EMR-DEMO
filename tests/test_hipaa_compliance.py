# tests/test_hipaa_compliance.py
import sys
import os
import unittest
import json
import urllib.request
import urllib.parse
import threading
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.domain import (
    mask_ephi,
    generate_audit_checksum,
    check_rbac_permission,
    generate_pure_hmac_token,
    verify_pure_hmac_token
)
import db_manager
from serve_demo import G1HealthRequestHandler, create_session_token, verify_session_token

class TestHIPAACompliance(unittest.TestCase):
    def test_ephi_safe_harbor_masking(self):
        # Phone masking
        phone = "+63 917 123 4567"
        masked_phone = mask_ephi(phone, "phone")
        self.assertIn("***", masked_phone)
        self.assertTrue(masked_phone.endswith("4567"))
        self.assertFalse("123" in masked_phone)

        # Insurance ID masking
        ins = "PH-99281-90"
        masked_ins = mask_ephi(ins, "insurance")
        self.assertIn("****", masked_ins)
        self.assertTrue(masked_ins.startswith("PH-"))
        self.assertTrue(masked_ins.endswith("90"))

        # Address masking
        addr = "123 Mabini St, Quezon City, Metro Manila"
        masked_addr = mask_ephi(addr, "address")
        self.assertIn("[Restricted Address]", masked_addr)
        self.assertNotIn("123 Mabini St", masked_addr)

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

if __name__ == "__main__":
    unittest.main()
