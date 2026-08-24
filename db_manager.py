import sqlite3
import os
import json
import time

DB_PATH = os.environ.get("DANPHE_DB_PATH", os.path.join(os.path.dirname(__file__), "danphe_emr.db"))

# Handle serverless /tmp writable path for Vercel
if not os.access(os.path.dirname(DB_PATH) or ".", os.W_OK):
    DB_PATH = "/tmp/danphe_emr.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Patients Table
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

    # 2. Appointments Table
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

    # 3. ADT Beds Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS adt_beds (
        id TEXT PRIMARY KEY,
        ward_name TEXT NOT NULL,
        patient_name TEXT,
        diagnosis TEXT,
        attending_doctor TEXT,
        admission_date TEXT,
        status TEXT NOT NULL,
        updated_at TEXT
    )
    """)

    # 4. ER Cases Table
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

    # 5. Prescriptions Table
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

    # 6. Billing Invoices Table
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

    # 7. Lab Orders Table
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

    # 8. Accounting Journal Vouchers Table
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

    # 9. AI CRM Leads Table
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

    # 10. Audit Trail Logs Table
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

    # Seed initial clinical data if empty
    cursor.execute("SELECT COUNT(*) FROM patients")
    if cursor.fetchone()[0] == 0:
        seed_initial_data(cursor)
        conn.commit()

    conn.close()

def seed_initial_data(cursor):
    # Seed Patients
    patients = [
        ('G1-2026-0090', 'Juan Dela Cruz', 45, 'Male', '+63 917 123 4567', 'Quezon City, Metro Manila', 'O+', 'PH-99281-90', '2026-08-24 08:00:00'),
        ('G1-2026-0091', 'Maria Santos', 38, 'Female', '+63 918 234 5678', 'Makati City, Metro Manila', 'A+', 'PH-44812-33', '2026-08-24 08:15:00'),
        ('G1-2026-0092', 'Antonio Reyes', 62, 'Male', '+63 920 345 6789', 'Pasig City, Metro Manila', 'B+', 'PH-11029-44', '2026-08-24 08:30:00'),
        ('G1-2026-0093', 'Elena Ramos', 29, 'Female', '+63 922 456 7890', 'Taguig City, Metro Manila', 'AB+', 'PH-88931-12', '2026-08-24 08:45:00'),
        ('G1-2026-0094', 'Carlos Mendoza', 51, 'Male', '+63 926 567 8901', 'Mandaluyong City, Metro Manila', 'O-', 'PH-77123-55', '2026-08-24 09:00:00')
    ]
    cursor.executemany("INSERT INTO patients (patient_no, name, age, gender, phone, address, blood_group, insurance_no, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", patients)

    # Seed Beds
    beds = [
        ('ICU-101', 'ICU (Critical Care)', 'Antonio Reyes', 'Acute Respiratory Distress Syndrome', 'Dr. Edward Hernandez, MD', '2026-08-23', 'occupied', '2026-08-24 09:00:00'),
        ('ICU-102', 'ICU (Critical Care)', None, None, None, None, 'available', '2026-08-24 09:00:00'),
        ('ICU-103', 'ICU (Critical Care)', None, None, None, None, 'cleaning', '2026-08-24 09:00:00'),
        ('WARD-201', 'General Ward 2nd Flr', 'Maria Santos', 'Type 2 Diabetes with Hyperglycemia', 'Dr. Vincent Lim, MD', '2026-08-22', 'occupied', '2026-08-24 09:00:00'),
        ('WARD-202', 'General Ward 2nd Flr', None, None, None, None, 'available', '2026-08-24 09:00:00'),
        ('WARD-203', 'General Ward 2nd Flr', 'Elena Ramos', 'Post-Op Appendectomy Recovery', 'Dr. Miguel Garcia, MD', '2026-08-23', 'occupied', '2026-08-24 09:00:00'),
        ('CARD-301', 'Cardiology Ward 3rd Flr', 'Juan Dela Cruz', 'Hypertensive Urgency / Angina', 'Dr. Roberto Tan, MD', '2026-08-24', 'occupied', '2026-08-24 09:00:00'),
        ('CARD-302', 'Cardiology Ward 3rd Flr', None, None, None, None, 'available', '2026-08-24 09:00:00'),
        ('PED-401', 'Pediatric Ward 4th Flr', 'Leo Bautista (Pediatric)', 'Acute Bronchiolitis', 'Dr. Patricia Santos, MD', '2026-08-24', 'occupied', '2026-08-24 09:00:00'),
        ('PED-402', 'Pediatric Ward 4th Flr', None, None, None, None, 'available', '2026-08-24 09:00:00')
    ]
    cursor.executemany("INSERT INTO adt_beds (id, ward_name, patient_name, diagnosis, attending_doctor, admission_date, status, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", beds)

    # Seed ER Cases
    er_cases = [
        ('ER-2026-01', 'Level 1', 'Carlos Mendoza', '51 / M', 'Acute Anterior STEMI (Chest Pain radiating to jaw)', 'BP: 165/105 | HR: 112 | SpO2: 91%', 'ER Bay 01 (STAT)', 'Dr. Roberto Tan, MD / Nurse Clara Dizon', 'Admit to Cath Lab / ICU', 'Active', '2026-08-24 08:30:00'),
        ('ER-2026-02', 'Level 2', 'Beatriz Aquino', '34 / F', 'Acute Severe Asthma Exacerbation', 'BP: 130/85 | HR: 98 | SpO2: 92%', 'ER Bay 02', 'Dr. Edward Hernandez, MD / Nurse Clara Dizon', 'Nebulization & Inpatient Observation', 'Active', '2026-08-24 08:45:00'),
        ('ER-2026-03', 'Level 3', 'Ramon Gomez', '27 / M', 'Right Forearm Deep Laceration with Active Bleeding', 'BP: 120/80 | HR: 82 | SpO2: 99%', 'ER Bay 03', 'Dr. Miguel Garcia, MD / Nurse Joy Cruz', 'Surgical Wound Suture & Tetanus Toxoid', 'Active', '2026-08-24 09:10:00'),
        ('ER-2026-04', 'Level 4', 'Liza Del Rosario', '42 / F', 'Acute Gastroenteritis with Moderate Dehydration', 'BP: 110/70 | HR: 88 | SpO2: 98%', 'ER Bay 04', 'Dr. Patricia Santos, MD / Nurse Joy Cruz', 'IV Hydration & Electrolyte Repletion', 'Active', '2026-08-24 09:20:00')
    ]
    cursor.executemany("INSERT INTO er_cases (case_no, triage_level, patient_name, age_sex, chief_complaint, vitals, bay_no, doctor_nurse, disposition, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", er_cases)

    # Seed Appointments
    appointments = [
        ('Juan Dela Cruz', 'Dr. Roberto Tan, MD', 'Cardiology', '2026-08-24', '10:00 AM', 'OPD Follow-up', 'Confirmed', '2026-08-24 08:00:00'),
        ('Maria Santos', 'Dr. Vincent Lim, MD', 'Internal Medicine', '2026-08-24', '10:30 AM', 'New Consultation', 'Confirmed', '2026-08-24 08:15:00'),
        ('Antonio Reyes', 'Dr. Edward Hernandez, MD', 'Pulmonology', '2026-08-24', '11:00 AM', 'Diagnostic Review', 'Scheduled', '2026-08-24 08:30:00'),
        ('Elena Ramos', 'Dr. Miguel Garcia, MD', 'General Surgery', '2026-08-24', '01:30 PM', 'Post-Op Suture Removal', 'Scheduled', '2026-08-24 08:45:00')
    ]
    cursor.executemany("INSERT INTO appointments (patient_name, doctor_name, department, appointment_date, appointment_time, appointment_type, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", appointments)

    # Seed Prescriptions
    prescriptions = [
        ('Juan Dela Cruz', 'Dr. Roberto Tan, MD', 'Amlodipine 10mg Tablets', '1 Tab', 'Once Daily (OD)', '30 Days', 'Dispensed', '2026-08-24 08:00:00'),
        ('Juan Dela Cruz', 'Dr. Roberto Tan, MD', 'Atorvastatin 20mg Tablets', '1 Tab', 'At Bedtime (HS)', '30 Days', 'Dispensed', '2026-08-24 08:00:00'),
        ('Maria Santos', 'Dr. Vincent Lim, MD', 'Metformin 500mg Tablets', '1 Tab', 'Twice Daily (BID)', '30 Days', 'Dispensed', '2026-08-24 08:15:00'),
        ('Carlos Mendoza', 'Dr. Miguel Garcia, MD', 'Celecoxib 200mg Capsules', '1 Cap', 'Once Daily (OD)', '14 Days', 'Pending', '2026-08-24 08:30:00')
    ]
    cursor.executemany("INSERT INTO prescriptions (patient_name, doctor_name, medicine_name, dosage, frequency, duration, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", prescriptions)

    # Seed Billing Invoices
    invoices = [
        ('INV-2026-0891', 'Juan Dela Cruz', 'OPD Cardiology Consultation & 12-Lead ECG', 2850.00, 0.00, 2850.00, 'Paid', '2026-08-24 09:30:00'),
        ('INV-2026-0892', 'Maria Santos', 'Fast Blood Sugar (FBS) & HbA1c Lab Panel', 1450.00, 290.00, 1160.00, 'Paid', '2026-08-24 09:45:00'),
        ('INV-2026-0893', 'Carlos Mendoza', 'ER Trauma Bay Admission & STAT Cardiac Troponin-I', 8500.00, 0.00, 8500.00, 'Pending PhilHealth', '2026-08-24 10:00:00')
    ]
    cursor.executemany("INSERT INTO billing_invoices (invoice_no, patient_name, item_desc, amount, discount, net_total, payment_status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", invoices)

    # Seed Accounting Vouchers
    vouchers = [
        ('JV-2026-041', 'OPD Consultation Fee Receipt (Cash)', '1010 - Cash on Hand', '4010 - OPD Consultation Revenue', 2850.00, 'Posted', '2026-08-24 08:00:00'),
        ('JV-2026-042', 'Pharmacy Drug Sales Daily Batch', '1020 - Cash at Bank', '4020 - Pharmacy Sales Revenue', 18450.00, 'Posted', '2026-08-24 08:30:00'),
        ('JV-2026-043', 'Purchase of Sterile Medical Consumables', '5020 - Medical Supplies Exp', '2010 - Accounts Payable (Metro Pharma)', 85000.00, 'Posted', '2026-08-24 09:00:00')
    ]
    cursor.executemany("INSERT INTO accounting_vouchers (voucher_no, narration, debit_acc, credit_acc, amount, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)", vouchers)

    # Seed AI CRM Leads
    crm_leads = [
        ('CRM-0101', 'Carlos Mendoza', 'WhatsApp', 'Persistent joint pain in knees for 2 weeks', 'Orthopedics', 'Positive (0.82)', 'Booked', '2026-08-24 08:00:00'),
        ('CRM-0102', 'Beatriz Aquino', 'Web Portal', 'Post-discharge question about wound dressing', 'General Surgery (Post-Op)', 'Neutral (0.10)', 'Nurse Contacted', '2026-08-24 08:30:00')
    ]
    cursor.executemany("INSERT INTO ai_crm_leads (lead_no, patient_name, channel, symptoms, predicted_dept, sentiment, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", crm_leads)

    # Seed Audit Logs
    audit_logs = [
        ('2026-08-24 08:00:15', 'admin', 'SYSTEM_LOGIN', '192.168.1.100', 'SUCCESS'),
        ('2026-08-24 08:05:22', 'doctor', 'VIEW_PATIENT_CHART (G1-2026-0090)', '192.168.1.102', 'SUCCESS'),
        ('2026-08-24 08:12:45', 'nurse', 'UPDATE_BED_STATUS (CARD-301 -> OCCUPIED)', '192.168.1.104', 'SUCCESS'),
        ('2026-08-24 08:20:10', 'accountant', 'POST_JOURNAL_VOUCHER (JV-2026-041)', '192.168.1.108', 'SUCCESS')
    ]
    cursor.executemany("INSERT INTO audit_logs (timestamp, user_id, action_name, ip_address, status) VALUES (?, ?, ?, ?, ?)", audit_logs)

# Data Query & Mutation APIs
def get_all_patients():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM patients ORDER BY id DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def insert_patient(data):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO patients (patient_no, name, age, gender, phone, address, blood_group, insurance_no, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
    """, (data.get('patient_no'), data.get('name'), data.get('age'), data.get('gender'), data.get('phone'), data.get('address'), data.get('blood_group'), data.get('insurance_no')))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id

def get_all_appointments():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM appointments ORDER BY id DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def insert_appointment(data):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO appointments (patient_name, doctor_name, department, appointment_date, appointment_time, appointment_type, status, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
    """, (data.get('patient_name'), data.get('doctor_name'), data.get('department'), data.get('appointment_date'), data.get('appointment_time'), data.get('appointment_type', 'Consultation'), data.get('status', 'Confirmed')))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id

def get_all_beds():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM adt_beds ORDER BY id ASC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def update_bed_record(bed_id, status, patient_name=None, diagnosis=None, doctor=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE adt_beds
    SET status = ?, patient_name = ?, diagnosis = ?, attending_doctor = ?, updated_at = datetime('now')
    WHERE id = ?
    """, (status, patient_name, diagnosis, doctor, bed_id))
    conn.commit()
    conn.close()
    return True

def get_all_er_cases():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM er_cases ORDER BY id DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def insert_er_case(data):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO er_cases (case_no, triage_level, patient_name, age_sex, chief_complaint, vitals, bay_no, doctor_nurse, disposition, status, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
    """, (data.get('case_no'), data.get('triage_level'), data.get('patient_name'), data.get('age_sex'), data.get('chief_complaint'), data.get('vitals'), data.get('bay_no'), data.get('doctor_nurse'), data.get('disposition'), data.get('status', 'Active')))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id

def get_all_billing_invoices():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM billing_invoices ORDER BY id DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def insert_billing_invoice(data):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO billing_invoices (invoice_no, patient_name, item_desc, amount, discount, net_total, payment_status, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
    """, (data.get('invoice_no'), data.get('patient_name'), data.get('item_desc'), data.get('amount'), data.get('discount', 0), data.get('net_total'), data.get('payment_status', 'Paid')))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id

def get_all_accounting_vouchers():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM accounting_vouchers ORDER BY id DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def insert_accounting_voucher(data):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO accounting_vouchers (voucher_no, narration, debit_acc, credit_acc, amount, status, created_at)
    VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
    """, (data.get('voucher_no'), data.get('narration'), data.get('debit_acc'), data.get('credit_acc'), data.get('amount'), data.get('status', 'Posted')))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id

def get_all_crm_leads():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM ai_crm_leads ORDER BY id DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def insert_crm_lead(data):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO ai_crm_leads (lead_no, patient_name, channel, symptoms, predicted_dept, sentiment, status, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
    """, (data.get('lead_no'), data.get('patient_name'), data.get('channel', 'WhatsApp'), data.get('symptoms'), data.get('predicted_dept'), data.get('sentiment'), data.get('status', 'Active')))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id

def get_all_audit_logs():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM audit_logs ORDER BY id DESC LIMIT 50").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def log_audit_event(user_id, action_name, ip_address='127.0.0.1', status='SUCCESS'):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO audit_logs (timestamp, user_id, action_name, ip_address, status)
    VALUES (datetime('now', 'localtime'), ?, ?, ?, ?)
    """, (user_id, action_name, ip_address, status))
    conn.commit()
    conn.close()

def get_full_emr_state():
    return {
        "patients": get_all_patients(),
        "appointments": get_all_appointments(),
        "beds": get_all_beds(),
        "er_cases": get_all_er_cases(),
        "billing_invoices": get_all_billing_invoices(),
        "accounting_vouchers": get_all_accounting_vouchers(),
        "crm_leads": get_all_crm_leads(),
        "audit_logs": get_all_audit_logs()
    }

# Initialize on module load
init_database()


def insert_bed(data):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO adt_beds (id, ward_name, patient_name, diagnosis, attending_doctor, admission_date, status, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
    ''', (data.get('id'), data.get('ward_name'), data.get('patient_name'), data.get('diagnosis'), data.get('attending_doctor'), data.get('admission_date'), data.get('status', 'available')))
    conn.commit()
    conn.close()
    return data.get('id')
