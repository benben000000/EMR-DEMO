# tests/test_dependency_injection_and_repositories.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.repositories import InMemoryRepository, IRepository
from core.services import ServiceContainer, PatientService, BillingService, TriageService

def test_in_memory_repository_crud():
    repo = InMemoryRepository()
    
    # 1. Insert
    item_id = repo.insert({"name": "Paracetamol 500mg", "qty": 100})
    assert item_id == 1
    
    # 2. Get by ID
    item = repo.get_by_id(1)
    assert item["name"] == "Paracetamol 500mg"
    assert item["qty"] == 100
    
    # 3. Update
    repo.update(1, {"qty": 85})
    updated = repo.get_by_id(1)
    assert updated["qty"] == 85
    
    # 4. Get all
    all_items = repo.get_all()
    assert len(all_items) == 1
    
    # 5. Delete
    deleted = repo.delete(1)
    assert deleted is True
    assert repo.get_by_id(1) is None

def test_dependency_injection_container_resolution():
    # Construct DI container configured with in-memory test doubles
    container = ServiceContainer(use_in_memory=True)
    
    patient_svc = container.get_service("patient_service")
    billing_svc = container.get_service("billing_service")
    triage_svc = container.get_service("triage_service")
    
    assert isinstance(patient_svc, PatientService)
    assert isinstance(billing_svc, BillingService)
    assert isinstance(triage_svc, TriageService)
    
    # Verify constructor-injected repositories adhere to IRepository interface
    assert isinstance(patient_svc.patient_repo, IRepository)
    assert isinstance(billing_svc.billing_repo, IRepository)
    assert isinstance(triage_svc.er_repo, IRepository)

def test_patient_service_with_injected_audit():
    patient_repo = InMemoryRepository()
    audit_repo = InMemoryRepository()
    
    # Injected PatientService
    service = PatientService(patient_repo=patient_repo, audit_repo=audit_repo)
    
    patient = service.register_patient({
        "name": "Clara Oswald",
        "age": 28,
        "gender": "Female",
        "phone": "+63 917 111 2222",
        "insurance_no": "HMO-CARE-01"
    }, operator="receptionist_01")
    
    assert patient["id"] == 1
    assert patient["name"] == "Clara Oswald"
    assert patient_repo.get_by_id(1) is not None
    
    # Verify decoupled audit log was recorded
    audit_entries = audit_repo.get_all()
    assert len(audit_entries) == 1
    assert audit_entries[0]["user_id"] == "receptionist_01"
    assert "REGISTER_PATIENT" in audit_entries[0]["action_name"]

def test_billing_service_with_injected_discounts():
    billing_repo = InMemoryRepository()
    audit_repo = InMemoryRepository()
    
    service = BillingService(billing_repo=billing_repo, audit_repo=audit_repo)
    
    # Senior citizen 20% on ₱5,000 Consultation & ECG
    invoice = service.create_invoice(
        patient_name="Lolo Francisco",
        item_desc="Executive Cardiac Consultation",
        gross_amount=5000.00,
        is_senior=True,
        philhealth_rate=1000.00,
        operator="cashier_02"
    )
    
    assert invoice["amount"] == 5000.00
    assert invoice["discount"] == 1000.00  # 20% of 5,000
    assert invoice["net_total"] == 3000.00 # 4,000 - 1,000 PhilHealth
    assert billing_repo.get_by_id(invoice["id"]) is not None

def test_triage_service_emergency_escalation():
    er_repo = InMemoryRepository()
    audit_repo = InMemoryRepository()
    
    service = TriageService(er_repo=er_repo, audit_repo=audit_repo)
    
    er_case = service.triage_patient(
        patient_name="Mateo Silva",
        age_sex="55 / M",
        complaint="Crushing substernal chest pain with diaphoresis",
        hr=128,
        spo2=89,
        sys_bp=185,
        operator="triage_nurse_joy"
    )
    
    assert er_case["triage_level"] == "Level 1"
    assert "Bay 01 (STAT)" in er_case["bay_no"]
    assert "Dr. Roberto Tan, MD" in er_case["doctor_nurse"]
    assert er_repo.get_by_id(er_case["id"]) is not None

if __name__ == "__main__":
    test_in_memory_repository_crud()
    test_dependency_injection_container_resolution()
    test_patient_service_with_injected_audit()
    test_billing_service_with_injected_discounts()
    test_triage_service_emergency_escalation()
    print("🎉 All Dependency Injection & Repository tests passed successfully!")
