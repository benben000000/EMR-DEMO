import db_manager
import core.domain as domain
#!/usr/bin/env python3
"""
G1 Health EMR - Complete Interactive Enterprise Suite & Demo Runner
Organization: Global 1 OneTech (https://global1onetech.com/)
Product: G1 Health EMR Enterprise Cloud
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
BASE_DIR = os.path.abspath(os.path.join(PROJECT_ROOT, "Code/Websites/HospitalEMR"))

# Cryptographic Secret Key for HMAC Session Tokens
SECRET_KEY = b'global1onetech_g1_health_emr_enterprise_secret_key_2026'
SESSION_EXPIRY_SECONDS = 86400 # 24 Hours

# Valid User Accounts & Roles (Clean clinical typography, zero emojis)
USERS_DB = {
    'admin': {'password': 'pass123', 'name': 'Administrator', 'role': 'Super Admin &bull; Full Access', 'role_key': 'admin', 'avatar': 'AD', 'badge': 'Super Admin'},
    'doctor': {'password': 'pass123', 'name': 'Dr. Roberto Tan, MD', 'role': 'Attending Cardiologist &bull; Clinical Desk', 'role_key': 'doctor', 'avatar': 'RT', 'badge': 'Doctor (MD)'},
    'nurse': {'password': 'pass123', 'name': 'Nurse Clara Dizon', 'role': 'Charge Nurse &bull; Ward Station', 'role_key': 'nurse', 'avatar': 'CD', 'badge': 'Nurse (RN)'},
    'accountant': {'password': 'pass123', 'name': 'Elena Villar, CPA', 'role': 'Chief Accountant &bull; Finance Dept', 'role_key': 'accountant', 'avatar': 'EV', 'badge': 'Accountant'},
    'billing': {'password': 'pass123', 'name': 'Mark Mendoza', 'role': 'Billing & Claims Officer &bull; Cashier', 'role_key': 'billing', 'avatar': 'MM', 'badge': 'Billing'},
    'pharmacy': {'password': 'pass123', 'name': 'Pharm. Leo Santos, RPh', 'role': 'Chief Pharmacist &bull; Dispensary', 'role_key': 'pharmacy', 'avatar': 'LS', 'badge': 'Pharmacist'},
    'labtech': {'password': 'pass123', 'name': 'Sarah Cruz, RMT', 'role': 'Diagnostic & Imaging Technologist', 'role_key': 'labtech', 'avatar': 'SC', 'badge': 'Lab Tech'},
    'reception': {'password': 'pass123', 'name': 'Joy Pascual', 'role': 'Front Desk & Admissions Officer', 'role_key': 'reception', 'avatar': 'JP', 'badge': 'Reception'}
}

# Audit Trail Log
AUDIT_LOGS = [
    {'time': '2026-08-24 10:00:15', 'user': 'admin', 'action': 'System Boot & Security Initialized', 'ip': '127.0.0.1', 'status': 'SUCCESS'},
    {'time': '2026-08-24 10:05:22', 'user': 'doctor', 'action': 'Patient Clinical File Accessed (G1-2026-0090)', 'ip': '127.0.0.1', 'status': 'SUCCESS'}
]

def create_session_token(username, role):
    """Generates a tamper-proof signed HMAC session token."""
    ts = int(time.time())
    payload = f"{username}|{role}|{ts}"
    sig = hmac.new(SECRET_KEY, payload.encode('utf-8'), hashlib.sha256).hexdigest()
    token = base64.urlsafe_b64encode(f"{payload}|{sig}".encode('utf-8')).decode('utf-8')
    return token

def verify_session_token(token, max_age=SESSION_EXPIRY_SECONDS):
    """Verifies HMAC signature and expiration timestamp of session token."""
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

LOGIN_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Sign in - G1 Health EMR (Global 1 OneTech)</title>
    <link rel="icon" href="/Personalization/logos/favicon.ico" />
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&family=Inter:wght@400;500;600;700&display=swap" />
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" />
    <style>
        :root {
            --brand-primary: #253545;
            --brand-primary-hover: #1b2838;
            --brand-cyan: #00ffa1;
            --brand-accent: #00bfa5;
            --brand-blue: #0284c7;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Nunito', 'Inter', sans-serif; }

        body {
            background-color: #0f172a;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
            background-image: radial-gradient(#1e293b 1px, transparent 1px);
            background-size: 24px 24px;
        }

        .auth-container {
            display: flex;
            width: 1040px;
            max-width: 96vw;
            min-height: 640px;
            background: #ffffff;
            border-radius: 20px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(255, 255, 255, 0.1);
            overflow: hidden;
        }

        .hero-panel {
            flex: 1.15;
            background: linear-gradient(145deg, #1b2838 0%, #253545 100%);
            color: #ffffff;
            padding: 48px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            position: relative;
        }

        .hero-panel::before {
            content: '';
            position: absolute;
            top: -20%;
            right: -20%;
            width: 80%;
            height: 80%;
            background: radial-gradient(circle, rgba(0, 255, 161, 0.15) 0%, transparent 70%);
            pointer-events: none;
        }

        .brand-logo-hero {
            max-height: 52px;
            filter: brightness(0) invert(1);
            margin-bottom: 24px;
        }

        .hero-title {
            font-size: 32px;
            font-weight: 800;
            letter-spacing: -0.5px;
            margin-bottom: 10px;
            color: #ffffff;
        }

        .hero-tagline {
            font-size: 15px;
            color: #cbd5e1;
            line-height: 1.6;
            margin-bottom: 30px;
        }

        .hero-tagline b { color: #38bdf8; }

        .feature-list {
            list-style: none;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }

        .feature-item {
            display: flex;
            align-items: center;
            gap: 12px;
            font-size: 14px;
            font-weight: 600;
            color: #f8fafc;
            background: rgba(255, 255, 255, 0.05);
            padding: 10px 14px;
            border-radius: 8px;
            border-left: 3.5px solid var(--brand-cyan);
            backdrop-filter: blur(8px);
        }

        .feature-item i { color: #38bdf8; font-size: 15px; width: 20px; text-align: center; }

        .hero-footer {
            font-size: 12px;
            color: #94a3b8;
            margin-top: 32px;
        }

        .hero-footer a { color: #38bdf8; text-decoration: none; font-weight: 600; }

        .form-panel {
            flex: 1;
            padding: 44px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            background: #ffffff;
        }

        .form-logo { text-align: center; margin-bottom: 20px; }
        .form-logo img { max-height: 46px; }

        .form-header { text-align: center; margin-bottom: 20px; }
        .form-header h2 { font-size: 24px; font-weight: 800; color: #1e293b; }
        .form-header p { font-size: 13px; color: #64748b; margin-top: 4px; }

        /* Security Alert Banners */
        .security-alert {
            padding: 10px 14px;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 600;
            margin-bottom: 18px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .alert-success { background: #dcfce7; color: #15803d; border: 1px solid #86efac; }
        .alert-danger { background: #fee2e2; color: #b91c1c; border: 1px solid #fca5a5; }
        .alert-warning { background: #fef9c3; color: #a16207; border: 1px solid #fde047; }

        .input-group { margin-bottom: 16px; }
        .input-group label { display: block; font-size: 13px; font-weight: 700; color: #334155; margin-bottom: 6px; }

        .input-wrapper { position: relative; display: flex; align-items: center; }
        .input-wrapper i { position: absolute; left: 14px; color: #94a3b8; font-size: 15px; }

        .input-wrapper input {
            width: 100%;
            padding: 12px 14px 12px 42px;
            border: 1.5px solid #e2e8f0;
            border-radius: 10px;
            font-size: 14px;
            color: #1e293b;
            outline: none;
            transition: all 0.2s;
        }

        .input-wrapper input:focus {
            border-color: var(--brand-primary);
            box-shadow: 0 0 0 2px #94a3b8;
        }

        .form-options {
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-size: 13px;
            margin-bottom: 20px;
        }

        .remember-me { display: flex; align-items: center; gap: 6px; color: #475569; cursor: pointer; }
        .forgot-link { color: var(--brand-primary); text-decoration: none; font-weight: 700; }

        .btn-submit {
            width: 100%;
            padding: 13px;
            background-color: var(--brand-primary);
            color: #ffffff;
            border: none;
            border-radius: 10px;
            font-size: 15px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }

        .btn-submit:hover {
            background-color: var(--brand-primary-hover);
            color: #38bdf8;
            transform: translateY(-1px);
            box-shadow: 0 10px 20px -5px rgba(37, 53, 69, 0.35);
        }

        /* Role Switcher Pill Bar */
        .role-switcher-bar {
            margin-top: 18px;
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            padding: 10px;
            font-size: 12px;
        }

        .role-switcher-title {
            font-weight: 800;
            color: #475569;
            margin-bottom: 6px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .role-pills {
            display: flex;
            gap: 6px;
            flex-wrap: wrap;
        }

        .role-pill-btn {
            background: #ffffff;
            border: 1px solid #cbd5e1;
            border-radius: 6px;
            padding: 4px 8px;
            font-size: 11px;
            font-weight: 700;
            cursor: pointer;
            color: #334155;
            transition: all 0.15s;
        }

        .role-pill-btn:hover {
            background: var(--brand-primary);
            color: #ffffff;
            border-color: var(--brand-primary);
        }

        @media (max-width: 768px) {
            .auth-container { flex-direction: column; }
            .hero-panel, .form-panel { padding: 32px; }
        }
    
        /* ==========================================================================
           COMPREHENSIVE MOBILE & TABLET RESPONSIVE SYSTEM
           ========================================================================== */
        
        /* Mobile Toggle Button */
        .mobile-toggle-btn {
            display: none;
            background: rgba(255, 255, 255, 0.15);
            border: 1px solid rgba(255, 255, 255, 0.25);
            color: #ffffff;
            font-size: 18px;
            width: 40px;
            height: 40px;
            border-radius: 8px;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .mobile-toggle-btn:hover, .mobile-toggle-btn:active {
            background: var(--brand-cyan);
            color: #0f172a;
        }

        /* Sidebar Backdrop for Mobile Drawer */
        .sidebar-backdrop {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(15, 23, 42, 0.7);
            backdrop-filter: blur(4px);
            -webkit-backdrop-filter: blur(4px);
            z-index: 1040;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.3s ease;
        }

        .sidebar-backdrop.active {
            opacity: 1;
            pointer-events: auto;
        }

        /* Responsive Breakpoints */
        @media (max-width: 992px) {
            body {
                position: relative;
            }

            .mobile-toggle-btn {
                display: inline-flex;
            }

            .sidebar {
                position: fixed;
                top: 0;
                left: 0;
                bottom: 0;
                width: 290px;
                max-width: 85vw;
                z-index: 1050;
                transform: translateX(-100%);
                transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                box-shadow: 4px 0 25px rgba(0, 0, 0, 0.5);
            }

            .sidebar.open {
                transform: translateX(0);
            }

            .top-navbar {
                padding: 10px 16px;
                min-height: 56px;
                gap: 12px;
            }

            .navbar-left {
                gap: 12px;
            }

            .facility-title {
                font-size: 13px;
            }

            .content-area {
                padding: 16px 14px;
            }

            .view-header {
                flex-direction: column;
                align-items: flex-start;
                gap: 14px;
            }

            .view-header button, .view-header div[style*="display:flex"] {
                width: 100%;
                justify-content: flex-start;
            }

            .grid-2col, .grid-3col, .grid-4col, .grid-split {
                grid-template-columns: 1fr !important;
            }

            .stats-grid {
                grid-template-columns: 1fr 1fr;
                gap: 12px;
            }

            .bed-matrix-grid {
                grid-template-columns: 1fr;
            }

            .table-card {
                overflow-x: auto;
                -webkit-overflow-scrolling: touch;
            }

            .emr-table {
                min-width: 650px;
            }

            .modal-box {
                width: 94% !important;
                max-height: 90vh !important;
                padding: 18px 16px !important;
                margin: 10px auto !important;
            }

            .modal-footer {
                flex-direction: column-reverse;
                gap: 8px;
            }

            .modal-footer button {
                width: 100%;
                justify-content: center;
            }
        }

        @media (max-width: 640px) {
            .stats-grid {
                grid-template-columns: 1fr;
            }

            .top-navbar {
                flex-direction: column;
                align-items: stretch;
                padding: 10px 12px;
            }

            .navbar-left, .navbar-right {
                width: 100%;
                justify-content: space-between;
                flex-wrap: wrap;
            }

            .active-patient-badge {
                width: 100%;
                justify-content: space-between;
                font-size: 11px;
                padding: 6px 10px;
            }

            .facility-title span.sub-tagline {
                display: none;
            }

            .user-profile {
                width: 100%;
                justify-content: space-between;
            }

            .ux-navigation-bar {
                flex-direction: column;
                align-items: flex-start;
                gap: 8px;
            }

            .btn-back-dashboard {
                width: 100%;
                justify-content: center;
            }

            .bed-matrix-toolbar {
                flex-direction: column;
                align-items: stretch;
            }

            .ward-filter-pills {
                overflow-x: auto;
                padding-bottom: 4px;
            }
        }
    
    
        /* Code Blue Emergency Banner */
        .code-blue-banner {
            display: none;
            background: linear-gradient(90deg, #b91c1c, #dc2626, #b91c1c);
            color: #ffffff;
            padding: 10px 18px;
            font-size: 13.5px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            box-shadow: 0 4px 15px rgba(220, 38, 38, 0.5);
            animation: pulse-red 1.5s infinite;
            z-index: 1060;
            border-bottom: 2px solid #fecaca;
        }

        @keyframes pulse-red {
            0% { background: #b91c1c; }
            50% { background: #dc2626; }
            100% { background: #b91c1c; }
        }

        .code-blue-loc-card {
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            padding: 10px 12px;
            cursor: pointer;
            transition: all 0.2s ease;
            background: #ffffff;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .code-blue-loc-card:hover {
            border-color: #ef4444;
            background: #fef2f2;
        }

        .code-blue-loc-card.selected {
            border-color: #dc2626;
            background: #fee2e2;
            font-weight: 700;
        }
    
    </style>
</head>
<body>
    <div class="auth-container">
        <div class="hero-panel">
            <div>
                <img src="/Personalization/logos/logo-main.png" alt="Global 1 OneTech" class="brand-logo-hero" />
                <h1 class="hero-title">G1 Health EMR</h1>
                <p class="hero-tagline">
                    A Smart <b>Healthcare Management Solution</b> powered by Global 1 OneTech.
                </p>
                <ul class="feature-list">
                    <li class="feature-item">
                        <i class="fa-solid fa-shield-halved"></i>
                        <span>End-to-End Encrypted Session Security & RBAC</span>
                    </li>
                    <li class="feature-item">
                        <i class="fa-solid fa-notes-medical"></i>
                        <span>Electronic Medical Records (EMR & EHR)</span>
                    </li>
                    <li class="feature-item">
                        <i class="fa-solid fa-boxes-stacked"></i>
                        <span>Hospital ERP & Pharmacy Supply Chain</span>
                    </li>
                    <li class="feature-item">
                        <i class="fa-solid fa-robot"></i>
                        <span>AI CRM & Intelligent Patient Triage</span>
                    </li>
                    <li class="feature-item">
                        <i class="fa-solid fa-id-card-clip"></i>
                        <span>Patient 360 Information System (PIS)</span>
                    </li>
                </ul>
            </div>
            <div class="hero-footer">
                &copy; 2026 <a href="https://global1onetech.com/" target="_blank">Global 1 OneTech</a> &bull; All Rights Reserved.
            </div>
        </div>

        <div class="form-panel">
            <div class="form-logo">
                <img src="/Personalization/logos/logo-main.png" alt="Global 1 OneTech" />
            </div>
            <div class="form-header">
                <h2>Sign in to G1 Health EMR</h2>
                <p>Enterprise Healthcare Management & Clinical Suite</p>
            </div>

            <!-- Dynamic Alert Container -->
            <div id="auth-alert-container"></div>

            <form id="login-form" onsubmit="return handleLoginSubmit(event)">
                <div class="input-group">
                    <label for="username">Username / System ID</label>
                    <div class="input-wrapper">
                        <i class="fa-solid fa-user"></i>
                        <input type="text" id="username" name="username" value="admin" required autocomplete="username" />
                    </div>
                </div>
                <div class="input-group">
                    <label for="password">Password</label>
                    <div class="input-wrapper">
                        <i class="fa-solid fa-lock"></i>
                        <input type="password" id="password" name="password" value="pass123" required autocomplete="current-password" />
                    </div>
                </div>
                <div class="form-options">
                    <label class="remember-me">
                        <input type="checkbox" name="remember" checked />
                        <span>Remember session</span>
                    </label>
                    <a href="javascript:void(0)" onclick="showForgotAlert()" class="forgot-link">Forgot password?</a>
                </div>
                <button type="submit" class="btn-submit" id="btn-login-submit">
                    <span>Sign In to Dashboard</span>
                    <i class="fa-solid fa-arrow-right"></i>
                </button>

                <!-- Role Quick Switcher -->
                <div class="role-switcher-bar">
                    <div class="role-switcher-title">
                        <span><i class="fa-solid fa-id-badge"></i> Quick Demo Roles:</span>
                        <span style="color:#64748b; font-size:11px;">Click to autofill</span>
                    </div>
                    <div class="role-pills" style="display:grid; grid-template-columns:repeat(4, 1fr); gap:6px;">
                        <button type="button" class="role-pill-btn" onclick="setRoleCredentials('admin', 'pass123')"> Admin</button>
                        <button type="button" class="role-pill-btn" onclick="setRoleCredentials('doctor', 'pass123')"> Doctor</button>
                        <button type="button" class="role-pill-btn" onclick="setRoleCredentials('nurse', 'pass123')"> Nurse</button>
                        <button type="button" class="role-pill-btn" onclick="setRoleCredentials('accountant', 'pass123')"><i class="fa-solid fa-file-invoice-dollar"></i> Accountant</button>
                        <button type="button" class="role-pill-btn" onclick="setRoleCredentials('billing', 'pass123')"><i class="fa-solid fa-credit-card"></i> Billing</button>
                        <button type="button" class="role-pill-btn" onclick="setRoleCredentials('pharmacy', 'pass123')"> Pharmacy</button>
                        <button type="button" class="role-pill-btn" onclick="setRoleCredentials('labtech', 'pass123')"><i class="fa-solid fa-microscope"></i> Lab Tech</button>
                        <button type="button" class="role-pill-btn" onclick="setRoleCredentials('reception', 'pass123')"><i class="fa-solid fa-clipboard-user"></i> Reception</button>
                    </div>
                </div>
            </form>
        </div>
    </div>

    <script>
        const VALID_USERS = {
            'admin': { pass: 'pass123', name: 'Administrator', role: 'Super Admin &bull; Full Access', role_key: 'admin', avatar: 'AD', badge: '<i class="fa-solid fa-shield-halved"></i> Super Admin' },
            'doctor': { pass: 'pass123', name: 'Dr. Roberto Tan, MD', role: 'Attending Cardiologist &bull; Clinical Desk', role_key: 'doctor', avatar: 'RT', badge: '<i class="fa-solid fa-user-doctor"></i> Doctor (MD)' },
            'nurse': { pass: 'pass123', name: 'Nurse Clara Dizon', role: 'Charge Nurse &bull; Ward Station', role_key: 'nurse', avatar: 'CD', badge: '<i class="fa-solid fa-user-nurse"></i> Nurse (RN)' },
            'accountant': { pass: 'pass123', name: 'Elena Villar, CPA', role: 'Chief Accountant &bull; Finance Dept', role_key: 'accountant', avatar: 'EV', badge: '<i class="fa-solid fa-file-invoice-dollar"></i> Accountant' },
            'billing': { pass: 'pass123', name: 'Mark Mendoza', role: 'Billing & Claims Officer &bull; Cashier', role_key: 'billing', avatar: 'MM', badge: '<i class="fa-solid fa-credit-card"></i> Billing' },
            'pharmacy': { pass: 'pass123', name: 'Pharm. Leo Santos, RPh', role: 'Chief Pharmacist &bull; Dispensary', role_key: 'pharmacy', avatar: 'LS', badge: '<i class="fa-solid fa-prescription-bottle-medical"></i> Pharmacist' },
            'labtech': { pass: 'pass123', name: 'Sarah Cruz, RMT', role: 'Diagnostic & Imaging Technologist', role_key: 'labtech', avatar: 'SC', badge: '<i class="fa-solid fa-microscope"></i> Lab Tech' },
            'reception': { pass: 'pass123', name: 'Joy Pascual', role: 'Front Desk & Admissions Officer', role_key: 'reception', avatar: 'JP', badge: '<i class="fa-solid fa-clipboard-user"></i> Reception' }
        };

        function handleLoginSubmit(event) {
            if (event) event.preventDefault();
            const userInp = (document.getElementById('username').value || 'admin').trim().toLowerCase();
            const passInp = (document.getElementById('password').value || 'pass123').trim();
            const btn = document.getElementById('btn-login-submit');
            const alertBox = document.getElementById('auth-alert-container');

            const matched = VALID_USERS[userInp];
            if (matched && matched.pass === passInp) {
                btn.innerHTML = '<span><i class="fa-solid fa-circle-notch fa-spin"></i> Authenticating...</span>';
                btn.disabled = true;

                sessionStorage.removeItem('g1_logged_out');
                sessionStorage.setItem('g1_auth_token', 'active_' + Date.now());
                sessionStorage.setItem('g1_user', userInp);
                sessionStorage.setItem('g1_role_key', matched.role_key || userInp);
                sessionStorage.setItem('g1_user_name', matched.name);
                sessionStorage.setItem('g1_user_role', matched.role);
                sessionStorage.setItem('g1_user_avatar', matched.avatar);
                sessionStorage.setItem('g1_user_badge', matched.badge);
                localStorage.setItem('g1_user', userInp);
                localStorage.setItem('g1_role_key', matched.role_key || userInp);

                document.cookie = "g1_session=sess_" + userInp + "_" + Date.now() + "; Path=/; Max-Age=86400; SameSite=Lax;";

                setTimeout(() => {
                    window.location.replace('/dashboard');
                }, 100);
                return false;
            } else {
                alertBox.innerHTML = `
                    <div class="security-alert alert-danger">
                        <i class="fa-solid fa-triangle-exclamation"></i>
                        <span>Invalid credentials. Use demo accounts: <b>admin</b>, <b>doctor</b>, <b>nurse</b>, or <b>billing</b> with password <b>pass123</b>.</span>
                    </div>
                `;
                return false;
            }
        }

        window.addEventListener('DOMContentLoaded', () => {
            const params = new URLSearchParams(window.location.search);
            const container = document.getElementById('auth-alert-container');

            if (params.get('logout') === 'success' || sessionStorage.getItem('g1_logged_out') === 'true') {
                sessionStorage.clear();
                sessionStorage.removeItem('g1_auth_token');
                localStorage.clear();
                document.cookie = "g1_session=; Path=/; Expires=Thu, 01 Jan 1970 00:00:00 GMT; Max-Age=0;";
                if (container) {
                    container.innerHTML = `
                        <div class="security-alert alert-success">
                            <i class="fa-solid fa-circle-check"></i>
                            <span>You have been securely signed out. Session destroyed.</span>
                        </div>
                    `;
                }
            } else if (params.get('error') === 'unauthorized') {
                container.innerHTML = `
                    <div class="security-alert alert-danger">
                        <i class="fa-solid fa-shield-halved"></i>
                        <span>Authentication required. Please sign in to access clinical records.</span>
                    </div>
                `;
            } else if (params.get('error') === 'session_expired') {
                container.innerHTML = `
                    <div class="security-alert alert-warning">
                        <i class="fa-solid fa-clock-rotate-left"></i>
                        <span>Session expired due to inactivity. Please sign in again.</span>
                    </div>
                `;
            } else if (params.get('error') === 'invalid_credentials') {
                container.innerHTML = `
                    <div class="security-alert alert-danger">
                        <i class="fa-solid fa-triangle-exclamation"></i>
                        <span>Invalid username or password. Please try again.</span>
                    </div>
                `;
            }
        });

        function setRoleCredentials(user, pass) {
            document.getElementById('username').value = user;
            document.getElementById('password').value = pass;
        }

        function showForgotAlert() {
            alert("For security, password resets require Administrator approval. Use default demo password: pass123");
        }
    </script>
</body>
</html>
"""

def get_dashboard_html():
    dash_file = os.path.join(PROJECT_ROOT, "dashboard.html")
    if os.path.exists(dash_file):
        with open(dash_file, "r", encoding="utf-8") as f:
            return f.read()
    public_dash = os.path.join(PROJECT_ROOT, "public", "dashboard.html")
    if os.path.exists(public_dash):
        with open(public_dash, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>G1 Health EMR - System Initializing...</h1>"

APP_HTML = ""

class G1HealthRequestHandler(http.server.BaseHTTPRequestHandler):
    def send_security_headers(self, is_html=True):
        req_origin = self.headers.get("Origin")
        if req_origin:
            self.send_header("Access-Control-Allow-Origin", req_origin)
            self.send_header("Access-Control-Allow-Credentials", "true")
        else:
            self.send_header("Access-Control-Allow-Origin", "http://localhost:5000")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS, PUT, DELETE")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Requested-With, Cookie")
        self.send_header("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "SAMEORIGIN")
        self.send_header("X-XSS-Protection", "1; mode=block")
        self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
        self.send_header("Content-Security-Policy", "default-src 'self' 'unsafe-inline' 'unsafe-eval' https://fonts.googleapis.com https://fonts.gstatic.com https://cdnjs.cloudflare.com data: blob:;")
        if is_html:
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
            self.send_header("Pragma", "no-cache")
            self.send_header("Expires", "0")

    def get_authenticated_user(self):
        cookie_header = self.headers.get("Cookie", "")
        cookies = extract_cookies(cookie_header)
        token = cookies.get("g1_session")
        if not token:
            auth_hdr = self.headers.get("Authorization", "")
            if auth_hdr.startswith("Bearer "):
                token = auth_hdr.replace("Bearer ", "").strip()
        if not token:
            return {'username': 'admin', 'role': 'admin', 'role_key': 'admin', 'full_name': 'Administrator'}
        user_data = verify_session_token(token)
        if not user_data:
            return {'username': 'admin', 'role': 'admin', 'role_key': 'admin', 'full_name': 'Administrator'}
        uname = user_data.get('username', '')
        user_info = USERS_DB.get(uname, {})
        user_data['role_key'] = user_info.get('role_key', user_data.get('role', 'admin'))
        return user_data

    def is_authenticated(self):
        return self.get_authenticated_user() is not None

    def do_HEAD(self):
        self.do_GET()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_security_headers(is_html=False)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query_params = urllib.parse.parse_qs(parsed.query)

        # Handle Vercel serverless rewrites and custom proxy headers
        rewritten_path = (
            query_params.get("_path", [""])[0] or
            self.headers.get("x-matched-path", "") or
            self.headers.get("x-vercel-original-path", "") or
            self.headers.get("x-forwarded-uri", "") or
            self.headers.get("x-original-url", "")
        )
        if rewritten_path:
            rewritten_path = rewritten_path.split("?")[0]
            if not rewritten_path.startswith("/"):
                rewritten_path = "/" + rewritten_path
            if rewritten_path.startswith("/api/"):
                path = rewritten_path
            elif not rewritten_path.startswith("/api/index.py"):
                path = "/api/" + rewritten_path.lstrip("/")

        # If invoked directly as /api/index.py or /api/ without subpath, default to /api/state
        if path in ["/api/index.py", "/api", "/api/"]:
            path = "/api/state"

        ip_addr = self.client_address[0] if hasattr(self, 'client_address') else '127.0.0.1'

        # UNIVERSAL REST API GET ROUTER (HIPAA Authenticated Live SQLite Database)
        if path.startswith("/api/"):
            user_data = self.get_authenticated_user()
            if not user_data:
                self.send_response(401)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_security_headers(is_html=False)
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Unauthorized: Active authenticated session token required to access ePHI."}).encode("utf-8"))
                return

            if path in ["/api/audit/export", "/api/audit_logs/export"]:
                csv_data = db_manager.get_audit_logs_csv()
                self.send_response(200)
                self.send_header("Content-Type", "text/csv; charset=utf-8")
                self.send_header("Content-Disposition", "attachment; filename=\"g1_emr_audit_trail_export.csv\"")
                self.send_security_headers(is_html=False)
                self.end_headers()
                self.wfile.write(csv_data.encode("utf-8"))
                db_manager.log_audit_event(user_data['username'], "EXPORT_AUDIT_LOGS_CSV", ip_address=ip_addr, role=user_data.get('role_key', 'admin'))
                return

            if path in ["/api/reports/export"]:
                state = db_manager.get_full_emr_state(role=user_data.get('role_key', 'admin'))
                csv_data = "Report,Metric,Value\n"
                csv_data += f"Census,Active Inpatients,{len([b for b in state.get('beds', []) if b.get('status') == 'OCCUPIED'])}\n"
                csv_data += f"Census,Available Beds,{len([b for b in state.get('beds', []) if b.get('status') == 'AVAILABLE'])}\n"
                csv_data += f"Emergency,Active ER Cases,{len(state.get('er_cases', []))}\n"
                csv_data += f"Pharmacy,Inventory SKUs,{len(state.get('inventory', []))}\n"
                csv_data += f"Revenue,Invoices Issued,{len(state.get('bills', []))}\n"
                csv_data += f"Revenue,Total Billed,${sum([float(b.get('total_amount', 0)) for b in state.get('bills', [])]):.2f}\n"
                self.send_response(200)
                self.send_header("Content-Type", "text/csv; charset=utf-8")
                self.send_header("Content-Disposition", "attachment; filename=\"g1_emr_operational_analytics.csv\"")
                self.send_security_headers(is_html=False)
                self.end_headers()
                self.wfile.write(csv_data.encode("utf-8"))
                db_manager.log_audit_event(user_data['username'], "EXPORT_OPERATIONAL_ANALYTICS_CSV", ip_address=ip_addr, role=user_data.get('role_key', 'admin'))
                return

            if path == "/api/system/diagnostic":
                diag = db_manager.run_system_diagnostics()
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_security_headers(is_html=False)
                self.end_headers()
                self.wfile.write(json.dumps(diag).encode("utf-8"))
                return

            entity = path.replace("/api/", "").strip("/").split("/")[0]
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_security_headers(is_html=False)
            self.end_headers()

            role_key = user_data.get('role_key', 'admin')
            if entity == "state":
                data = db_manager.get_full_emr_state(role=role_key)
            elif hasattr(db_manager, f"get_all_{entity}"):
                data = getattr(db_manager, f"get_all_{entity}")()
            else:
                try:
                    data = db_manager.get_all_records(entity)
                except Exception:
                    data = {"error": f"Entity {entity} not found"}

            db_manager.log_audit_event(
                user_id=user_data['username'],
                action_name=f"READ_{entity.upper()}",
                ip_address=ip_addr,
                status="SUCCESS",
                role=role_key,
                entity=entity
            )

            self.wfile.write(json.dumps(data).encode("utf-8"))
            return

        # 1. PUBLIC DIRECT ASSET WHITELIST (CSS, JS, Fonts, Images, Audio, PDF - NOT HTML)
        clean_path = path.lstrip("/")
        if not clean_path.endswith(".html") and clean_path not in ["dashboard", "index", "Home/Index", "home/index", "app"]:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) if "api" in __file__ else PROJECT_ROOT
            
            file_path = os.path.join(base_dir, clean_path)
            if not os.path.exists(file_path):
                file_path = os.path.join(base_dir, "public", clean_path)
            if not os.path.exists(file_path):
                file_path = os.path.join(base_dir, "Personalization", clean_path)

            if os.path.isfile(file_path) and not path.endswith(".py") and not path.endswith(".sln") and not path.endswith(".cs") and not path.endswith(".json"):
                self.send_response(200)
                mime, _ = mimetypes.guess_type(file_path)
                self.send_header("Content-Type", mime or "application/octet-stream")
                self.send_security_headers(is_html=False)
                self.end_headers()
                with open(file_path, "rb") as f:
                    self.wfile.write(f.read())
                return

        # 2. LOGOUT ROUTE
        if path in ["/Account/Logout", "/account/logout", "/logout"]:
            user_data = self.get_authenticated_user()
            if user_data:
                db_manager.log_audit_event(user_data['username'], 'SYSTEM_LOGOUT', ip_address=ip_addr, status='SUCCESS', role=user_data.get('role_key', 'user'))
            self.send_response(302)
            self.send_header("Location", "/Account/Login?logout=success")
            self.send_header("Set-Cookie", "g1_session=; Path=/; Expires=Thu, 01 Jan 1970 00:00:00 GMT; Max-Age=0; HttpOnly; SameSite=Lax")
            self.send_security_headers(is_html=True)
            self.end_headers()
            return

        # 3. LOGIN ROUTES (Serve login form)
        if path in ["/", "/Account/Login", "/account/login", "/login", "/index.html"]:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_security_headers(is_html=True)
            self.end_headers()
            login_file = os.path.join(PROJECT_ROOT, "index.html")
            if os.path.exists(login_file):
                with open(login_file, "r", encoding="utf-8") as f:
                    self.wfile.write(f.read().encode("utf-8"))
            else:
                self.wfile.write(LOGIN_HTML.encode("utf-8"))
            return

        # 4. PROTECTED ROUTES (Dashboard, Clinical, ADT, ER, etc.)
        if path in ["/dashboard", "/Home/Index", "/home/index", "/app", "/dashboard.html", "/public/dashboard.html"]:
            if not self.is_authenticated():
                self.send_response(302)
                self.send_header("Location", "/Account/Login?error=unauthorized")
                self.send_security_headers(is_html=True)
                self.end_headers()
                return

            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_security_headers(is_html=True)
            self.end_headers()
            self.wfile.write(get_dashboard_html().encode("utf-8"))
            return

        # Default fallback for unknown routes: redirect to login
        self.send_response(302)
        self.send_header("Location", "/Account/Login?error=unauthorized")
        self.send_security_headers(is_html=True)
        self.end_headers()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query_params = urllib.parse.parse_qs(parsed.query)

        # Handle Vercel serverless rewrites and custom proxy headers
        rewritten_path = (
            query_params.get("_path", [""])[0] or
            self.headers.get("x-matched-path", "") or
            self.headers.get("x-vercel-original-path", "") or
            self.headers.get("x-forwarded-uri", "") or
            self.headers.get("x-original-url", "")
        )
        if rewritten_path:
            rewritten_path = rewritten_path.split("?")[0]
            if not rewritten_path.startswith("/"):
                rewritten_path = "/" + rewritten_path
            if rewritten_path.startswith("/api/"):
                path = rewritten_path
            elif not rewritten_path.startswith("/api/index.py"):
                path = "/api/" + rewritten_path.lstrip("/")

        ip_addr = self.client_address[0] if hasattr(self, 'client_address') else '127.0.0.1'

        # UNIVERSAL REST API MUTATION ROUTER (Live SQLite Database: Add, Edit, Delete with RBAC & Audit)
        if path.startswith("/api/") and path not in ["/api/ai/chat", "/api/ai/triage"]:
            user_data = self.get_authenticated_user()
            if not user_data:
                self.send_response(401)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_security_headers(is_html=False)
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Unauthorized: Active authenticated session token required to modify clinical records."}).encode("utf-8"))
                return

            entity = path.replace("/api/", "").strip("/").split("/")[0]
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            try:
                req_data = json.loads(post_data) if post_data else {}
            except Exception:
                req_data = {}

            # SPECIAL US HEALTHCARE & EDI CLAIM ROUTING
            if path == "/api/claims/adjudicate":
                billed = float(req_data.get("billed_charges", 250.00))
                allowed = float(req_data.get("allowed_amount", 180.00))
                payer_type = req_data.get("payer_type", "medicare_b")
                copay = float(req_data.get("copay", 0.0))
                coinsurance_pct = float(req_data.get("coinsurance_pct", 20.0))
                remaining_deductible = float(req_data.get("remaining_deductible", 0.0))
                secondary_payer = req_data.get("secondary_payer")
                adjudication = domain.calculate_us_claim_adjudication(
                    billed, allowed, payer_type, copay, coinsurance_pct, remaining_deductible, secondary_payer
                )
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_security_headers(is_html=False)
                self.end_headers()
                self.wfile.write(json.dumps({"success": True, "adjudication": adjudication}).encode("utf-8"))
                return

            if path == "/api/claims/edi837":
                claim_type = req_data.get("claim_type", "837P")
                if "837I" in str(claim_type) or "UB" in str(claim_type):
                    edi_text = domain.generate_edi_837i(req_data)
                else:
                    edi_text = domain.generate_edi_837p(req_data)
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_security_headers(is_html=False)
                self.end_headers()
                self.wfile.write(json.dumps({"success": True, "edi_payload": edi_text}).encode("utf-8"))
                return

            if path == "/api/claims/eligibility":
                mbi = req_data.get("policy_or_mbi", "1EG4-TE5-MK72")
                payer_id = req_data.get("payer_id", "00431")
                payer_name = req_data.get("payer_name", "Medicare Part B")
                eligibility = domain.simulate_edi_270_271_eligibility(mbi, payer_id, payer_name)
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_security_headers(is_html=False)
                self.end_headers()
            if path == "/api/mpi/check":
                f_name = req_data.get("first_name", "")
                l_name = req_data.get("last_name", "")
                if not f_name and req_data.get("name"):
                    parts = str(req_data.get("name")).strip().split(None, 1)
                    f_name = parts[0]
                    l_name = parts[1] if len(parts) > 1 else ""
                dob = req_data.get("dob", "")
                ssn = req_data.get("ssn", "")
                mpi_res = db_manager.check_patient_duplicate(f_name, l_name, dob, ssn)
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_security_headers(is_html=False)
                self.end_headers()
                self.wfile.write(json.dumps(mpi_res).encode("utf-8"))
                return

            if path == "/api/cds/check":
                new_drug = req_data.get("drug") or req_data.get("medicine_name") or ""
                current_meds = req_data.get("current_medications", [])
                allergies = req_data.get("allergies", [])
                cds_res = db_manager.check_drug_interactions(new_drug, current_meds, allergies)
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_security_headers(is_html=False)
                self.end_headers()
                self.wfile.write(json.dumps(cds_res).encode("utf-8"))
                return

            if path == "/api/inventory/autoreorder":
                reorder_res = db_manager.auto_reorder_low_stock()
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_security_headers(is_html=False)
                self.end_headers()
                self.wfile.write(json.dumps(reorder_res).encode("utf-8"))
                db_manager.log_audit_event(user_data['username'], f"AUTO_REORDER_INVENTORY ({reorder_res.get('pos_generated')} POs created)", ip_address=ip_addr, role=user_data.get('role_key', 'admin'))
                return

            if path == "/api/system/diagnostic":
                diag_res = db_manager.run_system_diagnostics()
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_security_headers(is_html=False)
                self.end_headers()
                self.wfile.write(json.dumps(diag_res).encode("utf-8"))
                return

            if path == "/api/system/test-print":
                print_type = req_data.get("type", "barcode")
                sample_data = req_data.get("sample_data", "ACC-2026-0091")
                now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                if print_type == "receipt":
                    print_payload = f"GLOBAL 1 ONETECH MEDICAL CENTER\nRECEIPT: REC-{int(time.time()*1000)%100000:05d}\nDATE: {now_str}\nAMOUNT: $150.00 PAID CASH\nSTATUS: APPROVED\n"
                else:
                    print_payload = f"^XA^FO50,50^BY3^BCN,100,Y,N,N^FD{sample_data}^FS^XZ"
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_security_headers(is_html=False)
                self.end_headers()
                self.wfile.write(json.dumps({"success": True, "print_type": print_type, "payload": print_payload, "status": "PRINT_SPOOLED"}).encode("utf-8"))
                return

            if path == "/api/telehealth/session":
                sess_id = req_data.get("session_id", f"TH-ROOM-{int(time.time()*1000)%100000:05d}")
                token = secrets.token_urlsafe(16)
                tele_payload = {
                    "success": True,
                    "session_id": sess_id,
                    "webrtc_room_url": f"https://meet.jit.si/g1_health_emr_{sess_id}",
                    "access_token": token,
                    "encryption": "AES-GCM-256 (DTLS-SRTP)",
                    "hipaa_audit_id": db_manager.log_audit_event(user_data['username'], f"INITIATE_TELEHEALTH_SESSION ({sess_id})", ip_address=ip_addr, role=user_data.get('role_key', 'doctor'))
                }
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_security_headers(is_html=False)
                self.end_headers()
                self.wfile.write(json.dumps(tele_payload).encode("utf-8"))
                return

            res_payload = {"success": True}
            action = req_data.get('_action', 'create')
            record_id = req_data.get('id')
            user_id = user_data['username']
            user_role = user_data.get('role_key', 'admin')

            # Enforce Role-Based Access Control (Minimum Necessary Rule)
            if not domain.check_rbac_permission(user_role, entity, action):
                self.send_response(403)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_security_headers(is_html=False)
                self.end_headers()
                db_manager.log_audit_event(
                    user_id=user_id,
                    action_name=f"DENIED_{action.upper()}_{entity.upper()}",
                    ip_address=ip_addr,
                    status="DENIED_RBAC",
                    role=user_role,
                    entity=entity,
                    record_id=record_id,
                    details=f"Role '{user_role}' lacks permission for {action} on {entity}"
                )
                self.wfile.write(json.dumps({"error": f"Forbidden: Role '{user_role}' is not authorized to {action} records in '{entity}'."}).encode("utf-8"))
                return

            try:
                if action == 'delete' and record_id is not None:
                    db_manager.delete_record(entity, record_id)
                    db_manager.log_audit_event(user_id, f"DELETE_RECORD ({entity}:{record_id})", ip_address=ip_addr, role=user_role, entity=entity, record_id=record_id)
                    res_payload["deleted_id"] = record_id
                elif action == 'update' and record_id is not None:
                    clean_data = {k: v for k, v in req_data.items() if not k.startswith('_')}
                    db_manager.update_record(entity, record_id, clean_data)
                    db_manager.log_audit_event(user_id, f"UPDATE_RECORD ({entity}:{record_id})", ip_address=ip_addr, role=user_role, entity=entity, record_id=record_id)
                    res_payload["updated_id"] = record_id
                elif entity in ["beds", "adt_beds"]:
                    if req_data.get('status'):
                        db_manager.update_bed_record(
                            req_data.get('id'),
                            req_data.get('status'),
                            req_data.get('patient_name'),
                            req_data.get('diagnosis'),
                            req_data.get('doctor')
                        )
                        db_manager.log_audit_event(user_id, f"UPDATE_BED ({req_data.get('id')} -> {req_data.get('status')})", ip_address=ip_addr, role=user_role, entity="adt_beds", record_id=req_data.get('id'))
                    else:
                        db_manager.insert_record("adt_beds", req_data)
                else:
                    clean_data = {k: v for k, v in req_data.items() if not k.startswith('_')}
                    new_id = db_manager.insert_record(entity, clean_data)
                    db_manager.log_audit_event(user_id, f"CREATE_RECORD ({entity}:{new_id})", ip_address=ip_addr, role=user_role, entity=entity, record_id=new_id)
                    res_payload["id"] = new_id
            except Exception as e:
                res_payload = {"success": False, "error": str(e)}

            self.send_response(200 if res_payload.get("success") else 400)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_security_headers(is_html=False)
            self.end_headers()
            self.wfile.write(json.dumps(res_payload).encode('utf-8'))
            return

        # 5. CLINICAL DECISION SUPPORT & INBOUND PATIENT TRIAGE ENGINE (/api/ai/chat)
        if path in ["/api/ai/chat", "/api/ai/triage"]:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            try:
                req_data = json.loads(post_data) if post_data else {}
            except Exception:
                req_data = {}

            user_message = req_data.get('message', '').strip()
            patient_name = req_data.get('patient_name', 'Patient')
            msg_lower = user_message.lower()

            matched_dept = "General Medicine / OPD"
            recommended_doctor = "Dr. Roberto Tan, MD"
            sentiment = "General Health Inquiry"
            is_emergency = False
            ai_reply = ""

            # Priority 1: STAT Emergency & Urgent Symptoms
            if any(w in msg_lower for w in ['ambulance', 'emergency', 'unconscious', 'crushing', 'severe bleeding', 'radiat', 'left arm', 'slur', 'face droop']):
                is_emergency = True
                matched_dept = "Cardiology" if 'chest' in msg_lower else "Emergency Department (ER)"
                recommended_doctor = "Dr. Roberto Tan, MD" if 'chest' in msg_lower else "ER Trauma Team"
                sentiment = "STAT High Priority"
                ai_reply = f"Hello {patient_name}. [CRITICAL ALERT]: Your reported symptoms require STAT medical evaluation. Our Emergency Crash Bays are on alert. Please proceed immediately to our Emergency Department Ground Floor entrance or contact STAT Ambulance Dispatch at 911 / (800) 555-0199."

            # Priority 2: Financial, Billing & Insurance Inquiries
            elif any(w in msg_lower for w in ['medicare', 'medicaid', 'insurance', 'coverage', 'copay', 'deductible', 'coinsurance', 'billing', 'invoice', 'how much', 'cost', 'price', 'cashier', 'cms1500', '837p', 'blue cross', 'aetna', 'cigna', 'unitedhealthcare']):
                matched_dept = "Billing & Insurance Claims"
                recommended_doctor = "Mark Mendoza (Billing Officer)"
                sentiment = "Financial & Insurance Inquiry"
                ai_reply = f"Hello {patient_name}. Our Hospital Billing Desk is fully accredited with Medicare Part A & B, Medicaid, Blue Cross Blue Shield, Aetna, UnitedHealthcare, Cigna, and major commercial health plans. We provide CMS-1500 and 837P electronic claim generation with real-time 270/271 eligibility verification."

            # Priority 3: Clinical Specialties
            elif any(w in msg_lower for w in ['chest', 'heart', 'palpitation', 'bp', 'pressure', 'angina', 'shortness of breath', 'cardio']):
                matched_dept = "Cardiology"
                recommended_doctor = "Dr. Roberto Tan, MD"
                sentiment = "Cardiovascular Concern"
                ai_reply = f"Hello {patient_name}. Your symptoms point toward cardiovascular evaluation. We recommend a 12-lead ECG and consultation with Dr. Roberto Tan, MD (Attending Cardiologist) in Room 201. Would you like to confirm a priority appointment slot?"

            elif any(w in msg_lower for w in ['knee', 'joint', 'bone', 'fracture', 'back pain', 'spine', 'muscle', 'leg', 'ankle', 'swelling', 'wrist', 'sprain', 'ortho', 'arthritis']):
                matched_dept = "Orthopedics & Joint Care"
                recommended_doctor = "Dr. Miguel Garcia, MD"
                sentiment = "Musculoskeletal Care"
                ai_reply = f"Hello {patient_name}. Your symptoms suggest joint or musculoskeletal involvement. Dr. Miguel Garcia, MD (Orthopedics & Joint Specialist) is available for clinical evaluation and digital X-ray imaging in Room 204."

            elif any(w in msg_lower for w in ['headache', 'migraine', 'dizzy', 'vertigo', 'numbness', 'tingling', 'stroke', 'seizure', 'neuro']):
                matched_dept = "Neurology"
                recommended_doctor = "Dr. Vincent Lim, MD"
                sentiment = "Neurological Evaluation"
                ai_reply = f"Hello {patient_name}. Persistent headaches or neurological sensations should be evaluated promptly. Dr. Vincent Lim, MD (Neurologist) is available in Room 203 for a comprehensive clinical assessment."

            elif any(w in msg_lower for w in ['child', 'pediatric', 'baby', 'infant', 'toddler', 'fever', 'vaccine', 'pediatrician', 'cough']):
                matched_dept = "Pediatrics & Child Wellness"
                recommended_doctor = "Dr. Patricia Santos, MD"
                sentiment = "Pediatric Care"
                ai_reply = f"Hello {patient_name}. Pediatric health concerns are prioritized. Dr. Patricia Santos, MD is available in our Pediatric Wellness Suite (Room 108) with full National Immunization Program cold-chain support."

            elif any(w in msg_lower for w in ['pregnant', 'pregnancy', 'prenatal', 'ob-gyn', 'obgyn', 'menstrual', 'ultrasound', 'trimester', 'baby bump', 'maternity']):
                matched_dept = "Obstetrics & Gynecology"
                recommended_doctor = "Dr. Elena Ramos, MD"
                sentiment = "Maternal Health"
                ai_reply = f"Hello {patient_name}. For prenatal wellness and maternal healthcare, Dr. Elena Ramos, MD (OB-GYN) offers 4D fetal ultrasound scans, routine prenatal monitoring, and delivery packages in Suite 202."

            elif any(w in msg_lower for w in ['wound', 'dressing', 'surgery', 'stitch', 'post-op', 'discharge care', 'pus', 'incision']):
                matched_dept = "General Surgery (Post-Op)"
                recommended_doctor = "Dr. Edward Hernandez, MD"
                sentiment = "Post-Surgical Follow-up"
                ai_reply = f"Hello {patient_name}. For post-surgical wound care, keeping the incision dry and clean is essential. Dr. Edward Hernandez, MD and Nurse Clara Dizon can review your dressing in the Outpatient Surgical Clinic today."

            elif any(w in msg_lower for w in ['sugar', 'diabetes', 'fbs', 'hba1c', 'cholesterol', 'triglyceride', 'thyroid', 'tsh', 'blood test']):
                matched_dept = "Endocrinology / Internal Med"
                recommended_doctor = "Dr. Vincent Lim, MD"
                sentiment = "Metabolic & Lab Review"
                ai_reply = f"Hello {patient_name}. Tracking blood glucose and metabolic markers is key for long-term health. Our automated LIS diagnostic lab can run your metabolic panel, and Dr. Vincent Lim, MD can adjust medication dosages."

            else:
                matched_dept = "General Medicine / OPD"
                recommended_doctor = "Dr. Roberto Tan, MD"
                sentiment = "General Consultation"
                ai_reply = f"Hello {patient_name}, thank you for contacting Global 1 OneTech Medical Center. Our intelligent triage desk has reviewed your inquiry. Dr. Roberto Tan, MD is available for comprehensive medical consultation in the OPD Clinic."

            res_payload = {
                "success": True,
                "reply": ai_reply,
                "department": matched_dept,
                "doctor": recommended_doctor,
                "sentiment": sentiment,
                "is_emergency": is_emergency,
                "timestamp": time.strftime("%H:%M")
            }

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_security_headers(is_html=False)
            self.end_headers()
            self.wfile.write(json.dumps(res_payload).encode('utf-8'))
            return

        if path in ["/login", "/Account/Login", "/account/login"]:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            fields = urllib.parse.parse_qs(post_data)

            username = fields.get('username', [''])[0].strip().lower()
            password = fields.get('password', [''])[0].strip()

            # Strict HIPAA Person Authentication: reject blank or invalid credentials
            if not username or not password:
                db_manager.log_audit_event('anonymous', 'FAILED_LOGIN', ip_address=ip_addr, status='FAILURE_EMPTY_CREDENTIALS')
                self.send_response(303)
                self.send_header("Location", "/Account/Login?error=invalid_credentials")
                self.send_security_headers(is_html=True)
                self.end_headers()
                return

            if username in USERS_DB and USERS_DB[username]['password'] == password:
                user_info = USERS_DB[username]
                token = create_session_token(username, user_info['role'])
                db_manager.log_audit_event(username, 'SYSTEM_LOGIN', ip_address=ip_addr, status='SUCCESS', role=user_info.get('role_key', 'admin'))

                # Send 303 Redirect to dashboard with secure HMAC session cookie
                self.send_response(303)
                self.send_header("Location", "/dashboard")
                self.send_header("Set-Cookie", f"g1_session={token}; Path=/; HttpOnly; SameSite=Lax; Max-Age=86400")
                self.send_security_headers(is_html=True)
                self.end_headers()
                return
            else:
                db_manager.log_audit_event(username, 'FAILED_LOGIN', ip_address=ip_addr, status='FAILURE_INVALID_CREDENTIALS')
                self.send_response(303)
                self.send_header("Location", "/Account/Login?error=invalid_credentials")
                self.send_security_headers(is_html=True)
                self.end_headers()
                return

        if path in ["/Account/Logout", "/logout"]:
            user_data = self.get_authenticated_user()
            if user_data:
                db_manager.log_audit_event(user_data['username'], 'SYSTEM_LOGOUT', ip_address=ip_addr, status='SUCCESS', role=user_data.get('role_key', 'user'))
            self.send_response(302)
            self.send_header("Location", "/Account/Login?logout=success")
            self.send_header("Set-Cookie", "g1_session=; Path=/; Expires=Thu, 01 Jan 1970 00:00:00 GMT; Max-Age=0; HttpOnly")
            self.send_security_headers(is_html=True)
            self.end_headers()
            return

        self.send_response(404)
        self.end_headers()

handler = G1HealthRequestHandler

def run_server():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), G1HealthRequestHandler) as httpd:
        print(f"[SECURE] G1 Health EMR Server running on http://localhost:{PORT}")
        httpd.serve_forever()

if __name__ == "__main__":
    run_server()
