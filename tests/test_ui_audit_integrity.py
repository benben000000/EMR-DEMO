# tests/test_ui_audit_integrity.py
import os
import re
import unittest

root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

class TestUIAuditIntegrity(unittest.TestCase):
    def test_zero_emojis_in_frontend_and_servers(self):
        emoji_pattern = re.compile("[\U00010000-\U0010ffff\u2600-\u27ff\u2300-\u23ff\u2b50\u2b55\u200d\u20e3]")
        files_to_check = [
            "dashboard.html",
            "index.html",
            "public/dashboard.html",
            "public/index.html",
            "serve_demo.py",
            "api/index.py"
        ]

        for rel_path in files_to_check:
            abs_p = os.path.join(root, rel_path)
            if not os.path.exists(abs_p):
                continue
            with open(abs_p, encoding="utf-8") as f:
                content = f.read()
            matches = emoji_pattern.findall(content)
            self.assertEqual(
                len(matches), 0,
                f"File {rel_path} still contains {len(matches)} emojis: {[hex(ord(c)) for c in set(matches)]}"
            )

    def test_zero_glowing_pulse_animations(self):
        with open(os.path.join(root, "dashboard.html"), encoding="utf-8") as f:
            dash = f.read()

        # Assert no pulse-red animation or neon box-shadows
        self.assertNotIn("pulse-red", dash)
        self.assertNotIn("box-shadow: 0 4px 15px rgba(220, 38, 38, 0.5)", dash)
        self.assertNotIn('<span class="badge-new">NEW</span>', dash)

    def test_all_35_views_present_in_dashboard(self):
        with open(os.path.join(root, "dashboard.html"), encoding="utf-8") as f:
            dash = f.read()

        expected_views = [
            "view-dashboard", "view-patient-reg", "view-appointments", "view-adt",
            "view-emergency", "view-clinical", "view-nursing", "view-ot",
            "view-laboratory", "view-radiology", "view-pharmacy", "view-aicrm",
            "view-patient360", "view-ehs", "view-telehealth", "view-billing",
            "view-whitelabel", "view-clinicalsettings", "view-inventory",
            "view-procurement", "view-substore", "view-fixedassets", "view-accounting",
            "view-claimmgmt", "view-incentive", "view-verification", "view-vaccination",
            "view-queue", "view-cssd", "view-medicalrecords", "view-mktreferral",
            "view-helpdesk", "view-reports", "view-utilities", "view-systemadmin"
        ]

        for v in expected_views:
            self.assertIn(f'id="{v}"', dash, f"Missing view element: {v}")

    def test_personalization_inputs_wired(self):
        with open(os.path.join(root, "dashboard.html"), encoding="utf-8") as f:
            dash = f.read()

        self.assertIn("cfg-brand-title", dash)
        self.assertIn("cfg-email", dash)
        self.assertIn("cfg-website", dash)
        self.assertIn("cfg-color-primary", dash)
        self.assertIn("cfg-color-accent", dash)
        self.assertIn("function savePersonalizationSettings()", dash)
        self.assertIn("document.getElementById('cfg-brand-title')", dash)

if __name__ == "__main__":
    unittest.main()
