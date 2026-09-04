#!/usr/bin/env python3
"""
G1 Health EMR - Comprehensive Playwright QA Engine (Hardened)
Executes end-to-end browser automation, interaction auditing, and Neon DB sync verification
across all 35 views / 34 workspaces.
"""

import json
import os
import time
from datetime import datetime

from playwright.sync_api import sync_playwright

import db_manager

BASE_URL = "http://127.0.0.1:5000"
ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), "qa_artifacts")
SCREENSHOTS_DIR = os.path.join(ARTIFACTS_DIR, "screenshots")

os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

VIEWS_TO_TEST = [
    ("view-dashboard", "Executive Dashboard", "dashboard"),
    ("view-patient-reg", "Patient Registration & Census", "patients"),
    ("view-patient360", "Patient 360 Longitudinal Chart", "patient360"),
    ("view-appointments", "Outpatient Appointment Desk", "appointments"),
    ("view-queue", "Patient Flow & Queue Management", "queue"),
    ("view-clinical", "Physician Clinical Desk & CPOE", "clinical"),
    ("view-nursing", "Inpatient Ward Nursing Station", "nursing"),
    ("view-emergency", "Emergency Department (ED / Trauma)", "emergency"),
    ("view-adt", "Admission, Discharge & Transfer (ADT)", "adt"),
    ("view-laboratory", "Laboratory Information System (LIS)", "laboratory"),
    ("view-radiology", "Radiology Information System (RIS)", "radiology"),
    ("view-pharmacy", "Pharmacy & Medication Dispensing", "pharmacy"),
    ("view-ot", "Operating Theatre (OT / Surgical)", "ot"),
    ("view-cssd", "Central Sterile Services Dept (CSSD)", "cssd"),
    ("view-procurement", "Supply Chain & PO Management", "procurement"),
    ("view-inventory", "Hospital Central Inventory & Stock", "inventory"),
    ("view-substore", "Departmental Substore Distribution", "substore"),
    ("view-billing", "Patient Billing & Cashiering Hub", "billing"),
    ("view-claimmgmt", "US Claims & EDI Clearinghouse RCM", "claimmgmt"),
    ("view-accounting", "Hospital General Ledger & Vouchers", "accounting"),
    ("view-fixedassets", "Biomedical & Fixed Asset Register", "fixedassets"),
    ("view-incentive", "Physician RVU & Incentive Accounting", "incentive"),
    ("view-medicalrecords", "Medical Records Department (MRD)", "medicalrecords"),
    ("view-verification", "Clinical Verification & Panic Flags", "verification"),
    ("view-reports", "Operational & Financial BI Analytics", "reports"),
    ("view-ehs", "Environmental Health & Safety (EHS)", "ehs"),
    ("view-helpdesk", "IT & Biomedical Support Helpdesk", "helpdesk"),
    ("view-telehealth", "HIPAA-Compliant Telehealth Hub", "telehealth"),
    ("view-aicrm", "AI CRM & Smart Inbound Triage", "aicrm"),
    ("view-mktreferral", "Physician Referral Network", "mktreferral"),
    ("view-vaccination", "Immunization & Vaccine Registry", "vaccination"),
    ("view-clinicalsettings", "Clinical Templates & Order Sets", "clinicalsettings"),
    ("view-whitelabel", "Hospital White-Labeling & Branding", "whitelabel"),
    ("view-systemadmin", "System Administration & RBAC", "systemadmin"),
    ("view-utilities", "System Maintenance & Utilities", "utilities")
]

class QAEngine:
    def __init__(self):
        self.results = {}
        self.console_logs = []
        self.network_calls = []
        self.neon_conn = None

    def connect_neon(self):
        try:
            self.neon_conn = db_manager.get_db_connection()
            print("[DB] Connected to Neon PostgreSQL successfully.")
        except Exception as e:
            print(f"[DB ERROR] Failed to connect to Neon DB: {e}")

    def get_neon_count(self, table_name):
        if not self.neon_conn:
            return None
        try:
            cur = self.neon_conn.cursor()
            cur.execute(f"SELECT COUNT(*) FROM {table_name}")
            row = cur.fetchone()
            if isinstance(row, dict):
                return next(iter(row.values()))
            return row[0]
        except Exception as e:
            self.neon_conn.rollback()
            return f"Err: {e}"

    def run(self):
        self.connect_neon()

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                viewport={"width": 1440, "height": 900},
                user_agent="G1-EMR-Playwright-QA-Agent/2.0"
            )

            # Ingest session storage before scripts run
            context.add_init_script('''
                sessionStorage.setItem('g1_auth_token', 'admin_playwright_verified_token_2026');
                sessionStorage.setItem('g1_logged_out', 'false');
                sessionStorage.setItem('g1_user_name', 'Administrator');
                sessionStorage.setItem('g1_user_role', 'Super Admin');
                sessionStorage.setItem('g1_role_key', 'admin');
                sessionStorage.setItem('g1_user', JSON.stringify({
                    username: 'admin',
                    role_key: 'admin',
                    name: 'Administrator'
                }));
            ''')

            page = context.new_page()

            # Listen to console and network
            page.on("console", lambda msg: self.console_logs.append({
                "time": datetime.now().isoformat(),
                "type": msg.type,
                "text": msg.text
            }))

            page.on("request", lambda req: self.network_calls.append({
                "time": datetime.now().isoformat(),
                "method": req.method,
                "url": req.url
            }))

            print("\n=== STEP 1: LOAD DASHBOARD & WAIT FOR HYDRATION ===")
            page.goto(f"{BASE_URL}/dashboard")
            page.wait_for_selector("#tbody-appointments tr", state="attached", timeout=20000)
            page.wait_for_timeout(1000)

            page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "00_initial_dashboard.png"))
            print("[QA] Initial dashboard rendered and hydrated from Neon PostgreSQL.")

            # STEP 2: MODULE-BY-MODULE TESTING
            print("\n=== STEP 2: SYSTEMATIC AUDIT OF ALL 35 MODULES ===")
            for view_id, view_name, nav_key in VIEWS_TO_TEST:
                self.audit_module(page, view_id, view_name, nav_key)

            # STEP 3: INTERCONNECTION & DATA SYNC TESTS
            print("\n=== STEP 3: CROSS-DEPARTMENTAL INTERCONNECTION & PERSISTENCE ===")
            self.audit_interconnections(page)

            browser.close()

        if self.neon_conn:
            self.neon_conn.close()

        # STEP 4: COMPILE FINAL AUDIT REPORT
        self.compile_report()

    def audit_module(self, page, view_id, view_name, nav_key):
        print(f"\n---> Auditing Module: {view_name} (#{view_id})")
        mod_result = {
            "view_id": view_id,
            "view_name": view_name,
            "nav_key": nav_key,
            "navigation_success": False,
            "dom_visible": False,
            "tables_found": 0,
            "table_rows_rendered": 0,
            "buttons_found": 0,
            "buttons_clicked": 0,
            "inputs_found": 0,
            "modals_triggered": [],
            "console_errors": [],
            "critique_notes": []
        }

        try:
            # Switch to tab using switchTab
            switch_res = page.evaluate("""(vId) => {
                if (typeof switchTab === 'function') {
                    switchTab(vId);
                    return true;
                }
                return false;
            }""", view_id)
            page.wait_for_timeout(600)

            # Check visibility
            is_visible = page.is_visible(f"#{view_id}")
            mod_result["navigation_success"] = switch_res
            mod_result["dom_visible"] = is_visible

            if not is_visible:
                mod_result["critique_notes"].append(f"CRITICAL: View #{view_id} failed to display.")
                page.screenshot(path=os.path.join(SCREENSHOTS_DIR, f"FAIL_{view_id}.png"))
                self.results[view_id] = mod_result
                return

            # Capture screenshot
            page.screenshot(path=os.path.join(SCREENSHOTS_DIR, f"{view_id}.png"))

            # Audit tables and row counts
            table_info = page.evaluate("""(vId) => {
                const el = document.getElementById(vId);
                if (!el) return { tables: 0, rows: 0, tbodies: [] };
                const tables = el.querySelectorAll('table');
                let rowCount = 0;
                const tbodies = [];
                tables.forEach(t => {
                    const tb = t.querySelector('tbody');
                    if (tb) {
                        tbodies.push(tb.id || 'unnamed_tbody');
                        rowCount += tb.querySelectorAll('tr').length;
                    }
                });
                return { tables: tables.length, rows: rowCount, tbodies: tbodies };
            }""", view_id)

            mod_result["tables_found"] = table_info["tables"]
            mod_result["table_rows_rendered"] = table_info["rows"]
            mod_result["tbodies"] = table_info["tbodies"]

            # Audit buttons inside view
            button_info = page.evaluate("""(vId) => {
                const el = document.getElementById(vId);
                if (!el) return [];
                const btns = el.querySelectorAll('button, .btn-primary-action, .btn-secondary');
                const list = [];
                btns.forEach((b, idx) => {
                    list.push({
                        idx: idx,
                        text: b.innerText.trim(),
                        onclick: b.getAttribute('onclick') || '',
                        id: b.id || '',
                        className: b.className || ''
                    });
                });
                return list;
            }""", view_id)

            mod_result["buttons_found"] = len(button_info)

            # Audit inputs inside view
            input_count = page.evaluate("""(vId) => {
                const el = document.getElementById(vId);
                return el ? el.querySelectorAll('input, select, textarea').length : 0;
            }""", view_id)
            mod_result["inputs_found"] = input_count

            # Test Search/Filter input if present
            search_input = page.evaluate("""(vId) => {
                const el = document.getElementById(vId);
                if (!el) return false;
                const inp = el.querySelector('input[type="text"], input[type="search"]');
                if (inp) {
                    inp.value = 'test';
                    inp.dispatchEvent(new Event('input', { bubbles: true }));
                    inp.dispatchEvent(new Event('keyup', { bubbles: true }));
                    inp.value = '';
                    inp.dispatchEvent(new Event('input', { bubbles: true }));
                    return true;
                }
                return false;
            }""", view_id)
            if search_input:
                mod_result["search_box_tested"] = True

            # Module Inspection & Critique
            for b in button_info:
                oc = b["onclick"]
                if "showToast" in oc and "apiFetch" not in oc and "fetch" not in oc:
                    mod_result["critique_notes"].append(f"STUB WARNING: Button '{b['text']}' calls showToast without persistent backend API mutation ({oc}).")
                if "openModal" in oc:
                    mod_result["modals_triggered"].append(oc)

            # Record errors
            recent_errors = [log["text"] for log in self.console_logs[-10:] if log["type"] == "error"]
            mod_result["console_errors"] = recent_errors
            if recent_errors:
                mod_result["critique_notes"].append(f"Console errors detected: {recent_errors[:2]}")

            print(f"  [OK] Visible: {is_visible} | Tables: {table_info['tables']} (Rows: {table_info['rows']}) | Buttons: {len(button_info)} | Inputs: {input_count}")

        except Exception as e:
            mod_result["critique_notes"].append(f"EXCEPTION: {e!s}")
            print(f"  [ERROR] Audit error on {view_id}: {e}")

        self.results[view_id] = mod_result

    def audit_interconnections(self, page):
        print("\n--- Testing Specific Interconnected Departmental Flows ---")

        # 1. Register a new patient in Patient Registration -> Check Neon DB
        init_pat_cnt = self.get_neon_count("patients")
        print(f"[FLOW 1] Initial Patients in Neon DB: {init_pat_cnt}")

        test_pat_name = f"QA Test Patient {int(time.time())}"
        test_pat_phone = "+1 (555) 019-9988"

        res = page.evaluate(f"""async () => {{
            try {{
                const payload = {{
                    name: '{test_pat_name}',
                    dob: '1985-05-15',
                    gender: 'Female',
                    phone: '{test_pat_phone}',
                    address: '100 Test Ave, Boston, MA 02115',
                    blood_group: 'A+',
                    status: 'Active',
                    insurance_no: 'Blue Cross Blue Shield Massachusetts'
                }};
                const res = await apiFetch('/api/patients', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify(payload)
                }});
                await loadLiveEMRState();
                return res;
            }} catch(e) {{
                return {{ error: e.message }};
            }}
        }}""")
        page.wait_for_timeout(2000)

        new_pat_cnt = self.get_neon_count("patients")
        print(f"[FLOW 1 RESULT] API Response: {res} | Neon DB Count after insert: {new_pat_cnt}")

        # 2. Test Bed State Mutation in ADT
        print("\n--- Testing Bed Status Mutation (ADT -> Housekeeping -> Clinical) ---")
        bed_res = page.evaluate("""async () => {
            try {
                const res = await apiFetch('/api/adt_beds', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        id: 1,
                        status: 'Occupied',
                        patient_name: 'Robert Johnson (Admitted)',
                        diagnosis: 'Acute Coronary Syndrome',
                        doctor: 'Dr. Roberto Tan, MD'
                    })
                });
                await loadLiveEMRState();
                return res;
            } catch(e) {
                return { error: e.message };
            }
        }""")
        page.wait_for_timeout(1500)
        print(f"[FLOW 2 RESULT] Bed Mutation Response: {bed_res}")

        # 3. Test Claim Adjudication in Billing/Claims
        print("\n--- Testing Real-Time US Healthcare Claim Adjudication ---")
        adj_res = page.evaluate("""async () => {
            try {
                const res = await apiFetch('/api/claims/adjudicate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        billed_charges: 450.00,
                        allowed_amount: 320.00,
                        payer_type: 'commercial_bcbs',
                        copay: 30.00,
                        coinsurance_pct: 20.0,
                        remaining_deductible: 50.0
                    })
                });
                return res;
            } catch(e) {
                return { error: e.message };
            }
        }""")
        print(f"[FLOW 3 RESULT] Adjudication Response: {adj_res}")

        # 4. Test EDI 837 ANSI ASC X12 Loop Generation
        print("\n--- Testing EDI 837 Loop Generation ---")
        edi_res = page.evaluate("""async () => {
            try {
                const res = await apiFetch('/api/claims/edi837', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        claim_no: 'CLM-QA-2026-9999',
                        claim_type: '837P',
                        patient_name: 'Jane Smith',
                        billed_charges: 450.00,
                        cpt_codes: '99214, 93000'
                    })
                });
                return res;
            } catch(e) {
                return { error: e.message };
            }
        }""")
        has_isa = "ISA*" in str(edi_res.get("edi_payload", "")) if isinstance(edi_res, dict) else False
        print(f"[FLOW 4 RESULT] EDI 837 Generation: Success={has_isa} (Length={len(str(edi_res))})")

        # 5. Test Audit Trail Log Generation
        audit_cnt = self.get_neon_count("audit_logs")
        print(f"[FLOW 5 RESULT] Audit Logs Count in Neon DB: {audit_cnt}")

        # 6. Test Universal Editor Mutation & Sync
        print("\n--- Testing Universal Record Update ---")
        edit_res = page.evaluate("""async () => {
            try {
                const res = await apiFetch('/api/appointments', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        _action: 'update',
                        id: 1,
                        status: 'Confirmed'
                    })
                });
                await loadLiveEMRState();
                return res;
            } catch(e) {
                return { error: e.message };
            }
        }""")
        print(f"[FLOW 6 RESULT] Appointment Update Response: {edit_res}")

    def compile_report(self):
        report_path = os.path.join(ARTIFACTS_DIR, "detailed_qa_inspection_report.json")
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "total_views_tested": len(self.results),
                "view_results": self.results,
                "total_console_logs": len(self.console_logs),
                "total_network_calls": len(self.network_calls)
            }, f, indent=2)
        print(f"\n[REPORT] Detailed QA JSON report saved to: {report_path}")

if __name__ == '__main__':
    engine = QAEngine()
    engine.run()
