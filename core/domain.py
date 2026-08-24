# core/domain.py
"""
DOMAIN LAYER: Pure Business Functions
Contains deterministic, side-effect-free business rules for calculations,
validations, triage matrices, and cryptographic integrity.
"""

import hmac
import hashlib
import re

# 1. PURE FUNCTION: Calculate Patient Invoicing Breakdown (PhilHealth, Senior / PWD Discount, Net Total)
def calculate_invoice_breakdown(gross_amount: float, discount_pct: float = 0.0, is_senior_or_pwd: bool = False, philhealth_case_rate: float = 0.0) -> dict:
    """
    Calculates hospital invoice pricing with statutory deductions.
    Pure function: deterministic, no external I/O.
    """
    gross = float(max(0.0, gross_amount))
    
    # Statutory 20% discount for Senior Citizens / PWDs
    effective_discount_pct = 20.0 if is_senior_or_pwd else float(max(0.0, min(100.0, discount_pct)))
    discount_amount = round(gross * (effective_discount_pct / 100.0), 2)
    
    amount_after_discount = round(gross - discount_amount, 2)
    
    # PhilHealth benefit coverage deduction
    philhealth_coverage = round(min(amount_after_discount, max(0.0, float(philhealth_case_rate))), 2)
    net_patient_payable = round(max(0.0, amount_after_discount - philhealth_coverage), 2)
    
    return {
        "gross_amount": gross,
        "discount_percent": effective_discount_pct,
        "discount_amount": discount_amount,
        "philhealth_coverage": philhealth_coverage,
        "net_patient_payable": net_patient_payable
    }

# 2. PURE FUNCTION: ER Triage Acuity Decision Matrix
def evaluate_triage_acuity(complaint_text: str, hr: int = 75, spo2: int = 99, sys_bp: int = 120) -> dict:
    """
    Evaluates clinical urgency from symptoms and vitals.
    Returns Triage Level (1-5), Color Code, and Priority Name.
    """
    text = (complaint_text or "").lower()
    
    # Level 1 - Resuscitation (Life-Threatening STAT)
    if any(k in text for k in ['unconscious', 'pulseless', 'cardiac arrest', 'severe shock', 'crushing', 'unresponsive', 'apneic']) or spo2 < 85 or hr > 160 or sys_bp < 70:
        return {"level": "Level 1", "category": "Resuscitation", "color": "#dc2626", "urgent": True, "target_mins": 0}
    
    # Level 2 - Emergent (High Risk / Acute Organ Threat)
    if any(k in text for k in ['chest pain', 'stemi', 'stroke', 'slurred speech', 'facial droop', 'severe dyspnea', 'massive bleeding', 'anaphylaxis']) or spo2 < 92 or hr > 130 or sys_bp > 200 or sys_bp < 85:
        return {"level": "Level 2", "category": "Emergent", "color": "#ea580c", "urgent": True, "target_mins": 10}
    
    # Level 3 - Urgent (Moderate Distress)
    if any(k in text for k in ['fracture', 'deep laceration', 'severe abdominal pain', 'asthma', 'high fever', 'dehydration']) or sys_bp > 160 or hr > 105:
        return {"level": "Level 3", "category": "Urgent", "color": "#d97706", "urgent": False, "target_mins": 30}
    
    # Level 4 - Less Urgent
    if any(k in text for k in ['mild fever', 'cough', 'minor sprain', 'vomiting', 'sore throat', 'rash']):
        return {"level": "Level 4", "category": "Less Urgent", "color": "#16a34a", "urgent": False, "target_mins": 60}
    
    # Level 5 - Non-Urgent (Routine)
    return {"level": "Level 5", "category": "Non-Urgent", "color": "#0284c7", "urgent": False, "target_mins": 120}

# 3. PURE FUNCTION: Vital Signs Clinical Normalcy Validator
def validate_vitals_normalcy(systolic_bp: int, diastolic_bp: int, heart_rate: int, spo2_pct: int, temp_c: float) -> dict:
    """
    Evaluates vital signs against standard clinical physiological thresholds.
    """
    abnormal_flags = []
    
    if systolic_bp >= 140 or diastolic_bp >= 90:
        abnormal_flags.append("Hypertension")
    elif systolic_bp < 90 or diastolic_bp < 60:
        abnormal_flags.append("Hypotension")
        
    if heart_rate > 100:
        abnormal_flags.append("Tachycardia")
    elif heart_rate < 60:
        abnormal_flags.append("Bradycardia")
        
    if spo2_pct < 95:
        abnormal_flags.append("Hypoxemia")
        
    if temp_c >= 38.0:
        abnormal_flags.append("Pyrexia (Fever)")
    elif temp_c < 35.5:
        abnormal_flags.append("Hypothermia")
        
    return {
        "is_normal": len(abnormal_flags) == 0,
        "flags": abnormal_flags,
        "severity": "Normal" if len(abnormal_flags) == 0 else ("Critical" if len(abnormal_flags) >= 2 else "Elevated")
    }

# 4. PURE FUNCTION: Double-Entry Accounting Balance Validator
def validate_accounting_entry(debit_amount: float, credit_amount: float) -> bool:
    """
    Asserts mathematical equality between Debit and Credit in double-entry bookkeeping.
    """
    return round(float(debit_amount), 2) == round(float(credit_amount), 2) and float(debit_amount) > 0

# 5. PURE FUNCTION: Cryptographic HMAC Token Generator & Verifier
def generate_pure_hmac_token(secret_key: str, username: str, role: str, timestamp: int) -> str:
    """
    Generates a tamper-proof HMAC-SHA256 authenticated session payload.
    """
    payload = f"{username}:{role}:{timestamp}"
    signature = hmac.new(secret_key.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()
    return f"{payload}:{signature}"

def verify_pure_hmac_token(secret_key: str, token_str: str, max_age_seconds: int = 86400, current_time: int = None) -> dict:
    """
    Verifies HMAC token validity and expiry without side effects.
    """
    if not token_str or ":" not in token_str:
        return None
        
    parts = token_str.split(":")
    if len(parts) != 4:
        return None
        
    username, role, ts_str, signature = parts
    payload = f"{username}:{role}:{ts_str}"
    expected_sig = hmac.new(secret_key.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()
    
    if not hmac.compare_digest(expected_sig, signature):
        return None
        
    try:
        ts = int(ts_str)
        now = current_time if current_time is not None else int(time.time())
        if now - ts > max_age_seconds:
            return None
    except Exception:
        return None
        
    return {"username": username, "role": role, "timestamp": ts}
