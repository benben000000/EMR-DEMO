# tests/test_domain_pure_functions.py
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.domain import (
    calculate_invoice_breakdown,
    evaluate_triage_acuity,
    generate_pure_hmac_token,
    validate_accounting_entry,
    validate_vitals_normalcy,
    verify_pure_hmac_token,
)


def test_calculate_invoice_breakdown_regular():
    # 10% discount on ₱1,000 with 0 PhilHealth
    res = calculate_invoice_breakdown(gross_amount=1000.0, discount_pct=10.0, is_senior_or_pwd=False, philhealth_case_rate=0.0)
    assert res["gross_amount"] == 1000.0
    assert res["discount_amount"] == 100.0
    assert res["philhealth_coverage"] == 0.0
    assert res["net_patient_payable"] == 900.0

def test_calculate_invoice_breakdown_senior_with_philhealth():
    # Senior citizen 20% on ₱10,000 + ₱4,000 PhilHealth case rate
    # Gross: 10,000 -> 20% discount = 2,000 -> Remainder: 8,000 -> PhilHealth: 4,000 -> Net: 4,000
    res = calculate_invoice_breakdown(gross_amount=10000.0, is_senior_or_pwd=True, philhealth_case_rate=4000.0)
    assert res["discount_percent"] == 20.0
    assert res["discount_amount"] == 2000.0
    assert res["philhealth_coverage"] == 4000.0
    assert res["net_patient_payable"] == 4000.0

def test_evaluate_triage_acuity_level_1():
    res = evaluate_triage_acuity("Patient is pulseless and in cardiac arrest", hr=0, spo2=60, sys_bp=40)
    assert res["level"] == "Level 1"
    assert res["category"] == "Resuscitation"
    assert res["urgent"] is True

def test_evaluate_triage_acuity_level_2():
    res = evaluate_triage_acuity("Acute chest pain radiating to left arm", hr=115, spo2=91, sys_bp=165)
    assert res["level"] == "Level 2"
    assert res["category"] == "Emergent"
    assert res["urgent"] is True

def test_evaluate_triage_acuity_level_4():
    res = evaluate_triage_acuity("Mild cough and sore throat for 2 days", hr=72, spo2=99, sys_bp=118)
    assert res["level"] == "Level 4"
    assert res["urgent"] is False

def test_validate_vitals_normalcy():
    normal = validate_vitals_normalcy(systolic_bp=120, diastolic_bp=80, heart_rate=72, spo2_pct=99, temp_c=36.6)
    assert normal["is_normal"] is True
    assert normal["severity"] == "Normal"

    abnormal = validate_vitals_normalcy(systolic_bp=180, diastolic_bp=105, heart_rate=125, spo2_pct=88, temp_c=39.2)
    assert abnormal["is_normal"] is False
    assert "Hypertension" in abnormal["flags"]
    assert "Tachycardia" in abnormal["flags"]
    assert "Hypoxemia" in abnormal["flags"]
    assert "Pyrexia (Fever)" in abnormal["flags"]

def test_validate_accounting_entry():
    assert validate_accounting_entry(2500.00, 2500.00) is True
    assert validate_accounting_entry(2500.00, 2500.50) is False
    assert validate_accounting_entry(0.00, 0.00) is False

def test_hmac_token_cryptography():
    secret = "Danphe_EMR_Super_Secret_Key_2026"
    token = generate_pure_hmac_token(secret, "doctor_tan", "doctor", 1700000000)

    # Valid token verification
    verified = verify_pure_hmac_token(secret, token, max_age_seconds=86400, current_time=1700000500)
    assert verified is not None
    assert verified["username"] == "doctor_tan"
    assert verified["role"] == "doctor"

    # Expired token verification
    expired = verify_pure_hmac_token(secret, token, max_age_seconds=300, current_time=1700001000)
    assert expired is None

    # Tampered token verification
    tampered_token = token.replace("doctor_tan", "admin_hacker")
    assert verify_pure_hmac_token(secret, tampered_token) is None

if __name__ == "__main__":
    test_calculate_invoice_breakdown_regular()
    test_calculate_invoice_breakdown_senior_with_philhealth()
    test_evaluate_triage_acuity_level_1()
    test_evaluate_triage_acuity_level_2()
    test_evaluate_triage_acuity_level_4()
    test_validate_vitals_normalcy()
    test_validate_accounting_entry()
    test_hmac_token_cryptography()
    print("[PASS] All Pure Domain Function tests passed successfully!")
