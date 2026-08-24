import os

# assemble_emr.py
# Modular compiler for G1 Health EMR Complete 33-Module HMIS Suite with RBAC

def compile_emr_suite():
    # 1. Header & Server Code
    py_header = '''#!/usr/bin/env python3
"""
G1 Health EMR - Complete Enterprise HMIS & Role-Based Healthcare Suite
Organization: Global 1 OneTech (https://global1onetech.com/)
Product: G1 Health EMR Enterprise Cloud

Features:
- Complete 33-Module HMIS Architecture
- Departmental Role-Based Access Control (RBAC)
- Real-time Sidebar Search ("Search Menu Items...")
- 1-Click Role Switcher (Doctor, Nurse, Accountant, Billing, Pharmacist, Lab Tech, Receptionist, Admin)
- Inactivity Lock Screen & Anti-bfcache Back-button Guard
- Zero 404 / 405 Serverless Vercel & macOS Edge Compatibility
"""

import http.server
import socketserver
import urllib.parse
import os
import mimetypes
import json
import secrets
import time
import hmac
import hashlib
import base64

PORT = 5000
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

SECRET_KEY = b'global1onetech_g1_health_emr_enterprise_secret_key_2026'
SESSION_EXPIRY_SECONDS = 86400

USERS_DB = {
    'admin': {
        'password': 'pass123',
        'name': 'Administrator',
        'role': 'Super Admin &bull; Full Access',
        'role_key': 'admin',
        'avatar': 'AD',
        'badge': '👑 Super Admin'
    },
    'doctor': {
        'password': 'pass123',
        'name': 'Dr. Roberto Tan, MD',
        'role': 'Attending Cardiologist &bull; Clinical Desk',
        'role_key': 'doctor',
        'avatar': 'RT',
        'badge': '🩺 Doctor (MD)'
    },
    'nurse': {
        'password': 'pass123',
        'name': 'Nurse Clara Dizon',
        'role': 'Charge Nurse &bull; Ward Station',
        'role_key': 'nurse',
        'avatar': 'CD',
        'badge': '💉 Nurse (RN)'
    },
    'accountant': {
        'password': 'pass123',
        'name': 'Elena Villar, CPA',
        'role': 'Chief Accountant &bull; Finance Dept',
        'role_key': 'accountant',
        'avatar': 'EV',
        'badge': '💰 Accountant'
    },
    'billing': {
        'password': 'pass123',
        'name': 'Mark Mendoza',
        'role': 'Billing & Claims Officer &bull; Cashier',
        'role_key': 'billing',
        'avatar': 'MM',
        'badge': '💳 Billing'
    },
    'pharmacy': {
        'password': 'pass123',
        'name': 'Pharm. Leo Santos, RPh',
        'role': 'Chief Pharmacist &bull; Dispensary',
        'role_key': 'pharmacy',
        'avatar': 'LS',
        'badge': '💊 Pharmacist'
    },
    'labtech': {
        'password': 'pass123',
        'name': 'Sarah Cruz, RMT',
        'role': 'Diagnostic & Imaging Technologist',
        'role_key': 'labtech',
        'avatar': 'SC',
        'badge': '🔬 Lab Tech'
    },
    'reception': {
        'password': 'pass123',
        'name': 'Joy Pascual',
        'role': 'Front Desk & Admissions Officer',
        'role_key': 'reception',
        'avatar': 'JP',
        'badge': '📋 Reception'
    }
}

AUDIT_LOGS = [
    {'time': '2026-08-24 10:00:15', 'user': 'admin', 'action': 'System Boot & RBAC Access Matrix Initialized', 'ip': '127.0.0.1', 'status': 'SUCCESS'},
    {'time': '2026-08-24 10:05:22', 'user': 'doctor', 'action': 'Clinical EMR Chart Accessed (Juan Dela Cruz)', 'ip': '127.0.0.1', 'status': 'SUCCESS'},
    {'time': '2026-08-24 11:30:10', 'user': 'accountant', 'action': 'Daybook Journal & Voucher Verified (INV-2026-0412)', 'ip': '127.0.0.1', 'status': 'SUCCESS'}
]

def create_session_token(username, role):
    ts = int(time.time())
    payload = f"{username}|{role}|{ts}"
    sig = hmac.new(SECRET_KEY, payload.encode('utf-8'), hashlib.sha256).hexdigest()
    token = base64.urlsafe_b64encode(f"{payload}|{sig}".encode('utf-8')).decode('utf-8')
    return token

def verify_session_token(token, max_age=SESSION_EXPIRY_SECONDS):
    if not token:
        return None
    try:
        raw = base64.urlsafe_b64decode(token.encode('utf-8')).decode('utf-8')
        parts = raw.split('|')
        if len(parts) != 4:
            return None
        username, role, ts_str, sig = parts
        payload = f"{username}|{role}|{ts_str}"
        expected_sig = hmac.new(SECRET_KEY, payload.encode('utf-8'), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expected_sig):
            return None
        ts = int(ts_str)
        if time.time() - ts > max_age:
            return None
        return {'username': username, 'role': role}
    except Exception:
        return None

def extract_cookies(header_val):
    cookies = {}
    if not header_val:
        return cookies
    for item in header_val.split(';'):
        if '=' in item:
            k, v = item.strip().split('=', 1)
            cookies[k] = v
    return cookies
'''
    print("Header defined.")

compile_emr_suite()
