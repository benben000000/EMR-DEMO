# G1 Health EMR

> **Smart Healthcare Management Solution**  
> Powered by [Global 1 OneTech](https://global1onetech.com/)

---

## Access & Demo Credentials

Once the system is launched, access the portal in your browser:

- **Local URL**: `http://localhost:5000`
- **Username**: `admin`
- **Password**: `pass123`

---

## How to Deploy to Vercel (1-Click Setup)

This repository is pre-configured with `vercel.json` and serverless Python / static edge routing.

### Option A: Via Vercel Web Dashboard (Easiest)
1. Go to [https://vercel.com/new](https://vercel.com/new) and log in with your GitHub account.
2. Select and import the repository: **`benben000000/EMR-DEMO`**.
3. Leave all default build settings as configured (Vercel automatically detects `vercel.json` and `api/index.py`).
4. Click **Deploy**.
5. Your live G1 Health EMR site will be accessible immediately at `https://emr-demo.vercel.app` (or your assigned Vercel URL)!

### Option B: Via Vercel CLI
```bash
npm i -g vercel
vercel login
vercel --prod
```

---

## How to Run Locally

### macOS / Linux / Windows (Instant Runner)
```bash
python3 serve_demo.py
```
Open **`http://localhost:5000`** in your browser.

---

## Interactive Departments Included
- **Executive Dashboard** (`/dashboard`)
- **Patient Registration & Master Index**
- **Doctor Appointments & OPD Queue**
- **Inpatient ADT & Editable Ward Bed Matrix** (1-Click Vacate/Admit/Cleaning toggles)
- **Emergency Department (ER & Trauma Triage)** (Level 1 to 5 Acuities, Bay tracking, STAT clinical orders)
- **Clinical Doctor Consultation Desk** (Vitals, ICD-10, Dynamic Prescription Builder)
- **Nursing Station & Inpatient Care** (e-MAR)
- **Operation Theater (OT) Surgical Scheduling**
- **Laboratory Information System (LIS)**
- **Radiology & PACS DICOM Viewer**
- **Pharmacy & Inventory Supply Chain**
- **AI CRM & Intelligent Lead Triage**
- **Patient 360 Information System (PIS)**
- **Employee Health & Safety (EHS Occupational Health)**
- **Telehealth & Virtual Consultations**
- **Billing & Invoicing with Branded Printable Receipts**
- **White-Label & Personalization Settings**
