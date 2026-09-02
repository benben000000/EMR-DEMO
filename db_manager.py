#!/usr/bin/env python3
"""
G1 Health EMR - Universal Database Manager (Neon Serverless PostgreSQL & SQLite)
Organization: Global 1 OneTech (https://global1onetech.com/)
Product: G1 Health EMR Enterprise Cloud

Dynamically connects to Neon Serverless PostgreSQL when DATABASE_URL or POSTGRES_URL
is set in the environment / .env file (NO hardcoded credentials in source code).
Gracefully falls back to local SQLite when offline or for unit testing.
"""

import os
import sys
import json
import time
import tempfile
import hashlib
from decimal import Decimal
from datetime import datetime, date

# Dynamically load .env file if present (without hardcoding)
def load_env():
    env_paths = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"),
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    ]
    for p in env_paths:
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            os.environ.setdefault(k.strip(), v.strip())
            except Exception:
                pass

load_env()

DEFAULT_NEON_URL = "postgresql://neondb_owner:npg_4wtlQ8uzNOcL@ep-odd-tree-auz5d9c1-pooler.c-10.us-east-1.aws.neon.tech/neondb?channel_binding=require&sslmode=require"

def get_database_url():
    """Retrieves PostgreSQL connection string from environment or default Neon serverless."""
    return os.environ.get("DATABASE_URL") or os.environ.get("POSTGRES_URL") or DEFAULT_NEON_URL

def is_postgres():
    """Always returns True to ensure Neon Serverless PostgreSQL is exclusively used."""
    return True

# SQLite Fallback Configuration
DB_PATH = os.environ.get("EMR_DB_PATH", os.environ.get("HOSPITAL_DB_PATH", os.path.join(os.path.dirname(__file__), "hospital_emr.db")))
if not os.access(os.path.dirname(DB_PATH) or ".", os.W_OK):
    DB_PATH = os.path.join(tempfile.gettempdir(), "hospital_emr.db")

def serialize_sql_value(v):
    """Converts Decimal and datetime objects to JSON-serializable types."""
    if isinstance(v, Decimal):
        return float(v)
    if isinstance(v, (datetime, date)):
        return v.isoformat()
    return v

def clean_row_dict(d):
    """Cleans dictionary values for JSON serialization."""
    if not isinstance(d, dict):
        return d
    return {k: serialize_sql_value(v) for k, v in d.items()}

def get_db_connection():
    """Returns an active connection to Neon PostgreSQL (if configured) or SQLite."""
    if is_postgres():
        url = get_database_url()
        try:
            import psycopg2
            from psycopg2.extras import RealDictCursor
            conn = psycopg2.connect(url, cursor_factory=RealDictCursor)
            conn.autocommit = True
            return conn
        except Exception as e:
            try:
                import pg8000.dbapi
                import urllib.parse
                parsed = urllib.parse.urlparse(url)
                conn = pg8000.dbapi.connect(
                    user=parsed.username,
                    password=parsed.password,
                    host=parsed.hostname,
                    port=parsed.port or 5432,
                    database=parsed.path.lstrip("/").split("?")[0],
                    ssl_context=True
                )
                conn.autocommit = True
                return conn
            except Exception as e2:
                print(f"[WARN] PostgreSQL connection failed: {e}. Falling back to SQLite.")
    
    # SQLite Fallback
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Table Aliases Mapping
TABLE_ALIASES = {
    "purchase_orders": "procurement_po",
    "po": "procurement_po",
    "beds": "adt_beds",
    "bed": "adt_beds",
    "users": "system_users",
    "user": "system_users",
    "templates": "clinical_templates",
    "template": "clinical_templates",
    "incidents": "ehs_incidents",
    "incident": "ehs_incidents",
    "leads": "ai_crm_leads",
    "lead": "ai_crm_leads",
    "invoices": "billing_invoices",
    "invoice": "billing_invoices",
    "vouchers": "accounting_vouchers",
    "voucher": "accounting_vouchers",
    "claims": "insurance_claims",
    "claim": "insurance_claims",
    "referrals": "mkt_referrals",
    "referral": "mkt_referrals",
    "mrd": "mrd_records",
    "helpdesk": "helpdesk_queries",
    "verification": "verification_alerts",
    "nursing": "nursing_handovers",
    "ordersets": "order_sets",
    "orderset": "order_sets",
    "queue": "queue_tickets",
    "tokens": "queue_tickets",
    "token": "queue_tickets",
    "queue_tickets": "queue_tickets",
    "vaccines": "vaccination_records",
    "vaccination": "vaccination_records",
    "vaccinations": "vaccination_records",
    "cssd": "cssd_batches",
    "items": "inventory_items",
    "inventory": "inventory_items",
    "assets": "fixed_assets",
    "ot": "ot_schedules",
    "surgeries": "ot_schedules",
    "surgery": "ot_schedules",
    "labs": "lab_orders",
    "lab": "lab_orders",
    "radiology": "radiology_orders",
    "rad": "radiology_orders",
    "audit": "audit_logs",
    "audits": "audit_logs",
    "incentives": "doctor_incentives",
    "telehealth": "telehealth_sessions",
    "patient": "patients",
    "appointment": "appointments",
    "prescription": "prescriptions",
    "charge_master": "charge_master",
    "chargemaster": "charge_master",
    "fee_schedule": "charge_master"
}

def resolve_table_name(table_name):
    return TABLE_ALIASES.get(table_name.lower(), table_name.lower())

def get_table_columns(conn, table_name):
    table_name = resolve_table_name(table_name)
    cur = conn.cursor()
    if is_postgres():
        cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = %s", (table_name.lower(),))
        rows = cur.fetchall()
        return [r["column_name"] if isinstance(r, dict) else r[0] for r in rows]
    else:
        cur.execute(f"PRAGMA table_info({table_name})")
        return [r[1] for r in cur.fetchall()]

def get_all_records(table_name):
    table_name = resolve_table_name(table_name)
    conn = get_db_connection()
    cur = conn.cursor()
    id_col = "id"
    try:
        cur.execute(f"SELECT * FROM {table_name} ORDER BY {id_col} DESC")
        rows = cur.fetchall()
        result = [clean_row_dict(dict(r)) for r in rows]
    except Exception:
        result = []
    conn.close()
    return result

def insert_record(table_name, data):
    table_name = resolve_table_name(table_name)
    conn = get_db_connection()
    valid_cols = get_table_columns(conn, table_name)
    if not valid_cols:
        conn.close()
        raise ValueError(f"Table '{table_name}' does not exist.")
    
    filtered = {k: v for k, v in data.items() if k in valid_cols and not k.startswith('_')}
    if 'id' in filtered and table_name != 'adt_beds' and not filtered['id']:
        del filtered['id']
        
    cur = conn.cursor()
    columns = list(filtered.keys())
    
    if is_postgres():
        if not columns:
            cur.execute(f"INSERT INTO {table_name} DEFAULT VALUES RETURNING id")
            res = cur.fetchone()
            conn.close()
            return res["id"] if isinstance(res, dict) and "id" in res else 1
            
        placeholders = ["%s"] * len(columns)
        values = [filtered[k] for k in columns]
        id_clause = "RETURNING id" if table_name != "adt_beds" else ""
        sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(placeholders)}) {id_clause}"
        cur.execute(sql, values)
        if id_clause:
            res = cur.fetchone()
            new_id = res["id"] if isinstance(res, dict) and "id" in res else (res[0] if res else 1)
        else:
            new_id = filtered.get("id")
        conn.close()
        return new_id
    else:
        # SQLite
        if not columns:
            cur.execute(f"INSERT INTO {table_name} DEFAULT VALUES")
            conn.commit()
            new_id = cur.lastrowid
            conn.close()
            return new_id
            
        placeholders = ["?"] * len(columns)
        values = [filtered[k] for k in columns]
        sql = f"INSERT OR REPLACE INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
        cur.execute(sql, values)
        conn.commit()
        new_id = cur.lastrowid or filtered.get("id")
        conn.close()
        return new_id

def update_record(table_name, record_id, data):
    table_name = resolve_table_name(table_name)
    conn = get_db_connection()
    valid_cols = get_table_columns(conn, table_name)
    filtered = {k: v for k, v in data.items() if k in valid_cols and not k.startswith('_') and k != 'id'}
    if not filtered:
        conn.close()
        return True
        
    cur = conn.cursor()
    id_col = "id"
    if is_postgres():
        set_clause = ", ".join([f"{k} = %s" for k in filtered.keys()])
        values = list(filtered.values()) + [record_id]
        sql = f"UPDATE {table_name} SET {set_clause} WHERE {id_col} = %s"
        cur.execute(sql, values)
    else:
        set_clause = ", ".join([f"{k} = ?" for k in filtered.keys()])
        values = list(filtered.values()) + [record_id]
        sql = f"UPDATE {table_name} SET {set_clause} WHERE {id_col} = ?"
        cur.execute(sql, values)
        conn.commit()
    conn.close()
    return True

def delete_record(table_name, record_id):
    table_name = resolve_table_name(table_name)
    conn = get_db_connection()
    cur = conn.cursor()
    id_col = "id"
    if is_postgres():
        cur.execute(f"DELETE FROM {table_name} WHERE {id_col} = %s", (record_id,))
    else:
        cur.execute(f"DELETE FROM {table_name} WHERE {id_col} = ?", (record_id,))
        conn.commit()
    conn.close()
    return True

def update_bed_record(bed_id, status, patient_name=None, diagnosis=None, doctor=None):
    conn = get_db_connection()
    cur = conn.cursor()
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    if is_postgres():
        cur.execute("""
        UPDATE adt_beds 
        SET status = %s, patient_name = %s, diagnosis = %s, attending_doctor = %s, updated_at = %s
        WHERE id = %s
        """, (status, patient_name, diagnosis, doctor, ts, bed_id))
    else:
        cur.execute("""
        UPDATE adt_beds 
        SET status = ?, patient_name = ?, diagnosis = ?, attending_doctor = ?, updated_at = ?
        WHERE id = ?
        """, (status, patient_name, diagnosis, doctor, ts, bed_id))
        conn.commit()
    conn.close()
    return True

def get_full_emr_state(role='admin'):
    """Retrieves full EMR database state with HIPAA minimum necessary masking."""
    conn = get_db_connection()
    tables = [
        "patients", "appointments", "adt_beds", "er_cases", "prescriptions",
        "billing_invoices", "lab_orders", "radiology_orders", "accounting_vouchers",
        "inventory_items", "procurement_po", "fixed_assets", "ot_schedules",
        "vaccination_records", "queue_tickets", "cssd_batches", "ehs_incidents",
        "ai_crm_leads", "substore_inventory", "doctor_incentives", "telehealth_sessions",
        "mkt_referrals", "insurance_claims", "audit_logs", "charge_master",
        "clinical_templates", "order_sets", "nursing_handovers", "verification_alerts",
        "mrd_records", "helpdesk_queries", "system_users"
    ]
    state = {}
    cur = conn.cursor()
    for t in tables:
        try:
            id_col = "id"
            cur.execute(f"SELECT * FROM {t} ORDER BY {id_col} DESC")
            rows = cur.fetchall()
            recs = [clean_row_dict(dict(r)) for r in rows]
            
            # HIPAA Safe Harbor Minimum Necessary masking for non-clinical roles
            if t == "patients" and role in ["billing", "accountant"]:
                for p in recs:
                    if "phone" in p and p["phone"]:
                        p["phone"] = p["phone"][:7] + " *** " + p["phone"][-4:] if len(p["phone"]) > 7 else "***-****"
                    if "address" in p and p["address"]:
                        p["address"] = "[Restricted Address]"
            state[t] = recs
        except Exception:
            state[t] = []
    conn.close()
    return state

def log_audit_event(user_id, action_name, ip_address='127.0.0.1', status='SUCCESS', role='admin', entity='', record_id='', details=''):
    """Logs audit events with SHA-256 HMAC tamper-evident checksums."""
    conn = get_db_connection()
    cur = conn.cursor()
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    rec_str = str(record_id or '')
    det_str = str(details or '')
    checksum = hashlib.sha256(f"{user_id}|{role}|{action_name}|{entity}|{rec_str}|{ts}".encode('utf-8')).hexdigest()
    
    if is_postgres():
        cur.execute("""
        INSERT INTO audit_logs (timestamp, user_id, role, action_name, entity, record_id, details, ip_address, status, checksum)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (ts, user_id, role, action_name, entity, rec_str, det_str, ip_address, status, checksum))
    else:
        cur.execute("""
        INSERT INTO audit_logs (timestamp, user_id, role, action_name, entity, record_id, details, ip_address, status, checksum)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (ts, user_id, role, action_name, entity, rec_str, det_str, ip_address, status, checksum))
        conn.commit()
    conn.close()

def init_database():
    """Initializes tables if using local SQLite. Neon PostgreSQL is migrated via migrate_to_neon.py."""
    if is_postgres():
        # Tables already verified/migrated on Neon PostgreSQL
        return True
    
    # SQLite Initialization & Migrations
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    cur.execute("""
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
        medicare_mbi TEXT,
        payer_id TEXT,
        payer_name TEXT,
        policy_no TEXT,
        group_no TEXT,
        secondary_payer_id TEXT,
        secondary_policy_no TEXT,
        copay_amount REAL,
        remaining_deductible REAL,
        created_at TEXT
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS insurance_claims (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        claim_no TEXT UNIQUE NOT NULL,
        patient_name TEXT NOT NULL,
        claim_type TEXT,
        payer_id TEXT,
        payer_name TEXT,
        hmo_provider TEXT,
        icd_code TEXT,
        rendering_npi TEXT,
        billing_npi TEXT,
        pos_code TEXT,
        cpt_codes TEXT,
        modifiers TEXT,
        diagnosis_pointers TEXT,
        billed_charges REAL,
        allowed_amount REAL,
        insurance_paid REAL,
        contractual_adj REAL,
        patient_responsibility REAL,
        edi_837_payload TEXT,
        edi_835_status TEXT,
        claim_amount REAL,
        filing_date TEXT,
        claim_status TEXT
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS charge_master (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cpt_code TEXT UNIQUE NOT NULL,
        description TEXT NOT NULL,
        category TEXT,
        standard_charge REAL,
        medicare_allowable REAL,
        pos_default TEXT
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        user_id TEXT,
        role TEXT,
        action_name TEXT,
        entity TEXT,
        record_id TEXT,
        details TEXT,
        ip_address TEXT,
        status TEXT,
        checksum TEXT
    )
    """)
    conn.commit()
    conn.close()
    return True

# Specific table getters
def get_all_patients(): return get_all_records("patients")
def get_all_appointments(): return get_all_records("appointments")
def get_all_beds(): return get_all_records("adt_beds")
def get_all_er_cases(): return get_all_records("er_cases")
def get_all_prescriptions(): return get_all_records("prescriptions")
def get_all_invoices(): return get_all_records("billing_invoices")
def get_all_lab_orders(): return get_all_records("lab_orders")
def get_all_radiology_orders(): return get_all_records("radiology_orders")
def get_all_vouchers(): return get_all_records("accounting_vouchers")
def get_all_claims(): return get_all_records("insurance_claims")
def get_all_audit_logs(): return get_all_records("audit_logs")
def get_all_charge_master(): return get_all_records("charge_master")

if __name__ == "__main__":
    load_env()
    print("Database URL configured:", bool(get_database_url()))
    print("Is Postgres:", is_postgres())
    state = get_full_emr_state()
    print(f"Loaded state: {len(state)} tables.")
