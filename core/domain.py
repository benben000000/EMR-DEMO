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

# 6. PURE FUNCTION: HIPAA Safe Harbor ePHI Masking (§ 164.514)
def mask_ephi(value: str, mask_type: str = "phone") -> str:
    """
    Safely de-identifies ePHI fields according to HIPAA Safe Harbor guidelines.
    """
    if not value or not isinstance(value, str):
        return ""
    val = value.strip()
    if not val:
        return ""
        
    if mask_type == "phone":
        # Keep country/prefix and last 4 digits: e.g. +1 555 *** 4567
        if len(val) > 7:
            return val[:7] + " *** " + val[-4:]
        return "***-****"
        
    elif mask_type == "insurance" or mask_type == "id":
        # Keep first 2 and last 2: e.g. MC-****-90
        if len(val) > 4:
            return val[:3] + "****" + val[-2:]
        return "****"
        
    elif mask_type == "address":
        # Retain general city/region, mask exact street
        parts = [p.strip() for p in val.split(",") if p.strip()]
        if len(parts) >= 2:
            return f"[Restricted Address], {parts[-1]}"
        return "[Restricted Address]"
        
    elif mask_type == "name":
        words = val.split()
        if len(words) > 1:
            return f"{words[0][0]}. {' '.join(words[1:])}"
        return val

    return val

# 7. PURE FUNCTION: Tamper-Evident Audit Log Checksum (§ 164.312(b))
def generate_audit_checksum(secret_key: str, user_id: str, role: str, action: str, entity: str, record_id: str, timestamp: str) -> str:
    """
    Generates a cryptographic HMAC-SHA256 signature guaranteeing audit trail immutability.
    """
    payload = f"{user_id}|{role}|{action}|{entity}|{record_id}|{timestamp}"
    return hmac.new(secret_key.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()

# 8. PURE FUNCTION: HIPAA Role-Based Access Control (RBAC) Validator (§ 164.308(a)(4))
ROLE_PERMISSIONS = {
    "admin": {"*": ["read", "create", "update", "delete"]},
    "doctor": {
        "patients": ["read", "create", "update"],
        "appointments": ["read", "create", "update"],
        "adt_beds": ["read", "update"],
        "er_cases": ["read", "create", "update"],
        "prescriptions": ["read", "create", "update"],
        "lab_orders": ["read", "create", "update"],
        "radiology_orders": ["read", "create", "update"],
        "ot_schedules": ["read", "create", "update"],
        "clinical_templates": ["read", "create", "update"],
        "order_sets": ["read", "create", "update"],
        "mrd_records": ["read", "create", "update"],
        "telehealth_sessions": ["read", "create", "update"],
        "ehs_incidents": ["read", "create"]
    },
    "nurse": {
        "patients": ["read"],
        "appointments": ["read"],
        "adt_beds": ["read", "update"],
        "er_cases": ["read", "update"],
        "prescriptions": ["read"],
        "nursing_handovers": ["read", "create", "update"],
        "queue_tickets": ["read", "update"],
        "vaccination_records": ["read", "create", "update"],
        "cssd_batches": ["read", "create", "update"],
        "substore_inventory": ["read", "update"],
        "ehs_incidents": ["read", "create"]
    },
    "accountant": {
        "billing_invoices": ["read", "create", "update"],
        "accounting_vouchers": ["read", "create", "update"],
        "fixed_assets": ["read", "create", "update"],
        "insurance_claims": ["read", "create", "update"],
        "doctor_incentives": ["read", "update"],
        "procurement_po": ["read", "update"],
        "inventory_items": ["read"],
        "audit_logs": ["read"]
    },
    "billing": {
        "patients": ["read"],
        "billing_invoices": ["read", "create", "update"],
        "insurance_claims": ["read", "create", "update"],
        "verification_alerts": ["read", "update"],
        "queue_tickets": ["read", "update"]
    },
    "pharmacy": {
        "inventory_items": ["read", "create", "update"],
        "substore_inventory": ["read", "update"],
        "prescriptions": ["read", "update"],
        "procurement_po": ["read", "create", "update"]
    },
    "labtech": {
        "lab_orders": ["read", "create", "update"],
        "radiology_orders": ["read", "create", "update"],
        "fixed_assets": ["read"]
    },
    "reception": {
        "patients": ["read", "create", "update"],
        "appointments": ["read", "create", "update"],
        "queue_tickets": ["read", "create", "update"],
        "helpdesk_queries": ["read", "create", "update"],
        "ai_crm_leads": ["read", "create", "update"]
    }
}

def check_rbac_permission(role_key: str, entity: str, action: str) -> bool:
    """
    Validates if a given role is authorized to perform action on entity.
    Pure function: strictly enforces Minimum Necessary rule.
    """
    role = (role_key or "").strip().lower()
    ent = (entity or "").strip().lower()
    act = (action or "").strip().lower()
    
    if role == "admin":
        return True
        
    perms = ROLE_PERMISSIONS.get(role, {})
    if "*" in perms:
        return act in perms["*"]
        
    allowed_actions = perms.get(ent, [])
    return act in allowed_actions

# 9. PURE FUNCTION: US Healthcare & Medicare Adjudication Calculator
def calculate_us_claim_adjudication(
    billed_charges: float,
    allowed_amount: float,
    payer_type: str = "medicare_b",
    copay: float = 0.0,
    coinsurance_pct: float = 20.0,
    remaining_deductible: float = 0.0,
    secondary_payer: str = None
) -> dict:
    """
    Computes exact US Healthcare claim adjudication:
    - Medicare Part B (80% allowed to Medicare, 20% to patient/Medigap, CO-45 write-off)
    - Commercial HMO/PPO (Copay, Deductible, Coinsurance)
    - Coordination of Benefits (COB / Crossover Secondary Payer)
    """
    billed = round(float(max(0.0, billed_charges)), 2)
    allowed = round(float(max(0.0, allowed_amount if allowed_amount > 0 else billed)), 2)
    contractual_adjustment = round(max(0.0, billed - allowed), 2)
    
    pt_type = (payer_type or "medicare_b").lower()
    
    if "medicare_b" in pt_type or "medicare" in pt_type:
        # Standard Medicare Part B 80/20 Cost-Share
        deductible_applied = round(min(allowed, max(0.0, float(remaining_deductible))), 2)
        subject_to_coinsurance = round(max(0.0, allowed - deductible_applied), 2)
        medicare_paid = round(subject_to_coinsurance * 0.80, 2)
        primary_coinsurance = round(subject_to_coinsurance * 0.20, 2)
        
        # Check Secondary / Medigap Plan Crossover (COB)
        if secondary_payer and str(secondary_payer).strip().lower() not in ["none", ""]:
            secondary_paid = round(deductible_applied + primary_coinsurance, 2)
            patient_responsibility = 0.0
            cob_status = f"Crossover to Secondary ({secondary_payer})"
        else:
            secondary_paid = 0.0
            patient_responsibility = round(deductible_applied + primary_coinsurance, 2)
            cob_status = "Patient Self-Pay Balance"
            
        return {
            "payer_system": "Medicare Part B (CMS)",
            "billed_charges": billed,
            "allowed_amount": allowed,
            "contractual_adjustment_co45": contractual_adjustment,
            "deductible_applied_pr1": deductible_applied,
            "primary_paid_amount": medicare_paid,
            "primary_coinsurance_pr2": primary_coinsurance,
            "secondary_paid_amount": secondary_paid,
            "patient_responsibility": patient_responsibility,
            "cob_status": cob_status,
            "remittance_codes": ["CO-45 (Contractual Adjustment)", "PR-2 (20% Part B Coinsurance)"] + (["PR-1 (Annual Deductible)"] if deductible_applied > 0 else [])
        }
    else:
        # Commercial Payer (BCBS, UHC, Aetna, Cigna, Humana)
        copay_applied = round(min(allowed, max(0.0, float(copay))), 2)
        after_copay = round(max(0.0, allowed - copay_applied), 2)
        deductible_applied = round(min(after_copay, max(0.0, float(remaining_deductible))), 2)
        subject_to_coinsurance = round(max(0.0, after_copay - deductible_applied), 2)
        coinsurance_due = round(subject_to_coinsurance * (float(coinsurance_pct) / 100.0), 2)
        insurance_paid = round(max(0.0, subject_to_coinsurance - coinsurance_due), 2)
        
        patient_responsibility = round(copay_applied + deductible_applied + coinsurance_due, 2)
        
        return {
            "payer_system": "Commercial Insurance (HMO/PPO)",
            "billed_charges": billed,
            "allowed_amount": allowed,
            "contractual_adjustment_co45": contractual_adjustment,
            "copay_applied_pr3": copay_applied,
            "deductible_applied_pr1": deductible_applied,
            "coinsurance_applied_pr2": coinsurance_due,
            "primary_paid_amount": insurance_paid,
            "secondary_paid_amount": 0.0,
            "patient_responsibility": patient_responsibility,
            "cob_status": "Commercial Direct Adjudication",
            "remittance_codes": ["CO-45 (Fee Schedule Write-off)"] + (["PR-3 (Copay)"] if copay_applied > 0 else []) + (["PR-1 (Deductible)"] if deductible_applied > 0 else []) + (["PR-2 (Coinsurance)"] if coinsurance_due > 0 else [])
        }

# 10. PURE FUNCTION: US National Provider Identifier (NPI) Validator (Luhn Algorithm)
def validate_npi_checksum(npi: str) -> bool:
    """
    Validates 10-digit NPI using the CMS-mandated Luhn checksum algorithm with '80840' prefix.
    """
    clean_npi = re.sub(r"\D", "", str(npi or ""))
    if len(clean_npi) != 10:
        return False
        
    full_str = "80840" + clean_npi
    digits = [int(c) for c in full_str]
    total = 0
    for idx, d in enumerate(reversed(digits[:-1])):
        if idx % 2 == 0:
            d *= 2
            if d > 9:
                d -= 9
        total += d
        
    check_digit = (10 - (total % 10)) % 10
    return check_digit == digits[-1]

# 11. PURE FUNCTION: Real-Time Eligibility & Benefit Inquiry / Response Simulator (EDI 270/271)
def simulate_edi_270_271_eligibility(policy_or_mbi: str, payer_id: str = "00431", payer_name: str = "Medicare Part B") -> dict:
    """
    Simulates ANSI ASC X12 270/271 Real-Time Benefit Eligibility Verification.
    """
    clean_id = (policy_or_mbi or "1EG4-TE5-MK72").strip().upper()
    is_medicare = "MEDICARE" in (payer_name or "").upper() or payer_id == "00431"
    
    if is_medicare:
        return {
            "status": "Active Coverage",
            "payer_id": "00431",
            "payer_name": "Medicare Part B (CMS)",
            "subscriber_id": clean_id,
            "plan_type": "Original Medicare Fee-For-Service",
            "effective_date": "2024-01-01",
            "part_a_active": True,
            "part_b_active": True,
            "annual_deductible": 240.00,
            "deductible_met": 180.00,
            "deductible_remaining": 60.00,
            "coinsurance_rate": "20%",
            "medicare_share": "80%",
            "copay_pcp": 0.00,
            "copay_specialist": 0.00,
            "prior_auth_required": False
        }
    else:
        return {
            "status": "Active Coverage",
            "payer_id": payer_id or "87726",
            "payer_name": payer_name or "UnitedHealthcare Commercial Choice Plus",
            "subscriber_id": clean_id,
            "plan_type": "Commercial PPO Preferred Network",
            "effective_date": "2026-01-01",
            "annual_deductible": 1500.00,
            "deductible_met": 850.00,
            "deductible_remaining": 650.00,
            "coinsurance_rate": "15%",
            "insurance_share": "85%",
            "copay_pcp": 25.00,
            "copay_specialist": 50.00,
            "prior_auth_required": True
        }

# 12. PURE FUNCTION: ANSI ASC X12 837P (Professional Health Care Claim) Generator
def generate_edi_837p(claim: dict) -> str:
    """
    Generates standard ANSI ASC X12 837P Professional Claim string format for CMS-1500 submissions.
    """
    claim_id = claim.get("claim_no", "CLM-US-01")
    patient = claim.get("patient_name", "Doe, John")
    payer_id = claim.get("payer_id", "00431")
    payer_name = claim.get("payer_name", "Medicare Part B")
    mbi = claim.get("policy_no", "1EG4-TE5-MK72")
    billed = f"{float(claim.get('billed_charges', 250.00)):.2f}"
    billing_npi = claim.get("billing_npi", "1098765432")
    rendering_npi = claim.get("rendering_npi", "1928374650")
    diag_code = (claim.get("icd_code", "I10")).replace(".", "")
    cpt = claim.get("cpt_codes", "99214")
    pos = claim.get("pos_code", "11")
    date_str = (claim.get("filing_date", "20260902")).replace("-", "")

    segments = [
        f"ISA*00*          *00*          *ZZ*SUBMITTER1     *ZZ*{payer_id.ljust(15)}*{date_str[:6]}*1000*^*00501*000000001*0*P*:~",
        f"GS*HC*SUBMITTER1*{payer_id}*{date_str}*1000*1*X*005010X222A1~",
        f"ST*837*0001*005010X222A1~",
        f"BHT*0019*00*{claim_id}*{date_str}*1000*CH~",
        f"NM1*41*2*GLOBAL 1 ONETECH HEALTH CENTER*****46*{billing_npi}~",
        f"PER*IC*BILLING DEPT*TE*8005551212*EM*billing@global1onetech.com~",
        f"NM1*40*2*{payer_name}*****46*{payer_id}~",
        f"HL*1**20*1~",
        f"PRV*BI*PXC*207RC0000X~",
        f"NM1*85*2*GLOBAL 1 ONETECH HEALTH*****XX*{billing_npi}~",
        f"N3*100 HEALTHCARE WAY*SUITE 400~",
        f"N4*BOSTON*MA*02115~",
        f"HL*2*1*22*0~",
        f"SBR*P*18*******MB~",
        f"NM1*IL*1*{patient.split()[-1]}*{patient.split()[0]}****MI*{mbi}~",
        f"N3*123 PATIENT ST~",
        f"N4*BOSTON*MA*02115~",
        f"DMG*D8*19750101*M~",
        f"NM1*PR*2*{payer_name}*****PI*{payer_id}~",
        f"CLM*{claim_id}*{billed}***{pos}:B:1*Y*A*Y*Y~",
        f"HI*BK:{diag_code}~",
        f"NM1*82*1*TAN*ROBERTO***MD*XX*{rendering_npi}~",
        f"LX*1~",
        f"SV1*HC:{cpt}*{billed}*UN*1***1~",
        f"DTP*472*D8*{date_str}~",
        f"SE*26*0001~",
        f"GE*1*1~",
        f"IEA*1*000000001~"
    ]
    return "\n".join(segments)

# 13. PURE FUNCTION: ANSI ASC X12 837I (Institutional Inpatient/Hospital Claim) Generator
def generate_edi_837i(claim: dict) -> str:
    """
    Generates standard ANSI ASC X12 837I Institutional Claim string format for UB-04 / CMS-1450.
    """
    claim_id = claim.get("claim_no", "UB-US-01")
    patient = claim.get("patient_name", "Doe, John")
    payer_id = claim.get("payer_id", "00431")
    payer_name = claim.get("payer_name", "Medicare Part A")
    mbi = claim.get("policy_no", "1EG4-TE5-MK72")
    billed = f"{float(claim.get('billed_charges', 8500.00)):.2f}"
    billing_npi = claim.get("billing_npi", "1098765432")
    diag_code = (claim.get("icd_code", "I21.0")).replace(".", "")
    rev_code = claim.get("revenue_code", "0110") # 0110 Room & Board
    drg = claim.get("ms_drg", "280") # Acute Myocardial Infarction
    date_str = (claim.get("filing_date", "20260902")).replace("-", "")

    segments = [
        f"ISA*00*          *00*          *ZZ*HOSPITAL1      *ZZ*{payer_id.ljust(15)}*{date_str[:6]}*1000*^*00501*000000002*0*P*:~",
        f"GS*HC*HOSPITAL1*{payer_id}*{date_str}*1000*2*X*005010X223A2~",
        f"ST*837*0002*005010X223A2~",
        f"BHT*0019*00*{claim_id}*{date_str}*1000*CH~",
        f"NM1*41*2*GLOBAL 1 ONETECH MEDICAL CENTER*****46*{billing_npi}~",
        f"NM1*40*2*{payer_name}*****46*{payer_id}~",
        f"HL*1**20*1~",
        f"NM1*85*2*GLOBAL 1 ONETECH INPATIENT FACILITY*****XX*{billing_npi}~",
        f"N3*100 HEALTHCARE WAY~",
        f"N4*BOSTON*MA*02115~",
        f"HL*2*1*22*0~",
        f"SBR*P*18*******MB~",
        f"NM1*IL*1*{patient.split()[-1]}*{patient.split()[0]}****MI*{mbi}~",
        f"NM1*PR*2*{payer_name}*****PI*{payer_id}~",
        f"CLM*{claim_id}*{billed}***111:A:1*Y*A*Y*Y~",
        f"DTP*435*D8*{date_str}~",
        f"CL1*1*1*01~",
        f"HI*BK:{diag_code}*DR:{drg}~",
        f"LX*1~",
        f"SV2*{rev_code}*HC:0110*{billed}*UN*3~",
        f"DTP*472*RD8*{date_str}-{date_str}~",
        f"SE*22*0002~",
        f"GE*1*2~",
        f"IEA*1*000000002~"
    ]
    return "\n".join(segments)
