# tests/test_us_healthcare_billing.py
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import db_manager
from core.domain import (
    calculate_us_claim_adjudication,
    generate_edi_837i,
    generate_edi_837p,
    simulate_edi_270_271_eligibility,
    validate_npi_checksum,
)


class TestUSHealthcareBilling(unittest.TestCase):
    def test_medicare_part_b_80_20_split(self):
        # Standard Medicare Part B with 0 deductible remaining
        res = calculate_us_claim_adjudication(
            billed_charges=305.00,
            allowed_amount=183.00,
            payer_type="medicare_b",
            remaining_deductible=0.00
        )
        self.assertEqual(res["billed_charges"], 305.00)
        self.assertEqual(res["allowed_amount"], 183.00)
        self.assertEqual(res["contractual_adjustment_co45"], 122.00) # Provider write-off
        self.assertEqual(res["primary_paid_amount"], 146.40) # 80% Medicare
        self.assertEqual(res["primary_coinsurance_pr2"], 36.60) # 20% Patient Coinsurance
        self.assertEqual(res["patient_responsibility"], 36.60)
        self.assertIn("CO-45 (Contractual Adjustment)", res["remittance_codes"])
        self.assertIn("PR-2 (20% Part B Coinsurance)", res["remittance_codes"])

    def test_medicare_part_b_with_remaining_deductible(self):
        # Patient has $60 remaining Part B deductible
        res = calculate_us_claim_adjudication(
            billed_charges=305.00,
            allowed_amount=183.00,
            payer_type="medicare_b",
            remaining_deductible=60.00
        )
        self.assertEqual(res["deductible_applied_pr1"], 60.00)
        self.assertEqual(res["primary_paid_amount"], 98.40) # 80% of (183 - 60 = 123)
        self.assertEqual(res["primary_coinsurance_pr2"], 24.60) # 20% of 123
        self.assertEqual(res["patient_responsibility"], 84.60) # 60 + 24.60
        self.assertIn("PR-1 (Annual Deductible)", res["remittance_codes"])

    def test_medicare_secondary_medigap_crossover(self):
        # Patient has Secondary Medigap Plan G
        res = calculate_us_claim_adjudication(
            billed_charges=305.00,
            allowed_amount=183.00,
            payer_type="medicare_b",
            remaining_deductible=60.00,
            secondary_payer="Mutual of Omaha Medigap Plan G"
        )
        self.assertEqual(res["primary_paid_amount"], 98.40)
        self.assertEqual(res["secondary_paid_amount"], 84.60) # Medigap covers 100% of pt share
        self.assertEqual(res["patient_responsibility"], 0.00)
        self.assertIn("Crossover to Secondary", res["cob_status"])

    def test_commercial_insurance_adjudication(self):
        # Commercial Blue Cross Blue Shield with $35 copay, $50 deductible, 15% coinsurance
        res = calculate_us_claim_adjudication(
            billed_charges=370.00,
            allowed_amount=208.50,
            payer_type="commercial",
            copay=35.00,
            remaining_deductible=50.00,
            coinsurance_pct=15.0
        )
        self.assertEqual(res["billed_charges"], 370.00)
        self.assertEqual(res["allowed_amount"], 208.50)
        self.assertEqual(res["contractual_adjustment_co45"], 161.50)
        self.assertEqual(res["copay_applied_pr3"], 35.00)
        self.assertEqual(res["deductible_applied_pr1"], 50.00)
        self.assertEqual(res["coinsurance_applied_pr2"], 18.52) # 15% of (208.50 - 35 - 50 = 123.50)
        self.assertEqual(res["primary_paid_amount"], 104.98) # 123.50 - 18.52
        self.assertEqual(res["patient_responsibility"], 103.52) # 35 + 50 + 18.52

    def test_validate_npi_checksum(self):
        # 10-digit NPI Luhn checksum
        self.assertTrue(validate_npi_checksum("1928374655"))
        self.assertFalse(validate_npi_checksum("1928374651"))
        self.assertFalse(validate_npi_checksum("12345")) # Invalid length
        self.assertFalse(validate_npi_checksum(""))

    def test_edi_837p_professional_generation(self):
        claim_data = {
            "claim_no": "CLM-US-2026-0101",
            "patient_name": "Doe, John",
            "payer_id": "00431",
            "payer_name": "Medicare Part B",
            "policy_no": "1EG4-TE5-MK72",
            "billed_charges": 305.00,
            "billing_npi": "1098765432",
            "rendering_npi": "1928374650",
            "cpt_codes": "99214",
            "icd_code": "I10",
            "pos_code": "11"
        }
        edi_text = generate_edi_837p(claim_data)
        self.assertIn("ISA*00*", edi_text)
        self.assertIn("ST*837*0001*005010X222A1~", edi_text)
        self.assertIn("CLM*CLM-US-2026-0101*305.00", edi_text)
        self.assertIn("HI*BK:I10~", edi_text)
        self.assertIn("SV1*HC:99214*305.00*UN*1", edi_text)
        self.assertIn("SE*26*0001~", edi_text)

    def test_edi_837i_institutional_generation(self):
        claim_data = {
            "claim_no": "UB-US-2026-0045",
            "patient_name": "Johnson, Robert",
            "payer_id": "00431",
            "payer_name": "Medicare Part A",
            "policy_no": "2MB7-FA9-KL10",
            "billed_charges": 14800.00,
            "billing_npi": "1098765432",
            "icd_code": "I21.0",
            "revenue_code": "0110",
            "ms_drg": "280"
        }
        edi_text = generate_edi_837i(claim_data)
        self.assertIn("ISA*00*", edi_text)
        self.assertIn("ST*837*0002*005010X223A2~", edi_text)
        self.assertIn("CLM*UB-US-2026-0045*14800.00***111:A:1", edi_text)
        self.assertIn("HI*BK:I210*DR:280~", edi_text)
        self.assertIn("SV2*0110*HC:0110*14800.00", edi_text)

    def test_edi_270_271_real_time_eligibility(self):
        medicare_el = simulate_edi_270_271_eligibility("1EG4-TE5-MK72", "00431", "Medicare Part B")
        self.assertEqual(medicare_el["status"], "Active Coverage")
        self.assertEqual(medicare_el["payer_id"], "00431")
        self.assertEqual(medicare_el["annual_deductible"], 240.00)
        self.assertEqual(medicare_el["coinsurance_rate"], "20%")

        bcbs_el = simulate_edi_270_271_eligibility("BCBS-90218-44", "00060", "Blue Cross Blue Shield")
        self.assertEqual(bcbs_el["status"], "Active Coverage")
        self.assertEqual(bcbs_el["copay_pcp"], 25.00)
        self.assertEqual(bcbs_el["annual_deductible"], 1500.00)

    def test_database_charge_master_and_us_claims(self):
        state = db_manager.get_full_emr_state()
        self.assertIn("charge_master", state)
        self.assertTrue(len(state["charge_master"]) >= 10)

        # Check that CPT 99214 and 93000 are present
        cpts = [c["cpt_code"] for c in state["charge_master"]]
        self.assertIn("99214", cpts)
        self.assertIn("93000", cpts)
        self.assertIn("0110", cpts)

        # Check US claims in database
        claims = state["insurance_claims"]
        us_claims = [c for c in claims if "CLM-US" in c["claim_no"] or "UB-US" in c["claim_no"]]
        self.assertTrue(len(us_claims) >= 3)
        self.assertTrue(any(c.get("payer_id") == "00431" for c in us_claims))

if __name__ == "__main__":
    unittest.main()
