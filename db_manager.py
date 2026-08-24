import sqlite3
import os
import json
import time

DB_PATH = os.environ.get("DANPHE_DB_PATH", os.path.join(os.path.dirname(__file__), "danphe_emr.db"))

if not os.access(os.path.dirname(DB_PATH) or ".", os.W_OK):
    DB_PATH = "/tmp/danphe_emr.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Patients
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_no TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        age INTEGER,
        gender TEXT,
        phone TEXT,
        address TEXT,
        blood_group TEXT,
        insurance_no TEXT,
        created_at TEXT
    )
    """)

    # 2. Appointments
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_name TEXT NOT NULL,
        doctor_name TEXT NOT NULL,
        department TEXT,
        appointment_date TEXT,
        appointment_time TEXT,
        appointment_type TEXT,
        status TEXT,
        created_at TEXT
    )
    """)

    # 3. ADT Beds
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS adt_beds (
        id TEXT PRIMARY KEY,
        ward_name TEXT NOT NULL,
        patient_name TEXT,
        diagnosis TEXT,
        attending_doctor TEXT,
        admission_date TEXT,
        status TEXT NOT NULL,
        price TEXT,
        updated_at TEXT
    )
    """)

    # 4. ER Cases
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS er_cases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_no TEXT UNIQUE NOT NULL,
        triage_level TEXT NOT NULL,
        patient_name TEXT NOT NULL,
        age_sex TEXT,
        chief_complaint TEXT,
        vitals TEXT,
        bay_no TEXT,
        doctor_nurse TEXT,
        disposition TEXT,
        status TEXT,
        created_at TEXT
    )
    """)

    # 5. Prescriptions
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS prescriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_name TEXT NOT NULL,
        doctor_name TEXT,
        medicine_name TEXT NOT NULL,
        dosage TEXT,
        frequency TEXT,
        duration TEXT,
        status TEXT,
        created_at TEXT
    )
    """)

    # 6. Billing Invoices
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS billing_invoices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_no TEXT UNIQUE NOT NULL,
        patient_name TEXT NOT NULL,
        item_desc TEXT,
        amount REAL,
        discount REAL,
        net_total REAL,
        payment_status TEXT,
        created_at TEXT
    )
    """)

    # 7. Lab Orders
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS lab_orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_no TEXT UNIQUE NOT NULL,
        patient_name TEXT NOT NULL,
        test_name TEXT NOT NULL,
        department TEXT,
        sample_status TEXT,
        result_value TEXT,
        reference_range TEXT,
        order_date TEXT
    )
    """)

    # 8. Radiology Orders
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS radiology_orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_no TEXT UNIQUE NOT NULL,
        patient_name TEXT NOT NULL,
        modality TEXT NOT NULL,
        anatomy TEXT NOT NULL,
        doctor_name TEXT,
        scheduled_date TEXT,
        status TEXT
    )
    """)

    # 9. Accounting Vouchers
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS accounting_vouchers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        voucher_no TEXT UNIQUE NOT NULL,
        narration TEXT,
        debit_acc TEXT,
        credit_acc TEXT,
        amount REAL,
        status TEXT,
        created_at TEXT
    )
    """)

    # 10. Inventory Items
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inventory_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_code TEXT UNIQUE NOT NULL,
        item_name TEXT NOT NULL,
        category TEXT,
        batch_no TEXT,
        expiry_date TEXT,
        unit_price REAL,
        stock_qty INTEGER,
        reorder_level INTEGER
    )
    """)

    # 11. Procurement POs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS procurement_po (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        po_no TEXT UNIQUE NOT NULL,
        supplier_name TEXT NOT NULL,
        items_summary TEXT,
        total_amount REAL,
        order_date TEXT,
        delivery_date TEXT,
        status TEXT
    )
    """)

    # 12. Fixed Assets
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fixed_assets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        asset_code TEXT UNIQUE NOT NULL,
        asset_name TEXT NOT NULL,
        department TEXT,
        serial_no TEXT,
        purchase_date TEXT,
        cost REAL,
        status TEXT
    )
    """)

    # 13. OT Schedules
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ot_schedules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        surgery_no TEXT UNIQUE NOT NULL,
        patient_name TEXT NOT NULL,
        procedure_name TEXT NOT NULL,
        ot_room TEXT,
        surgeon_name TEXT,
        anesthesiologist TEXT,
        schedule_date TEXT,
        status TEXT
    )
    """)

    # 14. Vaccination Records
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vaccination_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        record_no TEXT UNIQUE NOT NULL,
        patient_name TEXT NOT NULL,
        vaccine_name TEXT NOT NULL,
        dose_number TEXT,
        batch_no TEXT,
        administered_by TEXT,
        date_given TEXT
    )
    """)

    # 15. Queue Tickets
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS queue_tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        token_no TEXT UNIQUE NOT NULL,
        patient_name TEXT NOT NULL,
        department TEXT,
        counter_no TEXT,
        priority_level TEXT,
        status TEXT,
        issued_at TEXT
    )
    """)

    # 16. CSSD Batches
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cssd_batches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cycle_no TEXT UNIQUE NOT NULL,
        autoclave_unit TEXT NOT NULL,
        tray_type TEXT,
        sterilization_time TEXT,
        biological_indicator TEXT,
        operator TEXT,
        status TEXT
    )
    """)

    # 17. EHS Incidents
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ehs_incidents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        incident_no TEXT UNIQUE NOT NULL,
        incident_date TEXT NOT NULL,
        department TEXT,
        severity TEXT,
        description TEXT,
        reported_by TEXT,
        status TEXT
    )
    """)

    # 18. AI CRM Leads
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ai_crm_leads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lead_no TEXT UNIQUE NOT NULL,
        patient_name TEXT NOT NULL,
        channel TEXT,
        symptoms TEXT,
        predicted_dept TEXT,
        sentiment TEXT,
        status TEXT,
        created_at TEXT
    )
    """)

    # 19. Sub-Store Inventory
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS substore_inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        substore_name TEXT NOT NULL,
        item_name TEXT NOT NULL,
        current_stock TEXT,
        min_threshold TEXT,
        status TEXT
    )
    """)

    # 20. Doctor Incentives
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS doctor_incentives (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        doctor_name TEXT NOT NULL,
        department TEXT,
        total_encounters INTEGER,
        gross_billing REAL,
        incentive_rate TEXT,
        net_payable REAL,
        status TEXT
    )
    """)

    # 21. Telehealth Sessions
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS telehealth_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT UNIQUE NOT NULL,
        patient_name TEXT NOT NULL,
        doctor_name TEXT,
        platform TEXT,
        scheduled_time TEXT,
        connection_status TEXT
    )
    """)

    # 22. Marketing Referrals
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS mkt_referrals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ref_id TEXT UNIQUE NOT NULL,
        referrer_name TEXT NOT NULL,
        institution TEXT,
        patient_referred TEXT,
        specialty TEXT,
        referral_fee REAL,
        status TEXT
    )
    """)

    # 23. Insurance Claims
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS insurance_claims (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        claim_no TEXT UNIQUE NOT NULL,
        patient_name TEXT NOT NULL,
        hmo_provider TEXT,
        icd_code TEXT,
        claim_amount REAL,
        filing_date TEXT,
        claim_status TEXT
    )
    """)

    # 24. Audit Logs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        user_id TEXT,
        action_name TEXT,
        ip_address TEXT,
        status TEXT
    )
    """)

    conn.commit()

    # Seed each table individually if empty
    seed_if_empty(cursor, "patients", """INSERT INTO patients (patient_no, name, age, gender, phone, address, blood_group, insurance_no, created_at) VALUES 
        ('G1-2026-0090', 'Juan Dela Cruz', 45, 'Male', '+63 917 123 4567', 'Quezon City, Metro Manila', 'O+', 'PH-99281-90', '2026-08-24 08:00:00'),
        ('G1-2026-0091', 'Maria Santos', 38, 'Female', '+63 918 234 5678', 'Makati City, Metro Manila', 'A+', 'PH-44812-33', '2026-08-24 08:15:00'),
        ('G1-2026-0092', 'Antonio Reyes', 62, 'Male', '+63 920 345 6789', 'Pasig City, Metro Manila', 'B+', 'PH-11029-44', '2026-08-24 08:30:00'),
        ('G1-2026-0093', 'Elena Ramos', 29, 'Female', '+63 922 456 7890', 'Taguig City, Metro Manila', 'AB+', 'PH-88931-12', '2026-08-24 08:45:00'),
        ('G1-2026-0094', 'Carlos Mendoza', 51, 'Male', '+63 926 567 8901', 'Mandaluyong City, Metro Manila', 'O-', 'PH-77123-55', '2026-08-24 09:00:00')
    """)

    seed_if_empty(cursor, "adt_beds", """INSERT INTO adt_beds (id, ward_name, patient_name, diagnosis, attending_doctor, admission_date, status, price, updated_at) VALUES 
        ('ICU-101', 'ICU (Critical Care)', 'Antonio Reyes', 'Acute Respiratory Distress Syndrome', 'Dr. Edward Hernandez, MD', '2026-08-23', 'occupied', '₱ 8,500/day', '2026-08-24 09:00:00'),
        ('ICU-102', 'ICU (Critical Care)', NULL, NULL, NULL, NULL, 'available', '₱ 8,500/day', '2026-08-24 09:00:00'),
        ('ICU-103', 'ICU (Critical Care)', NULL, NULL, NULL, NULL, 'cleaning', '₱ 8,500/day', '2026-08-24 09:00:00'),
        ('WARD-201', 'General Ward 2nd Flr', 'Maria Santos', 'Type 2 Diabetes with Hyperglycemia', 'Dr. Vincent Lim, MD', '2026-08-22', 'occupied', '₱ 2,500/day', '2026-08-24 09:00:00'),
        ('WARD-202', 'General Ward 2nd Flr', NULL, NULL, NULL, NULL, 'available', '₱ 2,500/day', '2026-08-24 09:00:00'),
        ('WARD-203', 'General Ward 2nd Flr', 'Elena Ramos', 'Post-Op Appendectomy Recovery', 'Dr. Miguel Garcia, MD', '2026-08-23', 'occupied', '₱ 2,500/day', '2026-08-24 09:00:00'),
        ('CARD-301', 'Cardiology Ward 3rd Flr', 'Juan Dela Cruz', 'Hypertensive Urgency / Angina', 'Dr. Roberto Tan, MD', '2026-08-24', 'occupied', '₱ 3,500/day', '2026-08-24 09:00:00'),
        ('CARD-302', 'Cardiology Ward 3rd Flr', NULL, NULL, NULL, NULL, 'available', '₱ 3,500/day', '2026-08-24 09:00:00'),
        ('PED-401', 'Pediatric Ward 4th Flr', 'Leo Bautista (Pediatric)', 'Acute Bronchiolitis', 'Dr. Patricia Santos, MD', '2026-08-24', 'occupied', '₱ 2,800/day', '2026-08-24 09:00:00'),
        ('PED-402', 'Pediatric Ward 4th Flr', NULL, NULL, NULL, NULL, 'available', '₱ 2,800/day', '2026-08-24 09:00:00')
    """)

    seed_if_empty(cursor, "er_cases", """INSERT INTO er_cases (case_no, triage_level, patient_name, age_sex, chief_complaint, vitals, bay_no, doctor_nurse, disposition, status, created_at) VALUES 
        ('ER-2026-01', 'Level 1', 'Carlos Mendoza', '51 / M', 'Acute Anterior STEMI (Chest Pain)', 'BP: 165/105 | HR: 112 | SpO2: 91%', 'ER Bay 01 (STAT)', 'Dr. Roberto Tan, MD / Nurse Clara Dizon', 'Admit to Cath Lab / ICU', 'Active', '2026-08-24 08:30:00'),
        ('ER-2026-02', 'Level 2', 'Beatriz Aquino', '34 / F', 'Acute Severe Asthma Exacerbation', 'BP: 130/85 | HR: 98 | SpO2: 92%', 'ER Bay 02', 'Dr. Edward Hernandez, MD / Nurse Clara Dizon', 'Nebulization & Observation', 'Active', '2026-08-24 08:45:00'),
        ('ER-2026-03', 'Level 3', 'Ramon Gomez', '27 / M', 'Right Forearm Deep Laceration', 'BP: 120/80 | HR: 82 | SpO2: 99%', 'ER Bay 03', 'Dr. Miguel Garcia, MD / Nurse Joy Cruz', 'Surgical Suture & Tetanus Toxoid', 'Active', '2026-08-24 09:10:00'),
        ('ER-2026-04', 'Level 4', 'Liza Del Rosario', '42 / F', 'Acute Gastroenteritis', 'BP: 110/70 | HR: 88 | SpO2: 98%', 'ER Bay 04', 'Dr. Patricia Santos, MD / Nurse Joy Cruz', 'IV Hydration & Electrolytes', 'Active', '2026-08-24 09:20:00')
    """)

    seed_if_empty(cursor, "appointments", """INSERT INTO appointments (patient_name, doctor_name, department, appointment_date, appointment_time, appointment_type, status, created_at) VALUES 
        ('Juan Dela Cruz', 'Dr. Roberto Tan, MD', 'Cardiology', '2026-08-24', '10:00 AM', 'OPD Follow-up', 'Confirmed', '2026-08-24 08:00:00'),
        ('Maria Santos', 'Dr. Vincent Lim, MD', 'Internal Medicine', '2026-08-24', '10:30 AM', 'New Consultation', 'Confirmed', '2026-08-24 08:15:00'),
        ('Antonio Reyes', 'Dr. Edward Hernandez, MD', 'Pulmonology', '2026-08-24', '11:00 AM', 'Diagnostic Review', 'Scheduled', '2026-08-24 08:30:00'),
        ('Elena Ramos', 'Dr. Miguel Garcia, MD', 'General Surgery', '2026-08-24', '01:30 PM', 'Post-Op Suture Removal', 'Scheduled', '2026-08-24 08:45:00')
    """)

    seed_if_empty(cursor, "prescriptions", """INSERT INTO prescriptions (patient_name, doctor_name, medicine_name, dosage, frequency, duration, status, created_at) VALUES 
        ('Juan Dela Cruz', 'Dr. Roberto Tan, MD', 'Amlodipine 10mg Tablets', '1 Tab', 'Once Daily (OD)', '30 Days', 'Dispensed', '2026-08-24 08:00:00'),
        ('Juan Dela Cruz', 'Dr. Roberto Tan, MD', 'Atorvastatin 20mg Tablets', '1 Tab', 'At Bedtime (HS)', '30 Days', 'Dispensed', '2026-08-24 08:00:00'),
        ('Maria Santos', 'Dr. Vincent Lim, MD', 'Metformin 500mg Tablets', '1 Tab', 'Twice Daily (BID)', '30 Days', 'Dispensed', '2026-08-24 08:15:00'),
        ('Carlos Mendoza', 'Dr. Miguel Garcia, MD', 'Celecoxib 200mg Capsules', '1 Cap', 'Once Daily (OD)', '14 Days', 'Pending', '2026-08-24 08:30:00')
    """)

    seed_if_empty(cursor, "billing_invoices", """INSERT INTO billing_invoices (invoice_no, patient_name, item_desc, amount, discount, net_total, payment_status, created_at) VALUES 
        ('INV-2026-0891', 'Juan Dela Cruz', 'OPD Cardiology Consultation & 12-Lead ECG', 2850.00, 0.00, 2850.00, 'Paid', '2026-08-24 09:30:00'),
        ('INV-2026-0892', 'Maria Santos', 'Fast Blood Sugar (FBS) & HbA1c Lab Panel', 1450.00, 290.00, 1160.00, 'Paid', '2026-08-24 09:45:00'),
        ('INV-2026-0893', 'Carlos Mendoza', 'ER Trauma Bay Admission & STAT Cardiac Troponin-I', 8500.00, 0.00, 8500.00, 'Pending PhilHealth', '2026-08-24 10:00:00')
    """)

    seed_if_empty(cursor, "accounting_vouchers", """INSERT INTO accounting_vouchers (voucher_no, narration, debit_acc, credit_acc, amount, status, created_at) VALUES 
        ('JV-2026-041', 'OPD Consultation Fee Receipt (Cash)', '1010 - Cash on Hand', '4010 - OPD Consultation Revenue', 2850.00, 'Posted', '2026-08-24 08:00:00'),
        ('JV-2026-042', 'Pharmacy Drug Sales Daily Batch', '1020 - Cash at Bank', '4020 - Pharmacy Sales Revenue', 18450.00, 'Posted', '2026-08-24 08:30:00'),
        ('JV-2026-043', 'Purchase of Sterile Medical Consumables', '5020 - Medical Supplies Exp', '2010 - Accounts Payable (Metro Pharma)', 85000.00, 'Posted', '2026-08-24 09:00:00')
    """)

    seed_if_empty(cursor, "inventory_items", """INSERT INTO inventory_items (item_code, item_name, category, batch_no, expiry_date, unit_price, stock_qty, reorder_level) VALUES 
        ('MED-001', 'Paracetamol 500mg Tablets', 'Analgesics / Antipyretic', 'BN-88910', '2027-12-31', 4.50, 4850, 500),
        ('MED-002', 'Amoxicillin 500mg Capsules', 'Antibiotics', 'BN-44129', '2027-06-30', 8.75, 2300, 300),
        ('MED-003', 'Amlodipine 10mg Tablets', 'Cardiovascular', 'BN-99201', '2028-03-31', 12.00, 1420, 200),
        ('SUP-101', 'Sterile Surgical Gloves (Size 7.5)', 'Consumables', 'BN-22019', '2029-01-31', 45.00, 890, 150),
        ('SUP-102', 'IV Cannula 20G with Injection Port', 'Consumables', 'BN-33918', '2028-09-30', 65.00, 640, 100)
    """)

    seed_if_empty(cursor, "procurement_po", """INSERT INTO procurement_po (po_no, supplier_name, items_summary, total_amount, order_date, delivery_date, status) VALUES 
        ('PO-2026-001', 'Metro Pharma Distribution Inc.', 'Essential Cardiovascular & Antibiotic Restock', 145000.00, '2026-08-20', '2026-08-25', 'Approved / En Route'),
        ('PO-2026-002', 'MedTech Diagnostics Asia Corp', 'LIS Hematology Reagents & Chemistry Cartridges', 88500.00, '2026-08-22', '2026-08-28', 'Pending Approval'),
        ('PO-2026-003', 'Surgical Solutions Philippines', 'Sterile Drape Packs & Electrosurgical Tips', 62000.00, '2026-08-23', '2026-08-29', 'Draft')
    """)

    seed_if_empty(cursor, "fixed_assets", """INSERT INTO fixed_assets (asset_code, asset_name, department, serial_no, purchase_date, cost, status) VALUES 
        ('AST-BME-001', 'Siemens SOMATOM CT Scanner 64-Slice', 'Radiology', 'SN-SM-99281', '2023-04-15', 18500000.00, 'Operational (Calibrated)'),
        ('AST-BME-002', 'Mindray Resona 7 Ultrasound System', 'Radiology / OB-GYN', 'SN-MR-44102', '2024-01-10', 3200000.00, 'Operational'),
        ('AST-BME-003', 'Zoll R Series Defibrillator / Monitor', 'Emergency (Bay 01)', 'SN-ZL-11094', '2024-06-20', 850000.00, 'Operational (Passed Check)'),
        ('AST-BME-004', 'Maquet Betastar Operating Table', 'Operating Theater 1', 'SN-MQ-55201', '2022-11-30', 2100000.00, 'Operational')
    """)

    seed_if_empty(cursor, "lab_orders", """INSERT INTO lab_orders (order_no, patient_name, test_name, department, sample_status, result_value, reference_range, order_date) VALUES 
        ('LAB-2026-0901', 'Juan Dela Cruz', 'Complete Blood Count (CBC) with Platelets', 'Hematology', 'Collected', 'WBC: 7.2 | Hb: 14.5 | Plt: 250k', 'Normal (4.5-11.0)', '2026-08-24'),
        ('LAB-2026-0902', 'Maria Santos', 'Fasting Blood Sugar (FBS)', 'Clinical Chemistry', 'Completed', '142 mg/dL', 'Normal (< 100 mg/dL)', '2026-08-24'),
        ('LAB-2026-0903', 'Carlos Mendoza', 'High-Sensitivity Troponin-I (STAT)', 'Clinical Chemistry', 'Completed', '0.45 ng/mL (ELEVATED)', '< 0.04 ng/mL', '2026-08-24')
    """)

    seed_if_empty(cursor, "radiology_orders", """INSERT INTO radiology_orders (order_no, patient_name, modality, anatomy, doctor_name, scheduled_date, status) VALUES 
        ('RAD-2026-0401', 'Juan Dela Cruz', 'Digital Chest X-Ray (PA View)', 'Chest & Lungs', 'Dr. Roberto Tan, MD', '2026-08-24 11:00 AM', 'Completed / Verified'),
        ('RAD-2026-0402', 'Elena Ramos', 'Abdominal Pelvic Ultrasound', 'Abdomen', 'Dr. Miguel Garcia, MD', '2026-08-24 02:00 PM', 'Scheduled')
    """)

    seed_if_empty(cursor, "ot_schedules", """INSERT INTO ot_schedules (surgery_no, patient_name, procedure_name, ot_room, surgeon_name, anesthesiologist, schedule_date, status) VALUES 
        ('OT-2026-081', 'Elena Ramos', 'Laparoscopic Cholecystectomy', 'OT Room 1', 'Dr. Miguel Garcia, MD', 'Dr. Edward Hernandez, MD', '2026-08-25 08:30 AM', 'Scheduled'),
        ('OT-2026-082', 'Ramon Gomez', 'Right Forearm Tendon Repair', 'OT Room 2', 'Dr. Miguel Garcia, MD', 'Dr. Edward Hernandez, MD', '2026-08-25 10:30 AM', 'Scheduled')
    """)

    seed_if_empty(cursor, "vaccination_records", """INSERT INTO vaccination_records (record_no, patient_name, vaccine_name, dose_number, batch_no, administered_by, date_given) VALUES 
        ('VAX-2026-0101', 'Leo Bautista (Pediatric)', 'Pentavalent (DTP-HepB-Hib)', 'Dose 1', 'BN-VX-991', 'Nurse Joy Cruz', '2026-08-24'),
        ('VAX-2026-0102', 'Juan Dela Cruz', 'Influenza Quadrivalent Vaccine', 'Annual Booster', 'BN-FL-440', 'Nurse Clara Dizon', '2026-08-24')
    """)

    seed_if_empty(cursor, "queue_tickets", """INSERT INTO queue_tickets (token_no, patient_name, department, counter_no, priority_level, status, issued_at) VALUES 
        ('Q-101', 'Juan Dela Cruz', 'Cardiology Clinic (Room 201)', 'Counter 1', 'Regular', 'Called / Serving', '2026-08-24 09:55:00'),
        ('Q-102', 'Maria Santos', 'Internal Medicine (Room 203)', 'Counter 2', 'Senior Citizen', 'Waiting (Next)', '2026-08-24 10:05:00'),
        ('Q-103', 'Antonio Reyes', 'Pulmonology Clinic (Room 205)', 'Counter 3', 'PWD', 'Waiting', '2026-08-24 10:15:00')
    """)

    seed_if_empty(cursor, "cssd_batches", """INSERT INTO cssd_batches (cycle_no, autoclave_unit, tray_type, sterilization_time, biological_indicator, operator, status) VALUES 
        ('CSSD-CYC-089', 'Steam Autoclave Unit 01 (Getinge)', 'Major Laparotomy Surgical Tray #04', '60 min @ 134°C', 'Passed (Negative Bacillus)', 'Tech Rommel Santos', 'Sterilized & Released'),
        ('CSSD-CYC-090', 'Plasma Sterilizer Unit 02 (Sterrad)', 'Laparoscopic Optics & HD Camera Set', '45 min Low Temp', 'Passed (Biological OK)', 'Tech Rommel Santos', 'Sterilized & Released')
    """)

    seed_if_empty(cursor, "ehs_incidents", """INSERT INTO ehs_incidents (incident_no, incident_date, department, severity, description, reported_by, status) VALUES 
        ('INC-2026-012', '2026-08-24 07:45 AM', 'Central Laboratory', 'Low (Non-Injury)', 'Accidental saline spill on floor; cleaned immediately', 'Tech Joy Cruz', 'Resolved & Logged'),
        ('INC-2026-013', '2026-08-23 04:30 PM', 'Inpatient Ward 3', 'Low (Near Miss)', 'Needle recapping near miss during disposal', 'Nurse Clara Dizon', 'Safety Retraining Completed')
    """)

    seed_if_empty(cursor, "ai_crm_leads", """INSERT INTO ai_crm_leads (lead_no, patient_name, channel, symptoms, predicted_dept, sentiment, status, created_at) VALUES 
        ('CRM-0101', 'Carlos Mendoza', 'WhatsApp', 'Persistent joint pain in knees for 2 weeks', 'Orthopedics', 'Positive (0.82)', 'Booked', '2026-08-24 08:00:00'),
        ('CRM-0102', 'Beatriz Aquino', 'Web Portal', 'Post-discharge question about wound dressing', 'General Surgery (Post-Op)', 'Neutral (0.10)', 'Nurse Contacted', '2026-08-24 08:30:00')
    """)

    seed_if_empty(cursor, "substore_inventory", """INSERT INTO substore_inventory (substore_name, item_name, current_stock, min_threshold, status) VALUES 
        ('ER SubStore (Crash Cart)', 'Epinephrine 1mg/mL Ampules', '12 Ampules', '10 Ampules', 'Optimal Floor Stock'),
        ('ICU SubStore Cabinet', 'Norepinephrine 4mg/4mL Vials', '8 Vials', '6 Vials', 'Optimal Stock'),
        ('Operating Room SubStore', 'Propofol 1% 20mL Emulsion', '15 Vials', '10 Vials', 'Optimal Stock')
    """)

    seed_if_empty(cursor, "doctor_incentives", """INSERT INTO doctor_incentives (doctor_name, department, total_encounters, gross_billing, incentive_rate, net_payable, status) VALUES 
        ('Dr. Roberto Tan, MD', 'Cardiology', 42, 185000.00, '60%', 111000.00, 'Approved for Payroll'),
        ('Dr. Miguel Garcia, MD', 'Orthopedics / Surgery', 35, 240000.00, '65%', 156000.00, 'Approved for Payroll'),
        ('Dr. Vincent Lim, MD', 'Internal Medicine', 29, 115000.00, '60%', 69000.00, 'Pending Review')
    """)

    seed_if_empty(cursor, "telehealth_sessions", """INSERT INTO telehealth_sessions (session_id, patient_name, doctor_name, platform, scheduled_time, connection_status) VALUES 
        ('TH-2026-091', 'Juan Dela Cruz', 'Dr. Roberto Tan, MD', 'WebRTC HD Video Portal', 'Today 04:00 PM', 'Waiting Room Ready'),
        ('TH-2026-092', 'Maria Santos', 'Dr. Vincent Lim, MD', 'WebRTC HD Video Portal', 'Today 04:30 PM', 'Link Dispatched')
    """)

    seed_if_empty(cursor, "mkt_referrals", """INSERT INTO mkt_referrals (ref_id, referrer_name, institution, patient_referred, specialty, referral_fee, status) VALUES 
        ('REF-2026-041', 'Dr. Ferdinand Santos, MD', 'Makati Family Care Clinic', 'Juan Dela Cruz', 'Cardiology Consult', 500.00, 'Credited'),
        ('REF-2026-042', 'Dr. Carmelita Reyes, MD', 'St. Luke Community Polyclinic', 'Elena Ramos', 'General Surgery Workup', 750.00, 'Credited')
    """)

    seed_if_empty(cursor, "insurance_claims", """INSERT INTO insurance_claims (claim_no, patient_name, hmo_provider, icd_code, claim_amount, filing_date, claim_status) VALUES 
        ('CLM-2026-019', 'Juan Dela Cruz', 'PhilHealth', 'I20.9 - Angina Pectoris', 15000.00, '2026-08-22', 'Approved / Reimbursed'),
        ('CLM-2026-020', 'Maria Santos', 'Maxicare Healthcare', 'E11.9 - Type 2 Diabetes', 8500.00, '2026-08-23', 'In Process / Verified'),
        ('CLM-2026-021', 'Carlos Mendoza', 'Intellicare HMO', 'I21.0 - STEMI Acute', 45000.00, '2026-08-24', 'Pre-Authorized')
    """)

    seed_if_empty(cursor, "audit_logs", """INSERT INTO audit_logs (timestamp, user_id, action_name, ip_address, status) VALUES 
        ('2026-08-24 08:00:15', 'admin', 'SYSTEM_LOGIN', '192.168.1.100', 'SUCCESS'),
        ('2026-08-24 08:05:22', 'doctor', 'VIEW_PATIENT_CHART (G1-2026-0090)', '192.168.1.102', 'SUCCESS'),
        ('2026-08-24 08:12:45', 'nurse', 'UPDATE_BED_STATUS (CARD-301 -> OCCUPIED)', '192.168.1.104', 'SUCCESS'),
        ('2026-08-24 08:20:10', 'accountant', 'POST_JOURNAL_VOUCHER (JV-2026-041)', '192.168.1.108', 'SUCCESS')
    """)

    conn.commit()
    conn.close()

def seed_if_empty(cursor, table_name, insert_sql):
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    if cursor.fetchone()[0] == 0:
        cursor.execute(insert_sql)

# Universal Generic CRUD Helpers
def get_all_records(table_name):
    conn = get_db_connection()
    id_col = "id" if table_name != "adt_beds" else "id"
    rows = conn.execute(f"SELECT * FROM {table_name} ORDER BY {id_col} DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def insert_record(table_name, data):
    conn = get_db_connection()
    cursor = conn.cursor()
    columns = [k for k in data.keys() if k != 'id' or table_name == 'adt_beds']
    placeholders = ['?'] * len(columns)
    values = [data[k] for k in columns]
    sql = f"INSERT OR REPLACE INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
    cursor.execute(sql, values)
    conn.commit()
    new_id = cursor.lastrowid or data.get('id')
    conn.close()
    return new_id

def update_record(table_name, record_id, data):
    conn = get_db_connection()
    cursor = conn.cursor()
    columns = [k for k in data.keys() if k != 'id']
    set_clause = ', '.join([f"{k} = ?" for k in columns])
    values = [data[k] for k in columns]
    values.append(record_id)
    id_field = "id"
    sql = f"UPDATE {table_name} SET {set_clause} WHERE {id_field} = ?"
    cursor.execute(sql, values)
    conn.commit()
    conn.close()
    return True

def delete_record(table_name, record_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    id_field = "id"
    sql = f"DELETE FROM {table_name} WHERE {id_field} = ?"
    cursor.execute(sql, (record_id,))
    conn.commit()
    conn.close()
    return True

def get_full_emr_state():
    conn = get_db_connection()
    tables = [
        "patients", "appointments", "adt_beds", "er_cases", "prescriptions",
        "billing_invoices", "lab_orders", "radiology_orders", "accounting_vouchers",
        "inventory_items", "procurement_po", "fixed_assets", "ot_schedules",
        "vaccination_records", "queue_tickets", "cssd_batches", "ehs_incidents",
        "ai_crm_leads", "substore_inventory", "doctor_incentives", "telehealth_sessions",
        "mkt_referrals", "insurance_claims", "audit_logs"
    ]
    state = {}
    for t in tables:
        try:
            id_col = "id" if t != "adt_beds" else "id"
            rows = conn.execute(f"SELECT * FROM {t} ORDER BY {id_col} DESC").fetchall()
            state[t] = [dict(r) for r in rows]
        except Exception:
            state[t] = []
    conn.close()
    return state

def log_audit_event(user_id, action_name, ip_address='127.0.0.1', status='SUCCESS'):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO audit_logs (timestamp, user_id, action_name, ip_address, status)
    VALUES (datetime('now', 'localtime'), ?, ?, ?, ?)
    """, (user_id, action_name, ip_address, status))
    conn.commit()
    conn.close()

# Specific table getters
def get_all_patients(): return get_all_records("patients")
def insert_patient(data): return insert_record("patients", data)
def get_all_appointments(): return get_all_records("appointments")
def insert_appointment(data): return insert_record("appointments", data)
def get_all_beds(): return get_all_records("adt_beds")
def update_bed_record(bed_id, status, patient_name=None, diagnosis=None, doctor=None):
    return update_record("adt_beds", bed_id, {
        "status": status,
        "patient_name": patient_name,
        "diagnosis": diagnosis,
        "attending_doctor": doctor,
        "updated_at": time.strftime("%Y-%m-%d %H:%M:%S")
    })
def get_all_er_cases(): return get_all_records("er_cases")
def insert_er_case(data): return insert_record("er_cases", data)
def get_all_billing_invoices(): return get_all_records("billing_invoices")
def insert_billing_invoice(data): return insert_record("billing_invoices", data)
def get_all_accounting_vouchers(): return get_all_records("accounting_vouchers")
def insert_accounting_voucher(data): return insert_record("accounting_vouchers", data)
def get_all_crm_leads(): return get_all_records("ai_crm_leads")
def insert_crm_lead(data): return insert_record("ai_crm_leads", data)
def get_all_audit_logs(): return get_all_records("audit_logs")

# Initialize database schema and seeds
init_database()
