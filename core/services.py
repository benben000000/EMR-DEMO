# core/services.py
"""
APPLICATION SERVICE LAYER: Dependency Injection & Orchestration
Implements constructor-injected services adhering to SOLID and Separation of Concerns.
"""

from typing import Dict, Any, List, Optional
from core.repositories import IRepository, InMemoryRepository, SQLiteRepository
from core.domain import calculate_invoice_breakdown, evaluate_triage_acuity, validate_accounting_entry

# 1. PATIENT APPLICATION SERVICE
class PatientService:
    def __init__(self, patient_repo: IRepository, audit_repo: Optional[IRepository] = None):
        self.patient_repo = patient_repo
        self.audit_repo = audit_repo

    def register_patient(self, data: Dict[str, Any], operator: str = "reception") -> Dict[str, Any]:
        if not data.get("name"):
            raise ValueError("Patient name is required.")
            
        pat_no = data.get("patient_no") or f"G1-2026-{abs(hash(data['name'])) % 9000 + 1000}"
        payload = {
            "patient_no": pat_no,
            "name": data["name"],
            "age": int(data.get("age", 30)),
            "gender": data.get("gender", "Male"),
            "phone": data.get("phone", ""),
            "address": data.get("address", ""),
            "blood_group": data.get("blood_group", "O+"),
            "insurance_no": data.get("insurance_no", "PhilHealth")
        }
        
        new_id = self.patient_repo.insert(payload)
        payload["id"] = new_id

        if self.audit_repo:
            self.audit_repo.insert({
                "timestamp": "2026-08-24 09:00:00",
                "user_id": operator,
                "action_name": f"REGISTER_PATIENT ({pat_no})",
                "ip_address": "127.0.0.1",
                "status": "SUCCESS"
            })

        return payload

    def get_all_patients(self) -> List[Dict[str, Any]]:
        return self.patient_repo.get_all()


# 2. BILLING APPLICATION SERVICE
class BillingService:
    def __init__(self, billing_repo: IRepository, audit_repo: Optional[IRepository] = None):
        self.billing_repo = billing_repo
        self.audit_repo = audit_repo

    def create_invoice(self, patient_name: str, item_desc: str, gross_amount: float, discount_pct: float = 0.0, is_senior: bool = False, philhealth_rate: float = 0.0, operator: str = "billing") -> Dict[str, Any]:
        breakdown = calculate_invoice_breakdown(gross_amount, discount_pct, is_senior, philhealth_rate)
        inv_no = f"INV-2026-{abs(hash(patient_name + item_desc)) % 9000 + 1000}"
        
        invoice_record = {
            "invoice_no": inv_no,
            "patient_name": patient_name,
            "item_desc": item_desc,
            "amount": breakdown["gross_amount"],
            "discount": breakdown["discount_amount"],
            "net_total": breakdown["net_patient_payable"],
            "payment_status": "Paid"
        }
        
        new_id = self.billing_repo.insert(invoice_record)
        invoice_record["id"] = new_id

        if self.audit_repo:
            self.audit_repo.insert({
                "timestamp": "2026-08-24 09:00:00",
                "user_id": operator,
                "action_name": f"CREATE_INVOICE ({inv_no})",
                "ip_address": "127.0.0.1",
                "status": "SUCCESS"
            })

        return invoice_record


# 3. ER TRIAGE APPLICATION SERVICE
class TriageService:
    def __init__(self, er_repo: IRepository, audit_repo: Optional[IRepository] = None):
        self.er_repo = er_repo
        self.audit_repo = audit_repo

    def triage_patient(self, patient_name: str, age_sex: str, complaint: str, hr: int = 75, spo2: int = 99, sys_bp: int = 120, operator: str = "triage_nurse") -> Dict[str, Any]:
        acuity = evaluate_triage_acuity(complaint, hr, spo2, sys_bp)
        case_no = f"ER-2026-{abs(hash(patient_name + complaint)) % 9000 + 1000}"
        
        bay = "ER Bay 01 (STAT)" if acuity["urgent"] else "ER Bay 03"
        doctor = "Dr. Roberto Tan, MD" if acuity["urgent"] else "Dr. Miguel Garcia, MD"
        
        er_record = {
            "case_no": case_no,
            "triage_level": acuity["level"],
            "patient_name": patient_name,
            "age_sex": age_sex,
            "chief_complaint": complaint,
            "vitals": f"BP: {sys_bp}/80 | HR: {hr} | SpO2: {spo2}%",
            "bay_no": bay,
            "doctor_nurse": f"{doctor} / Nurse Clara Dizon",
            "disposition": "Admit to ICU/Cath Lab" if acuity["urgent"] else "Observation & Workup",
            "status": "Active"
        }
        
        new_id = self.er_repo.insert(er_record)
        er_record["id"] = new_id

        if self.audit_repo:
            self.audit_repo.insert({
                "timestamp": "2026-08-24 09:00:00",
                "user_id": operator,
                "action_name": f"TRIAGE_ER_CASE ({case_no} - {acuity['level']})",
                "ip_address": "127.0.0.1",
                "status": "SUCCESS"
            })

        return er_record


# 4. DEPENDENCY INJECTION (DI) CONTAINER
class ServiceContainer:
    def __init__(self, use_in_memory: bool = False, db_path: str = "danphe_emr.db"):
        self.use_in_memory = use_in_memory
        self.db_path = db_path
        self._repositories: Dict[str, IRepository] = {}
        self._services: Dict[str, Any] = {}
        self._build_container()

    def _get_or_create_repo(self, table_name: str) -> IRepository:
        if table_name not in self._repositories:
            if self.use_in_memory:
                self._repositories[table_name] = InMemoryRepository()
            else:
                self._repositories[table_name] = SQLiteRepository(table_name, self.db_path)
        return self._repositories[table_name]

    def _build_container(self):
        # Repositories
        patient_repo = self._get_or_create_repo("patients")
        billing_repo = self._get_or_create_repo("billing_invoices")
        er_repo = self._get_or_create_repo("er_cases")
        audit_repo = self._get_or_create_repo("audit_logs")

        # Services with Constructor Dependency Injection
        self._services["patient_service"] = PatientService(patient_repo, audit_repo)
        self._services["billing_service"] = BillingService(billing_repo, audit_repo)
        self._services["triage_service"] = TriageService(er_repo, audit_repo)

    def get_service(self, service_name: str) -> Any:
        return self._services.get(service_name)

    def get_repository(self, table_name: str) -> IRepository:
        return self._get_or_create_repo(table_name)
