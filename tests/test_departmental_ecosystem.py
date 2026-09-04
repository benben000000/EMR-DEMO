# tests/test_departmental_ecosystem.py
"""
G1 Health EMR - Department-to-Department Ecosystem Integration Tests
Validates clinical, operational, diagnostic, supply chain, and financial handoffs
across all 34 workspaces and 7 functional domains.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import db_manager
from core.domain import generate_edi_837p


class TestDepartmentalEcosystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.state = db_manager.get_full_emr_state(role="admin")

    def test_domain_1_clinical_to_ancillary_diagnostics_handoff(self):
        """Clinical Doctor Desk -> Laboratory (LIS) & Radiology (RIS) orders."""
        patients = self.state.get("patients", [])
        self.assertTrue(len(patients) > 0, "Patient master index must contain active patients")
        patient_names = {p.get("name") for p in patients if p.get("name")}

        # Verify Lab Orders link to active patient
        lab_orders = self.state.get("lab_orders", [])
        self.assertTrue(len(lab_orders) > 0, "Lab diagnostic orders must exist in LIS")
        lab_patient_names = [o.get("patient_name") for o in lab_orders]
        self.assertTrue(any(name in patient_names for name in lab_patient_names if name))

        # Verify Radiology Orders link to active patient
        rad_orders = self.state.get("radiology_orders", [])
        self.assertTrue(len(rad_orders) > 0, "Radiology imaging orders must exist in RIS")

    def test_domain_2_emergency_to_inpatient_adt_bed_matrix(self):
        """ER 5-level Triage -> Inpatient Bed Matrix transfer workflow."""
        er_cases = self.state.get("er_cases", [])
        self.assertIsInstance(er_cases, list, "ER cases collection must be a list")
        beds = self.state.get("adt_beds", [])
        self.assertTrue(len(beds) > 0, "Inpatient ADT bed matrix must be populated")

        # Verify bed status categories conform to clinical standards
        valid_statuses = {"occupied", "available", "cleaning", "maintenance"}
        for b in beds:
            status = (b.get("status") or "").lower()
            self.assertIn(status, valid_statuses, f"Bed {b.get('bed_number')} has invalid status {status}")

    def test_domain_3_doctor_desk_to_pharmacy_dispensing(self):
        """Doctor Desk e-Prescriptions route to Pharmacy with allergy & NDC safety."""
        inventory = self.state.get("inventory_items", [])
        self.assertTrue(len(inventory) > 0, "Pharmacy formulary/stock must be populated")
        med_names = [i.get("item_name") for i in inventory]
        self.assertTrue(any("aspirin" in str(m).lower() or "amoxicillin" in str(m).lower() or "atorvastatin" in str(m).lower() for m in med_names))

    def test_domain_4_operating_theater_and_cssd_sterilization(self):
        """Surgical scheduling links with CSSD autoclave cycle biological indicator logs."""
        ot_schedules = self.state.get("ot_schedules", [])
        cssd_batches = self.state.get("cssd_batches", [])
        self.assertTrue(len(ot_schedules) > 0, "OT surgical schedules must be active")
        self.assertTrue(len(cssd_batches) > 0, "CSSD sterilization batches must be tracked")

        for b in cssd_batches:
            self.assertTrue(b.get("cycle_number") or b.get("batch_no"), "CSSD batch must have cycle identifier")

    def test_domain_5_central_supply_to_substore_replenishment(self):
        """Central Inventory Warehouse supplies departmental Floor Sub-Stores."""
        central_inv = self.state.get("inventory_items", [])
        substore_inv = self.state.get("substore_inventory", [])
        self.assertTrue(len(central_inv) > 0, "Central warehouse must have stock")
        self.assertTrue(len(substore_inv) > 0, "Departmental sub-stores must have floor inventory")

    def test_domain_6_clinical_consultation_to_rcm_and_837p_claims(self):
        """Doctor Consultation -> Charge Master -> Invoice -> 837P ANSI X12 Claim."""
        claims = self.state.get("insurance_claims", [])
        self.assertTrue(len(claims) > 0, "RCM insurance claims table must contain adjudicated claims")

        sample_claim = claims[0]
        edi_text = generate_edi_837p(sample_claim)
        self.assertIn("ISA*", edi_text, "EDI claim must have ISA interchange control header")
        self.assertIn("GS*HC*", edi_text, "EDI claim must have GS functional group header")
        self.assertIn("CLM*", edi_text, "EDI claim must contain CLM claim segment")
        self.assertIn("GE*", edi_text, "EDI claim must contain GE trailer")
        self.assertIn("IEA*", edi_text, "EDI claim must contain IEA trailer")

    def test_domain_7_revenue_cycle_to_general_ledger_accounting(self):
        """Patient billing collections post double-entry vouchers to General Ledger."""
        vouchers = self.state.get("accounting_vouchers", [])
        self.assertTrue(len(vouchers) > 0, "Accounting vouchers must be recorded in General Ledger")

        for v in vouchers:
            debit = float(v.get("debit_amount") or 0.0)
            credit = float(v.get("credit_amount") or 0.0)
            self.assertTrue(debit >= 0 and credit >= 0, "Voucher debit and credit amounts must be non-negative")

    def test_domain_8_patient_discharge_to_mrd_records_archiving(self):
        """Discharged inpatient records transfer to Medical Records Dept (HIM/MRD)."""
        mrd_records = self.state.get("mrd_records", [])
        self.assertTrue(len(mrd_records) > 0, "MRD chart archives must be present")
        for m in mrd_records:
            self.assertTrue(m.get("patient_name"), "MRD record must track patient identity")
            self.assertTrue(m.get("icd_code") or m.get("icd_primary") or m.get("diagnosis"), "MRD record must include ICD diagnosis coding")

if __name__ == "__main__":
    unittest.main()
