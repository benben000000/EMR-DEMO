#!/usr/bin/env python3
"""
Neon Serverless PostgreSQL Migration & Seeder
Organization: Global 1 OneTech (https://global1onetech.com/)
Product: G1 Health EMR Enterprise Cloud

This script connects to Neon PostgreSQL using environment variables
(NO hardcoded credentials in source code) and initializes all 32 tables
with full US Healthcare Medicare, Commercial Insurance, and RCM schemas.
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor

def load_env():
    """Dynamically loads environment variables from .env if present."""
    env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.exists(env_file):
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())

load_env()

DATABASE_URL = os.environ.get("DATABASE_URL") or os.environ.get("POSTGRES_URL")

if not DATABASE_URL:
    print("ERROR: DATABASE_URL or POSTGRES_URL environment variable is not set!")
    sys.exit(1)

print("[INFO] Connecting to Neon Serverless PostgreSQL...")
conn = psycopg2.connect(DATABASE_URL)
conn.autocommit = True
cursor = conn.cursor()

print("[INFO] Creating tables in Neon PostgreSQL...")

# 1. Patients
cursor.execute("""
CREATE TABLE IF NOT EXISTS patients (
    id SERIAL PRIMARY KEY,
    patient_no VARCHAR(64) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    age INTEGER,
    gender VARCHAR(32),
    phone VARCHAR(64),
    address TEXT,
    blood_group VARCHAR(16),
    insurance_no VARCHAR(128),
    medicare_mbi VARCHAR(64),
    payer_id VARCHAR(64),
    payer_name VARCHAR(255),
    policy_no VARCHAR(128),
    group_no VARCHAR(128),
    secondary_payer_id VARCHAR(64),
    secondary_policy_no VARCHAR(128),
    copay_amount NUMERIC(10,2) DEFAULT 0.00,
    remaining_deductible NUMERIC(10,2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

# 2. Appointments
cursor.execute("""
CREATE TABLE IF NOT EXISTS appointments (
    id SERIAL PRIMARY KEY,
    patient_name VARCHAR(255) NOT NULL,
    doctor_name VARCHAR(255) NOT NULL,
    department VARCHAR(128),
    appointment_date VARCHAR(64),
    appointment_time VARCHAR(64),
    appointment_type VARCHAR(64),
    status VARCHAR(64),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

# 3. ADT Beds
cursor.execute("""
CREATE TABLE IF NOT EXISTS adt_beds (
    id VARCHAR(64) PRIMARY KEY,
    ward_name VARCHAR(128) NOT NULL,
    patient_name VARCHAR(255),
    diagnosis TEXT,
    attending_doctor VARCHAR(255),
    admission_date VARCHAR(64),
    status VARCHAR(64) NOT NULL,
    price VARCHAR(64),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

# 4. ER Cases
cursor.execute("""
CREATE TABLE IF NOT EXISTS er_cases (
    id SERIAL PRIMARY KEY,
    case_no VARCHAR(64) UNIQUE NOT NULL,
    triage_level VARCHAR(64) NOT NULL,
    patient_name VARCHAR(255) NOT NULL,
    age_sex VARCHAR(64),
    chief_complaint TEXT,
    vitals TEXT,
    bay_no VARCHAR(64),
    doctor_nurse VARCHAR(255),
    disposition TEXT,
    status VARCHAR(64),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

# 5. Prescriptions
cursor.execute("""
CREATE TABLE IF NOT EXISTS prescriptions (
    id SERIAL PRIMARY KEY,
    patient_name VARCHAR(255) NOT NULL,
    doctor_name VARCHAR(255),
    medicine_name VARCHAR(255) NOT NULL,
    dosage VARCHAR(128),
    frequency VARCHAR(128),
    duration VARCHAR(128),
    status VARCHAR(64),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

# 6. Billing Invoices
cursor.execute("""
CREATE TABLE IF NOT EXISTS billing_invoices (
    id SERIAL PRIMARY KEY,
    invoice_no VARCHAR(64) UNIQUE NOT NULL,
    patient_name VARCHAR(255) NOT NULL,
    item_desc TEXT,
    amount NUMERIC(10,2) DEFAULT 0.00,
    discount NUMERIC(10,2) DEFAULT 0.00,
    net_total NUMERIC(10,2) DEFAULT 0.00,
    payment_status VARCHAR(64),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

# 7. Lab Orders
cursor.execute("""
CREATE TABLE IF NOT EXISTS lab_orders (
    id SERIAL PRIMARY KEY,
    order_no VARCHAR(64) UNIQUE NOT NULL,
    patient_name VARCHAR(255) NOT NULL,
    test_name VARCHAR(255) NOT NULL,
    department VARCHAR(128),
    sample_status VARCHAR(64),
    result_value TEXT,
    reference_range VARCHAR(128),
    order_date VARCHAR(64)
);
""")

# 8. Radiology Orders
cursor.execute("""
CREATE TABLE IF NOT EXISTS radiology_orders (
    id SERIAL PRIMARY KEY,
    order_no VARCHAR(64) UNIQUE NOT NULL,
    patient_name VARCHAR(255) NOT NULL,
    modality VARCHAR(64) NOT NULL,
    anatomy VARCHAR(128) NOT NULL,
    doctor_name VARCHAR(255),
    scheduled_date VARCHAR(64),
    pacs_status VARCHAR(64),
    radiologist_report TEXT
);
""")

# 9. Accounting Vouchers
cursor.execute("""
CREATE TABLE IF NOT EXISTS accounting_vouchers (
    id SERIAL PRIMARY KEY,
    voucher_no VARCHAR(64) UNIQUE NOT NULL,
    narration TEXT NOT NULL,
    debit_acc VARCHAR(128) NOT NULL,
    credit_acc VARCHAR(128) NOT NULL,
    amount NUMERIC(12,2) DEFAULT 0.00,
    status VARCHAR(64),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

# 10. Inventory Items
cursor.execute("""
CREATE TABLE IF NOT EXISTS inventory_items (
    id SERIAL PRIMARY KEY,
    item_code VARCHAR(64) UNIQUE NOT NULL,
    item_name VARCHAR(255) NOT NULL,
    category VARCHAR(128) NOT NULL,
    batch_no VARCHAR(64),
    expiry_date VARCHAR(64),
    unit_price NUMERIC(10,2) DEFAULT 0.00,
    stock_qty INTEGER DEFAULT 0,
    reorder_level INTEGER DEFAULT 0
);
""")

# 11. Procurement PO
cursor.execute("""
CREATE TABLE IF NOT EXISTS procurement_po (
    id SERIAL PRIMARY KEY,
    po_no VARCHAR(64) UNIQUE NOT NULL,
    vendor_name VARCHAR(255) NOT NULL,
    total_amount NUMERIC(12,2) DEFAULT 0.00,
    po_date VARCHAR(64),
    delivery_status VARCHAR(64),
    payment_terms VARCHAR(128)
);
""")

# 12. Fixed Assets
cursor.execute("""
CREATE TABLE IF NOT EXISTS fixed_assets (
    id SERIAL PRIMARY KEY,
    asset_tag VARCHAR(64) UNIQUE NOT NULL,
    asset_name VARCHAR(255) NOT NULL,
    department VARCHAR(128) NOT NULL,
    purchase_date VARCHAR(64),
    cost NUMERIC(12,2) DEFAULT 0.00,
    status VARCHAR(64)
);
""")

# 13. OT Schedules
cursor.execute("""
CREATE TABLE IF NOT EXISTS ot_schedules (
    id SERIAL PRIMARY KEY,
    surgery_no VARCHAR(64) UNIQUE NOT NULL,
    patient_name VARCHAR(255) NOT NULL,
    procedure_name VARCHAR(255) NOT NULL,
    theater_no VARCHAR(64),
    surgeon_name VARCHAR(255),
    anesthetist VARCHAR(255),
    surgery_date VARCHAR(64),
    status VARCHAR(64)
);
""")

# 14. Vaccination Records
cursor.execute("""
CREATE TABLE IF NOT EXISTS vaccination_records (
    id SERIAL PRIMARY KEY,
    reg_no VARCHAR(64) UNIQUE NOT NULL,
    patient_name VARCHAR(255) NOT NULL,
    vaccine_name VARCHAR(255) NOT NULL,
    dose_stage VARCHAR(64),
    administered_date VARCHAR(64),
    next_due_date VARCHAR(64),
    batch_lot VARCHAR(64)
);
""")

# 15. Queue Tickets
cursor.execute("""
CREATE TABLE IF NOT EXISTS queue_tickets (
    id SERIAL PRIMARY KEY,
    token_no VARCHAR(64) UNIQUE NOT NULL,
    patient_name VARCHAR(255) NOT NULL,
    service_desk VARCHAR(128),
    issued_time VARCHAR(64),
    status VARCHAR(64)
);
""")

# 16. CSSD Batches
cursor.execute("""
CREATE TABLE IF NOT EXISTS cssd_batches (
    id SERIAL PRIMARY KEY,
    batch_no VARCHAR(64) UNIQUE NOT NULL,
    set_name VARCHAR(255) NOT NULL,
    tray_count INTEGER DEFAULT 1,
    autoclave_cycle VARCHAR(64),
    status VARCHAR(64),
    expiry_date VARCHAR(64)
);
""")

# 17. EHS Incidents
cursor.execute("""
CREATE TABLE IF NOT EXISTS ehs_incidents (
    id SERIAL PRIMARY KEY,
    incident_id VARCHAR(64) UNIQUE NOT NULL,
    employee_name VARCHAR(255) NOT NULL,
    department VARCHAR(128),
    incident_type VARCHAR(128),
    severity VARCHAR(64),
    logged_date VARCHAR(64),
    status VARCHAR(64)
);
""")

# 18. AI CRM Leads
cursor.execute("""
CREATE TABLE IF NOT EXISTS ai_crm_leads (
    id SERIAL PRIMARY KEY,
    lead_no VARCHAR(64) UNIQUE NOT NULL,
    patient_name VARCHAR(255) NOT NULL,
    channel VARCHAR(64),
    symptoms TEXT,
    predicted_dept VARCHAR(128),
    sentiment VARCHAR(64),
    status VARCHAR(64)
);
""")

# 19. SubStore Inventory
cursor.execute("""
CREATE TABLE IF NOT EXISTS substore_inventory (
    id SERIAL PRIMARY KEY,
    store_name VARCHAR(128) NOT NULL,
    item_name VARCHAR(255) NOT NULL,
    qty_available VARCHAR(64),
    min_required VARCHAR(64),
    restock_status VARCHAR(64)
);
""")

# 20. Doctor Incentives
cursor.execute("""
CREATE TABLE IF NOT EXISTS doctor_incentives (
    id SERIAL PRIMARY KEY,
    doctor_name VARCHAR(255) NOT NULL,
    department VARCHAR(128),
    total_encounters INTEGER DEFAULT 0,
    gross_billing NUMERIC(12,2) DEFAULT 0.00,
    incentive_rate VARCHAR(64),
    net_payable NUMERIC(12,2) DEFAULT 0.00,
    status VARCHAR(64)
);
""")

# 21. Telehealth Sessions
cursor.execute("""
CREATE TABLE IF NOT EXISTS telehealth_sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(64) UNIQUE NOT NULL,
    patient_name VARCHAR(255) NOT NULL,
    doctor_name VARCHAR(255) NOT NULL,
    platform VARCHAR(128),
    scheduled_time VARCHAR(64),
    connection_status VARCHAR(64)
);
""")

# 22. Marketing Referrals
cursor.execute("""
CREATE TABLE IF NOT EXISTS mkt_referrals (
    id SERIAL PRIMARY KEY,
    ref_id VARCHAR(64) UNIQUE NOT NULL,
    referrer_name VARCHAR(255) NOT NULL,
    institution VARCHAR(255),
    patient_referred VARCHAR(255),
    specialty VARCHAR(128),
    referral_fee NUMERIC(10,2) DEFAULT 0.00,
    status VARCHAR(64)
);
""")

# 23. Insurance Claims (US Healthcare & EDI 837P / 837I / CMS-1500 / UB-04)
cursor.execute("""
CREATE TABLE IF NOT EXISTS insurance_claims (
    id SERIAL PRIMARY KEY,
    claim_no VARCHAR(64) UNIQUE NOT NULL,
    patient_name VARCHAR(255) NOT NULL,
    claim_type VARCHAR(64),
    payer_id VARCHAR(64),
    payer_name VARCHAR(255),
    hmo_provider VARCHAR(255),
    icd_code VARCHAR(255),
    rendering_npi VARCHAR(64),
    billing_npi VARCHAR(64),
    pos_code VARCHAR(32),
    cpt_codes VARCHAR(255),
    modifiers VARCHAR(64),
    diagnosis_pointers VARCHAR(64),
    billed_charges NUMERIC(12,2) DEFAULT 0.00,
    allowed_amount NUMERIC(12,2) DEFAULT 0.00,
    insurance_paid NUMERIC(12,2) DEFAULT 0.00,
    contractual_adj NUMERIC(12,2) DEFAULT 0.00,
    patient_responsibility NUMERIC(12,2) DEFAULT 0.00,
    edi_837_payload TEXT,
    edi_835_status VARCHAR(64),
    claim_amount NUMERIC(12,2) DEFAULT 0.00,
    filing_date VARCHAR(64),
    claim_status VARCHAR(64)
);
""")

# 23B. Charge Master (US CPT/HCPCS Fee Schedule)
cursor.execute("""
CREATE TABLE IF NOT EXISTS charge_master (
    id SERIAL PRIMARY KEY,
    cpt_code VARCHAR(32) UNIQUE NOT NULL,
    description VARCHAR(255) NOT NULL,
    category VARCHAR(128),
    standard_charge NUMERIC(10,2) DEFAULT 0.00,
    medicare_allowable NUMERIC(10,2) DEFAULT 0.00,
    pos_default VARCHAR(32)
);
""")

# 24. Audit Logs (HIPAA Compliant with Tamper-Evident SHA-256 Checksum)
cursor.execute("""
CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    timestamp VARCHAR(64) NOT NULL,
    user_id VARCHAR(128) NOT NULL,
    role VARCHAR(64),
    action_name VARCHAR(255) NOT NULL,
    entity VARCHAR(128),
    record_id VARCHAR(128),
    details TEXT,
    ip_address VARCHAR(64),
    status VARCHAR(64),
    checksum VARCHAR(128)
);
""")

# 25. Clinical Templates
cursor.execute("""
CREATE TABLE IF NOT EXISTS clinical_templates (
    id SERIAL PRIMARY KEY,
    template_code VARCHAR(64) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    icd_code VARCHAR(128),
    template_body TEXT,
    created_date VARCHAR(64)
);
""")

# 26. Order Sets
cursor.execute("""
CREATE TABLE IF NOT EXISTS order_sets (
    id SERIAL PRIMARY KEY,
    set_name VARCHAR(255) UNIQUE NOT NULL,
    department VARCHAR(128),
    items_count VARCHAR(64),
    description TEXT
);
""")

# 27. Nursing Handovers
cursor.execute("""
CREATE TABLE IF NOT EXISTS nursing_handovers (
    id SERIAL PRIMARY KEY,
    bed_no VARCHAR(64) NOT NULL,
    patient_name VARCHAR(255) NOT NULL,
    medication_due VARCHAR(255),
    dose_route VARCHAR(128),
    scheduled_time VARCHAR(64),
    status VARCHAR(64)
);
""")

# 28. Verification Alerts
cursor.execute("""
CREATE TABLE IF NOT EXISTS verification_alerts (
    id SERIAL PRIMARY KEY,
    order_title VARCHAR(255) NOT NULL,
    department VARCHAR(128),
    requested_by VARCHAR(255),
    verification_reason TEXT,
    status VARCHAR(64)
);
""")

# 29. MRD Records
cursor.execute("""
CREATE TABLE IF NOT EXISTS mrd_records (
    id SERIAL PRIMARY KEY,
    mrd_no VARCHAR(64) UNIQUE NOT NULL,
    patient_name VARCHAR(255) NOT NULL,
    admission_date VARCHAR(64),
    discharge_date VARCHAR(64),
    icd_primary VARCHAR(128),
    custody_status VARCHAR(64)
);
""")

# 30. Helpdesk Queries
cursor.execute("""
CREATE TABLE IF NOT EXISTS helpdesk_queries (
    id SERIAL PRIMARY KEY,
    ticket_no VARCHAR(64) UNIQUE NOT NULL,
    caller_name VARCHAR(255) NOT NULL,
    department VARCHAR(128),
    query_text TEXT,
    priority VARCHAR(64),
    status VARCHAR(64)
);
""")

# 31. System Users
cursor.execute("""
CREATE TABLE IF NOT EXISTS system_users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(128) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role_key VARCHAR(64) NOT NULL,
    department VARCHAR(128),
    badge_label VARCHAR(128),
    status VARCHAR(64)
);
""")

print("[SUCCESS] All 32 tables successfully created in Neon PostgreSQL!")

def seed_if_empty(table_name, insert_sql):
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    if count == 0:
        cursor.execute(insert_sql)
        print(f"  [SEED] Seeded {table_name}")
    else:
        print(f"  [EXISTS] {table_name} already has {count} records")

print("\n[INFO] Seeding tables with US Healthcare & Clinical data...")

# Seed Patients
seed_if_empty("patients", """INSERT INTO patients (patient_no, name, age, gender, phone, address, blood_group, insurance_no, medicare_mbi, payer_id, payer_name, policy_no, group_no, copay_amount, remaining_deductible) VALUES 
    ('G1-US-0090', 'John Doe', 68, 'Male', '+1 (617) 555-0142', '124 Beacon St, Boston, MA 02116', 'O+', '1EG4-TE5-MK72', '1EG4-TE5-MK72', '00431', 'Medicare Part B (CMS)', '1EG4-TE5-MK72', 'MED-STD', 0.00, 60.00),
    ('G1-US-0091', 'Mary Smith', 42, 'Female', '+1 (617) 555-0198', '45 Commonwealth Ave, Boston, MA 02116', 'A+', 'BCBS-90218-44', NULL, '00060', 'Blue Cross Blue Shield (BCBS)', 'BCBS-90218-44', 'GRP-TECH99', 35.00, 450.00),
    ('G1-US-0092', 'Robert Johnson', 71, 'Male', '+1 (617) 555-0211', '89 Tremont St, Boston, MA 02108', 'B+', '2MB7-FA9-KL10', '2MB7-FA9-KL10', '00431', 'Medicare Part A and B', '2MB7-FA9-KL10', 'MED-SR', 0.00, 0.00),
    ('G1-US-0093', 'Emily Davis', 34, 'Female', '+1 (617) 555-0315', '210 Boylston St, Boston, MA 02116', 'AB+', 'UHC-88192-01', NULL, '87726', 'UnitedHealthcare Choice Plus', 'UHC-88192-01', 'UHC-CORP-4', 25.00, 200.00),
    ('G1-US-0094', 'Carlos Martinez', 53, 'Male', '+1 (617) 555-0456', '55 Cambridge Pkwy, Cambridge, MA 02142', 'O-', 'AET-44912-88', NULL, '60054', 'Aetna Open Access PPO', 'AET-44912-88', 'AET-8820', 30.00, 650.00)
""")

# Seed Charge Master
seed_if_empty("charge_master", """INSERT INTO charge_master (cpt_code, description, category, standard_charge, medicare_allowable, pos_default) VALUES 
    ('99204', 'Office Outpatient New Patient Level 4 (45-59 min)', 'Evaluation & Management', 285.00, 172.50, '11'),
    ('99214', 'Office Outpatient Established Patient Level 4 (30-39 min)', 'Evaluation & Management', 210.00, 134.80, '11'),
    ('99284', 'Emergency Department Visit Level 4 (High Severity)', 'Emergency Medicine', 650.00, 340.00, '23'),
    ('93000', '12-Lead Electrocardiogram (ECG) with interpretation & report', 'Cardiology Diagnostics', 95.00, 48.20, '11'),
    ('71046', 'Chest X-Ray 2-Views PA & Lateral', 'Radiology / Imaging', 145.00, 82.50, '11'),
    ('80053', 'Comprehensive Metabolic Panel (CMP Blood Test)', 'Laboratory Pathology', 85.00, 36.00, '11'),
    ('85025', 'Complete Blood Count (CBC) with Automated Differential', 'Laboratory Pathology', 65.00, 28.50, '11'),
    ('80061', 'Lipid Profile Panel (Cholesterol, HDL, Triglycerides)', 'Laboratory Pathology', 75.00, 32.00, '11'),
    ('0110', 'Inpatient Hospital Room & Board - General Medical Ward (Daily)', 'Institutional Facility', 1850.00, 1250.00, '21'),
    ('0200', 'Intensive Care Unit (ICU) Critical Care Bed (Daily)', 'Institutional Facility', 4500.00, 3200.00, '21'),
    ('44970', 'Laparoscopic Appendectomy Surgical Procedure', 'Surgical Procedures', 5400.00, 3650.00, '21')
""")

# Seed Insurance Claims
seed_if_empty("insurance_claims", """INSERT INTO insurance_claims (claim_no, patient_name, claim_type, payer_id, payer_name, hmo_provider, icd_code, rendering_npi, billing_npi, pos_code, cpt_codes, modifiers, diagnosis_pointers, billed_charges, allowed_amount, insurance_paid, contractual_adj, patient_responsibility, claim_amount, filing_date, claim_status) VALUES 
    ('CLM-US-2026-0101', 'John Doe', '837P (Professional)', '00431', 'Medicare Part B (CMS)', 'Medicare Part B', 'I10 - Essential HTN', '1928374655', '1098765432', '11', '99214, 93000', '-25', '1:1', 305.00, 183.00, 146.40, 122.00, 36.60, 305.00, '2026-08-22', 'Adjudicated / Paid (835)'),
    ('CLM-US-2026-0102', 'Mary Smith', '837P (Professional)', '00060', 'Blue Cross Blue Shield (BCBS)', 'BCBS Preferred PPO', 'E11.9 - Type 2 Diabetes', '1827364519', '1098765432', '11', '99204, 80053', '', '1:1', 370.00, 208.50, 123.50, 161.50, 85.00, 370.00, '2026-08-23', 'Submitted (837P)'),
    ('UB-US-2026-0045', 'Robert Johnson', '837I (Institutional)', '00431', 'Medicare Part A (CMS)', 'Medicare Part A', 'I21.0 - Acute STEMI', '1928374655', '1098765432', '21', 'MS-DRG 280 (Rev 0110, 0200)', '', '1:1', 14800.00, 9200.00, 7568.00, 5600.00, 0.00, 14800.00, '2026-08-23', 'Paid / Crossover Complete (835)'),
    ('CLM-US-2026-0103', 'Emily Davis', '837P (Professional)', '87726', 'UnitedHealthcare Choice Plus', 'UnitedHealthcare', 'J45.909 - Bronchial Asthma', '1738291045', '1098765432', '23', '99284, 71046', '', '1:1', 795.00, 422.50, 338.00, 372.50, 84.50, 795.00, '2026-08-24', 'Pre-Authorized / Ready for Billing')
""")

# Seed ADT Beds
seed_if_empty("adt_beds", """INSERT INTO adt_beds (id, ward_name, patient_name, diagnosis, attending_doctor, admission_date, status, price) VALUES 
    ('ICU-101', 'ICU (Critical Care)', 'Robert Johnson', 'Acute Anterior STEMI / Cath Lab Post-Op', 'Dr. Roberto Tan, MD', '2026-08-23', 'occupied', '$ 4,500/day'),
    ('ICU-102', 'ICU (Critical Care)', NULL, NULL, NULL, NULL, 'available', '$ 4,500/day'),
    ('ICU-103', 'ICU (Critical Care)', NULL, NULL, NULL, NULL, 'cleaning', '$ 4,500/day'),
    ('WARD-201', 'General Ward 2nd Flr', 'Mary Smith', 'Type 2 Diabetes with Hyperglycemia', 'Dr. Vincent Lim, MD', '2026-08-22', 'occupied', '$ 1,850/day'),
    ('WARD-202', 'General Ward 2nd Flr', NULL, NULL, NULL, NULL, 'available', '$ 1,850/day'),
    ('WARD-203', 'General Ward 2nd Flr', 'Emily Davis', 'Bronchial Asthma Exacerbation', 'Dr. Edward Hernandez, MD', '2026-08-23', 'occupied', '$ 1,850/day'),
    ('CARD-301', 'Cardiology Ward 3rd Flr', 'John Doe', 'Hypertensive Urgency / Angina', 'Dr. Roberto Tan, MD', '2026-08-24', 'occupied', '$ 2,200/day'),
    ('CARD-302', 'Cardiology Ward 3rd Flr', NULL, NULL, NULL, NULL, 'available', '$ 2,200/day'),
    ('PED-401', 'Pediatric Ward 4th Flr', 'Tommy Brown (Pediatric)', 'Acute Bronchiolitis', 'Dr. Patricia Santos, MD', '2026-08-24', 'occupied', '$ 1,950/day'),
    ('PED-402', 'Pediatric Ward 4th Flr', NULL, NULL, NULL, NULL, 'available', '$ 1,950/day')
""")

# Seed Billing Invoices
seed_if_empty("billing_invoices", """INSERT INTO billing_invoices (invoice_no, patient_name, item_desc, amount, discount, net_total, payment_status) VALUES 
    ('INV-2026-0891', 'John Doe', 'CPT 99214 Office Visit + CPT 93000 12-Lead ECG', 305.00, 122.00, 183.00, 'Paid (Medicare Part B 80% / Pt 20%)'),
    ('INV-2026-0892', 'Mary Smith', 'CPT 99204 New Patient + CPT 80053 CMP Comprehensive Panel', 370.00, 161.50, 208.50, 'Paid (BCBS Copay + Deductible)'),
    ('INV-2026-0893', 'Robert Johnson', 'UB-04 Inpatient Admission (Acute STEMI) - MS-DRG 280', 14800.00, 5600.00, 9200.00, 'Paid (Medicare Part A & Medigap Crossover)')
""")

# Seed ER Cases
seed_if_empty("er_cases", """INSERT INTO er_cases (case_no, triage_level, patient_name, age_sex, chief_complaint, vitals, bay_no, doctor_nurse, disposition, status) VALUES 
    ('ER-2026-01', 'Level 1', 'Carlos Martinez', '53 / M', 'Acute Anterior STEMI (Chest Pain)', 'BP: 165/105 | HR: 112 | SpO2: 91%', 'ER Bay 01 (STAT)', 'Dr. Roberto Tan, MD / Nurse Clara Dizon', 'Admit to Cath Lab / ICU', 'Active'),
    ('ER-2026-02', 'Level 2', 'Emily Davis', '34 / F', 'Acute Severe Asthma Exacerbation', 'BP: 130/85 | HR: 98 | SpO2: 92%', 'ER Bay 02', 'Dr. Edward Hernandez, MD / Nurse Clara Dizon', 'Nebulization & Observation', 'Active'),
    ('ER-2026-03', 'Level 3', 'Ramon Gomez', '27 / M', 'Right Forearm Deep Laceration', 'BP: 120/80 | HR: 82 | SpO2: 99%', 'ER Bay 03', 'Dr. Miguel Garcia, MD / Nurse Joy Cruz', 'Surgical Suture & Tetanus Toxoid', 'Active'),
    ('ER-2026-04', 'Level 4', 'Lisa Miller', '42 / F', 'Acute Gastroenteritis', 'BP: 110/70 | HR: 88 | SpO2: 98%', 'ER Bay 04', 'Dr. Patricia Santos, MD / Nurse Joy Cruz', 'IV Hydration & Electrolytes', 'Active')
""")

# Seed Appointments
seed_if_empty("appointments", """INSERT INTO appointments (patient_name, doctor_name, department, appointment_date, appointment_time, appointment_type, status) VALUES 
    ('John Doe', 'Dr. Roberto Tan, MD', 'Cardiology', '2026-08-24', '10:00 AM', 'OPD Follow-up', 'Confirmed'),
    ('Mary Smith', 'Dr. Vincent Lim, MD', 'Internal Medicine', '2026-08-24', '10:30 AM', 'New Consultation', 'Confirmed'),
    ('Robert Johnson', 'Dr. Edward Hernandez, MD', 'Pulmonology', '2026-08-24', '11:00 AM', 'Diagnostic Review', 'Scheduled'),
    ('Emily Davis', 'Dr. Miguel Garcia, MD', 'General Surgery', '2026-08-24', '01:30 PM', 'Post-Op Suture Removal', 'Scheduled')
""")

# Seed Prescriptions
seed_if_empty("prescriptions", """INSERT INTO prescriptions (patient_name, doctor_name, medicine_name, dosage, frequency, duration, status) VALUES 
    ('John Doe', 'Dr. Roberto Tan, MD', 'Amlodipine 10mg Tablets', '1 Tab', 'Once Daily (OD)', '30 Days', 'Dispensed'),
    ('John Doe', 'Dr. Roberto Tan, MD', 'Atorvastatin 20mg Tablets', '1 Tab', 'At Bedtime (HS)', '30 Days', 'Dispensed'),
    ('Mary Smith', 'Dr. Vincent Lim, MD', 'Metformin 500mg Tablets', '1 Tab', 'Twice Daily (BID)', '30 Days', 'Dispensed'),
    ('Carlos Martinez', 'Dr. Miguel Garcia, MD', 'Celecoxib 200mg Capsules', '1 Cap', 'Once Daily (OD)', '14 Days', 'Pending')
""")

# Seed Accounting Vouchers
seed_if_empty("accounting_vouchers", """INSERT INTO accounting_vouchers (voucher_no, narration, debit_acc, credit_acc, amount, status) VALUES 
    ('JV-2026-041', 'OPD Consultation Fee Receipt (Medicare Part B Electronic Transfer)', '1020 - Cash at Bank (Operating)', '4010 - OPD Consultation Revenue', 1830.00, 'Posted'),
    ('JV-2026-042', 'Pharmacy Drug Sales Daily Batch Reconciliation', '1020 - Cash at Bank (Operating)', '4020 - Pharmacy Sales Revenue', 14250.00, 'Posted'),
    ('JV-2026-043', 'Purchase of Sterile Medical Consumables & PPE', '5020 - Medical Supplies Exp', '2010 - Accounts Payable (MedSupply Inc)', 48500.00, 'Posted')
""")

# Seed Inventory Items
seed_if_empty("inventory_items", """INSERT INTO inventory_items (item_code, item_name, category, batch_no, expiry_date, unit_price, stock_qty, reorder_level) VALUES 
    ('MED-001', 'Amoxicillin 500mg Capsules', 'Antibiotics', 'BAT-2026-A1', '2027-08-31', 12.50, 450, 100),
    ('MED-002', 'Paracetamol 500mg Tablets', 'Analgesics', 'BAT-2026-B2', '2028-01-15', 3.50, 1200, 250),
    ('MED-003', 'Atorvastatin 20mg Tablets', 'Cardiovascular', 'BAT-2026-C3', '2027-11-30', 18.00, 380, 80),
    ('SUP-101', 'Sterile Surgical Gloves (Size 7.5)', 'Consumables', 'GLV-8819', '2029-05-01', 4.50, 850, 200),
    ('SUP-102', 'IV Cannula 20G with Injection Port', 'Consumables', 'CAN-9912', '2028-09-15', 2.80, 620, 150)
""")

# Seed Lab Orders
seed_if_empty("lab_orders", """INSERT INTO lab_orders (order_no, patient_name, test_name, department, sample_status, result_value, reference_range, order_date) VALUES 
    ('LAB-2026-091', 'John Doe', 'Complete Blood Count (CBC) with diff', 'Hematology', 'Resulted', 'WBC: 7.2 | Hb: 14.1 | Plt: 245', 'WBC 4.5-11.0 k/uL', '2026-08-24'),
    ('LAB-2026-092', 'Mary Smith', 'Comprehensive Metabolic Panel (CMP)', 'Clinical Chemistry', 'Resulted', 'Glucose: 118 | Creatinine: 0.9', 'Glucose 70-99 mg/dL', '2026-08-24'),
    ('LAB-2026-093', 'Robert Johnson', 'STAT High-Sensitivity Troponin-I', 'Critical Care Lab', 'Resulted', 'Troponin-I: 1.85 ng/mL (ELEVATED)', '< 0.04 ng/mL', '2026-08-24')
""")

# Seed Radiology Orders
seed_if_empty("radiology_orders", """INSERT INTO radiology_orders (order_no, patient_name, modality, anatomy, doctor_name, scheduled_date, pacs_status, radiologist_report) VALUES 
    ('RAD-2026-041', 'Robert Johnson', 'Chest X-Ray Digital', 'Chest 2-Views PA & Lat', 'Dr. Roberto Tan, MD', '2026-08-24', 'Verified in PACS', 'Cardiomegaly noted with mild pulmonary vascular congestion.'),
    ('RAD-2026-042', 'Mary Smith', 'Ultrasound Abdominal', 'Whole Abdomen', 'Dr. Vincent Lim, MD', '2026-08-24', 'Scheduled', 'Pending radiologist review.')
""")

# Seed Clinical Templates
seed_if_empty("clinical_templates", """INSERT INTO clinical_templates (template_code, title, icd_code, template_body, created_date) VALUES 
    ('.HTN-FOLLOWUP', 'Hypertension Routine Review', 'I10 - Essential HTN', 'Patient presents for routine BP follow-up. Medications tolerated well. No palpitations or chest pain.', '2026-08-24'),
    ('.DM-PANEL', 'Type 2 Diabetes Screening', 'E11.9 - DM Type 2', 'Fast Blood Sugar & HbA1c review. Diet compliance assessed. Foot examination normal.', '2026-08-24'),
    ('.ASTHMA-STAT', 'Acute Bronchospasm Protocol', 'J45.9 - Bronchial Asthma', 'Wheezing and chest tightness on exertion. Nebulization with Salbutamol administered.', '2026-08-24')
""")

# Seed Order Sets
seed_if_empty("order_sets", """INSERT INTO order_sets (set_name, department, items_count, description) VALUES 
    ('Standard Triple Therapy (H. Pylori)', 'Gastroenterology', '3 Meds', 'Omeprazole 20mg + Clarithromycin 500mg + Amoxicillin 1g for 14 Days'),
    ('Pediatric URI Starter Pack', 'Pediatrics', '2 Meds', 'Paracetamol Syrup 120mg/5mL + Cetirizine Drops 2.5mg/mL'),
    ('Post-Op Pain Management', 'Orthopedics', '3 Meds', 'Celecoxib 200mg + Tramadol 50mg PRN + Paracetamol 500mg IV')
""")

# Seed Nursing Handovers
seed_if_empty("nursing_handovers", """INSERT INTO nursing_handovers (bed_no, patient_name, medication_due, dose_route, scheduled_time, status) VALUES 
    ('ICU-101', 'Robert Johnson', 'Heparin Sodium Infusion', '500 Units/hr IV', '10:00 AM', 'Given / Verified'),
    ('WARD-201', 'Mary Smith', 'Insulin Glargine (Lantus)', '14 Units SubQ', '12:00 PM', 'Due Soon')
""")

# Seed Verification Alerts
seed_if_empty("verification_alerts", """INSERT INTO verification_alerts (order_title, department, requested_by, verification_reason, status) VALUES 
    ('Morphine Sulfate 10mg STAT IV', 'ICU Critical Care', 'Dr. Roberto Tan, MD', 'High-Alert Narcotic Dual Witness Required', 'Pending Witness Sign-Off'),
    ('Packed Red Blood Cells (PRBC) 2 Units', 'Trauma Bay', 'Dr. Edward Hernandez, MD', 'Transfusion Crossmatch Verification', 'Dual Witness Verified')
""")

# Seed AI CRM Leads
seed_if_empty("ai_crm_leads", """INSERT INTO ai_crm_leads (lead_no, patient_name, channel, symptoms, predicted_dept, sentiment, status) VALUES 
    ('LEAD-US-01', 'David Wilson', 'Web Portal', 'Experiencing sudden chest tightness and shortness of breath', 'Cardiology (OPD)', 'STAT High Priority', 'Routed to Triage'),
    ('LEAD-US-02', 'Sarah Jenkins', 'Patient Portal', 'Need routine follow up appointment for blood sugar review', 'Endocrinology', 'Routine Scheduled', 'Slot Confirmed')
""")

# Seed Telehealth Sessions
seed_if_empty("telehealth_sessions", """INSERT INTO telehealth_sessions (session_id, patient_name, doctor_name, platform, scheduled_time, connection_status) VALUES 
    ('TH-US-01', 'Mary Smith', 'Dr. Vincent Lim, MD', 'HIPAA Secure WebRTC HD', 'Today 04:00 PM', 'Waiting Room Ready'),
    ('TH-US-02', 'John Doe', 'Dr. Roberto Tan, MD', 'HIPAA Secure WebRTC HD', 'Today 04:30 PM', 'Link Dispatched')
""")

# Seed Doctor Incentives
seed_if_empty("doctor_incentives", """INSERT INTO doctor_incentives (doctor_name, department, total_encounters, gross_billing, incentive_rate, net_payable, status) VALUES 
    ('Dr. Roberto Tan, MD', 'Cardiology', 42, 38500.00, '60%', 23100.00, 'Approved for Payroll'),
    ('Dr. Miguel Garcia, MD', 'General Surgery', 28, 48000.00, '65%', 31200.00, 'Approved for Payroll'),
    ('Dr. Vincent Lim, MD', 'Internal Medicine', 35, 24500.00, '60%', 14700.00, 'Pending Review')
""")

# Seed Procurement PO
seed_if_empty("procurement_po", """INSERT INTO procurement_po (po_no, vendor_name, total_amount, po_date, delivery_status, payment_terms) VALUES 
    ('PO-US-2026-001', 'McKesson Medical-Surgical Inc', 48500.00, '2026-08-20', 'Delivered & Received in Central Store', 'Net 30 Days'),
    ('PO-US-2026-002', 'AmerisourceBergen Pharmaceuticals', 34200.00, '2026-08-22', 'In Transit via FedEx Medical Express', 'Net 30 Days'),
    ('PO-US-2026-003', 'Medline Industries LP', 18600.00, '2026-08-23', 'Awaiting Warehouse Dock Inspection', 'Net 15 Days'),
    ('PO-US-2026-004', 'Cardinal Health Distribution', 26400.00, '2026-08-24', 'Order Confirmed / Dispatched', 'Net 30 Days'),
    ('PO-US-2026-005', 'Stryker Surgical Endoscopy', 52000.00, '2026-08-24', 'Scheduled for Bi-Weekly Delivery', 'Net 45 Days')
""")

# Seed Fixed Assets
seed_if_empty("fixed_assets", """INSERT INTO fixed_assets (asset_tag, asset_name, department, purchase_date, cost, status) VALUES 
    ('EQ-RAD-001', 'GE Signa Pioneer 1.5T Magnetic Resonance Imaging (MRI)', 'Radiology / Diagnostic Imaging', '2024-03-15', 1250000.00, 'Operational / Calibrated'),
    ('EQ-RAD-002', 'Siemens Somatom 128-Slice Computed Tomography (CT)', 'Emergency & Inpatient Radiology', '2024-06-20', 850000.00, 'Operational / Calibrated'),
    ('EQ-SUR-001', 'Stryker 1688 AIM 4K Laparoscopic Surgical Video Tower', 'Operating Theater Suite 1', '2025-01-10', 165000.00, 'Operational / Sterile'),
    ('EQ-CAR-001', 'Philips Azurion 7 Biplane Cardiac Catheterization Lab', 'Cardiology Interventional Suite', '2023-11-05', 1450000.00, 'Operational / Active'),
    ('EQ-ICU-001', 'Drager Evita V800 Critical Care Ventilators (x6 Units)', 'Intensive Care Unit (ICU)', '2024-09-12', 240000.00, 'Operational / Bio-Med Inspected'),
    ('EQ-LAB-001', 'Roche Cobas 8000 Clinical Chemistry & Immunoassay Analyzer', 'Diagnostic Pathology Laboratory', '2024-02-18', 420000.00, 'Operational / Daily QC Passed')
""")

# Seed OT Schedules
seed_if_empty("ot_schedules", """INSERT INTO ot_schedules (surgery_no, patient_name, procedure_name, theater_no, surgeon_name, anesthetist, surgery_date, status) VALUES 
    ('OT-2026-081', 'Carlos Martinez', 'Laparoscopic Appendectomy (CPT 44970)', 'OR Theater 1', 'Dr. Miguel Garcia, MD', 'Dr. Sarah Connor, MD', '2026-08-25 08:00 AM', 'Scheduled (Pre-Op Cleared)'),
    ('OT-2026-082', 'Robert Johnson', 'Percutaneous Coronary Intervention (PCI) & Drug-Eluting Stent', 'Cath Lab 1', 'Dr. Roberto Tan, MD', 'Dr. Vincent Lim, MD', '2026-08-25 10:30 AM', 'Completed / Recovering'),
    ('OT-2026-083', 'Jessica Taylor', 'Diagnostic Hysteroscopy & Polypectomy', 'OR Theater 2', 'Dr. Patricia Santos, MD', 'Dr. Sarah Connor, MD', '2026-08-25 01:00 PM', 'Scheduled (NPO Confirmed)'),
    ('OT-2026-084', 'James Anderson', 'Right Forearm Extensor Tendon Repair & Neurolysis', 'OR Theater 3', 'Dr. Miguel Garcia, MD', 'Dr. Edward Hernandez, MD', '2026-08-25 03:00 PM', 'Scheduled'),
    ('OT-2026-085', 'David Wilson', 'Total Knee Arthroplasty (CPT 27447)', 'OR Theater 1', 'Dr. Miguel Garcia, MD', 'Dr. Sarah Connor, MD', '2026-08-26 08:30 AM', 'Pre-Op Workup in Progress')
""")

# Seed Vaccination Records
seed_if_empty("vaccination_records", """INSERT INTO vaccination_records (reg_no, patient_name, vaccine_name, dose_stage, administered_date, next_due_date, batch_lot) VALUES 
    ('VAC-US-01', 'John Doe', 'Pneumococcal Conjugate PCV20 (Prevnar 20)', 'Single Adult Dose', '2026-08-24', 'Complete', 'LOT-PV20-8819'),
    ('VAC-US-02', 'Mary Smith', 'Influenza Quadrivalent Vaccine (Fluzone HD)', 'Annual Season 2026-2027', '2026-08-24', '2027-08-24', 'LOT-FLU-2026A'),
    ('VAC-US-03', 'Emily Davis', 'Tdap (Tetanus, Diphtheria, Acellular Pertussis)', '10-Yr Booster Dose', '2026-08-23', '2036-08-23', 'LOT-TDAP-4412'),
    ('VAC-US-04', 'Carlos Martinez', 'Recombinant Zoster Vaccine (Shingrix)', 'Dose 1 of 2 (Age 50+)', '2026-08-22', '2026-10-22', 'LOT-SHX-9901'),
    ('VAC-US-05', 'Jessica Taylor', 'Human Papillomavirus 9-Valent (Gardasil 9)', 'Dose 3 of 3 Series', '2026-08-20', 'Complete', 'LOT-G9-11823'),
    ('VAC-US-06', 'David Wilson', 'COVID-19 mRNA Updated Formulation (Comirnaty)', 'Fall 2026 Booster', '2026-08-24', '2027-08-24', 'LOT-CV19-7721')
""")

# Seed Queue Tickets
seed_if_empty("queue_tickets", """INSERT INTO queue_tickets (token_no, patient_name, service_desk, issued_time, status) VALUES 
    ('Q-REG-101', 'John Doe', 'Front Desk Admissions & Medicare Verify', '08:45 AM', 'Completed'),
    ('Q-CLIN-201', 'John Doe', 'Cardiology Clinic - Dr. Roberto Tan, MD', '09:00 AM', 'In Consultation'),
    ('Q-LAB-301', 'Mary Smith', 'Central Phlebotomy Lab Station 1', '09:15 AM', 'Serving Now'),
    ('Q-RAD-401', 'Emily Davis', 'Radiology Chest X-Ray Suite', '09:30 AM', 'Waiting'),
    ('Q-CASH-501', 'Carlos Martinez', 'Cashier Desk 2 - Insurance Copays', '09:40 AM', 'Waiting'),
    ('Q-PHRM-601', 'Sarah Jenkins', 'Outpatient Pharmacy Window 1', '09:45 AM', 'Ready for Pickup'),
    ('Q-REG-102', 'Jessica Taylor', 'Patient Registration Window 3', '09:50 AM', 'Calling'),
    ('Q-CLIN-202', 'David Wilson', 'Pulmonology Clinic - Dr. Hernandez', '10:00 AM', 'Waiting')
""")

# Seed CSSD Batches
seed_if_empty("cssd_batches", """INSERT INTO cssd_batches (batch_no, set_name, tray_count, autoclave_cycle, status, expiry_date) VALUES 
    ('CSSD-2026-041', 'Major Laparotomy & Vascular Surgical Set', 4, '134C High-Vacuum Steam (18 Min)', 'Sterile / Released (BI Negative)', '2026-09-24'),
    ('CSSD-2026-042', 'Laparoscopic Endosurgical Handpiece Set', 3, 'Low-Temp Hydrogen Peroxide Plasma', 'Sterile / Released (Chemical Passed)', '2026-09-24'),
    ('CSSD-2026-043', 'Orthopedic Total Joint Reamer Set', 6, '134C Porous Steam Cycle (25 Min)', 'In Autoclave Chamber #2', '2026-09-25'),
    ('CSSD-2026-044', 'Emergency Trauma Resuscitation Cutdown Trays', 4, '134C High-Vacuum Steam (18 Min)', 'Sterile / Stored in ER Sub-Store', '2026-09-24'),
    ('CSSD-2026-045', 'Ophthalmic Micro-Surgical Phaco Set', 2, 'Steam Gravity Displacement', 'Cooling & Packaging Station', '2026-09-25')
""")

# Seed EHS Incidents
seed_if_empty("ehs_incidents", """INSERT INTO ehs_incidents (incident_id, employee_name, department, incident_type, severity, logged_date, status) VALUES 
    ('EHS-2026-001', 'Nurse Clara Dizon', 'Inpatient Ward 2', 'Near-Miss Needlestick Safety Shield Activation', 'Minor / Zero Harm', '2026-08-20', 'Reviewed by EHS Officer / Closed'),
    ('EHS-2026-002', 'Tech Kevin Brooks', 'Diagnostic Pathology Laboratory', 'Formalin Vapor Containment Alarm Test', 'Informational Drill', '2026-08-22', 'Drill Completed 100% Passed'),
    ('EHS-2026-003', 'Elena Villar, CPA', 'Finance Administration', 'Ergonomic Desk & Display Review', 'Low Severity', '2026-08-23', 'Ergonomic Keyboard Deployed / Closed'),
    ('EHS-2026-004', 'Nurse Ronald Valdez', 'Emergency Department', 'Slip on Wet Floor during STAT Resuscitation', 'Minor / No Injury', '2026-08-24', 'Corrective Anti-Slip Mat Deployed')
""")

# Seed SubStore Inventory
seed_if_empty("substore_inventory", """INSERT INTO substore_inventory (store_name, item_name, qty_available, min_required, restock_status) VALUES 
    ('ICU Pyxis MedStation #1', 'Norepinephrine Bitartrate 4mg/4mL Injection', '18 Vials', '10 Vials', 'Optimal Stock'),
    ('ICU Pyxis MedStation #1', 'Midazolam HCl 5mg/mL STAT Injection', '24 Vials', '15 Vials', 'Optimal Stock'),
    ('ER Crash Cart Bay 01', 'Epinephrine 1mg/10mL Prefilled Syringes', '12 Syringes', '6 Syringes', 'Ready / Inspected'),
    ('ER Crash Cart Bay 01', 'Amiodarone HCl 150mg/3mL Vials', '8 Vials', '6 Vials', 'Ready / Inspected'),
    ('OR Satellite Pharmacy', 'Propofol Injectable Emulsion 20mL (1%)', '45 Vials', '20 Vials', 'Optimal Stock'),
    ('Ward 3 Clean Supply Room', '0.9% Normal Saline 500mL IV Bags', '64 Bags', '30 Bags', 'Optimal Stock'),
    ('Ward 3 Clean Supply Room', 'Luer-Lock 10mL Syringes with Safety Needles', '120 Units', '50 Units', 'Optimal Stock'),
    ('Dialysis Unit Pyxis', 'Heparin Sodium 10,000 Units/mL Vials', '15 Vials', '8 Vials', 'Optimal Stock')
""")

# Seed Marketing Referrals
seed_if_empty("mkt_referrals", """INSERT INTO mkt_referrals (ref_id, referrer_name, institution, patient_referred, specialty, referral_fee, status) VALUES 
    ('REF-US-001', 'Dr. Karen White, MD', 'Boston Primary Care Associates', 'John Doe', 'Cardiology', 150.00, 'Approved & Credited'),
    ('REF-US-002', 'Dr. Steven Cho, MD', 'Beacon Hill Family Medicine', 'Mary Smith', 'Endocrinology', 150.00, 'Approved & Credited'),
    ('REF-US-003', 'Dr. Laura Adams, MD', 'Cambridge Community Health Clinic', 'Robert Johnson', 'Interventional Cardiology', 200.00, 'Approved & Credited'),
    ('REF-US-004', 'Dr. Daniel Miller, MD', 'Mass General Brigham Affiliated PCP', 'Emily Davis', 'Pulmonology', 150.00, 'Processed'),
    ('REF-US-005', 'Dr. Rachel Green, MD', 'Back Bay Medical Group', 'Carlos Martinez', 'General Surgery', 175.00, 'Processed')
""")

# Seed MRD Records
seed_if_empty("mrd_records", """INSERT INTO mrd_records (mrd_no, patient_name, admission_date, discharge_date, icd_primary, custody_status) VALUES 
    ('MRD-2026-001', 'John Doe', '2026-08-15', '2026-08-18', 'I10 - Essential HTN', 'Archived / Digital Chart Locked'),
    ('MRD-2026-002', 'Mary Smith', '2026-08-10', '2026-08-14', 'E11.9 - Type 2 Diabetes', 'Archived / Certified Complete'),
    ('MRD-2026-003', 'Robert Johnson', '2026-08-01', '2026-08-05', 'I25.10 - CAD Native Artery', 'Archived / Legal Hold Cleared'),
    ('MRD-2026-004', 'Emily Davis', '2026-07-20', '2026-07-22', 'J45.909 - Bronchial Asthma', 'Archived / ROI Authorized'),
    ('MRD-2026-005', 'Carlos Martinez', '2026-08-20', '2026-08-22', 'K35.80 - Acute Appendicitis', 'In Review / Coding Audit')
""")

# Seed Helpdesk Queries
seed_if_empty("helpdesk_queries", """INSERT INTO helpdesk_queries (ticket_no, caller_name, department, query_text, priority, status) VALUES 
    ('TKT-2026-01', 'Dr. Roberto Tan, MD', 'Cardiology Clinic', 'DICOM PACS viewer calibration for High-DPI monitor', 'Medium Priority', 'Resolved / Workstation Calibrated'),
    ('TKT-2026-02', 'Nurse Clara Dizon', 'ICU Ward', 'Mindray telemetry bed 102 wireless signal check', 'High Priority', 'Completed / Network Channel Reassigned'),
    ('TKT-2026-03', 'Mark Mendoza', 'Billing & Cashier', 'Configure EDI 837 clearinghouse SFTP automated nightly submission', 'High Priority', 'Active / Testing Cleared'),
    ('TKT-2026-04', 'Pharm. Leo Santos, RPh', 'Pharmacy Dispensary', 'Barcode scanner recalibration for Pyxis dispensing drawer 3', 'Normal Priority', 'Resolved / Scanner Firmware Updated'),
    ('TKT-2026-05', 'Joy Pascual', 'Front Desk Admissions', 'Fast badge reader enrollment for new rotating clinical staff', 'Low Priority', 'Completed')
""")

# Seed System Users
seed_if_empty("system_users", """INSERT INTO system_users (username, full_name, role_key, department, badge_label, status) VALUES 
    ('admin', 'Administrator', 'admin', 'Hospital Administration', 'Super Admin', 'Active'),
    ('doctor', 'Dr. Roberto Tan, MD', 'doctor', 'Cardiology & Outpatient Clinic', 'Doctor (MD)', 'Active'),
    ('nurse', 'Nurse Clara Dizon', 'nurse', 'Inpatient Ward & Station', 'Nurse (RN)', 'Active'),
    ('accountant', 'Elena Villar, CPA', 'accountant', 'Finance & Accounting', 'Accountant', 'Active'),
    ('billing', 'Mark Mendoza', 'billing', 'Cashier & Insurance Claims', 'Billing', 'Active'),
    ('pharmacy', 'Pharm. Leo Santos, RPh', 'pharmacy', 'Hospital Pharmacy & Dispensary', 'Pharmacist', 'Active'),
    ('labtech', 'Sarah Cruz, RMT', 'labtech', 'Diagnostic Pathology Laboratory', 'Lab Tech', 'Active'),
    ('reception', 'Joy Pascual', 'reception', 'Front Desk & Patient Admissions', 'Reception', 'Active')
""")

# Seed Audit Logs
seed_if_empty("audit_logs", """INSERT INTO audit_logs (timestamp, user_id, role, action_name, entity, record_id, details, ip_address, status, checksum) VALUES 
    ('2026-08-24 08:00:15', 'admin', 'admin', 'SYSTEM_LOGIN', 'system_users', 'admin', 'Initial system login via secure token', '127.0.0.1', 'SUCCESS', 'a1b2c3d4e5f60718293a4b5c6d7e8f90a1b2c3d4e5f60718293a4b5c6d7e8f90'),
    ('2026-08-24 08:05:22', 'doctor', 'doctor', 'VIEW_PATIENT_CHART (G1-US-0090)', 'patients', 'G1-US-0090', 'Accessed electronic health chart for clinical encounter', '127.0.0.1', 'SUCCESS', 'b2c3d4e5f60718293a4b5c6d7e8f90a1b2c3d4e5f60718293a4b5c6d7e8f90a1'),
    ('2026-08-24 08:12:45', 'nurse', 'nurse', 'UPDATE_BED_STATUS (CARD-301 -> OCCUPIED)', 'adt_beds', 'CARD-301', 'Admitted patient to cardiology bed', '127.0.0.1', 'SUCCESS', 'c3d4e5f60718293a4b5c6d7e8f90a1b2c3d4e5f60718293a4b5c6d7e8f90a1b2')
""")

conn.close()
print("\n[SUCCESS] Neon PostgreSQL Migration & Seeding Complete 100%!")
