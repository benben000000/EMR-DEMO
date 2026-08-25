# tests/test_service_layer.py
import sys
import os
import sqlite3
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.services import ServiceContainer

def test_sqlite_container_integration():
    test_db = "/tmp/test_hospital_emr.db"
    if os.path.exists(test_db):
        os.remove(test_db)
        
    conn = sqlite3.connect(test_db)
    conn.execute("""
    CREATE TABLE patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_no TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        age INTEGER,
        gender TEXT,
        phone TEXT,
        address TEXT,
        blood_group TEXT,
        insurance_no TEXT
    )
    """)
    conn.execute("""
    CREATE TABLE audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        user_id TEXT,
        action_name TEXT,
        ip_address TEXT,
        status TEXT
    )
    """)
    conn.commit()
    conn.close()

    # Instantiate DI container targeting the test database
    container = ServiceContainer(use_in_memory=False, db_path=test_db)
    patient_svc = container.get_service("patient_service")
    
    # Register patient through service layer
    created = patient_svc.register_patient({
        "name": "David Tennant",
        "age": 52,
        "gender": "Male",
        "phone": "+63 917 999 8888",
        "insurance_no": "BBC-HMO-10"
    }, operator="sysadmin")

    assert created["id"] == 1
    assert created["name"] == "David Tennant"

    # Query back using repository
    patients = patient_svc.get_all_patients()
    assert len(patients) == 1
    assert patients[0]["name"] == "David Tennant"

    # Clean up
    if os.path.exists(test_db):
        os.remove(test_db)

    print("🎉 SQLite ServiceContainer integration test passed successfully!")

if __name__ == "__main__":
    test_sqlite_container_integration()
