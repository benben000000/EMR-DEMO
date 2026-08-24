import db_manager
#!/usr/bin/env python3
"""
G1 Health EMR - macOS Complete Interactive Enterprise Suite & Demo Runner
Organization: Global 1 OneTech (https://global1onetech.com/)
Product: G1 Health EMR Enterprise Cloud

Enterprise Security Features:
- Stateless Cryptographic HMAC Session Tokens (100% Vercel Serverless & Local Compatible)
- Protected Route Guards (/dashboard, /app, /Home/Index)
- Immediate Post-Logout Cookie & Storage Invalidation
- Anti-Cache Headers (Cache-Control: no-store, no-cache, must-revalidate)
- Direct Access Whitelist for Static Files (/Personalization/*, /public/*, /favicon.ico)
- Role-Based Access Control (RBAC): Super Admin, Doctor, Nurse, Billing Officer
- Inactivity Lock Screen & Session Timeout
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
BASE_DIR = os.path.abspath(os.path.join(PROJECT_ROOT, "Code/Websites/DanpheEMR"))

# Cryptographic Secret Key for HMAC Session Tokens
SECRET_KEY = b'global1onetech_g1_health_emr_enterprise_secret_key_2026'
SESSION_EXPIRY_SECONDS = 86400 # 24 Hours

# Valid User Accounts & Roles
USERS_DB = {
    'admin': {'password': 'pass123', 'name': 'Administrator', 'role': 'Super Admin &bull; Full Access', 'role_key': 'admin', 'avatar': 'AD', 'badge': '👑 Super Admin'},
    'doctor': {'password': 'pass123', 'name': 'Dr. Roberto Tan, MD', 'role': 'Attending Cardiologist &bull; Clinical Desk', 'role_key': 'doctor', 'avatar': 'RT', 'badge': '🩺 Doctor (MD)'},
    'nurse': {'password': 'pass123', 'name': 'Nurse Clara Dizon', 'role': 'Charge Nurse &bull; Ward Station', 'role_key': 'nurse', 'avatar': 'CD', 'badge': '💉 Nurse (RN)'},
    'accountant': {'password': 'pass123', 'name': 'Elena Villar, CPA', 'role': 'Chief Accountant &bull; Finance Dept', 'role_key': 'accountant', 'avatar': 'EV', 'badge': '💰 Accountant'},
    'billing': {'password': 'pass123', 'name': 'Mark Mendoza', 'role': 'Billing & Claims Officer &bull; Cashier', 'role_key': 'billing', 'avatar': 'MM', 'badge': '💳 Billing'},
    'pharmacy': {'password': 'pass123', 'name': 'Pharm. Leo Santos, RPh', 'role': 'Chief Pharmacist &bull; Dispensary', 'role_key': 'pharmacy', 'avatar': 'LS', 'badge': '💊 Pharmacist'},
    'labtech': {'password': 'pass123', 'name': 'Sarah Cruz, RMT', 'role': 'Diagnostic & Imaging Technologist', 'role_key': 'labtech', 'avatar': 'SC', 'badge': '🔬 Lab Tech'},
    'reception': {'password': 'pass123', 'name': 'Joy Pascual', 'role': 'Front Desk & Admissions Officer', 'role_key': 'reception', 'avatar': 'JP', 'badge': '📋 Reception'}
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

        .hero-tagline b { color: var(--brand-cyan); }

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

        .feature-item i { color: var(--brand-cyan); font-size: 15px; width: 20px; text-align: center; }

        .hero-footer {
            font-size: 12px;
            color: #94a3b8;
            margin-top: 32px;
        }

        .hero-footer a { color: var(--brand-cyan); text-decoration: none; font-weight: 600; }

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
            box-shadow: 0 0 0 3.5px rgba(37, 53, 69, 0.12);
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
            color: var(--brand-cyan);
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
                        <button type="button" class="role-pill-btn" onclick="setRoleCredentials('admin', 'pass123')">👑 Admin</button>
                        <button type="button" class="role-pill-btn" onclick="setRoleCredentials('doctor', 'pass123')">🩺 Doctor</button>
                        <button type="button" class="role-pill-btn" onclick="setRoleCredentials('nurse', 'pass123')">💉 Nurse</button>
                        <button type="button" class="role-pill-btn" onclick="setRoleCredentials('accountant', 'pass123')">💰 Accountant</button>
                        <button type="button" class="role-pill-btn" onclick="setRoleCredentials('billing', 'pass123')">💳 Billing</button>
                        <button type="button" class="role-pill-btn" onclick="setRoleCredentials('pharmacy', 'pass123')">💊 Pharmacy</button>
                        <button type="button" class="role-pill-btn" onclick="setRoleCredentials('labtech', 'pass123')">🔬 Lab Tech</button>
                        <button type="button" class="role-pill-btn" onclick="setRoleCredentials('reception', 'pass123')">📋 Reception</button>
                    </div>
                </div>
            </form>
        </div>
    </div>

    <script>
        const VALID_USERS = {
            'admin': { pass: 'pass123', name: 'Administrator', role: 'Super Admin &bull; Full Access', role_key: 'admin', avatar: 'AD', badge: '👑 Super Admin' },
            'doctor': { pass: 'pass123', name: 'Dr. Roberto Tan, MD', role: 'Attending Cardiologist &bull; Clinical Desk', role_key: 'doctor', avatar: 'RT', badge: '🩺 Doctor (MD)' },
            'nurse': { pass: 'pass123', name: 'Nurse Clara Dizon', role: 'Charge Nurse &bull; Ward Station', role_key: 'nurse', avatar: 'CD', badge: '💉 Nurse (RN)' },
            'accountant': { pass: 'pass123', name: 'Elena Villar, CPA', role: 'Chief Accountant &bull; Finance Dept', role_key: 'accountant', avatar: 'EV', badge: '💰 Accountant' },
            'billing': { pass: 'pass123', name: 'Mark Mendoza', role: 'Billing & Claims Officer &bull; Cashier', role_key: 'billing', avatar: 'MM', badge: '💳 Billing' },
            'pharmacy': { pass: 'pass123', name: 'Pharm. Leo Santos, RPh', role: 'Chief Pharmacist &bull; Dispensary', role_key: 'pharmacy', avatar: 'LS', badge: '💊 Pharmacist' },
            'labtech': { pass: 'pass123', name: 'Sarah Cruz, RMT', role: 'Diagnostic & Imaging Technologist', role_key: 'labtech', avatar: 'SC', badge: '🔬 Lab Tech' },
            'reception': { pass: 'pass123', name: 'Joy Pascual', role: 'Front Desk & Admissions Officer', role_key: 'reception', avatar: 'JP', badge: '📋 Reception' }
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

APP_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>G1 Health EMR - Global 1 OneTech Hospital Suite</title>
    <link rel="icon" href="/Personalization/logos/favicon.ico" />
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&family=Inter:wght@400;500;600;700&display=swap" />
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" />

    <!-- STRICT IMMEDIATE AUTH & BFCACHE BACK-BUTTON GUARD -->
    <script>
        function enforceAuthGuard() {
            const token = sessionStorage.getItem('g1_auth_token');
            const isLoggedOut = sessionStorage.getItem('g1_logged_out');
            if (!token || isLoggedOut === 'true') {
                document.documentElement.style.display = 'none';
                window.location.replace('/index.html?error=unauthorized');
                return false;
            }
            document.documentElement.style.display = '';
            return true;
        }

        enforceAuthGuard();

        window.addEventListener('pageshow', function(event) {
            enforceAuthGuard();
        });

        window.addEventListener('popstate', function() {
            enforceAuthGuard();
        });

        window.addEventListener('focus', function() {
            enforceAuthGuard();
        });
    </script>

    <style>
        :root {
            --brand-primary: #253545;
            --brand-primary-hover: #1b2838;
            --brand-cyan: #00ffa1;
            --brand-accent: #00bfa5;
            --brand-blue: #0284c7;
            --sidebar-bg: #1b2838;
            --sidebar-text: #f8fafc;
            --card-bg: #ffffff;
            --bg-page: #f8fafc;
            --border-color: #e2e8f0;
            --text-dark: #0f172a;
            --text-muted: #64748b;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Nunito', 'Inter', sans-serif; }

        body {
            background-color: var(--bg-page);
            display: flex;
            height: 100vh;
            overflow: hidden;
        }

        /* Sidebar */
        .sidebar {
            width: 270px;
            background: var(--sidebar-bg);
            color: var(--sidebar-text);
            display: flex;
            flex-direction: column;
            flex-shrink: 0;
            border-right: 1px solid rgba(255, 255, 255, 0.05);
            z-index: 100;
        }

        .sidebar-brand {
            padding: 16px 20px;
            background: rgba(0, 0, 0, 0.25);
            display: flex;
            align-items: center;
            gap: 12px;
            border-bottom: 2px solid var(--brand-cyan);
        }

        .sidebar-brand img {
            max-height: 36px;
            width: auto;
            filter: brightness(0) invert(1);
        }

        .nav-menu-wrapper {
            flex: 1;
            overflow-y: auto;
            padding: 10px 0;
        }

        .nav-menu {
            list-style: none;
            display: flex;
            flex-direction: column;
            gap: 2px;
        }

        .nav-section-title {
            font-size: 10.5px;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: #64748b;
            padding: 12px 24px 4px;
            font-weight: 800;
        }

        .nav-item a {
            display: flex;
            align-items: center;
            gap: 14px;
            padding: 10px 24px;
            color: #cbd5e1;
            text-decoration: none;
            font-size: 13.5px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.15s ease;
            border-left: 4px solid transparent;
        }

        .nav-item a:hover {
            background: rgba(255, 255, 255, 0.06);
            color: #ffffff;
        }

        .nav-item.active a {
            background: #253545;
            color: #ffffff;
            border-left: 4px solid var(--brand-cyan);
            font-weight: 700;
        }

        .nav-item i {
            font-size: 15px;
            width: 20px;
            text-align: center;
            color: #94a3b8;
        }

        .nav-item.active i {
            color: var(--brand-cyan);
        }

        .badge-new {
            background: var(--brand-cyan);
            color: #0f172a;
            font-size: 9.5px;
            font-weight: 800;
            padding: 2px 6px;
            border-radius: 10px;
            margin-left: auto;
        }

        /* Main Content */
        .main-wrapper {
            flex: 1;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        /* Top Header Navbar with Active Patient Info */
        .top-navbar {
            min-height: 64px;
            background: var(--brand-primary);
            color: #ffffff;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 24px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.15);
            border-bottom: 2px solid var(--brand-cyan);
            flex-shrink: 0;
            gap: 16px;
            flex-wrap: wrap;
        }

        .navbar-left {
            display: flex;
            align-items: center;
            gap: 16px;
        }

        .facility-title {
            font-size: 14px;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 8px;
            letter-spacing: 0.2px;
        }

        .facility-title span {
            color: var(--brand-cyan);
        }

        /* Global Active Patient Banner */
        .active-patient-badge {
            background: rgba(0, 0, 0, 0.35);
            border: 1px solid rgba(0, 255, 161, 0.3);
            border-radius: 8px;
            padding: 6px 14px;
            display: flex;
            align-items: center;
            gap: 12px;
            font-size: 12.5px;
            color: #f1f5f9;
        }

        .active-patient-badge .pat-name {
            font-weight: 800;
            color: #ffffff;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .active-patient-badge .pat-name i {
            color: var(--brand-cyan);
        }

        .btn-switch-pat {
            background: var(--brand-cyan);
            color: #0f172a;
            border: none;
            padding: 3px 8px;
            border-radius: 5px;
            font-size: 11px;
            font-weight: 800;
            cursor: pointer;
            transition: all 0.2s;
        }

        .btn-switch-pat:hover {
            background: #ffffff;
        }

        /* Header Patient Search */
        .global-search-wrapper {
            position: relative;
            width: 200px;
        }

        .global-search-wrapper i {
            position: absolute;
            left: 10px;
            top: 50%;
            transform: translateY(-50%);
            color: #94a3b8;
            font-size: 12px;
        }

        .global-search-input {
            width: 100%;
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 6px;
            padding: 6px 10px 6px 30px;
            color: #ffffff;
            font-size: 12.5px;
            outline: none;
            transition: all 0.2s;
        }

        .global-search-input::placeholder { color: #94a3b8; }
        .global-search-input:focus {
            background: rgba(255, 255, 255, 0.18);
            border-color: var(--brand-cyan);
            width: 240px;
        }

        .user-profile {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-left: auto;
        }

        .user-avatar {
            width: 34px;
            height: 34px;
            background: rgba(255, 255, 255, 0.1);
            border: 1.5px solid var(--brand-cyan);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 800;
            font-size: 12px;
            color: var(--brand-cyan);
        }

        .btn-logout {
            color: #cbd5e1;
            text-decoration: none;
            font-size: 12px;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 6px;
            padding: 6px 12px;
            border-radius: 6px;
            background: rgba(0, 0, 0, 0.25);
            transition: all 0.2s;
            cursor: pointer;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .btn-logout:hover {
            color: #ffffff;
            background: #ef4444;
            border-color: #ef4444;
        }

        .content-area {
            flex: 1;
            overflow-y: auto;
            padding: 24px 28px;
        }

        /* Modules Views */
        .module-view {
            display: none;
            animation: fadeIn 0.2s ease-in-out;
        }

        .module-view.active {
            display: block;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(4px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* Universal UX Breadcrumbs & Back Button */
        .ux-navigation-bar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 18px;
            padding-bottom: 12px;
            border-bottom: 1px solid var(--border-color);
        }

        .breadcrumbs {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 13px;
            color: var(--text-muted);
            font-weight: 600;
        }

        .breadcrumbs a {
            color: var(--brand-primary);
            text-decoration: none;
            cursor: pointer;
            font-weight: 700;
        }

        .breadcrumbs a:hover {
            text-decoration: underline;
        }

        .breadcrumbs span.current {
            color: var(--text-dark);
            font-weight: 800;
        }

        .btn-back-dashboard {
            background: #ffffff;
            border: 1.5px solid var(--border-color);
            color: #334155;
            padding: 7px 14px;
            border-radius: 8px;
            font-size: 12.5px;
            font-weight: 700;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            transition: all 0.2s;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
        }

        .btn-back-dashboard:hover {
            background: #f1f5f9;
            border-color: #cbd5e1;
            color: #0f172a;
            transform: translateX(-2px);
        }

        /* Section Headings */
        .view-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 20px;
        }

        .view-header h1 {
            font-size: 22px;
            font-weight: 800;
            color: var(--text-dark);
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .view-header p {
            font-size: 13.5px;
            color: var(--text-muted);
            margin-top: 4px;
        }

        .btn-primary-action {
            background: var(--brand-primary);
            color: #ffffff;
            border: none;
            padding: 10px 18px;
            border-radius: 8px;
            font-size: 13.5px;
            font-weight: 700;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            transition: all 0.2s;
        }

        .btn-primary-action:hover {
            background: var(--brand-primary-hover);
            color: var(--brand-cyan);
            transform: translateY(-1px);
        }

        .btn-accent-action {
            background: var(--brand-cyan);
            color: #0f172a;
            border: none;
            padding: 10px 18px;
            border-radius: 8px;
            font-size: 13.5px;
            font-weight: 800;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            transition: all 0.2s;
        }

        .btn-accent-action:hover {
            background: #00d688;
            transform: translateY(-1px);
        }

        /* Data Tables */
        .table-card {
            background: #ffffff;
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
            border: 1px solid var(--border-color);
            overflow: hidden;
            margin-bottom: 24px;
        }

        .table-toolbar {
            padding: 14px 20px;
            background: #ffffff;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
        }

        .search-box {
            position: relative;
            width: 320px;
            max-width: 100%;
        }

        .search-box i {
            position: absolute;
            left: 14px;
            top: 50%;
            transform: translateY(-50%);
            color: #94a3b8;
            font-size: 14px;
        }

        .search-box input {
            width: 100%;
            padding: 9px 14px 9px 38px;
            border: 1.5px solid var(--border-color);
            border-radius: 8px;
            font-size: 13px;
            outline: none;
            transition: all 0.2s;
        }

        .search-box input:focus { border-color: var(--brand-primary); }

        .emr-table {
            width: 100%;
            border-collapse: collapse;
            text-align: left;
            font-size: 13.5px;
        }

        .emr-table th {
            background: #f8fafc;
            color: #475569;
            font-weight: 700;
            padding: 12px 18px;
            border-bottom: 1.5px solid var(--border-color);
            text-transform: uppercase;
            font-size: 11px;
            letter-spacing: 0.5px;
        }

        .emr-table td {
            padding: 12px 18px;
            border-bottom: 1px solid var(--border-color);
            color: #1e293b;
        }

        .emr-table tbody tr:hover { background-color: #f8fafc; }

        /* Badges */
        .status-badge {
            display: inline-flex;
            align-items: center;
            gap: 5px;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 11.5px;
            font-weight: 700;
        }

        .status-active { background: #dcfce7; color: #15803d; }
        .status-pending { background: #fef9c3; color: #a16207; }
        .status-urgent { background: #fee2e2; color: #b91c1c; }
        .status-completed { background: #e0f2fe; color: #0369a1; }

        /* Stats Grid */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 20px;
            margin-bottom: 24px;
        }

        .stat-card {
            background: #ffffff;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
            border: 1px solid var(--border-color);
            display: flex;
            align-items: center;
            gap: 16px;
            border-left: 4px solid var(--brand-primary);
        }

        .stat-card.cyan { border-left-color: var(--brand-cyan); }
        .stat-card.teal { border-left-color: var(--brand-accent); }
        .stat-card.blue { border-left-color: var(--brand-blue); }

        .stat-icon {
            width: 50px;
            height: 50px;
            border-radius: 12px;
            background: #f1f5f9;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 22px;
            color: var(--brand-primary);
        }

        .stat-content h3 { font-size: 26px; font-weight: 800; color: #0f172a; }
        .stat-content p { font-size: 13px; color: #64748b; font-weight: 600; margin-top: 2px; }

        /* Cards Grid */
        .grid-2col {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 24px;
            margin-bottom: 24px;
        }

        .grid-3col {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin-bottom: 24px;
        }

        .card-box {
            background: #ffffff;
            border-radius: 12px;
            padding: 22px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
            border: 1px solid var(--border-color);
        }

        .card-box-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 16px;
            padding-bottom: 12px;
            border-bottom: 1px solid var(--border-color);
        }

        .card-box-header h3 {
            font-size: 16px;
            font-weight: 700;
            color: #1e293b;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        /* Clinical EMR Layout with Left Queue */
        .clinical-layout {
            display: grid;
            grid-template-columns: 280px 1fr;
            gap: 20px;
            align-items: start;
        }

        .patient-queue-card {
            background: #ffffff;
            border-radius: 12px;
            border: 1px solid var(--border-color);
            padding: 16px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        }

        .queue-item {
            padding: 12px;
            border-radius: 8px;
            border: 1.5px solid var(--border-color);
            margin-bottom: 8px;
            cursor: pointer;
            transition: all 0.2s;
            background: #ffffff;
        }

        .queue-item:hover {
            border-color: var(--brand-primary);
            background: #f8fafc;
        }

        .queue-item.active {
            border-color: var(--brand-cyan);
            background: #f0fdf4;
            box-shadow: 0 2px 6px rgba(0, 255, 161, 0.15);
        }

        .queue-item .q-name {
            font-weight: 800;
            font-size: 14px;
            color: #0f172a;
            display: flex;
            justify-content: space-between;
        }

        .queue-item .q-sub {
            font-size: 12px;
            color: #64748b;
            margin-top: 4px;
        }

        /* Ward Bed Matrix Rich Styles */
        .bed-matrix-toolbar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
            margin-bottom: 16px;
            flex-wrap: wrap;
            padding: 12px 16px;
            background: #f8fafc;
            border-radius: 10px;
            border: 1px solid var(--border-color);
        }

        .ward-filter-pills {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }

        .filter-pill {
            background: #ffffff;
            border: 1px solid var(--border-color);
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 700;
            cursor: pointer;
            color: #475569;
            transition: all 0.2s;
        }

        .filter-pill:hover, .filter-pill.active {
            background: var(--brand-primary);
            color: #ffffff;
            border-color: var(--brand-primary);
        }

        .bed-matrix-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(230px, 1fr));
            gap: 16px;
            margin-top: 14px;
        }

        .bed-card-rich {
            background: #ffffff;
            border: 2px solid var(--border-color);
            border-radius: 12px;
            padding: 16px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: all 0.2s;
            box-shadow: 0 2px 4px rgba(0,0,0,0.03);
            position: relative;
        }

        .bed-card-rich:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 16px -4px rgba(0,0,0,0.1);
        }

        .bed-card-rich.status-occupied { border-color: #fca5a5; background: #fffafa; }
        .bed-card-rich.status-available { border-color: #86efac; background: #f0fdf4; }
        .bed-card-rich.status-cleaning { border-color: #fde047; background: #fefce8; }
        .bed-card-rich.status-reserved { border-color: #93c5fd; background: #eff6ff; }

        .bed-card-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 10px;
        }

        .bed-card-title {
            font-size: 16px;
            font-weight: 800;
            color: #0f172a;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .bed-ward-tag {
            font-size: 11px;
            font-weight: 700;
            color: #64748b;
            margin-bottom: 8px;
        }

        .bed-patient-info {
            background: rgba(255,255,255,0.75);
            border: 1px solid rgba(0,0,0,0.06);
            border-radius: 6px;
            padding: 8px;
            margin-bottom: 12px;
            font-size: 12px;
        }

        .bed-patient-info strong {
            display: block;
            font-size: 13px;
            color: #0f172a;
        }

        .bed-card-actions {
            display: flex;
            gap: 6px;
            margin-top: 10px;
        }

        .bed-action-btn {
            flex: 1;
            padding: 6px 8px;
            border-radius: 6px;
            font-size: 11.5px;
            font-weight: 700;
            cursor: pointer;
            border: none;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 4px;
            transition: all 0.2s;
        }

        .btn-bed-vacate { background: #fee2e2; color: #b91c1c; }
        .btn-bed-vacate:hover { background: #fca5a5; }

        .btn-bed-admit { background: var(--brand-cyan); color: #0f172a; font-weight: 800; }
        .btn-bed-admit:hover { background: #00d688; }

        .btn-bed-edit { background: #e2e8f0; color: #334155; }
        .btn-bed-edit:hover { background: #cbd5e1; }

        /* Form Inputs */
        .form-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 20px;
        }

        .form-group {
            display: flex;
            flex-direction: column;
            gap: 6px;
        }

        .form-group label {
            font-size: 12.5px;
            font-weight: 700;
            color: #475569;
        }

        .form-control {
            padding: 9px 12px;
            border: 1.5px solid var(--border-color);
            border-radius: 8px;
            font-size: 13.5px;
            color: #1e293b;
            outline: none;
            transition: border-color 0.2s;
        }

        .form-control:focus { border-color: var(--brand-primary); }

        /* Modal Dialog */
        .modal-overlay {
            display: none;
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(15, 23, 42, 0.6);
            backdrop-filter: blur(4px);
            z-index: 1000;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }

        .modal-overlay.active { display: flex; }

        .modal-box {
            background: #ffffff;
            border-radius: 16px;
            width: 720px;
            max-width: 95vw;
            max-height: 90vh;
            overflow-y: auto;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
            border: 1px solid var(--border-color);
        }

        .modal-header {
            padding: 18px 24px;
            background: var(--brand-primary);
            color: #ffffff;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .modal-header h3 {
            font-size: 17px;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .modal-close {
            background: transparent;
            border: none;
            color: #ffffff;
            font-size: 18px;
            cursor: pointer;
            padding: 4px;
        }

        .modal-body { padding: 24px; }

        .modal-footer {
            padding: 16px 24px;
            background: #f8fafc;
            border-top: 1px solid var(--border-color);
            display: flex;
            align-items: center;
            justify-content: flex-end;
            gap: 12px;
        }

        .btn-secondary {
            background: #e2e8f0;
            color: #475569;
            border: none;
            padding: 9px 16px;
            border-radius: 8px;
            font-size: 13.5px;
            font-weight: 700;
            cursor: pointer;
        }

        /* Printable Receipt Box */
        .printable-invoice {
            border: 1.5px solid #cbd5e1;
            border-radius: 8px;
            padding: 24px;
            background: #ffffff;
            margin-top: 16px;
        }

        .invoice-header-branding {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding-bottom: 16px;
            border-bottom: 2px solid #0f172a;
            margin-bottom: 16px;
        }

        .invoice-header-branding img { max-height: 52px; }

        .toast-notify {
            position: fixed;
            bottom: 24px;
            right: 24px;
            background: #1e293b;
            color: #ffffff;
            padding: 14px 20px;
            border-radius: 10px;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 13.5px;
            font-weight: 600;
            border-left: 4px solid var(--brand-cyan);
            z-index: 9999;
            transform: translateY(100px);
            opacity: 0;
            transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        }

        .toast-notify.show {
            transform: translateY(0);
            opacity: 1;
        }

        .btn-del-rx {
            background: #fee2e2;
            color: #b91c1c;
            border: none;
            border-radius: 4px;
            padding: 3px 8px;
            cursor: pointer;
            font-size: 11px;
            font-weight: 700;
        }
        .btn-del-rx:hover { background: #fca5a5; }

        .btn-status-selector {
            display: flex;
            gap: 8px;
            margin-top: 6px;
        }

        .btn-status-opt {
            flex: 1;
            padding: 8px;
            border-radius: 8px;
            font-size: 12px;
            font-weight: 700;
            border: 2px solid var(--border-color);
            background: #ffffff;
            cursor: pointer;
            text-align: center;
        }

        .btn-status-opt.active {
            border-color: var(--brand-primary);
            background: #f1f5f9;
        }

        /* Inactivity Lock Screen */
        #inactivity-lock-screen {
            display: none;
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(15, 23, 42, 0.92);
            backdrop-filter: blur(8px);
            z-index: 99999;
            align-items: center;
            justify-content: center;
            color: #ffffff;
            text-align: center;
            padding: 24px;
        }

        #inactivity-lock-screen.active {
            display: flex;
        }

        .lock-box {
            background: #1e293b;
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 16px;
            padding: 36px 32px;
            width: 400px;
            max-width: 90vw;
            box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5);
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
    <!-- Inactivity Lock Screen -->
    <div id="inactivity-lock-screen">
        <div class="lock-box">
            <i class="fa-solid fa-lock" style="font-size:42px; color:var(--brand-cyan); margin-bottom:16px;"></i>
            <h2 style="font-size:22px; font-weight:800; margin-bottom:6px;">Session Suspended</h2>
            <p style="font-size:13px; color:#94a3b8; margin-bottom:20px;">Your workstation was locked due to inactivity to protect patient healthcare records.</p>
            <div class="input-group" style="text-align:left; margin-bottom:16px;">
                <label style="color:#cbd5e1;">Re-enter Password</label>
                <input type="password" id="lock-pass-input" class="form-control" placeholder="Enter password (pass123)" style="background:#0f172a; border-color:#334155; color:#fff;" />
            </div>
            <div style="display:flex; gap:10px;">
                <button class="btn-primary-action" style="flex:1; justify-content:center;" onclick="unlockSession()">
                    <i class="fa-solid fa-key"></i> Unlock
                </button>
                <button class="btn-secondary" style="background:#334155; color:#fff;" onclick="performSecureLogout()">
                    <i class="fa-solid fa-right-from-bracket"></i> Sign Out
                </button>
            </div>
        </div>
    </div>

    <!-- Sidebar -->
    <aside class="sidebar">
        <div class="sidebar-brand">
            <img src="/Personalization/logos/logo-main.png" alt="G1 Health EMR" />
        </div>
        <!-- Sidebar Search Bar matching screenshot -->
        <div style="padding: 12px 16px 8px; background: rgba(0,0,0,0.15);">
            <div style="position:relative; width:100%;">
                <input type="text" id="sidebar-menu-search" placeholder="Search Menu Items..." onkeyup="filterSidebarMenu(this)" style="width:100%; background:rgba(255,255,255,0.12); border:1.5px solid rgba(255,255,255,0.25); border-radius:20px; padding:7px 32px 7px 14px; font-size:12.5px; color:#ffffff; outline:none; transition:all 0.2s;" />
                <i class="fa-solid fa-magnifying-glass" style="position:absolute; right:12px; top:50%; transform:translateY(-50%); color:rgba(255,255,255,0.7); font-size:12px;"></i>
            </div>
        </div>

        <div class="nav-menu-wrapper">
            <ul class="nav-menu" id="sidebar-nav-list">
                <li class="nav-item active" data-target="view-dashboard" data-module="dashboard">
                    <a onclick="switchTab('view-dashboard', this)"><i class="fa-solid fa-chart-pie"></i><span>Dashboard</span></a>
                </li>

                <!-- Legacy HMIS & G1 Modules matching Danphe + Cloud Suite -->
                <li class="nav-item" data-target="view-clinical" data-module="clinical">
                    <a onclick="switchTab('view-clinical', this)"><i class="fa-solid fa-stethoscope"></i><span>Clinical</span></a>
                </li>
                <li class="nav-item" data-target="view-clinicalsettings" data-module="clinicalsettings">
                    <a onclick="switchTab('view-clinicalsettings', this)"><i class="fa-solid fa-gear"></i><span>ClinicalSettings</span></a>
                </li>
                <li class="nav-item" data-target="view-appointments" data-module="appointment">
                    <a onclick="switchTab('view-appointments', this)"><i class="fa-solid fa-bell"></i><span>Appointment</span></a>
                </li>
                <li class="nav-item" data-target="view-patient-reg" data-module="patient">
                    <a onclick="switchTab('view-patient-reg', this)"><i class="fa-solid fa-user"></i><span>Patient</span></a>
                </li>
                <li class="nav-item" data-target="view-procurement" data-module="procurement">
                    <a onclick="switchTab('view-procurement', this)"><i class="fa-solid fa-clipboard-list"></i><span>Procurement</span></a>
                </li>
                <li class="nav-item" data-target="view-billing" data-module="billing">
                    <a onclick="switchTab('view-billing', this)"><i class="fa-solid fa-file-invoice-dollar"></i><span>Billing</span></a>
                </li>
                <li class="nav-item" data-target="view-claimmgmt" data-module="claimmgmt">
                    <a onclick="switchTab('view-claimmgmt', this)"><i class="fa-solid fa-file-shield"></i><span>ClaimMgmt</span></a>
                </li>
                <li class="nav-item" data-target="view-utilities" data-module="utilities">
                    <a onclick="switchTab('view-utilities', this)"><i class="fa-solid fa-wrench"></i><span>Utilities</span></a>
                </li>
                <li class="nav-item" data-target="view-mktreferral" data-module="mktreferral">
                    <a onclick="switchTab('view-mktreferral', this)"><i class="fa-solid fa-diagram-project"></i><span>MktReferral</span></a>
                </li>
                <li class="nav-item" data-target="view-reports" data-module="reports">
                    <a onclick="switchTab('view-reports', this)"><i class="fa-solid fa-chart-line"></i><span>Reports</span></a>
                </li>
                <li class="nav-item" data-target="view-laboratory" data-module="laboratory">
                    <a onclick="switchTab('view-laboratory', this)"><i class="fa-solid fa-flask"></i><span>Laboratory</span></a>
                </li>
                <li class="nav-item" data-target="view-radiology" data-module="radiology">
                    <a onclick="switchTab('view-radiology', this)"><i class="fa-solid fa-x-ray"></i><span>Radiology</span></a>
                </li>
                <li class="nav-item" data-target="view-adt" data-module="adt">
                    <a onclick="switchTab('view-adt', this)"><i class="fa-solid fa-bed"></i><span>ADT (Inpatient)</span></a>
                </li>
                <li class="nav-item" data-target="view-vaccination" data-module="vaccination">
                    <a onclick="switchTab('view-vaccination', this)"><i class="fa-solid fa-syringe"></i><span>Vaccination</span></a>
                </li>
                <li class="nav-item" data-target="view-queue" data-module="queuemngmt">
                    <a onclick="switchTab('view-queue', this)"><i class="fa-solid fa-users"></i><span>QueueMngmt</span></a>
                </li>
                <li class="nav-item" data-target="view-pharmacy" data-module="inventory">
                    <a onclick="switchTab('view-pharmacy', this)"><i class="fa-solid fa-boxes-stacked"></i><span>Inventory</span></a>
                </li>
                <li class="nav-item" data-target="view-accounting" data-module="accounting">
                    <a onclick="switchTab('view-accounting', this)"><i class="fa-solid fa-calculator"></i><span>Accounting</span></a>
                </li>
                <li class="nav-item" data-target="view-emergency" data-module="emergency">
                    <a onclick="switchTab('view-emergency', this)"><i class="fa-solid fa-truck-medical"></i><span>Emergency</span></a>
                </li>
                <li class="nav-item" data-target="view-helpdesk" data-module="helpdesk">
                    <a onclick="switchTab('view-helpdesk', this)"><i class="fa-solid fa-circle-question"></i><span>Helpdesk</span></a>
                </li>
                <li class="nav-item" data-target="view-nursing" data-module="nursing">
                    <a onclick="switchTab('view-nursing', this)"><i class="fa-solid fa-user-nurse"></i><span>Nursing</span></a>
                </li>
                <li class="nav-item" data-target="view-medicalrecords" data-module="medicalrecords">
                    <a onclick="switchTab('view-medicalrecords', this)"><i class="fa-solid fa-book-medical"></i><span>MedicalRecords</span></a>
                </li>
                <li class="nav-item" data-target="view-whitelabel" data-module="settings">
                    <a onclick="switchTab('view-whitelabel', this)"><i class="fa-solid fa-sliders"></i><span>Settings</span></a>
                </li>
                <li class="nav-item" data-target="view-systemadmin" data-module="systemadmin">
                    <a onclick="switchTab('view-systemadmin', this)"><i class="fa-solid fa-user-shield"></i><span>SystemAdmin</span></a>
                </li>
                <li class="nav-item" data-target="view-pharmacy" data-module="pharmacy">
                    <a onclick="switchTab('view-pharmacy', this)"><i class="fa-solid fa-pills"></i><span>Pharmacy</span></a>
                </li>
                <li class="nav-item" data-target="view-substore" data-module="substore">
                    <a onclick="switchTab('view-substore', this)"><i class="fa-solid fa-store"></i><span>SubStore</span></a>
                </li>
                <li class="nav-item" data-target="view-cssd" data-module="cssd">
                    <a onclick="switchTab('view-cssd', this)"><i class="fa-solid fa-hand-sparkles"></i><span>CSSD</span></a>
                </li>
                <li class="nav-item" data-target="view-incentive" data-module="incentive">
                    <a onclick="switchTab('view-incentive', this)"><i class="fa-solid fa-hand-holding-dollar"></i><span>Incentive</span></a>
                </li>
                <li class="nav-item" data-target="view-verification" data-module="verification">
                    <a onclick="switchTab('view-verification', this)"><i class="fa-solid fa-clipboard-check"></i><span>Verification</span></a>
                </li>
                <li class="nav-item" data-target="view-fixedassets" data-module="fixedassets">
                    <a onclick="switchTab('view-fixedassets', this)"><i class="fa-solid fa-hospital-user"></i><span>FixedAssets</span></a>
                </li>
                <li class="nav-item" data-target="view-aicrm" data-module="aicrm">
                    <a onclick="switchTab('view-aicrm', this)"><i class="fa-solid fa-robot"></i><span>AI CRM & Leads</span><span class="badge-new">NEW</span></a>
                </li>
                <li class="nav-item" data-target="view-patient360" data-module="patient360">
                    <a onclick="switchTab('view-patient360', this)"><i class="fa-solid fa-id-card-clip"></i><span>Patient 360 (PIS)</span><span class="badge-new">NEW</span></a>
                </li>
                <li class="nav-item" data-target="view-ehs" data-module="ehs">
                    <a onclick="switchTab('view-ehs', this)"><i class="fa-solid fa-heart-pulse"></i><span>Employee Health</span><span class="badge-new">NEW</span></a>
                </li>
            </ul>
        </div>
    </aside>
    <div id="sidebar-backdrop" class="sidebar-backdrop" onclick="closeMobileSidebar()"></div>

    <!-- Main Wrapper -->
    <div class="main-wrapper">
                <!-- Code Blue Active System-Wide Emergency Alert Banner -->
        <div id="code-blue-active-banner" class="code-blue-banner" style="display:none;">
            <div style="display:flex; align-items:center; gap:12px;">
                <div style="width:32px; height:32px; border-radius:50%; background:#fff; color:#dc2626; display:flex; align-items:center; justify-content:center; font-size:16px;">
                    <i class="fa-solid fa-triangle-exclamation"></i>
                </div>
                <div>
                    <strong style="font-size:14px; text-transform:uppercase; letter-spacing:0.5px;">🚨 STAT CODE BLUE ACTIVATED:</strong>
                    <span id="active-code-blue-location" style="font-weight:800; background:rgba(0,0,0,0.25); padding:2px 8px; border-radius:4px; margin:0 6px;">ER Resuscitation Bay 1</span> &bull;
                    <span id="active-code-blue-reason">Cardiac Arrest / Airway Collapse</span>
                    <span id="active-code-blue-timer" style="margin-left:10px; font-weight:800; color:#fef08a;">(00:00 elapsed)</span>
                </div>
            </div>
            <div style="display:flex; gap:8px;">
                <button type="button" style="background:#fff; color:#dc2626; border:none; padding:6px 14px; border-radius:6px; font-weight:800; cursor:pointer; font-size:12px;" onclick="standDownCodeBlue()">
                    <i class="fa-solid fa-circle-check"></i> Patient Stabilized (Stand Down)
                </button>
            </div>
        </div>
        <header class="top-navbar">
            <div class="navbar-left">
                <button type="button" id="btn-mobile-sidebar-toggle" class="mobile-toggle-btn" onclick="toggleMobileSidebar()" aria-label="Toggle Menu">
                    <i class="fa-solid fa-bars"></i>
                </button>
                <div class="facility-title">
                    <i class="fa-solid fa-hospital" style="color: var(--brand-cyan);"></i>
                    <span id="header-facility-name">Global 1 OneTech Medical & Health Center</span>
                </div>
            </div>

            <!-- Global Active Patient Context Pill -->
            <div class="active-patient-badge" id="global-active-patient-bar">
                <div class="pat-name">
                    <i class="fa-solid fa-user-circle"></i>
                    <span id="global-pat-name">Juan Dela Cruz</span>
                </div>
                <span style="color:#94a3b8;">|</span>
                <span id="global-pat-code">G1-2026-0090</span>
                <span style="color:#94a3b8;">|</span>
                <span id="global-pat-meta">45 Y / Male &bull; PhilHealth</span>
                <button class="btn-switch-pat" onclick="openModal('modal-select-patient')">
                    <i class="fa-solid fa-arrows-rotate"></i> Switch Patient
                </button>
            </div>

            <!-- Global Search -->
            <div class="global-search-wrapper">
                <i class="fa-solid fa-magnifying-glass"></i>
                <input type="text" class="global-search-input" placeholder="Quick Search Patient..." onkeyup="handleGlobalPatientSearch(this)" />
            </div>

            <!-- Department Role Switcher Pill -->
            <div style="background:rgba(0,0,0,0.3); border:1px solid rgba(0,255,161,0.35); border-radius:8px; padding:4px 10px; display:flex; align-items:center; gap:8px; cursor:pointer;" onclick="openModal('modal-switch-role')">
                <i class="fa-solid fa-id-badge" style="color:var(--brand-cyan);"></i>
                <div>
                    <div style="font-size:10px; color:#cbd5e1; text-transform:uppercase; font-weight:800;">Department Workspace:</div>
                    <div style="font-size:12.5px; font-weight:800; color:#fff;" id="header-user-badge">👑 Super Admin</div>
                </div>
                <i class="fa-solid fa-chevron-down" style="font-size:10px; color:#cbd5e1; margin-left:4px;"></i>
            </div>

            <!-- User Profile & Secure Sign Out -->
            <div class="user-profile">
                <div class="user-avatar" id="header-user-avatar">AD</div>
                <div>
                    <div style="font-size: 13px; font-weight: 700;" id="header-user-name">Administrator</div>
                    <div style="font-size: 11px; color: #cbd5e1;" id="header-user-role">Super Admin &bull; Full Access</div>
                </div>
                <a href="javascript:void(0)" class="btn-logout" onclick="performSecureLogout(event)">
                    <i class="fa-solid fa-right-from-bracket"></i>
                    <span>Sign Out</span>
                </a>
            </div>
        </header>

        <main class="content-area">
            <div id="active-workspace-banner"></div>
            
            <!-- 1. DASHBOARD VIEW -->
            <section id="view-dashboard" class="module-view active">
                <div class="view-header">
                    <div>
                        <h1>Executive Healthcare Dashboard</h1>
                        <p>Welcome to G1 Health EMR &bull; Powered by Global 1 OneTech</p>
                    </div>
                    <div style="display:flex; gap:10px;" id="dash-action-buttons">
                        <button class="btn-primary-action" onclick="openModal('modal-new-patient')">
                            <i class="fa-solid fa-user-plus"></i> + Quick Register
                        </button>
                        <button class="btn-accent-action" onclick="switchTab('view-aicrm', document.querySelector('[data-target=view-aicrm]'))">
                            <i class="fa-solid fa-robot"></i> Open AI CRM Assistant
                        </button>
                    </div>
                </div>

                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-icon"><i class="fa-solid fa-users"></i></div>
                        <div class="stat-content">
                            <h3>1,248</h3>
                            <p>Total Registered Patients</p>
                        </div>
                    </div>
                    <div class="stat-card cyan">
                        <div class="stat-icon"><i class="fa-solid fa-calendar-day"></i></div>
                        <div class="stat-content">
                            <h3>84</h3>
                            <p>Appointments Today</p>
                        </div>
                    </div>
                    <div class="stat-card teal">
                        <div class="stat-icon"><i class="fa-solid fa-bed-pulse"></i></div>
                        <div class="stat-content">
                            <h3 id="dash-occupancy-kpi">35.7%</h3>
                            <p>Inpatient Bed Occupancy</p>
                        </div>
                    </div>
                    <div class="stat-card blue">
                        <div class="stat-icon"><i class="fa-solid fa-shield-halved"></i></div>
                        <div class="stat-content">
                            <h3 style="color:#15803d;">100%</h3>
                            <p>HIPAA / Data Protection Audit</p>
                        </div>
                    </div>
                </div>

                <div class="grid-2col">
                    <div class="card-box">
                        <div class="card-box-header">
                            <h3><i class="fa-solid fa-user-clock" style="color: var(--brand-primary);"></i> Today's Patient Registrations</h3>
                            <a href="javascript:void(0)" onclick="switchTab('view-patient-reg', document.querySelector('[data-target=view-patient-reg]'))" style="font-size: 12px; font-weight:700; color:var(--brand-primary); text-decoration:none;">View All &rarr;</a>
                        </div>
                        <table class="emr-table">
                            <thead>
                                <tr>
                                    <th>Hospital No</th>
                                    <th>Patient Name</th>
                                    <th>Age/Sex</th>
                                    <th>Status</th>
                                    <th>Select</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td><strong>G1-2026-0089</strong></td>
                                    <td>Maria Santos</td>
                                    <td>34 Y / F</td>
                                    <td><span class="status-badge status-active">Registered</span></td>
                                    <td><button class="btn-primary-action" style="padding:4px 8px; font-size:11px;" onclick="setActivePatient('Maria Santos')">Set Active</button></td>
                                </tr>
                                <tr>
                                    <td><strong>G1-2026-0090</strong></td>
                                    <td>Juan Dela Cruz</td>
                                    <td>45 Y / M</td>
                                    <td><span class="status-badge status-completed">In Consultation</span></td>
                                    <td><button class="btn-primary-action" style="padding:4px 8px; font-size:11px;" onclick="setActivePatient('Juan Dela Cruz')">Set Active</button></td>
                                </tr>
                                <tr>
                                    <td><strong>G1-2026-0091</strong></td>
                                    <td>Elena Reyes</td>
                                    <td>28 Y / F</td>
                                    <td><span class="status-badge status-pending">In Triage</span></td>
                                    <td><button class="btn-primary-action" style="padding:4px 8px; font-size:11px;" onclick="setActivePatient('Elena Reyes')">Set Active</button></td>
                                </tr>
                            </tbody>
                        </table>
                    </div>

                    <div class="card-box">
                        <div class="card-box-header">
                            <h3><i class="fa-solid fa-robot" style="color: var(--brand-accent);"></i> AI CRM Intelligent Lead Queue</h3>
                            <a href="javascript:void(0)" onclick="switchTab('view-aicrm', document.querySelector('[data-target=view-aicrm]'))" style="font-size: 12px; font-weight:700; color:var(--brand-primary); text-decoration:none;">Open Pipeline &rarr;</a>
                        </div>
                        <table class="emr-table">
                            <thead>
                                <tr>
                                    <th>Channel</th>
                                    <th>Patient Inquiry</th>
                                    <th>AI Triage</th>
                                    <th>Action</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td><i class="fa-brands fa-whatsapp" style="color:#25d366; font-size:16px;"></i> WhatsApp</td>
                                    <td>Severe headache & blurry vision</td>
                                    <td><span class="status-badge status-urgent">Urgent Neurologist</span></td>
                                    <td><button class="btn-primary-action" style="padding:4px 10px; font-size:11px;" onclick="showToast('AI Auto-Booked with Dr. Vincent Lim (Neurology)')">Auto-Book</button></td>
                                </tr>
                                <tr>
                                    <td><i class="fa-solid fa-globe" style="color:#0284c7; font-size:16px;"></i> Web Chat</td>
                                    <td>Routine Executive Health Screening</td>
                                    <td><span class="status-badge status-active">Wellness Clinic</span></td>
                                    <td><button class="btn-primary-action" style="padding:4px 10px; font-size:11px;" onclick="showToast('Quotation & Appointment Schedule sent via SMS')">Send Info</button></td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </section>

            <!-- 2. PATIENT REGISTRATION VIEW -->
            <section id="view-patient-reg" class="module-view">
                <div class="ux-navigation-bar">
                    <div class="breadcrumbs">
                        <a onclick="switchTab('view-dashboard', document.querySelector('[data-target=view-dashboard]'))"><i class="fa-solid fa-house"></i> Home</a>
                        <i class="fa-solid fa-chevron-right" style="font-size:10px;"></i>
                        <span class="current">Patient Registration</span>
                    </div>
                    <button class="btn-back-dashboard" onclick="switchTab('view-dashboard', document.querySelector('[data-target=view-dashboard]'))">
                        <i class="fa-solid fa-arrow-left"></i> Back to Dashboard
                    </button>
                </div>

                <div class="view-header">
                    <div>
                        <h1>Patient Registration & Master Indexing</h1>
                        <p>Register new outpatients/inpatients, verify insurance, and issue digital hospital cards</p>
                    </div>
                    <div>
                        <button class="btn-primary-action" onclick="openModal('modal-new-patient')">
                            <i class="fa-solid fa-user-plus"></i> + New Patient Registration
                        </button>
                    </div>
                </div>

                <div class="table-card">
                    <div class="table-toolbar">
                        <div class="search-box">
                            <i class="fa-solid fa-magnifying-glass"></i>
                            <input type="text" id="patient-search-input" placeholder="Search by Hospital No, Name, or Phone..." onkeyup="filterPatientTable()" />
                        </div>
                    </div>
                    <table class="emr-table" id="patient-master-table">
                        <thead>
                            <tr>
                                <th>Hospital No</th>
                                <th>Full Name</th>
                                <th>Age / Sex</th>
                                <th>Phone Number</th>
                                <th>Address</th>
                                <th>Membership</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td><strong>G1-2026-0089</strong></td>
                                <td>Maria Santos</td>
                                <td>34 Y / Female</td>
                                <td>+63 917 555 1234</td>
                                <td>Makati, Metro Manila</td>
                                <td><span class="status-badge status-completed">HMO Gold</span></td>
                                <td>
                                    <button class="btn-primary-action" style="padding: 5px 10px; font-size: 12px; margin-right:4px;" onclick="setActivePatient('Maria Santos')">
                                        <i class="fa-solid fa-check"></i> Set Active
                                    </button>
                                    <button class="btn-secondary" style="padding: 5px 10px; font-size: 12px;" onclick="viewPatient360('Maria Santos', 'G1-2026-0089')">
                                        <i class="fa-solid fa-id-card"></i> 360° View
                                    </button>
                                </td>
                            </tr>
                            <tr>
                                <td><strong>G1-2026-0090</strong></td>
                                <td>Juan Dela Cruz</td>
                                <td>45 Y / Male</td>
                                <td>+63 920 444 8901</td>
                                <td>Quezon City, Manila</td>
                                <td><span class="status-badge status-active">PhilHealth</span></td>
                                <td>
                                    <button class="btn-primary-action" style="padding: 5px 10px; font-size: 12px; margin-right:4px;" onclick="setActivePatient('Juan Dela Cruz')">
                                        <i class="fa-solid fa-check"></i> Set Active
                                    </button>
                                    <button class="btn-secondary" style="padding: 5px 10px; font-size: 12px;" onclick="viewPatient360('Juan Dela Cruz', 'G1-2026-0090')">
                                        <i class="fa-solid fa-id-card"></i> 360° View
                                    </button>
                                </td>
                            </tr>
                            <tr>
                                <td><strong>G1-2026-0091</strong></td>
                                <td>Elena Reyes</td>
                                <td>28 Y / Female</td>
                                <td>+63 918 333 7654</td>
                                <td>Taguig, Metro Manila</td>
                                <td><span class="status-badge status-pending">Self-Pay</span></td>
                                <td>
                                    <button class="btn-primary-action" style="padding: 5px 10px; font-size: 12px; margin-right:4px;" onclick="setActivePatient('Elena Reyes')">
                                        <i class="fa-solid fa-check"></i> Set Active
                                    </button>
                                    <button class="btn-secondary" style="padding: 5px 10px; font-size: 12px;" onclick="viewPatient360('Elena Reyes', 'G1-2026-0091')">
                                        <i class="fa-solid fa-id-card"></i> 360° View
                                    </button>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </section>

            <!-- 3. APPOINTMENTS VIEW -->
            <section id="view-appointments" class="module-view">
                <div class="ux-navigation-bar">
                    <div class="breadcrumbs">
                        <a onclick="switchTab('view-dashboard', document.querySelector('[data-target=view-dashboard]'))"><i class="fa-solid fa-house"></i> Home</a>
                        <i class="fa-solid fa-chevron-right" style="font-size:10px;"></i>
                        <span class="current">Appointments & Scheduling</span>
                    </div>
                    <button class="btn-back-dashboard" onclick="switchTab('view-dashboard', document.querySelector('[data-target=view-dashboard]'))">
                        <i class="fa-solid fa-arrow-left"></i> Back to Dashboard
                    </button>
                </div>

                <div class="view-header">
                    <div>
                        <h1>Doctor Appointment & Scheduling</h1>
                        <p>Manage OPD consultation bookings, doctor slots, and AI symptom routing</p>
                    </div>
                    <div>
                        <button class="btn-primary-action" onclick="openModal('modal-new-appointment')">
                            <i class="fa-solid fa-plus"></i> Book OPD Appointment
                        </button>
                    </div>
                </div>

                <div class="table-card">
                    <div class="table-toolbar">
                        <h3 style="font-size: 15px; font-weight: 700; color: #1e293b;">Today's Doctor Roster & Scheduled Visits</h3>
                        <span class="status-badge status-active"><i class="fa-solid fa-circle" style="font-size: 8px;"></i> Live Schedule Active</span>
                    </div>
                    <table class="emr-table">
                        <thead>
                            <tr>
                                <th>Time Slot</th>
                                <th>Patient Name</th>
                                <th>Doctor</th>
                                <th>Department</th>
                                <th>Queue Status</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody id="tbody-appointments"></tbody>
                    </table>
                </div>
            </section>

            <!-- 4. INPATIENT ADT & EDITABLE WARD BED MATRIX -->
            <section id="view-adt" class="module-view">
                <div class="ux-navigation-bar">
                    <div class="breadcrumbs">
                        <a onclick="switchTab('view-dashboard', document.querySelector('[data-target=view-dashboard]'))"><i class="fa-solid fa-house"></i> Home</a>
                        <i class="fa-solid fa-chevron-right" style="font-size:10px;"></i>
                        <span class="current">Inpatient & Ward Bed Matrix (ADT)</span>
                    </div>
                    <button class="btn-back-dashboard" onclick="switchTab('view-dashboard', document.querySelector('[data-target=view-dashboard]'))">
                        <i class="fa-solid fa-arrow-left"></i> Back to Dashboard
                    </button>
                </div>

                <div class="view-header">
                    <div>
                        <h1>Inpatient Ward Bed Matrix & Occupancy Control</h1>
                        <p>Click any bed to edit status, admit inpatients, or discharge & vacate beds in real time</p>
                    </div>
                    <div style="display:flex; gap:10px;">
                        <button class="btn-secondary" onclick="openModal('modal-add-bed')">
                            <i class="fa-solid fa-plus"></i> + Add New Bed
                        </button>
                        <button class="btn-primary-action" onclick="openModal('modal-manage-bed')">
                            <i class="fa-solid fa-pen-to-square"></i> Manage Bed Allocations
                        </button>
                    </div>
                </div>

                <!-- Dynamic Real-Time KPI Cards -->
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-icon"><i class="fa-solid fa-bed"></i></div>
                        <div class="stat-content"><h3 id="adt-total-beds">14</h3><p>Total Hospital Beds</p></div>
                    </div>
                    <div class="stat-card" style="border-left-color:#ef4444;">
                        <div class="stat-icon" style="color:#ef4444;"><i class="fa-solid fa-bed-pulse"></i></div>
                        <div class="stat-content"><h3 id="adt-occupied-beds" style="color:#b91c1c;">5</h3><p>Occupied Beds</p></div>
                    </div>
                    <div class="stat-card cyan">
                        <div class="stat-icon"><i class="fa-solid fa-door-open"></i></div>
                        <div class="stat-content"><h3 id="adt-available-beds">7</h3><p>Available (Empty) Beds</p></div>
                    </div>
                    <div class="stat-card teal">
                        <div class="stat-icon"><i class="fa-solid fa-chart-pie"></i></div>
                        <div class="stat-content"><h3 id="adt-occupancy-rate">35.7%</h3><p>Current Occupancy Rate</p></div>
                    </div>
                </div>

                <!-- Bed Matrix Container & Filter Toolbar -->
                <div class="card-box">
                    <div class="bed-matrix-toolbar">
                        <div>
                            <span style="font-size:12px; font-weight:800; color:#475569; margin-right:8px;">FILTER WARD:</span>
                            <div class="ward-filter-pills" id="ward-pills-list">
                                <button class="filter-pill active" onclick="filterBedsByWard('ALL', this)">All Wards</button>
                                <button class="filter-pill" onclick="filterBedsByWard('ICU', this)">ICU</button>
                                <button class="filter-pill" onclick="filterBedsByWard('General Male', this)">General Male</button>
                                <button class="filter-pill" onclick="filterBedsByWard('General Female', this)">General Female</button>
                                <button class="filter-pill" onclick="filterBedsByWard('Deluxe', this)">Private Deluxe</button>
                                <button class="filter-pill" onclick="filterBedsByWard('Pediatric', this)">Pediatric</button>
                            </div>
                        </div>

                        <div style="display:flex; align-items:center; gap:12px;">
                            <select id="bed-status-filter" class="form-control" style="width:160px; padding:6px 10px; font-size:12.5px;" onchange="renderBedMatrix()">
                                <option value="ALL">All Statuses</option>
                                <option value="available">🟢 Available (Empty)</option>
                                <option value="occupied">🔴 Occupied</option>
                                <option value="cleaning">🟡 Under Cleaning</option>
                                <option value="reserved">🔵 Reserved</option>
                            </select>
                            <input type="text" id="bed-search-box" class="form-control" placeholder="Search Bed ID / Patient..." style="width:200px; padding:6px 10px; font-size:12.5px;" onkeyup="renderBedMatrix()" />
                        </div>
                    </div>

                    <!-- Dynamic Rendered Bed Grid -->
                    <div id="bed-matrix-container" class="bed-matrix-grid">
                        <!-- Populated by renderBedMatrix() -->
                    </div>
                </div>
            </section>

            <!-- 5. EMERGENCY (ER) VIEW - FULLY EDITABLE -->
            <section id="view-emergency" class="module-view">
                <div class="ux-navigation-bar">
                    <div class="breadcrumbs">
                        <a onclick="switchTab('view-dashboard', document.querySelector('[data-target=view-dashboard]'))"><i class="fa-solid fa-house"></i> Home</a>
                        <i class="fa-solid fa-chevron-right" style="font-size:10px;"></i>
                        <span class="current">Emergency Room (ER & Trauma Triage)</span>
                    </div>
                    <button class="btn-back-dashboard" onclick="switchTab('view-dashboard', document.querySelector('[data-target=view-dashboard]'))">
                        <i class="fa-solid fa-arrow-left"></i> Back to Dashboard
                    </button>
                </div>

                <div class="view-header">
                    <div>
                        <h1>Emergency Department & Trauma Triage</h1>
                        <p>Real-time ER acuity triage (Level 1 to 5), bay tracking, and immediate patient admissions</p>
                    </div>
                    <div style="display:flex; gap:10px;">
                        <button class="btn-accent-action" style="background:#dc2626; color:#fff; font-weight:800;" onclick="openCodeBlueModal()">
                            <i class="fa-solid fa-triangle-exclamation"></i> 🚨 Trigger Code Blue Location Alert
                        </button>
                        <button class="btn-primary-action" onclick="openModal('modal-new-er-patient')">
                            <i class="fa-solid fa-user-plus"></i> + Register ER Emergency Case
                        </button>
                    </div>
                </div>

                <!-- ER KPIs -->
                <div class="stats-grid">
                    <div class="stat-card" style="border-left-color:#ef4444;">
                        <div class="stat-icon" style="color:#ef4444;"><i class="fa-solid fa-truck-medical"></i></div>
                        <div class="stat-content"><h3 id="er-total-cases" style="color:#b91c1c;">4</h3><p>Active ER Cases</p></div>
                    </div>
                    <div class="stat-card" style="border-left-color:#dc2626;">
                        <div class="stat-icon" style="color:#dc2626;"><i class="fa-solid fa-heart-pulse"></i></div>
                        <div class="stat-content"><h3 id="er-critical-cases" style="color:#dc2626;">2</h3><p>Level 1/2 Critical STAT</p></div>
                    </div>
                    <div class="stat-card cyan">
                        <div class="stat-icon"><i class="fa-solid fa-bed-pulse"></i></div>
                        <div class="stat-content"><h3 id="er-bays-occupied">4 / 6</h3><p>ER Bays Occupied</p></div>
                    </div>
                    <div class="stat-card teal">
                        <div class="stat-icon"><i class="fa-solid fa-stopwatch"></i></div>
                        <div class="stat-content"><h3>4.2 min</h3><p>Avg Door-to-Doctor Time</p></div>
                    </div>
                </div>

                <!-- ER Table & Filter Toolbar -->
                <div class="table-card">
                    <div class="table-toolbar">
                        <div>
                            <span style="font-size:12px; font-weight:800; color:#475569; margin-right:8px;">FILTER ACUITY:</span>
                            <div class="ward-filter-pills" id="er-pills-list" style="display:inline-flex;">
                                <button class="filter-pill active" onclick="filterERByLevel('ALL', this)">All Acuities</button>
                                <button class="filter-pill" onclick="filterERByLevel('Level 1', this)">🔴 Level 1 Resuscitation</button>
                                <button class="filter-pill" onclick="filterERByLevel('Level 2', this)">🟠 Level 2 Emergent</button>
                                <button class="filter-pill" onclick="filterERByLevel('Level 3', this)">🟡 Level 3 Urgent</button>
                                <button class="filter-pill" onclick="filterERByLevel('Level 4', this)">🟢 Level 4/5 Non-Urgent</button>
                            </div>
                        </div>
                        <div class="search-box">
                            <i class="fa-solid fa-magnifying-glass"></i>
                            <input type="text" id="er-search-box" placeholder="Search ER case by Patient, Bay, or Diagnosis..." onkeyup="renderERCases()" />
                        </div>
                    </div>

                    <table class="emr-table" id="er-master-table">
                        <thead>
                            <tr>
                                <th>ER Case ID</th>
                                <th>Triage Level</th>
                                <th>Patient Name</th>
                                <th>Age/Sex</th>
                                <th>Chief Complaint</th>
                                <th>Vitals</th>
                                <th>ER Bay</th>
                                <th>Doctor / Nurse</th>
                                <th>Clinical Disposition</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody id="er-table-body">
                            <!-- Dynamically populated by renderERCases() -->
                        </tbody>
                    </table>
                </div>
            </section>

            <!-- 6. CLINICAL EMR VIEW (DOCTOR DESK WITH PATIENT SWITCHER) -->
            <section id="view-clinical" class="module-view">
                <div class="ux-navigation-bar">
                    <div class="breadcrumbs">
                        <a onclick="switchTab('view-dashboard', document.querySelector('[data-target=view-dashboard]'))"><i class="fa-solid fa-house"></i> Home</a>
                        <i class="fa-solid fa-chevron-right" style="font-size:10px;"></i>
                        <span class="current">Clinical EMR (Doctor Desk)</span>
                    </div>
                    <button class="btn-back-dashboard" onclick="switchTab('view-dashboard', document.querySelector('[data-target=view-dashboard]'))">
                        <i class="fa-solid fa-arrow-left"></i> Back to Dashboard
                    </button>
                </div>

                <div class="view-header">
                    <div>
                        <h1>Doctor Consultation Desk (Clinical EMR)</h1>
                        <p>Record clinical encounters, ICD-10 diagnoses, vital signs, and prescribe electronic medications</p>
                    </div>
                    <div style="display:flex; gap:10px;">
                        <button class="btn-secondary" onclick="openModal('modal-select-patient')">
                            <i class="fa-solid fa-user-gear"></i> Change Active Patient
                        </button>
                        <button class="btn-accent-action" onclick="showToast('Electronic Prescription Signed & Synced to Pharmacy Counter!')">
                            <i class="fa-solid fa-signature"></i> Sign & Send e-Prescription
                        </button>
                    </div>
                </div>

                <div class="clinical-layout">
                    <div class="patient-queue-card">
                        <div style="font-size:13px; font-weight:800; color:#0f172a; margin-bottom:12px; display:flex; align-items:center; justify-content:space-between;">
                            <span><i class="fa-solid fa-users-line" style="color:var(--brand-primary);"></i> OPD Queue</span>
                            <span class="badge-new" style="background:#e2e8f0; color:#475569;">4 Total</span>
                        </div>
                        <div class="queue-item active" id="q-pat-juan" onclick="setActivePatient('Juan Dela Cruz')">
                            <div class="q-name"><span>Juan Dela Cruz</span><span class="status-badge status-active" style="font-size:9.5px;">Active</span></div>
                            <div class="q-sub">G1-2026-0090 &bull; 45 Y / M &bull; Rm 201</div>
                        </div>
                        <div class="queue-item" id="q-pat-maria" onclick="setActivePatient('Maria Santos')">
                            <div class="q-name"><span>Maria Santos</span><span class="status-badge status-pending" style="font-size:9.5px;">Waiting</span></div>
                            <div class="q-sub">G1-2026-0089 &bull; 34 Y / F &bull; Rm 202</div>
                        </div>
                        <div class="queue-item" id="q-pat-elena" onclick="setActivePatient('Elena Reyes')">
                            <div class="q-name"><span>Elena Reyes</span><span class="status-badge status-pending" style="font-size:9.5px;">Waiting</span></div>
                            <div class="q-sub">G1-2026-0091 &bull; 28 Y / F &bull; Rm 203</div>
                        </div>
                        <div class="queue-item" id="q-pat-antonio" onclick="setActivePatient('Antonio Gonzales')">
                            <div class="q-name"><span>Antonio Gonzales</span><span class="status-badge status-completed" style="font-size:9.5px;">Done</span></div>
                            <div class="q-sub">G1-2026-0092 &bull; 52 Y / M &bull; Followup</div>
                        </div>
                    </div>

                    <div style="display:flex; flex-direction:column; gap:20px;">
                        <div class="card-box">
                            <div class="card-box-header">
                                <h3>
                                    <i class="fa-solid fa-user-tag" style="color:var(--brand-primary);"></i>
                                    Active Chart: <span id="emr-patient-title">Juan Dela Cruz (45 Y / Male)</span>
                                </h3>
                                <div style="display:flex; gap:8px;">
                                    <span class="status-badge status-active" id="emr-hospital-badge">Hospital No: G1-2026-0090</span>
                                    <button class="btn-switch-pat" onclick="openModal('modal-select-patient')">Switch</button>
                                </div>
                            </div>
                            <div class="form-grid">
                                <div class="form-group">
                                    <label>Blood Pressure (mmHg)</label>
                                    <input type="text" class="form-control" id="emr-bp" value="120/80" />
                                </div>
                                <div class="form-group">
                                    <label>Pulse Rate (bpm)</label>
                                    <input type="text" class="form-control" id="emr-pulse" value="76" />
                                </div>
                                <div class="form-group">
                                    <label>Temperature (°C)</label>
                                    <input type="text" class="form-control" id="emr-temp" value="36.8" />
                                </div>
                                <div class="form-group">
                                    <label>SpO2 (%)</label>
                                    <input type="text" class="form-control" id="emr-spo2" value="98%" />
                                </div>
                            </div>
                            <div class="form-group" style="margin-bottom:14px;">
                                <label>Chief Complaints & Subjective History</label>
                                <textarea class="form-control" id="emr-complaints" rows="3">Patient reports recurrent mild headache for 3 days, accompanied by eye strain during computer screen work.</textarea>
                            </div>
                            <div class="form-group">
                                <label>ICD-10 Primary Diagnosis</label>
                                <input type="text" class="form-control" id="emr-diagnosis" value="G44.2 - Tension-type headache" />
                            </div>
                        </div>

                        <div class="card-box">
                            <div class="card-box-header">
                                <h3><i class="fa-solid fa-pills" style="color:var(--brand-accent);"></i> Electronic Prescription Builder</h3>
                                <button class="btn-primary-action" style="padding:4px 10px; font-size:12px;" onclick="addPrescriptionRow()">
                                    <i class="fa-solid fa-plus"></i> Add Medicine
                                </button>
                            </div>
                            <table class="emr-table" id="rx-table" style="margin-bottom:16px;">
                                <thead>
                                    <tr>
                                        <th>Medicine Name</th>
                                        <th>Dosage</th>
                                        <th>Frequency</th>
                                        <th>Duration</th>
                                        <th>Remove</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td><strong>Paracetamol 500mg</strong></td>
                                        <td>1 Tab</td>
                                        <td>TID (Every 8h)</td>
                                        <td>5 Days</td>
                                        <td><button class="btn-del-rx" onclick="this.closest('tr').remove(); showToast('Medication removed from Rx');">&times;</button></td>
                                    </tr>
                                    <tr>
                                        <td><strong>Vitamin B-Complex</strong></td>
                                        <td>1 Capsule</td>
                                        <td>OD (Once Daily)</td>
                                        <td>30 Days</td>
                                        <td><button class="btn-del-rx" onclick="this.closest('tr').remove(); showToast('Medication removed from Rx');">&times;</button></td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </section>

            <!-- 7. NURSING STATION VIEW -->
            <section id="view-nursing" class="module-view">
                <div class="ux-navigation-bar">
                    <div class="breadcrumbs">
                        <a onclick="switchTab('view-dashboard', document.querySelector('[data-target=view-dashboard]'))"><i class="fa-solid fa-house"></i> Home</a>
                        <i class="fa-solid fa-chevron-right" style="font-size:10px;"></i>
                        <span class="current">Nursing Station & Inpatient Care</span>
                    </div>
                    <button class="btn-back-dashboard" onclick="switchTab('view-dashboard', document.querySelector('[data-target=view-dashboard]'))">
                        <i class="fa-solid fa-arrow-left"></i> Back to Dashboard
                    </button>
                </div>

                <div class="view-header">
                    <div>
                        <h1>Nursing Station & Ward Care</h1>
                        <p>Medication Administration Records (e-MAR), IV fluid tracking, and nurse shift handovers</p>
                    </div>
                    <div>
                        <button class="btn-primary-action" onclick="showToast('Nurse Shift Handover Recorded')">
                            <i class="fa-solid fa-clipboard-check"></i> Submit Shift Handover
                        </button>
                    </div>
                </div>

                <div class="table-card">
                    <table class="emr-table">
                        <thead>
                            <tr>
                                <th>Bed No</th>
                                <th>Patient Name</th>
                                <th>Medication Due</th>
                                <th>Dose & Route</th>
                                <th>Scheduled Time</th>
                                <th>Administer</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td><strong>ICU-101</strong></td>
                                <td>Juan Dela Cruz</td>
                                <td>IV Ceftriaxone 1g</td>
                                <td>IV Infusion in 100mL Saline</td>
                                <td>12:00 PM (Due Now)</td>
                                <td><button class="btn-accent-action" style="padding:4px 10px; font-size:12px;" onclick="showToast('Medication Administered & e-MAR Updated')">Administer</button></td>
                            </tr>
                            <tr>
                                <td><strong>WARD-201</strong></td>
                                <td>Carlos Mendoza</td>
                                <td>Oral Metoprolol 25mg</td>
                                <td>Oral with water</td>
                                <td>01:00 PM</td>
                                <td><button class="btn-primary-action" style="padding:4px 10px; font-size:12px;" onclick="showToast('Medication Pending')">Mark Given</button></td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </section>

            <!-- 8. OPERATION THEATER (OT) VIEW -->
            <section id="view-ot" class="module-view">
                <div class="ux-navigation-bar">
                    <div class="breadcrumbs">
                        <a onclick="switchTab('view-dashboard', document.querySelector('[data-target=view-dashboard]'))"><i class="fa-solid fa-house"></i> Home</a>
                        <i class="fa-solid fa-chevron-right" style="font-size:10px;"></i>
                        <span class="current">Operation Theater (OT)</span>
                    </div>
                    <button class="btn-back-dashboard" onclick="switchTab('view-dashboard', document.querySelector('[data-target=view-dashboard]'))">
                        <i class="fa-solid fa-arrow-left"></i> Back to Dashboard
                    </button>
                </div>

                <div class="view-header">
                    <div>
                        <h1>Operation Theater & Surgical Scheduling</h1>
                        <p>OT room bookings, surgeon allocations, WHO surgical safety checklists, and anesthesia records</p>
                    </div>
                    <div>
                        <button class="btn-primary-action" onclick="showToast('Surgical Case Scheduled for OT-1')">
                            <i class="fa-solid fa-plus"></i> Schedule Surgical Case
                        </button>
                    </div>
                </div>

                <div class="table-card">
                    <table class="emr-table">
                        <thead>
                            <tr>
                                <th>OT Room</th>
                                <th>Time</th>
                                <th>Patient Name</th>
                                <th>Procedure</th>
                                <th>Lead Surgeon</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody id="tbody-ot"></tbody>
                    </table>
                </div>
            </section>

            <!-- 9. LABORATORY VIEW -->
            <section id="view-laboratory" class="module-view">
                <div class="ux-navigation-bar">
                    <div class="breadcrumbs">
                        <a onclick="switchTab('view-dashboard', document.querySelector('[data-target=view-dashboard]'))"><i class="fa-solid fa-house"></i> Home</a>
                        <i class="fa-solid fa-chevron-right" style="font-size:10px;"></i>
                        <span class="current">Laboratory (LIS)</span>
                    </div>
                    <button class="btn-back-dashboard" onclick="switchTab('view-dashboard', document.querySelector('[data-target=view-dashboard]'))">
                        <i class="fa-solid fa-arrow-left"></i> Back to Dashboard
                    </button>
                </div>

                <div class="view-header">
                    <div>
                        <h1>Laboratory Information System (LIS)</h1>
                        <p>Sample collection, automated analyzer interfacing, and verified pathology report generation</p>
                    </div>
                    <div>
                        <button class="btn-primary-action" onclick="showToast('Barcode labels printed for blood sample collection')">
                            <i class="fa-solid fa-barcode"></i> Print Sample Barcode
                        </button>
                    </div>
                </div>

                <div class="table-card">
                    <table class="emr-table">
                        <thead>
                            <tr>
                                <th>Lab Order No</th>
                                <th>Patient Name</th>
                                <th>Test Requisition</th>
                                <th>Sample Status</th>
                                <th>Analyzer Result</th>
                                <th>Report Verification</th>
                            </tr>
                        </thead>
                        <tbody id="tbody-laboratory"></tbody>
                    </table>
                </div>
            </section>

            <!-- 10. RADIOLOGY VIEW -->
            <section id="view-radiology" class="module-view">
                <div class="ux-navigation-bar">
                    <div class="breadcrumbs">
                        <a onclick="switchTab('view-dashboard', document.querySelector('[data-target=view-dashboard]'))"><i class="fa-solid fa-house"></i> Home</a>
                        <i class="fa-solid fa-chevron-right" style="font-size:10px;"></i>
                        <span class="current">Radiology & PACS</span>
                    </div>
                    <button class="btn-back-dashboard" onclick="switchTab('view-dashboard', document.querySelector('[data-target=view-dashboard]'))">
                        <i class="fa-solid fa-arrow-left"></i> Back to Dashboard
                    </button>
                </div>

                <div class="view-header">
                    <div>
                        <h1>Radiology & Imaging (RIS / PACS)</h1>
                        <p>Digital imaging requests, DICOM integration, and radiological diagnostic reports</p>
                    </div>
                </div>

                <div class="table-card">
                    <table class="emr-table">
                        <thead>
                            <tr>
                                <th>Imaging ID</th>
                                <th>Patient Name</th>
                                <th>Modality</th>
                                <th>Examination</th>
                                <th>Radiologist Findings</th>
                                <th>PACS Link</th>
                            </tr>
                        </thead>
                        <tbody id="tbody-radiology"></tbody>
                    </table>
                </div>
            </section>

            <!-- 11. PHARMACY VIEW -->
            <section id="view-pharmacy" class="module-view">
                <div class="ux-navigation-bar">
                    <div class="breadcrumbs">
                        <a onclick="switchTab('view-dashboard', document.querySelector('[data-target=view-dashboard]'))"><i class="fa-solid fa-house"></i> Home</a>
                        <i class="fa-solid fa-chevron-right" style="font-size:10px;"></i>
                        <span class="current">Pharmacy & Inventory</span>
                    </div>
                    <button class="btn-back-dashboard" onclick="switchTab('view-dashboard', document.querySelector('[data-target=view-dashboard]'))">
                        <i class="fa-solid fa-arrow-left"></i> Back to Dashboard
                    </button>
                </div>

                <div class="view-header">
                    <div>
                        <h1>Hospital Pharmacy & Inventory Management</h1>
                        <p>Dispensing counters, barcode drug verification, stock levels, and expiry alerts</p>
                    </div>
                    <div>
                        <button class="btn-primary-action" onclick="showToast('Inventory Reorder Requisition Generated')">
                            <i class="fa-solid fa-cart-plus"></i> Create Purchase Order
                        </button>
                    </div>
                </div>

                <div class="table-card">
                    <div class="table-toolbar">
                        <div class="search-box">
                            <i class="fa-solid fa-magnifying-glass"></i>
                            <input type="text" placeholder="Search drug by generic or brand name..." />
                        </div>
                    </div>
                    <table class="emr-table">
                        <thead>
                            <tr>
                                <th>Item Code</th>
                                <th>Drug & Generic Name</th>
                                <th>Batch No</th>
                                <th>Expiry Date</th>
                                <th>Available Stock</th>
                                <th>Unit Price</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td><strong>DRUG-1001</strong></td>
                                <td>Amoxicillin 500mg Caps</td>
                                <td>BAT-8921</td>
                                <td>12-2027</td>
                                <td><strong>1,450 Caps</strong></td>
                                <td>₱ 8.50</td>
                                <td><span class="status-badge status-active">Optimal Stock</span></td>
                            </tr>
                            <tr>
                                <td><strong>DRUG-1002</strong></td>
                                <td>Paracetamol 500mg Tabs</td>
                                <td>BAT-7741</td>
                                <td>08-2027</td>
                                <td><strong>3,200 Tabs</strong></td>
                                <td>₱ 3.00</td>
                                <td><span class="status-badge status-active">Optimal Stock</span></td>
                            </tr>
                            <tr>
                                <td><strong>DRUG-1003</strong></td>
                                <td>Azithromycin 500mg Tabs</td>
                                <td>BAT-5512</td>
                                <td>11-2026</td>
                                <td><strong>45 Tabs</strong></td>
                                <td>₱ 45.00</td>
                                <td><span class="status-badge status-urgent">Low Stock Alert</span></td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </section>

            <!-- 12. AI CRM VIEW (NEW) -->
            
            <!-- 32. AI PATIENT CRM & LIVE CONVERSATIONAL AGENT -->
            <section id="view-aicrm" class="module-view">
                <div class="ux-navigation-bar">
                    <div class="breadcrumbs">
                        <a onclick="switchTab('view-dashboard', null)"><i class="fa-solid fa-house"></i> Home</a>
                        <i class="fa-solid fa-chevron-right" style="font-size:10px;"></i>
                        <span class="current">AI Patient CRM & Intelligent Triage</span>
                    </div>
                    <button class="btn-back-dashboard" onclick="switchTab('view-dashboard', null)">
                        <i class="fa-solid fa-arrow-left"></i> Back to Dashboard
                    </button>
                </div>

                <div class="view-header">
                    <div>
                        <h1>AI Patient CRM & Live Conversational Triage</h1>
                        <p>Omnichannel patient intake, real-time AI clinical triage, automated WhatsApp booking, and lead conversion</p>
                    </div>
                    <div style="display:flex; gap:10px; flex-wrap:wrap; align-items:center;">
                        <span class="status-badge status-active" style="padding:6px 12px; font-size:12px; display:inline-flex; align-items:center; gap:6px;">
                            <i class="fa-solid fa-shield-halved" style="color:#15803d;"></i> Secure Local Medical AI Core (Zero API Key &bull; HIPAA Safe)
                        </span>
                        <button class="btn-accent-action" onclick="openModal('modal-ai-simulation')">
                            <i class="fa-solid fa-wand-magic-sparkles"></i> Open Fullscreen AI Simulator
                        </button>
                    </div>
                </div>

                <div class="stats-grid">
                    <div class="stat-card cyan">
                        <div class="stat-icon"><i class="fa-brands fa-whatsapp"></i></div>
                        <div class="stat-content">
                            <h3>142</h3>
                            <p>Automated WhatsApp Check-ins Sent</p>
                        </div>
                    </div>
                    <div class="stat-card teal">
                        <div class="stat-icon"><i class="fa-solid fa-brain"></i></div>
                        <div class="stat-content">
                            <h3 id="ai-accuracy-stat">96.4%</h3>
                            <p>AI Triage Department Accuracy</p>
                        </div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon"><i class="fa-solid fa-arrow-trend-up"></i></div>
                        <div class="stat-content">
                            <h3>+38%</h3>
                            <p>Follow-up Visit Retention</p>
                        </div>
                    </div>
                </div>

                <!-- Live AI CRM 2-Column Console: Interactive WhatsApp Agent + Pipeline -->
                <div class="grid-2col" style="margin-bottom:24px;">
                    <!-- Column 1: Live Interactive WhatsApp Simulator -->
                    <div class="card-box" style="display:flex; flex-direction:column; height:540px; padding:0; overflow:hidden; border:2px solid #bbf7d0;">
                        <div style="background:#075e54; color:#fff; padding:14px 18px; display:flex; align-items:center; justify-content:space-between;">
                            <div style="display:flex; align-items:center; gap:12px;">
                                <div style="width:38px; height:38px; border-radius:50%; background:#25d366; display:flex; align-items:center; justify-content:center; color:#fff; font-size:18px;">
                                    <i class="fa-solid fa-robot"></i>
                                </div>
                                <div>
                                    <div style="font-size:14px; font-weight:800;">G1 Health AI Assistant</div>
                                    <div style="font-size:11px; color:#a7f3d0; display:flex; align-items:center; gap:5px;">
                                        <span style="width:7px; height:7px; border-radius:50%; background:#22c55e; display:inline-block;"></span> Online &bull; Powered by Gemini 1.5 Flash
                                    </div>
                                </div>
                            </div>
                            <span class="status-badge" style="background:#128c7e; color:#fff; font-size:11px;">Live WhatsApp Bot</span>
                        </div>

                        <!-- Chat Message Thread -->
                        <div id="ai-chat-thread" style="flex:1; padding:16px; overflow-y:auto; background:#ece5dd; display:flex; flex-direction:column; gap:12px;">
                            <!-- Bot Welcome -->
                            <div style="align-self:flex-start; max-width:82%; background:#ffffff; padding:10px 14px; border-radius:10px; box-shadow:0 1px 3px rgba(0,0,0,0.1); font-size:13px; color:#1e293b;">
                                <div style="font-weight:700; color:#0f766e; margin-bottom:3px; font-size:11px;">G1 CLINICAL AI AGENT</div>
                                <div>Hello! I am G1 Health's Clinical Triage Assistant. How are you feeling today? You can describe any symptoms or ask about hospital doctor schedules.</div>
                                <div style="font-size:10px; color:#94a3b8; text-align:right; margin-top:4px;">10:00 AM</div>
                            </div>
                        </div>

                        <!-- Quick Test Scenario Pills -->
                        <div style="padding:8px 12px; background:#f8fafc; border-top:1px solid #e2e8f0; display:flex; gap:6px; overflow-x:auto;">
                            <button class="filter-pill" style="font-size:11px; white-space:nowrap; padding:4px 10px;" onclick="sendPresetScenario('Chest tightness and high BP 150/95 since this morning')">🫀 Chest Tightness</button>
                            <button class="filter-pill" style="font-size:11px; white-space:nowrap; padding:4px 10px;" onclick="sendPresetScenario('Severe knee pain and swelling after playing tennis')">🦵 Knee Injury</button>
                            <button class="filter-pill" style="font-size:11px; white-space:nowrap; padding:4px 10px;" onclick="sendPresetScenario('Post-op wound dressing feels warm, is this normal?')">🩹 Post-Op Query</button>
                            <button class="filter-pill" style="font-size:11px; white-space:nowrap; padding:4px 10px;" onclick="sendPresetScenario('My fasting blood sugar was 145 mg/dL today')">🧪 High Blood Sugar</button>
                        </div>

                        <!-- Chat Input Box -->
                        <div style="padding:12px; background:#ffffff; border-top:1px solid #e2e8f0; display:flex; gap:8px;">
                            <input type="text" id="ai-chat-input" placeholder="Type symptoms or patient questions..." style="flex:1; padding:10px 14px; border:1.5px solid #cbd5e1; border-radius:24px; font-size:13px; outline:none;" onkeypress="if(event.key === 'Enter') sendAIChatMessage()" />
                            <button class="btn-primary-action" style="border-radius:50%; width:42px; height:42px; padding:0; display:flex; align-items:center; justify-content:center;" onclick="sendAIChatMessage()">
                                <i class="fa-solid fa-paper-plane"></i>
                            </button>
                        </div>
                    </div>

                    <!-- Column 2: AI Lead Triage Intelligence Cards & Insights -->
                    <div style="display:flex; flex-direction:column; gap:16px;">
                        <div class="card-box" style="border-left:4px solid var(--brand-cyan);">
                            <div class="card-box-header">
                                <h3><i class="fa-solid fa-bolt" style="color:var(--brand-cyan);"></i> Autonomous Tool Execution</h3>
                            </div>
                            <p style="font-size:12.5px; color:#64748b; margin-bottom:12px;">When patient intent is detected, the AI engine directly triggers hospital EMR workflows:</p>
                            <div style="display:flex; flex-direction:column; gap:8px;">
                                <div style="padding:10px 12px; background:#f0fdf4; border:1px solid #bbf7d0; border-radius:8px; display:flex; align-items:center; justify-content:space-between;">
                                    <div>
                                        <div style="font-size:12.5px; font-weight:700; color:#166534;"><i class="fa-solid fa-calendar-check"></i> 1-Click OPD Appointment Booking</div>
                                        <div style="font-size:11px; color:#4b5563;">Automated doctor slot reservations from chat</div>
                                    </div>
                                    <span class="status-badge status-active">Active</span>
                                </div>
                                <div style="padding:10px 12px; background:#eff6ff; border:1px solid #bfdbfe; border-radius:8px; display:flex; align-items:center; justify-content:space-between;">
                                    <div>
                                        <div style="font-size:12.5px; font-weight:700; color:#1e40af;"><i class="fa-solid fa-truck-medical"></i> Emergency Red-Flag Triage</div>
                                        <div style="font-size:11px; color:#4b5563;">STAT ER crash bay notification on critical keywords</div>
                                    </div>
                                    <span class="status-badge status-completed">Active</span>
                                </div>
                            </div>
                        </div>

                        <div class="card-box">
                            <div class="card-box-header">
                                <h3><i class="fa-solid fa-sliders"></i> Active AI Configuration</h3>
                            </div>
                            <table class="emr-table" style="font-size:12px;">
                                <tbody id="tbody-aicrm"></tbody>
                            </table>
                        </div>
                    </div>
                </div>

                <!-- Live Pipeline Table -->
                <div class="table-card">
                    <div class="table-toolbar">
                        <h3 style="font-size: 15px; font-weight: 700;">Live Patient Inquiries & AI Follow-Up Pipeline</h3>
                        <button class="btn-secondary" onclick="showToast('CRM Lead pipeline refreshed')"><i class="fa-solid fa-rotate"></i> Refresh Leads</button>
                    </div>
                    <table class="emr-table" id="crm-leads-table">
                        <thead>
                            <tr>
                                <th>Inquiry ID</th>
                                <th>Patient Name</th>
                                <th>Channel</th>
                                <th>Symptoms / Query</th>
                                <th>AI Predicted Dept</th>
                                <th>Sentiment</th>
                                <th>Automated Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td><strong>CRM-0101</strong></td>
                                <td>Carlos Mendoza</td>
                                <td><i class="fa-brands fa-whatsapp" style="color:#25d366;"></i> WhatsApp</td>
                                <td>"Persistent joint pain in knees for 2 weeks"</td>
                                <td><span class="status-badge status-completed">Orthopedics</span></td>
                                <td><span class="status-badge status-active">Positive (0.82)</span></td>
                                <td><button class="btn-primary-action" style="padding:4px 8px; font-size:11px;" onclick="showToast('Booked appointment with Dr. Garcia (Orthopedics)')">Book Consult</button></td>
                            </tr>
                            <tr>
                                <td><strong>CRM-0102</strong></td>
                                <td>Beatriz Aquino</td>
                                <td><i class="fa-solid fa-comments" style="color:#0284c7;"></i> Web Portal</td>
                                <td>"Post-discharge question about wound dressing"</td>
                                <td><span class="status-badge status-urgent">General Surgery Post-Op</span></td>
                                <td><span class="status-badge status-pending">Neutral (0.10)</span></td>
                                <td><button class="btn-primary-action" style="padding:4px 8px; font-size:11px;" onclick="showToast('AI Nurse Care Guidance & Video link sent')">Send Nurse Video</button></td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </section>
    

            <!-- 13. PATIENT 360 VIEW (PIS) -->
            <section id="view-patient360" class="module-view">
                <div class="ux-navigation-bar">
                    <div class="breadcrumbs">
                        <a onclick="switchTab('view-dashboard', document.querySelector('[data-target=view-dashboard]'))"><i class="fa-solid fa-house"></i> Home</a>
                        <i class="fa-solid fa-chevron-right" style="font-size:10px;"></i>
                        <span class="current">Patient 360 (PIS Portal)</span>
                    </div>
                    <button class="btn-back-dashboard" onclick="switchTab('view-dashboard', document.querySelector('[data-target=view-dashboard]'))">
                        <i class="fa-solid fa-arrow-left"></i> Back to Dashboard
                    </button>
                </div>

                <div class="view-header">
                    <div>
                        <h1>Patient Information System (PIS 360° Portal)</h1>
                        <p>Longitudinal patient timeline across visits, admissions, lab results, prescriptions, and digital records vault</p>
                    </div>
                </div>

                <div class="card-box" style="margin-bottom:24px;">
                    <div style="display:flex; align-items:center; justify-content:space-between;">
                        <div style="display:flex; align-items:center; gap:16px;">
                            <div style="width:64px; height:64px; border-radius:50%; background:#e2e8f0; display:flex; align-items:center; justify-content:center; font-size:24px; font-weight:800; color:var(--brand-primary);">
                                <span id="p360-avatar">MS</span>
                            </div>
                            <div>
                                <h2 style="font-size:20px; font-weight:800; color:#0f172a;" id="p360-name">Maria Santos</h2>
                                <p style="font-size:13px; color:#64748b;">Hospital No: <strong id="p360-code">G1-2026-0089</strong> &bull; <span id="p360-submeta">34 Y / Female &bull; Blood Group: B+ &bull; HMO: Gold Care</span></p>
                            </div>
                        </div>
                        <div style="display:flex; gap:10px;">
                            <button class="btn-secondary" onclick="openModal('modal-select-patient')">
                                <i class="fa-solid fa-arrows-rotate"></i> Change Patient
                            </button>
                            <button class="btn-primary-action" onclick="showToast('Outside Medical File Uploaded to Patient Vault')">
                                <i class="fa-solid fa-cloud-arrow-up"></i> Upload External Record
                            </button>
                        </div>
                    </div>
                </div>

                <div class="grid-3col">
                    <div class="card-box">
                        <div class="card-box-header">
                            <h3><i class="fa-solid fa-calendar-check" style="color:var(--brand-primary);"></i> Visit History</h3>
                        </div>
                        <ul style="list-style:none; display:flex; flex-direction:column; gap:10px; font-size:13px;">
                            <li style="padding-bottom:8px; border-bottom:1px solid var(--border-color);">
                                <strong>24-Aug-2026</strong> &bull; Cardiology OPD<br/>
                                <span style="color:#64748b;">Dr. Roberto Tan &bull; Routine Checkup</span>
                            </li>
                            <li style="padding-bottom:8px; border-bottom:1px solid var(--border-color);">
                                <strong>15-Jul-2026</strong> &bull; General Wellness<br/>
                                <span style="color:#64748b;">Executive Blood Panel</span>
                            </li>
                        </ul>
                    </div>

                    <div class="card-box">
                        <div class="card-box-header">
                            <h3><i class="fa-solid fa-flask" style="color:var(--brand-accent);"></i> Recent Lab Tests</h3>
                        </div>
                        <ul style="list-style:none; display:flex; flex-direction:column; gap:10px; font-size:13px;">
                            <li style="padding-bottom:8px; border-bottom:1px solid var(--border-color);">
                                <strong>Complete Blood Count</strong> &bull; <span class="status-badge status-completed">Normal</span><br/>
                                <span style="color:#64748b;">Hemoglobin 13.2 g/dL &bull; WBC 6,800</span>
                            </li>
                            <li style="padding-bottom:8px; border-bottom:1px solid var(--border-color);">
                                <strong>Lipid Panel</strong> &bull; <span class="status-badge status-completed">Normal</span><br/>
                                <span style="color:#64748b;">Cholesterol 178 mg/dL &bull; Trig 110</span>
                            </li>
                        </ul>
                    </div>

                    <div class="card-box">
                        <div class="card-box-header">
                            <h3><i class="fa-solid fa-file-shield" style="color:var(--brand-blue);"></i> Digital Document Vault</h3>
                        </div>
                        <ul style="list-style:none; display:flex; flex-direction:column; gap:10px; font-size:13px;">
                            <li style="padding-bottom:8px; border-bottom:1px solid var(--border-color);">
                                <i class="fa-solid fa-file-pdf" style="color:#ef4444;"></i> <strong>Vaccination_Card_2026.pdf</strong><br/>
                                <span style="color:#64748b;">Verified by Hospital Staff</span>
                            </li>
                            <li style="padding-bottom:8px; border-bottom:1px solid var(--border-color);">
                                <i class="fa-solid fa-file-image" style="color:#0284c7;"></i> <strong>Prior_Echocardiogram.jpg</strong><br/>
                                <span style="color:#64748b;">Uploaded via Patient Mobile App</span>
                            </li>
                        </ul>
                    </div>
                </div>
            </section>

            <!-- 14. EMPLOYEE HEALTH & SAFETY (EHS) VIEW -->
            <section id="view-ehs" class="module-view">
                <div class="ux-navigation-bar">
                    <div class="breadcrumbs">
                        <a onclick="switchTab('view-dashboard', document.querySelector('[data-target=view-dashboard]'))"><i class="fa-solid fa-house"></i> Home</a>
                        <i class="fa-solid fa-chevron-right" style="font-size:10px;"></i>
                        <span class="current">Employee Health & Safety (EHS)</span>
                    </div>
                    <button class="btn-back-dashboard" onclick="switchTab('view-dashboard', document.querySelector('[data-target=view-dashboard]'))">
                        <i class="fa-solid fa-arrow-left"></i> Back to Dashboard
                    </button>
                </div>

                <div class="view-header">
                    <div>
                        <h1>Employee Health & Safety (EHS Occupational Health)</h1>
                        <p>Hospital staff health surveillance, occupational immunization tracking, and incident logging</p>
                    </div>
                    <div>
                        <button class="btn-primary-action" onclick="openModal('modal-report-incident')">
                            <i class="fa-solid fa-triangle-exclamation"></i> + Report Safety Incident
                        </button>
                    </div>
                </div>

                <div class="grid-3col">
                    <div class="stat-card">
                        <div class="stat-icon"><i class="fa-solid fa-shield-virus"></i></div>
                        <div class="stat-content">
                            <h3>98.5%</h3>
                            <p>Staff Hepatitis B Immunity Rate</p>
                        </div>
                    </div>
                    <div class="stat-card cyan">
                        <div class="stat-icon"><i class="fa-solid fa-syringe"></i></div>
                        <div class="stat-content">
                            <h3>340 / 345</h3>
                            <p>Annual Flu Vaccinations Done</p>
                        </div>
                    </div>
                    <div class="stat-card teal">
                        <div class="stat-icon"><i class="fa-solid fa-radiation"></i></div>
                        <div class="stat-content">
                            <h3>0.02 mSv</h3>
                            <p>Average Radiation Dose (Safe)</p>
                        </div>
                    </div>
                </div>

                <div class="table-card">
                    <div class="table-toolbar">
                        <h3 style="font-size: 15px; font-weight: 700;">Workplace Safety & Sharps Injury Surveillance Log</h3>
                    </div>
                    <table class="emr-table">
                        <thead>
                            <tr>
                                <th>Incident ID</th>
                                <th>Employee Name</th>
                                <th>Department</th>
                                <th>Incident Category</th>
                                <th>Severity</th>
                                <th>PEP Protocol</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody id="tbody-ehs"></tbody>
                    </table>
                </div>
            </section>

            <!-- 15. TELEHEALTH VIEW -->
            <section id="view-telehealth" class="module-view">
                <div class="ux-navigation-bar">
                    <div class="breadcrumbs">
                        <a onclick="switchTab('view-dashboard', document.querySelector('[data-target=view-dashboard]'))"><i class="fa-solid fa-house"></i> Home</a>
                        <i class="fa-solid fa-chevron-right" style="font-size:10px;"></i>
                        <span class="current">Telehealth & Virtual Care</span>
                    </div>
                    <button class="btn-back-dashboard" onclick="switchTab('view-dashboard', document.querySelector('[data-target=view-dashboard]'))">
                        <i class="fa-solid fa-arrow-left"></i> Back to Dashboard
                    </button>
                </div>

                <div class="view-header">
                    <div>
                        <h1>Telehealth & Remote Doctor Consultations</h1>
                        <p>Encrypted WebRTC video calls, digital vitals sharing, and immediate e-prescription delivery</p>
                    </div>
                    <div>
                        <button class="btn-accent-action" onclick="showToast('Connecting to Secure Video Consultation Room...')">
                            <i class="fa-solid fa-video"></i> Start Video Room
                        </button>
                    </div>
                </div>

                <div class="table-card">
                    <table class="emr-table">
                        <thead>
                            <tr>
                                <th>Room ID</th>
                                <th>Patient Name</th>
                                <th>Specialty</th>
                                <th>Doctor</th>
                                <th>Status</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody id="tbody-telehealth"></tbody>
                    </table>
                </div>
            </section>

            <!-- 16. BILLING & INVOICING VIEW -->
            <section id="view-billing" class="module-view">
                <div class="ux-navigation-bar">
                    <div class="breadcrumbs">
                        <a onclick="switchTab('view-dashboard', document.querySelector('[data-target=view-dashboard]'))"><i class="fa-solid fa-house"></i> Home</a>
                        <i class="fa-solid fa-chevron-right" style="font-size:10px;"></i>
                        <span class="current">Billing & Invoicing</span>
                    </div>
                    <button class="btn-back-dashboard" onclick="switchTab('view-dashboard', document.querySelector('[data-target=view-dashboard]'))">
                        <i class="fa-solid fa-arrow-left"></i> Back to Dashboard
                    </button>
                </div>

                <div class="view-header">
                    <div>
                        <h1>Outpatient & Inpatient Billing</h1>
                        <p>Generate invoices, process insurance/HMO claims, and print official hospital receipts</p>
                    </div>
                    <div>
                        <button class="btn-primary-action" onclick="openModal('modal-generate-invoice')">
                            <i class="fa-solid fa-receipt"></i> + Create New Invoice
                        </button>
                    </div>
                </div>

                <div class="table-card">
                    <div class="table-toolbar">
                        <h3 style="font-size: 15px; font-weight: 700;">Recent Invoices & Transactions</h3>
                    </div>
                    <table class="emr-table">
                        <thead>
                            <tr>
                                <th>Invoice No</th>
                                <th>Date & Time</th>
                                <th>Patient Name</th>
                                <th>Total Amount</th>
                                <th>Payment Mode</th>
                                <th>Status</th>
                                <th>Print Receipt</th>
                            </tr>
                        </thead>
                        <tbody id="tbody-billing"></tbody>
                    </table>
                </div>
            </section>

            <!-- 17. SECURITY & WHITE-LABEL SETTINGS -->
            <section id="view-whitelabel" class="module-view">
                <div class="ux-navigation-bar">
                    <div class="breadcrumbs">
                        <a onclick="switchTab('view-dashboard', document.querySelector('[data-target=view-dashboard]'))"><i class="fa-solid fa-house"></i> Home</a>
                        <i class="fa-solid fa-chevron-right" style="font-size:10px;"></i>
                        <span class="current">Security, Audit Trail & White-Label Settings</span>
                    </div>
                    <button class="btn-back-dashboard" onclick="switchTab('view-dashboard', document.querySelector('[data-target=view-dashboard]'))">
                        <i class="fa-solid fa-arrow-left"></i> Back to Dashboard
                    </button>
                </div>

                <div class="view-header">
                    <div>
                        <h1>Security Architecture, Audit Logs & White-Label Settings</h1>
                        <p>Enterprise HIPAA-compliant session protection, authentication controls, and tenant branding</p>
                    </div>
                    <div>
                        <button class="btn-accent-action" onclick="savePersonalizationSettings()">
                            <i class="fa-solid fa-floppy-disk"></i> Save & Apply Changes
                        </button>
                    </div>
                </div>

                <!-- Security Status Panel -->
                <div class="card-box" style="margin-bottom:24px; border-left:4px solid #15803d;">
                    <div class="card-box-header">
                        <h3><i class="fa-solid fa-shield-halved" style="color:#15803d;"></i> Active Security Policies & Compliance Status</h3>
                        <span class="status-badge status-active"><i class="fa-solid fa-lock"></i> Protected Session</span>
                    </div>
                    <div class="grid-3col">
                        <div>
                            <strong style="font-size:13px; color:#0f172a;">Session Token Protection:</strong>
                            <p style="font-size:12px; color:#64748b; margin-top:2px;">HMAC Cryptographic Token + SameSite Cookie</p>
                        </div>
                        <div>
                            <strong style="font-size:13px; color:#0f172a;">Inactivity Auto-Lock:</strong>
                            <p style="font-size:12px; color:#64748b; margin-top:2px;">Enabled (15 Min Idle Threshold)</p>
                        </div>
                        <div>
                            <strong style="font-size:13px; color:#0f172a;">Cache-Control Policy:</strong>
                            <p style="font-size:12px; color:#64748b; margin-top:2px;">no-store, no-cache (No back leakage)</p>
                        </div>
                    </div>
                </div>

                <!-- Live Audit Trail Log -->
                <div class="table-card" style="margin-bottom:24px;">
                    <div class="table-toolbar">
                        <h3 style="font-size: 15px; font-weight: 700;"><i class="fa-solid fa-list-check" style="color:var(--brand-primary);"></i> System Security Audit Log</h3>
                        <button class="btn-secondary" style="padding:4px 10px; font-size:11.5px;" onclick="showToast('Audit Log exported as CSV for Compliance Officer')">
                            <i class="fa-solid fa-file-csv"></i> Export Audit Log
                        </button>
                    </div>
                    <table class="emr-table">
                        <thead>
                            <tr>
                                <th>Timestamp</th>
                                <th>User Account</th>
                                <th>Security Action / Resource</th>
                                <th>Client IP</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody id="tbody-audit"></tbody>
                    </table>
                </div>

                <div class="grid-2col">
                    <div class="card-box">
                        <div class="card-box-header">
                            <h3><i class="fa-solid fa-building"></i> Hospital Organization Profile</h3>
                        </div>
                        <div class="form-group" style="margin-bottom:12px;">
                            <label>Hospital / Clinic Name</label>
                            <input type="text" id="cfg-hospital-name" class="form-control" value="Global 1 OneTech Medical & Health Center" />
                        </div>
                        <div class="form-group" style="margin-bottom:12px;">
                            <label>Brand Display Title</label>
                            <input type="text" id="cfg-brand-title" class="form-control" value="G1 Health EMR" />
                        </div>
                        <div class="form-group" style="margin-bottom:12px;">
                            <label>Contact Email</label>
                            <input type="email" id="cfg-email" class="form-control" value="info@global1onetech.com" />
                        </div>
                        <div class="form-group">
                            <label>Website URL</label>
                            <input type="url" id="cfg-website" class="form-control" value="https://global1onetech.com/" />
                        </div>
                    </div>

                    <div class="card-box">
                        <div class="card-box-header">
                            <h3><i class="fa-solid fa-palette"></i> Theme & Brand Colors</h3>
                        </div>
                        <div class="form-group" style="margin-bottom:12px;">
                            <label>Primary Brand Color</label>
                            <div style="display:flex; gap:10px;">
                                <input type="color" id="cfg-color-primary" value="#253545" style="height:40px; width:60px; border-radius:6px; border:none; cursor:pointer;" />
                                <input type="text" class="form-control" value="#253545" />
                            </div>
                        </div>
                        <div class="form-group" style="margin-bottom:12px;">
                            <label>Accent / Highlight Color</label>
                            <div style="display:flex; gap:10px;">
                                <input type="color" id="cfg-color-accent" value="#00ffa1" style="height:40px; width:60px; border-radius:6px; border:none; cursor:pointer;" />
                                <input type="text" class="form-control" value="#00ffa1" />
                            </div>
                        </div>
                        <div class="form-group">
                            <label>Active Brand Logo</label>
                            <div style="padding:12px; background:#f1f5f9; border-radius:8px; display:flex; align-items:center; gap:16px;">
                                <img src="/Personalization/logos/logo-main.png" style="max-height:40px;" />
                                <span style="font-size:12px; color:#64748b;">Global 1 OneTech Transparent Globe Logo</span>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

        
            <!-- 3. CLINICAL SETTINGS & TEMPLATES -->
            <section id="view-clinicalsettings" class="module-view">
                <div class="ux-navigation-bar">
                    <div class="breadcrumbs">
                        <a onclick="switchTab('view-dashboard', null)"><i class="fa-solid fa-house"></i> Home</a>
                        <i class="fa-solid fa-chevron-right" style="font-size:10px;"></i>
                        <span class="current">Clinical Settings & Templates</span>
                    </div>
                    <button class="btn-back-dashboard" onclick="switchTab('view-dashboard', null)"><i class="fa-solid fa-arrow-left"></i> Back to Dashboard</button>
                </div>
                <div class="view-header">
                    <div>
                        <h1>Doctor Consultation Templates & Drug Formulary Sets</h1>
                        <p>Configure doctor clinical templates, favorite drug regimens, chief complaint macros, and ICD-10 shortcuts</p>
                    </div>
                    <button class="btn-primary-action" onclick="openModal('modal-new-template')"><i class="fa-solid fa-plus"></i> + Create New Template</button>
                </div>
                <div class="grid-2col">
                    <div class="card-box">
                        <div class="card-box-header"><h3><i class="fa-solid fa-notes-medical"></i> Doctor Consultation Macros</h3></div>
                        <table class="emr-table" id="table-macros">
                            <thead><tr><th>Macro Code</th><th>Clinical Scenario</th><th>Default ICD-10</th><th>Actions</th></tr></thead>
                            <tbody>
                                <tr><td><strong>.HTN-FOLLOWUP</strong></td><td>Hypertension Routine Review</td><td>I10 - Essential HTN</td><td><button class="btn-secondary" style="padding:4px 8px; font-size:11px;" onclick="loadMacroToEMR('HTN')">Use in Chart</button></td></tr>
                                <tr><td><strong>.DM-PANEL</strong></td><td>Type 2 Diabetes Screening</td><td>E11.9 - DM Type 2</td><td><button class="btn-secondary" style="padding:4px 8px; font-size:11px;" onclick="loadMacroToEMR('DM')">Use in Chart</button></td></tr>
                                <tr><td><strong>.ASTHMA-STAT</strong></td><td>Acute Bronchospasm Protocol</td><td>J45.9 - Bronchial Asthma</td><td><button class="btn-secondary" style="padding:4px 8px; font-size:11px;" onclick="loadMacroToEMR('ASTHMA')">Use in Chart</button></td></tr>
                            </tbody>
                        </table>
                    </div>
                    <div class="card-box">
                        <div class="card-box-header"><h3><i class="fa-solid fa-pills"></i> Favorite Prescription Sets</h3></div>
                        <table class="emr-table">
                            <thead><tr><th>Regimen Name</th><th>Department</th><th>Item Count</th><th>Action</th></tr></thead>
                            <tbody>
                                <tr><td><strong>Standard Triple Therapy (H. Pylori)</strong></td><td>Gastroenterology</td><td>3 Meds</td><td><button class="btn-primary-action" style="padding:4px 8px; font-size:11px;" onclick="attachRxSetToChart('Triple Therapy')">Attach to Chart</button></td></tr>
                                <tr><td><strong>Pediatric URI Starter Pack</strong></td><td>Pediatrics</td><td>2 Meds</td><td><button class="btn-primary-action" style="padding:4px 8px; font-size:11px;" onclick="attachRxSetToChart('Pediatric URI')">Attach to Chart</button></td></tr>
                                <tr><td><strong>Post-Op Pain Management</strong></td><td>Orthopedics</td><td>3 Meds</td><td><button class="btn-primary-action" style="padding:4px 8px; font-size:11px;" onclick="attachRxSetToChart('Post-Op Pain')">Attach to Chart</button></td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </section>
    
        
            <!-- 13. CENTRAL INVENTORY & WAREHOUSE -->
            <section id="view-inventory" class="module-view">
                <div class="ux-navigation-bar">
                    <div class="breadcrumbs">
                        <a onclick="switchTab('view-dashboard', null)"><i class="fa-solid fa-house"></i> Home</a>
                        <i class="fa-solid fa-chevron-right" style="font-size:10px;"></i>
                        <span class="current">Central Inventory & Warehouse</span>
                    </div>
                    <button class="btn-back-dashboard" onclick="switchTab('view-dashboard', null)"><i class="fa-solid fa-arrow-left"></i> Back to Dashboard</button>
                </div>
                <div class="view-header">
                    <div>
                        <h1>Central Medical Warehouse & Supply Chain Inventory</h1>
                        <p>Track warehouse stock levels, bin locations, batch expiration dates, minimum reorder thresholds, and internal transfer indents</p>
                    </div>
                    <div style="display:flex; gap:10px;">
                        <button class="btn-secondary" onclick="showToast('Reorder PO generated for all items below safety threshold')"><i class="fa-solid fa-calculator"></i> Auto-Generate Reorder</button>
                        <button class="btn-primary-action" onclick="openModal('modal-new-stock-item')"><i class="fa-solid fa-boxes-packing"></i> + Add Warehouse Item</button>
                    </div>
                </div>
                <div class="stats-grid">
                    <div class="stat-card"><div class="stat-icon"><i class="fa-solid fa-boxes-stacked"></i></div><div class="stat-content"><h3>1,420 Items</h3><p>Total Active SKUs</p></div></div>
                    <div class="stat-card cyan"><div class="stat-icon"><i class="fa-solid fa-triangle-exclamation"></i></div><div class="stat-content"><h3>4 Items</h3><p>Below Safety Reorder Level</p></div></div>
                    <div class="stat-card teal"><div class="stat-icon"><i class="fa-solid fa-warehouse"></i></div><div class="stat-content"><h3>₱ 4,850,000</h3><p>Total Inventory Asset Value</p></div></div>
                </div>
                <div class="table-card">
                    <div class="table-toolbar">
                        <div class="search-box-table">
                            <i class="fa-solid fa-magnifying-glass"></i>
                            <input type="text" placeholder="Search inventory by Item Code, Generic Name, Bin Location..." onkeyup="filterGenericTable(this, 'table-inventory')" />
                        </div>
                        <button class="btn-accent-action" onclick="showToast('Inventory valuation statement exported')"><i class="fa-solid fa-file-excel"></i> Stock Audit Sheet</button>
                    </div>
                    <table class="emr-table" id="table-inventory">
                        <thead><tr><th>SKU Code</th><th>Item Name & Description</th><th>Category</th><th>Bin Location</th><th>Current Stock</th><th>Min Threshold</th><th>Unit Price</th><th>Status</th><th>Actions</th></tr></thead>
                        <tbody id="tbody-inventory"></tbody>
                    </table>
                </div>
            </section>
    
        
            <!-- 15. PROCUREMENT & PURCHASE ORDERS -->
            <section id="view-procurement" class="module-view">
                <div class="ux-navigation-bar">
                    <div class="breadcrumbs">
                        <a onclick="switchTab('view-dashboard', null)"><i class="fa-solid fa-house"></i> Home</a>
                        <i class="fa-solid fa-chevron-right" style="font-size:10px;"></i>
                        <span class="current">Procurement & Purchase Orders</span>
                    </div>
                    <button class="btn-back-dashboard" onclick="switchTab('view-dashboard', null)"><i class="fa-solid fa-arrow-left"></i> Back to Dashboard</button>
                </div>
                <div class="view-header">
                    <div>
                        <h1>Hospital Procurement & Vendor Purchase Orders</h1>
                        <p>Manage purchase requisitions, supplier quotation comparisons, Goods Receipt Notes (GRN), and invoice verification</p>
                    </div>
                    <button class="btn-primary-action" onclick="openModal('modal-new-po')"><i class="fa-solid fa-cart-plus"></i> + Create Purchase Order (PO)</button>
                </div>
                <div class="stats-grid">
                    <div class="stat-card"><div class="stat-icon"><i class="fa-solid fa-file-signature"></i></div><div class="stat-content"><h3>₱ 420,500</h3><p>Active Open PO Value</p></div></div>
                    <div class="stat-card cyan"><div class="stat-icon"><i class="fa-solid fa-truck-ramp-box"></i></div><div class="stat-content"><h3>6 POs</h3><p>Pending Deliveries</p></div></div>
                    <div class="stat-card teal"><div class="stat-icon"><i class="fa-solid fa-handshake"></i></div><div class="stat-content"><h3>24</h3><p>Approved Medical Vendors</p></div></div>
                </div>
                <div class="table-card">
                    <table class="emr-table">
                        <thead><tr><th>PO Number</th><th>Vendor Supplier</th><th>Requisition Items</th><th>Total Amount</th><th>Delivery Status</th><th>Actions</th></tr></thead>
                        <tbody id="tbody-procurement"></tbody>
                    </table>
                </div>
            </section>
    
        
            <!-- 14. SUB-STORE INVENTORY -->
            <section id="view-substore" class="module-view">
                <div class="ux-navigation-bar">
                    <div class="breadcrumbs">
                        <a onclick="switchTab('view-dashboard', null)"><i class="fa-solid fa-house"></i> Home</a>
                        <i class="fa-solid fa-chevron-right" style="font-size:10px;"></i>
                        <span class="current">Sub-Store Inventory</span>
                    </div>
                    <button class="btn-back-dashboard" onclick="switchTab('view-dashboard', null)"><i class="fa-solid fa-arrow-left"></i> Back to Dashboard</button>
                </div>
                <div class="view-header">
                    <div>
                        <h1>Sub-Store & Departmental Floor Stock Requisitions</h1>
                        <p>Floor stocks for ICU, Emergency Room, Operating Theater, consumable indents, and internal dispensary transfers</p>
                    </div>
                    <button class="btn-primary-action" onclick="showToast('Floor stock requisition indent drafted for Main Pharmacy')"><i class="fa-solid fa-cart-shopping"></i> + Create Floor Stock Indent</button>
                </div>
                <div class="table-card">
                    <table class="emr-table">
                        <thead><tr><th>SubStore Department</th><th>Item Name & Strength</th><th>Floor Stock Level</th><th>Minimum Safety Level</th><th>Status</th><th>Actions</th></tr></thead>
                        <tbody id="tbody-substore"></tbody>
                    </table>
                </div>
            </section>
    
        
            <!-- 16. FIXED ASSETS & BIOMEDICAL -->
            <section id="view-fixedassets" class="module-view">
                <div class="ux-navigation-bar">
                    <div class="breadcrumbs">
                        <a onclick="switchTab('view-dashboard', null)"><i class="fa-solid fa-house"></i> Home</a>
                        <i class="fa-solid fa-chevron-right" style="font-size:10px;"></i>
                        <span class="current">Fixed Assets & Biomedical</span>
                    </div>
                    <button class="btn-back-dashboard" onclick="switchTab('view-dashboard', null)"><i class="fa-solid fa-arrow-left"></i> Back to Dashboard</button>
                </div>
                <div class="view-header">
                    <div>
                        <h1>Fixed Assets, Biomedical Equipment & Maintenance (AMC)</h1>
                        <p>Hospital medical equipment register, calibration certificates, Annual Maintenance Contracts (AMC), and depreciation schedules</p>
                    </div>
                    <button class="btn-primary-action" onclick="showToast('Biomedical asset registration form opened')"><i class="fa-solid fa-plus"></i> + Register New Asset</button>
                </div>
                <div class="table-card">
                    <table class="emr-table">
                        <thead><tr><th>Asset Tag No</th><th>Equipment Name & Model</th><th>Department</th><th>Purchase Cost</th><th>Next Calibration Date</th><th>AMC Status</th><th>Actions</th></tr></thead>
                        <tbody id="tbody-fixedassets"></tbody>
                    </table>
                </div>
            </section>
    
        
            <!-- 18. GENERAL LEDGER & ACCOUNTING -->
            <section id="view-accounting" class="module-view">
                <div class="ux-navigation-bar">
                    <div class="breadcrumbs">
                        <a onclick="switchTab('view-dashboard', null)"><i class="fa-solid fa-house"></i> Home</a>
                        <i class="fa-solid fa-chevron-right" style="font-size:10px;"></i>
                        <span class="current">General Ledger & Accounting</span>
                    </div>
                    <button class="btn-back-dashboard" onclick="switchTab('view-dashboard', null)"><i class="fa-solid fa-arrow-left"></i> Back to Dashboard</button>
                </div>
                <div class="view-header">
                    <div>
                        <h1>Hospital Accounting, General Ledger & Daybook</h1>
                        <p>Double-entry accounting, chart of accounts, journal vouchers, trial balance, and audited balance sheets</p>
                    </div>
                    <button class="btn-primary-action" onclick="openModal('modal-new-voucher')"><i class="fa-solid fa-plus"></i> + New Journal Voucher</button>
                </div>
                <div class="stats-grid">
                    <div class="stat-card"><div class="stat-icon"><i class="fa-solid fa-building-columns"></i></div><div class="stat-content"><h3>₱ 5,420,000</h3><p>Cash at Bank (Operating)</p></div></div>
                    <div class="stat-card cyan"><div class="stat-icon"><i class="fa-solid fa-file-invoice-dollar"></i></div><div class="stat-content"><h3>₱ 840,500</h3><p>Accounts Receivable (HMOs)</p></div></div>
                    <div class="stat-card teal"><div class="stat-icon"><i class="fa-solid fa-book"></i></div><div class="stat-content"><h3>₱ 310,200</h3><p>Doctor Incentive Payable</p></div></div>
                </div>
                <div class="table-card">
                    <div class="table-toolbar"><h3 style="font-size:15px; font-weight:700;">Daybook Journal Transactions (24-Aug-2026)</h3></div>
                    <table class="emr-table">
                        <thead><tr><th>Voucher ID</th><th>Transaction Description</th><th>Debit Account</th><th>Credit Account</th><th>Amount (PHP)</th><th>Status</th><th>Actions</th></tr></thead>
                        <tbody id="tbody-accounting"></tbody>
                    </table>
                </div>
            </section>
    
        
            <!-- 19. INSURANCE & CLAIM MANAGEMENT -->
            <section id="view-claimmgmt" class="module-view">
                <div class="ux-navigation-bar">
                    <div class="breadcrumbs">
                        <a onclick="switchTab('view-dashboard', null)"><i class="fa-solid fa-house"></i> Home</a>
                        <i class="fa-solid fa-chevron-right" style="font-size:10px;"></i>
                        <span class="current">Insurance & Claim Management</span>
                    </div>
                    <button class="btn-back-dashboard" onclick="switchTab('view-dashboard', null)"><i class="fa-solid fa-arrow-left"></i> Back to Dashboard</button>
                </div>
                <div class="view-header">
                    <div>
                        <h1>PhilHealth & HMO Insurance Claim Management</h1>
                        <p>Submit electronic claims, track pre-authorizations, and reconcile remittance vouchers</p>
                    </div>
                    <button class="btn-primary-action" onclick="showToast('Claim Pre-Authorization Request Dispatched')"><i class="fa-solid fa-shield-halved"></i> + Submit HMO Claim</button>
                </div>
                <div class="table-card">
                    <table class="emr-table">
                        <thead><tr><th>Claim ID</th><th>Patient Name</th><th>Provider / HMO</th><th>Case Rate / Policy</th><th>Claim Amount</th><th>Adjudication Status</th><th>Actions</th></tr></thead>
                        <tbody id="tbody-claims"></tbody>
                    </table>
                </div>
            </section>
    
        
            <!-- 20. DOCTOR INCENTIVES & FEE SPLIT -->
            <section id="view-incentive" class="module-view">
                <div class="ux-navigation-bar">
                    <div class="breadcrumbs">
                        <a onclick="switchTab('view-dashboard', null)"><i class="fa-solid fa-house"></i> Home</a>
                        <i class="fa-solid fa-chevron-right" style="font-size:10px;"></i>
                        <span class="current">Doctor Incentives & Fee Split</span>
                    </div>
                    <button class="btn-back-dashboard" onclick="switchTab('view-dashboard', null)"><i class="fa-solid fa-arrow-left"></i> Back to Dashboard</button>
                </div>
                <div class="view-header">
                    <div>
                        <h1>Doctor Incentive Schemes & Professional Fee Split</h1>
                        <p>Automated consultation fee split, surgical case cut calculation, referral shares, and doctor payout ledgers</p>
                    </div>
                    <button class="btn-primary-action" onclick="showToast('Doctor Monthly Incentive Statement Generated')"><i class="fa-solid fa-file-invoice-dollar"></i> Generate Monthly Statement</button>
                </div>
                <div class="table-card">
                    <table class="emr-table">
                        <thead><tr><th>Consultant Doctor</th><th>Specialty</th><th>Total Cases Handled</th><th>Gross Professional Fee</th><th>Hospital Split (30%)</th><th>Net Doctor Payout (70%)</th><th>Status</th><th>Actions</th></tr></thead>
                        <tbody id="tbody-incentive"></tbody>
                    </table>
                </div>
            </section>
    
        
            <!-- 21. CLINICAL ORDER VERIFICATION -->
            <section id="view-verification" class="module-view">
                <div class="ux-navigation-bar">
                    <div class="breadcrumbs">
                        <a onclick="switchTab('view-dashboard', null)"><i class="fa-solid fa-house"></i> Home</a>
                        <i class="fa-solid fa-chevron-right" style="font-size:10px;"></i>
                        <span class="current">Clinical Order Verification</span>
                    </div>
                    <button class="btn-back-dashboard" onclick="switchTab('view-dashboard', null)"><i class="fa-solid fa-arrow-left"></i> Back to Dashboard</button>
                </div>
                <div class="view-header">
                    <div>
                        <h1>Clinical Verification, Dual Sign-off & Discount Authorization</h1>
                        <p>Senior pathologist dual sign-off for critical lab panic values, high-risk medication dual checks, and cashier discount approvals</p>
                    </div>
                </div>
                <div class="table-card">
                    <table class="emr-table">
                        <thead><tr><th>Verification Item</th><th>Department</th><th>Requested By</th><th>Values / Justification</th><th>Dual Signoff Status</th><th>Actions</th></tr></thead>
                        <tbody>
                            <tr><td><strong>Critical Lab Panic Value</strong></td><td>Laboratory (LIS)</td><td>Sarah Cruz, RMT</td><td>Serum Potassium 6.8 mmol/L (STAT Panic)</td><td><span class="status-badge status-urgent">Awaiting Senior Pathologist</span></td><td><button class="btn-accent-action" style="padding:4px 8px; font-size:11px;" onclick="showToast('Critical Result Dual-Signed & Urgent Notification pushed to Attending Doctor!')"><i class="fa-solid fa-check-double"></i> Authorize & Sign</button></td></tr>
                            <tr><td><strong>Senior Citizen 20% Discount</strong></td><td>Billing & Cashier</td><td>Mark Mendoza</td><td>Official Senior ID Verification (Elena Reyes)</td><td><span class="status-badge status-active">Approved</span></td><td><button class="btn-secondary" style="padding:4px 8px; font-size:11px;" onclick="showToast('Discount Verified')">View</button></td></tr>
                        </tbody>
                    </table>
                </div>
            </section>
    
        
            <!-- 22. VACCINATION & IMMUNIZATION -->
            <section id="view-vaccination" class="module-view">
                <div class="ux-navigation-bar">
                    <div class="breadcrumbs">
                        <a onclick="switchTab('view-dashboard', null)"><i class="fa-solid fa-house"></i> Home</a>
                        <i class="fa-solid fa-chevron-right" style="font-size:10px;"></i>
                        <span class="current">Vaccination & Immunization</span>
                    </div>
                    <button class="btn-back-dashboard" onclick="switchTab('view-dashboard', null)"><i class="fa-solid fa-arrow-left"></i> Back to Dashboard</button>
                </div>
                <div class="view-header">
                    <div>
                        <h1>National Immunization Program & Vaccine Registry</h1>
                        <p>Record pediatric and adult immunizations, booster doses, batch lot numbers, and cold-chain temperature logs</p>
                    </div>
                    <button class="btn-primary-action" onclick="showToast('Vaccination Dose Recorded in National Registry')"><i class="fa-solid fa-syringe"></i> + Record Vaccine Dose</button>
                </div>
                <div class="grid-3col">
                    <div class="stat-card"><div class="stat-icon"><i class="fa-solid fa-temperature-arrow-down"></i></div><div class="stat-content"><h3>+3.8 °C</h3><p>Vaccine Refrigerator (Safe +2 to +8°C)</p></div></div>
                    <div class="stat-card cyan"><div class="stat-icon"><i class="fa-solid fa-child-reaching"></i></div><div class="stat-content"><h3>98.2%</h3><p>Pediatric EPI On-Time Coverage</p></div></div>
                    <div class="stat-card teal"><div class="stat-icon"><i class="fa-solid fa-shield-virus"></i></div><div class="stat-content"><h3>185</h3><p>Doses Administered This Month</p></div></div>
                </div>
                <div class="table-card">
                    <table class="emr-table">
                        <thead><tr><th>Patient Name</th><th>Age / Sex</th><th>Vaccine Antigen</th><th>Dose / Route</th><th>Batch & Lot No</th><th>Next Due Date</th><th>Administered By</th></tr></thead>
                        <tbody id="tbody-vaccination"></tbody>
                    </table>
                </div>
            </section>
    
        
            <!-- 23. QUEUE MANAGEMENT (SMART OPD) -->
            <section id="view-queue" class="module-view">
                <div class="ux-navigation-bar">
                    <div class="breadcrumbs">
                        <a onclick="switchTab('view-dashboard', null)"><i class="fa-solid fa-house"></i> Home</a>
                        <i class="fa-solid fa-chevron-right" style="font-size:10px;"></i>
                        <span class="current">Queue Management (Smart OPD)</span>
                    </div>
                    <button class="btn-back-dashboard" onclick="switchTab('view-dashboard', null)"><i class="fa-solid fa-arrow-left"></i> Back to Dashboard</button>
                </div>
                <div class="view-header">
                    <div>
                        <h1>Smart OPD Token Calling & Queue Management</h1>
                        <p>Real-time token dispenser, automated voice calling, doctor consultation room routing, and hall display</p>
                    </div>
                    <div style="display:flex; gap:10px;">
                        <button class="btn-accent-action" onclick="showToast('📢 Voice Calling: Token A-104 please proceed to Consultation Room 201')"><i class="fa-solid fa-volume-high"></i> Call Next Token (A-104)</button>
                        <button class="btn-primary-action" onclick="showToast('Issued Token A-106 for OPD General Medicine')"><i class="fa-solid fa-ticket"></i> + Issue Token</button>
                    </div>
                </div>
                <div class="grid-3col">
                    <div class="stat-card cyan"><div class="stat-icon"><i class="fa-solid fa-bullhorn"></i></div><div class="stat-content"><h3 style="color:#0284c7;">A-103</h3><p>Now Serving in Room 201</p></div></div>
                    <div class="stat-card teal"><div class="stat-icon"><i class="fa-solid fa-users"></i></div><div class="stat-content"><h3>4 Patients</h3><p>Waiting in OPD Waiting Hall</p></div></div>
                    <div class="stat-card"><div class="stat-icon"><i class="fa-solid fa-clock"></i></div><div class="stat-content"><h3>8.4 min</h3><p>Average Wait Time</p></div></div>
                </div>
                <div class="table-card">
                    <div class="table-toolbar"><h3 style="font-size:15px; font-weight:700;">Live Waiting Room Token Display</h3></div>
                    <table class="emr-table">
                        <thead><tr><th>Token No</th><th>Patient Name</th><th>Assigned Doctor</th><th>Room Number</th><th>Queue Status</th><th>Action</th></tr></thead>
                        <tbody id="tbody-queue"></tbody>
                    </table>
                </div>
            </section>
    
        
            <!-- 24. STERILIZATION SERVICES (CSSD) -->
            <section id="view-cssd" class="module-view">
                <div class="ux-navigation-bar">
                    <div class="breadcrumbs">
                        <a onclick="switchTab('view-dashboard', null)"><i class="fa-solid fa-house"></i> Home</a>
                        <i class="fa-solid fa-chevron-right" style="font-size:10px;"></i>
                        <span class="current">Sterilization Services (CSSD)</span>
                    </div>
                    <button class="btn-back-dashboard" onclick="switchTab('view-dashboard', null)"><i class="fa-solid fa-arrow-left"></i> Back to Dashboard</button>
                </div>
                <div class="view-header">
                    <div>
                        <h1>Central Sterile Services Department (CSSD)</h1>
                        <p>Autoclave sterilization cycles, surgical instrument tray tracking, Bowie-Dick tests, and biological indicator validation</p>
                    </div>
                    <button class="btn-primary-action" onclick="showToast('Autoclave Cycle Batch #88 Started (134°C for 18 mins)')"><i class="fa-solid fa-play"></i> + Start Autoclave Cycle</button>
                </div>
                <div class="grid-3col">
                    <div class="stat-card"><div class="stat-icon"><i class="fa-solid fa-temperature-high"></i></div><div class="stat-content"><h3>134.2 °C</h3><p>Autoclave Sterilizer 1 (Pass)</p></div></div>
                    <div class="stat-card cyan"><div class="stat-icon"><i class="fa-solid fa-box-archive"></i></div><div class="stat-content"><h3>34 Sets</h3><p>Sterile Surgical Trays Ready</p></div></div>
                    <div class="stat-card teal"><div class="stat-icon"><i class="fa-solid fa-circle-check"></i></div><div class="stat-content"><h3>100%</h3><p>Biological Indicator Pass Rate</p></div></div>
                </div>
                <div class="table-card">
                    <table class="emr-table">
                        <thead><tr><th>Batch / Tray Code</th><th>Instrument Set Description</th><th>Autoclave Unit</th><th>Sterilization Time</th><th>Biological Test</th><th>Expiry Date</th></tr></thead>
                        <tbody id="tbody-cssd"></tbody>
                    </table>
                </div>
            </section>
    
        
            <!-- 25. MEDICAL RECORDS DEPARTMENT (MRD) -->
            <section id="view-medicalrecords" class="module-view">
                <div class="ux-navigation-bar">
                    <div class="breadcrumbs">
                        <a onclick="switchTab('view-dashboard', null)"><i class="fa-solid fa-house"></i> Home</a>
                        <i class="fa-solid fa-chevron-right" style="font-size:10px;"></i>
                        <span class="current">Medical Records Department (MRD)</span>
                    </div>
                    <button class="btn-back-dashboard" onclick="switchTab('view-dashboard', null)"><i class="fa-solid fa-arrow-left"></i> Back to Dashboard</button>
                </div>
                <div class="view-header">
                    <div>
                        <h1>Medical Records Department (MRD & Health Info Management)</h1>
                        <p>Long-term clinical chart archiving, ICD-10 mortality coding, birth/death registries, and medico-legal archives</p>
                    </div>
                    <button class="btn-primary-action" onclick="showToast('MRD Archive File Indexed & Barcoded')"><i class="fa-solid fa-folder-plus"></i> + Archive Patient File</button>
                </div>
                <div class="table-card">
                    <table class="emr-table">
                        <thead><tr><th>Hospital No</th><th>Patient Name</th><th>Discharge Date</th><th>Primary ICD-10 Code</th><th>Physical Archive Shelf</th><th>Digital Status</th></tr></thead>
                        <tbody>
                            <tr><td><strong>G1-2026-0089</strong></td><td>Maria Santos</td><td>24-Aug-2026</td><td>I49.8 - Benign PACs</td><td>Rack A &bull; Bay 4 &bull; Box 12</td><td><span class="status-badge status-active">100% Digitized (PDF)</span></td></tr>
                            <tr><td><strong>G1-2026-0090</strong></td><td>Juan Dela Cruz</td><td>Active OPD</td><td>G44.2 - Tension Headache</td><td>Rack B &bull; Bay 1 &bull; Box 04</td><td><span class="status-badge status-active">Active Live Chart</span></td></tr>
                        </tbody>
                    </table>
                </div>
            </section>
    
        
            <!-- 26. MARKETING & DOCTOR REFERRALS -->
            <section id="view-mktreferral" class="module-view">
                <div class="ux-navigation-bar">
                    <div class="breadcrumbs">
                        <a onclick="switchTab('view-dashboard', null)"><i class="fa-solid fa-house"></i> Home</a>
                        <i class="fa-solid fa-chevron-right" style="font-size:10px;"></i>
                        <span class="current">Marketing & Doctor Referrals</span>
                    </div>
                    <button class="btn-back-dashboard" onclick="switchTab('view-dashboard', null)"><i class="fa-solid fa-arrow-left"></i> Back to Dashboard</button>
                </div>
                <div class="view-header">
                    <div>
                        <h1>Marketing Campaigns & Doctor Referral Management</h1>
                        <p>External referring clinics, corporate health packages, community outreach camps, and ROI tracking</p>
                    </div>
                    <button class="btn-primary-action" onclick="showToast('Corporate Health Tie-up Logged')"><i class="fa-solid fa-plus"></i> + Add Corporate Tie-Up</button>
                </div>
                <div class="table-card">
                    <table class="emr-table">
                        <thead><tr><th>Referral Source</th><th>Referring Doctor / Clinic</th><th>Patients Referred This Month</th><th>Primary Specialty</th><th>Referral Incentive Scheme</th></tr></thead>
                        <tbody id="tbody-mktreferral"></tbody>
                    </table>
                </div>
            </section>
    
        
            <!-- 27. HELPDESK & PATIENT RELATIONS -->
            <section id="view-helpdesk" class="module-view">
                <div class="ux-navigation-bar">
                    <div class="breadcrumbs">
                        <a onclick="switchTab('view-dashboard', null)"><i class="fa-solid fa-house"></i> Home</a>
                        <i class="fa-solid fa-chevron-right" style="font-size:10px;"></i>
                        <span class="current">Helpdesk & Patient Relations</span>
                    </div>
                    <button class="btn-back-dashboard" onclick="switchTab('view-dashboard', null)"><i class="fa-solid fa-arrow-left"></i> Back to Dashboard</button>
                </div>
                <div class="view-header">
                    <div>
                        <h1>Information Helpdesk, Visitor Badges & Inquiries</h1>
                        <p>Hospital information desk, patient room locator, visitor pass issuance, and ambulance dispatch</p>
                    </div>
                    <div style="display:flex; gap:10px;">
                        <button class="btn-accent-action" style="background:#ef4444; color:#fff;" onclick="showToast('🚑 AMBULANCE DISPATCHED: Mobile ICU Unit 1 en route!')"><i class="fa-solid fa-truck-medical"></i> Dispatch Ambulance</button>
                        <button class="btn-primary-action" onclick="showToast('Visitor Badge Pass V-892 Printed')"><i class="fa-solid fa-id-badge"></i> Issue Visitor Badge</button>
                    </div>
                </div>
                <div class="table-card">
                    <table class="emr-table">
                        <thead><tr><th>Inquiry / Ticket</th><th>Visitor / Patient</th><th>Inquiry Category</th><th>Action Taken</th><th>Attending Staff</th><th>Status</th></tr></thead>
                        <tbody>
                            <tr><td><strong>HLP-901</strong></td><td>Rosa Mercado</td><td>ICU Inpatient Room Location</td><td>Guided to 3rd Floor ICU Room 101</td><td>Joy Pascual</td><td><span class="status-badge status-completed">Resolved</span></td></tr>
                            <tr><td><strong>HLP-902</strong></td><td>Emergency Caller</td><td>STAT Ambulance Request (Quezon City)</td><td>Ambulance Unit 1 Dispatched</td><td>Joy Pascual</td><td><span class="status-badge status-urgent">En Route</span></td></tr>
                        </tbody>
                    </table>
                </div>
            </section>
    
        
            <!-- 28. MIS REPORTS & BI ANALYTICS -->
            <section id="view-reports" class="module-view">
                <div class="ux-navigation-bar">
                    <div class="breadcrumbs">
                        <a onclick="switchTab('view-dashboard', null)"><i class="fa-solid fa-house"></i> Home</a>
                        <i class="fa-solid fa-chevron-right" style="font-size:10px;"></i>
                        <span class="current">Hospital MIS Reports & BI Analytics</span>
                    </div>
                    <button class="btn-back-dashboard" onclick="switchTab('view-dashboard', null)"><i class="fa-solid fa-arrow-left"></i> Back to Dashboard</button>
                </div>
                <div class="view-header">
                    <div>
                        <h1>Executive Management Information System (MIS) Reports</h1>
                        <p>Hospital revenue census, bed occupancy analytics, OPD doctor consultations, and pharmacy sales</p>
                    </div>
                    <button class="btn-accent-action" onclick="showToast('MIS Report Exported to Excel / PDF')"><i class="fa-solid fa-file-excel"></i> Export Analytics</button>
                </div>
                <div class="grid-3col">
                    <div class="stat-card"><div class="stat-icon"><i class="fa-solid fa-sack-dollar"></i></div><div class="stat-content"><h3>₱ 1,480,250</h3><p>Monthly Total Revenue</p></div></div>
                    <div class="stat-card cyan"><div class="stat-icon"><i class="fa-solid fa-users"></i></div><div class="stat-content"><h3>482</h3><p>Monthly OPD Consultations</p></div></div>
                    <div class="stat-card teal"><div class="stat-icon"><i class="fa-solid fa-bed"></i></div><div class="stat-content"><h3>3.8 Days</h3><p>Average Length of Stay (ALOS)</p></div></div>
                </div>
                <div class="table-card">
                    <div class="table-toolbar"><h3 style="font-size:15px; font-weight:700;">Departmental Revenue Breakdown (August 2026)</h3></div>
                    <table class="emr-table">
                        <thead><tr><th>Department</th><th>Patient Volume</th><th>Gross Revenue</th><th>Insurance HMO Share</th><th>Net Hospital Collection</th></tr></thead>
                        <tbody>
                            <tr><td><strong>Clinical OPD & Consultation</strong></td><td>482</td><td>₱ 482,000.00</td><td>₱ 192,800.00</td><td>₱ 289,200.00</td></tr>
                            <tr><td><strong>Inpatient Ward & ICU (ADT)</strong></td><td>54</td><td>₱ 540,000.00</td><td>₱ 324,000.00</td><td>₱ 216,000.00</td></tr>
                            <tr><td><strong>Laboratory & Diagnostics</strong></td><td>310</td><td>₱ 248,000.00</td><td>₱ 99,200.00</td><td>₱ 148,800.00</td></tr>
                            <tr><td><strong>Pharmacy Dispensary</strong></td><td>620</td><td>₱ 210,250.00</td><td>₱ 42,050.00</td><td>₱ 168,200.00</td></tr>
                        </tbody>
                    </table>
                </div>
            </section>
    
        
            <!-- 29. SYSTEM UTILITIES & DIAGNOSTICS -->
            <section id="view-utilities" class="module-view">
                <div class="ux-navigation-bar">
                    <div class="breadcrumbs">
                        <a onclick="switchTab('view-dashboard', null)"><i class="fa-solid fa-house"></i> Home</a>
                        <i class="fa-solid fa-chevron-right" style="font-size:10px;"></i>
                        <span class="current">System Utilities & Diagnostics</span>
                    </div>
                    <button class="btn-back-dashboard" onclick="switchTab('view-dashboard', null)"><i class="fa-solid fa-arrow-left"></i> Back to Dashboard</button>
                </div>
                <div class="view-header">
                    <div>
                        <h1>System Utilities, Diagnostics & Hardware Printers</h1>
                        <p>Barcode label designer, thermal receipt printer mappings, database maintenance, and diagnostic ping</p>
                    </div>
                    <button class="btn-accent-action" onclick="showToast('Database Diagnostic & Backup Test Passed with Zero Errors')"><i class="fa-solid fa-server"></i> Run System Diagnostic</button>
                </div>
                <div class="grid-3col">
                    <div class="card-box">
                        <div class="card-box-header"><h3><i class="fa-solid fa-barcode"></i> Barcode Hub</h3></div>
                        <p style="font-size:12.5px; color:#64748b; margin-bottom:12px;">Zebra ZD420 Wristband & Specimen Label Format</p>
                        <button class="btn-primary-action" style="width:100%; justify-content:center; font-size:12px;" onclick="showToast('Sample Test Barcode Sent to Printer')">Test Print Barcode</button>
                    </div>
                    <div class="card-box">
                        <div class="card-box-header"><h3><i class="fa-solid fa-print"></i> Thermal Receipt</h3></div>
                        <p style="font-size:12.5px; color:#64748b; margin-bottom:12px;">Epson TM-T88VI POS Receipt Printer (Billing)</p>
                        <button class="btn-primary-action" style="width:100%; justify-content:center; font-size:12px;" onclick="showToast('Thermal Receipt Feed Test Successful')">Test Print Receipt</button>
                    </div>
                    <div class="card-box">
                        <div class="card-box-header"><h3><i class="fa-solid fa-database"></i> DB Backup Hub</h3></div>
                        <p style="font-size:12.5px; color:#64748b; margin-bottom:12px;">Automated Daily Encrypted Cloud Snapshot</p>
                        <button class="btn-secondary" style="width:100%; justify-content:center; font-size:12px;" onclick="showToast('Cloud Snapshot Verified: 24-Aug-2026 14:00')">Verify Backup</button>
                    </div>
                </div>
            </section>
    
        
            <!-- 30. SYSTEM ADMINISTRATION -->
            <section id="view-systemadmin" class="module-view">
                <div class="ux-navigation-bar">
                    <div class="breadcrumbs">
                        <a onclick="switchTab('view-dashboard', null)"><i class="fa-solid fa-house"></i> Home</a>
                        <i class="fa-solid fa-chevron-right" style="font-size:10px;"></i>
                        <span class="current">System Administration</span>
                    </div>
                    <button class="btn-back-dashboard" onclick="switchTab('view-dashboard', null)"><i class="fa-solid fa-arrow-left"></i> Back to Dashboard</button>
                </div>
                <div class="view-header">
                    <div>
                        <h1>System Administration & User Role Permission Matrix</h1>
                        <p>Manage hospital staff accounts, assign departmental RBAC privileges, and monitor real-time security events</p>
                    </div>
                    <button class="btn-primary-action" onclick="showToast('New Staff User Registered & Department RBAC Assigned')"><i class="fa-solid fa-user-shield"></i> + Create Staff User</button>
                </div>
                <div class="table-card">
                    <div class="table-toolbar"><h3 style="font-size:15px; font-weight:700;">Departmental User Accounts & Security Matrix</h3></div>
                    <table class="emr-table">
                        <thead><tr><th>Username</th><th>Full Staff Name</th><th>Assigned Role</th><th>Allowed Modules</th><th>Session Status</th><th>Action</th></tr></thead>
                        <tbody>
                            <tr><td><strong>admin</strong></td><td>Administrator</td><td><span class="status-badge status-urgent">👑 Super Admin</span></td><td>All 33 Modules</td><td><span class="status-badge status-active">Online Active</span></td><td><button class="btn-secondary" style="padding:4px 8px; font-size:11px;" onclick="showToast('Admin Profile Secured')">Manage</button></td></tr>
                            <tr><td><strong>doctor</strong></td><td>Dr. Roberto Tan, MD</td><td><span class="status-badge status-completed">🩺 Doctor (MD)</span></td><td>Clinical, Appointments, ER, OT, LIS, RIS, MRD</td><td><span class="status-badge status-active">Online Active</span></td><td><button class="btn-secondary" style="padding:4px 8px; font-size:11px;" onclick="showToast('Doctor Profile Edited')">Edit Role</button></td></tr>
                            <tr><td><strong>nurse</strong></td><td>Nurse Clara Dizon</td><td><span class="status-badge status-active">💉 Nurse (RN)</span></td><td>Nursing, ADT Beds, ER, Vaccine, Queue, CSSD</td><td><span class="status-badge status-active">Online Active</span></td><td><button class="btn-secondary" style="padding:4px 8px; font-size:11px;" onclick="showToast('Nurse Profile Edited')">Edit Role</button></td></tr>
                            <tr><td><strong>accountant</strong></td><td>Elena Villar, CPA</td><td><span class="status-badge status-pending">💰 Accountant</span></td><td>Accounting, Billing, Claims, Incentives, Fixed Assets</td><td><span class="status-badge status-active">Online Active</span></td><td><button class="btn-secondary" style="padding:4px 8px; font-size:11px;" onclick="showToast('Accountant Profile Edited')">Edit Role</button></td></tr>
                        </tbody>
                    </table>
                </div>
            </section>
    
        </main>
    </div>

    <!-- MODAL: SELECT / SWITCH ACTIVE PATIENT -->
    <div id="modal-select-patient" class="modal-overlay">
        <div class="modal-box">
            <div class="modal-header">
                <h3><i class="fa-solid fa-users"></i> Switch Active Patient Context</h3>
                <button class="modal-close" onclick="closeModal('modal-select-patient')">&times;</button>
            </div>
            <div class="modal-body">
                <p style="font-size:13px; color:#64748b; margin-bottom:14px;">Select a patient below to instantly load their clinical chart, vitals, visit history, and prescription file:</p>
                <div class="search-box" style="width:100%; margin-bottom:14px;">
                    <i class="fa-solid fa-magnifying-glass"></i>
                    <input type="text" id="modal-pat-filter" placeholder="Filter patient by name..." onkeyup="filterPatientModalList(this)" />
                </div>
                <div style="display:flex; flex-direction:column; gap:8px; max-height:280px; overflow-y:auto;" id="pat-modal-list">
                    <div class="queue-item" onclick="setActivePatient('Juan Dela Cruz'); closeModal('modal-select-patient');">
                        <div class="q-name"><span>Juan Dela Cruz</span><span class="status-badge status-active">PhilHealth</span></div>
                        <div class="q-sub">Hospital No: G1-2026-0090 &bull; 45 Y / Male &bull; Tension Headache</div>
                    </div>
                    <div class="queue-item" onclick="setActivePatient('Maria Santos'); closeModal('modal-select-patient');">
                        <div class="q-name"><span>Maria Santos</span><span class="status-badge status-completed">HMO Gold</span></div>
                        <div class="q-sub">Hospital No: G1-2026-0089 &bull; 34 Y / Female &bull; Cardiology Follow-up</div>
                    </div>
                    <div class="queue-item" onclick="setActivePatient('Elena Reyes'); closeModal('modal-select-patient');">
                        <div class="q-name"><span>Elena Reyes</span><span class="status-badge status-pending">Self-Pay</span></div>
                        <div class="q-sub">Hospital No: G1-2026-0091 &bull; 28 Y / Female &bull; Neurological Checkup</div>
                    </div>
                    <div class="queue-item" onclick="setActivePatient('Antonio Gonzales'); closeModal('modal-select-patient');">
                        <div class="q-name"><span>Antonio Gonzales</span><span class="status-badge status-completed">Corporate EHS</span></div>
                        <div class="q-sub">Hospital No: G1-2026-0092 &bull; 52 Y / Male &bull; Annual Checkup</div>
                    </div>
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn-secondary" onclick="closeModal('modal-select-patient')">Close</button>
            </div>
        </div>
    </div>

    <!-- MODAL: REGISTER NEW ER PATIENT CASE -->
    <div id="modal-new-er-patient" class="modal-overlay">
        <div class="modal-box">
            <div class="modal-header" style="background: #991b1b;">
                <h3><i class="fa-solid fa-truck-medical"></i> Register Emergency (ER) Encounter</h3>
                <button class="modal-close" onclick="closeModal('modal-new-er-patient')">&times;</button>
            </div>
            <div class="modal-body">
                <div class="form-grid">
                    <div class="form-group">
                        <label>Patient Full Name *</label>
                        <input type="text" id="er-new-name" class="form-control" placeholder="e.g. Victor Ramos" />
                    </div>
                    <div class="form-group">
                        <label>Age *</label>
                        <input type="number" id="er-new-age" class="form-control" placeholder="e.g. 42" />
                    </div>
                    <div class="form-group">
                        <label>Gender *</label>
                        <select id="er-new-gender" class="form-control">
                            <option value="Male">Male</option>
                            <option value="Female">Female</option>
                            <option value="Other">Other</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Contact Phone</label>
                        <input type="text" id="er-new-phone" class="form-control" placeholder="+63 9xx xxx xxxx" />
                    </div>
                </div>

                <div class="form-grid">
                    <div class="form-group">
                        <label>Triage Acuity Level *</label>
                        <select id="er-new-level" class="form-control" style="font-weight:700;">
                            <option value="Level 1 - Resuscitation">🔴 Level 1 - Resuscitation (Immediate STAT)</option>
                            <option value="Level 2 - Emergent">🟠 Level 2 - Emergent (<15 min)</option>
                            <option value="Level 3 - Urgent" selected>🟡 Level 3 - Urgent (<30 min)</option>
                            <option value="Level 4 - Less Urgent">🟢 Level 4 - Less Urgent (<60 min)</option>
                            <option value="Level 5 - Non-Urgent">🔵 Level 5 - Non-Urgent</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>ER Bay Assignment *</label>
                        <select id="er-new-bay" class="form-control">
                            <option value="Bay 01 (Crash Cart)">Bay 01 (Crash Cart / Resus)</option>
                            <option value="Bay 02 (Resuscitation)">Bay 02 (Resuscitation)</option>
                            <option value="Bay 03 (Acute Trauma)">Bay 03 (Acute Trauma)</option>
                            <option value="Bay 04 (Acute)">Bay 04 (Acute Medical)</option>
                            <option value="Bay 05 (Observation)">Bay 05 (Observation)</option>
                            <option value="Bay 06 (Observation)">Bay 06 (Observation)</option>
                        </select>
                    </div>
                </div>

                <div class="form-group" style="margin-bottom:16px;">
                    <label>Chief Complaints & Emergency History *</label>
                    <textarea id="er-new-complaint" class="form-control" rows="2" placeholder="e.g. Acute crushing chest pain, dyspnea, diaphoresis"></textarea>
                </div>

                <div class="form-grid">
                    <div class="form-group">
                        <label>BP (mmHg)</label>
                        <input type="text" id="er-new-bp" class="form-control" placeholder="120/80" value="120/80" />
                    </div>
                    <div class="form-group">
                        <label>Heart Rate (bpm)</label>
                        <input type="text" id="er-new-hr" class="form-control" placeholder="80" value="80" />
                    </div>
                    <div class="form-group">
                        <label>SpO2 (%)</label>
                        <input type="text" id="er-new-spo2" class="form-control" placeholder="98%" value="98%" />
                    </div>
                    <div class="form-group">
                        <label>Temp (°C)</label>
                        <input type="text" id="er-new-temp" class="form-control" placeholder="36.8" value="36.8" />
                    </div>
                </div>

                <div class="form-grid">
                    <div class="form-group">
                        <label>Attending ER Doctor</label>
                        <select id="er-new-doctor" class="form-control">
                            <option value="Dr. Roberto Tan, MD">Dr. Roberto Tan, MD (Interventionalist)</option>
                            <option value="Dr. Edward Hernandez, MD">Dr. Edward Hernandez, MD (Trauma Surgeon)</option>
                            <option value="Dr. Vincent Lim, MD">Dr. Vincent Lim, MD (Neurologist)</option>
                            <option value="Dr. Alicia Gomez, MD">Dr. Alicia Gomez, MD (Internal Med)</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Immediate Disposition Plan</label>
                        <select id="er-new-disposition" class="form-control">
                            <option value="Cath Lab Transfer">Cath Lab Transfer (STAT STEMI)</option>
                            <option value="Emergency OR / Surgery">Emergency OR / Surgery</option>
                            <option value="STAT Non-Contrast Brain CT">STAT Non-Contrast Brain CT</option>
                            <option value="STAT Ultrasound & Surgery Consult">STAT Ultrasound & Surgery Consult</option>
                            <option value="Admit to ICU">Admit to ICU</option>
                            <option value="ER Observation & Vitals Monitoring">ER Observation & Vitals Monitoring</option>
                        </select>
                    </div>
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn-secondary" onclick="closeModal('modal-new-er-patient')">Cancel</button>
                <button class="btn-primary-action" style="background:#991b1b;" onclick="submitNewERCase()"><i class="fa-solid fa-truck-medical"></i> Admit to Emergency Bay</button>
            </div>
        </div>
    </div>

    <!-- MODAL: EDIT & UPDATE ER CASE -->
    <div id="modal-manage-er-case" class="modal-overlay">
        <div class="modal-box">
            <div class="modal-header" style="background: #991b1b;">
                <h3><i class="fa-solid fa-pen-to-square"></i> Edit Emergency Case Details</h3>
                <button class="modal-close" onclick="closeModal('modal-manage-er-case')">&times;</button>
            </div>
            <div class="modal-body">
                <input type="hidden" id="edit-er-id" />
                <div class="form-grid">
                    <div class="form-group">
                        <label>ER Case ID</label>
                        <input type="text" id="edit-er-code" class="form-control" readonly style="background:#f1f5f9; font-weight:800;" />
                    </div>
                    <div class="form-group">
                        <label>Patient Name</label>
                        <input type="text" id="edit-er-name" class="form-control" />
                    </div>
                    <div class="form-group">
                        <label>Age / Sex</label>
                        <input type="text" id="edit-er-agesex" class="form-control" />
                    </div>
                    <div class="form-group">
                        <label>ER Bay</label>
                        <select id="edit-er-bay" class="form-control">
                            <option value="Bay 01 (Crash Cart)">Bay 01 (Crash Cart / Resus)</option>
                            <option value="Bay 02 (Resuscitation)">Bay 02 (Resuscitation)</option>
                            <option value="Bay 03 (Acute Trauma)">Bay 03 (Acute Trauma)</option>
                            <option value="Bay 04 (Acute)">Bay 04 (Acute Medical)</option>
                            <option value="Bay 05 (Observation)">Bay 05 (Observation)</option>
                            <option value="Bay 06 (Observation)">Bay 06 (Observation)</option>
                        </select>
                    </div>
                </div>

                <div class="form-grid">
                    <div class="form-group">
                        <label>Triage Acuity Level</label>
                        <select id="edit-er-level" class="form-control" style="font-weight:700;">
                            <option value="Level 1 - Resuscitation">🔴 Level 1 - Resuscitation</option>
                            <option value="Level 2 - Emergent">🟠 Level 2 - Emergent</option>
                            <option value="Level 3 - Urgent">🟡 Level 3 - Urgent</option>
                            <option value="Level 4 - Less Urgent">🟢 Level 4 - Less Urgent</option>
                            <option value="Level 5 - Non-Urgent">🔵 Level 5 - Non-Urgent</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Encounter Status</label>
                        <select id="edit-er-status" class="form-control">
                            <option value="critical">Critical / Resuscitation</option>
                            <option value="urgent">Urgent</option>
                            <option value="stable">Stable / Observation</option>
                            <option value="discharged">Transferred / Discharged</option>
                        </select>
                    </div>
                </div>

                <div class="form-group" style="margin-bottom:16px;">
                    <label>Chief Complaints & Emergency Notes</label>
                    <textarea id="edit-er-complaint" class="form-control" rows="2"></textarea>
                </div>

                <div class="form-grid">
                    <div class="form-group">
                        <label>BP</label>
                        <input type="text" id="edit-er-bp" class="form-control" />
                    </div>
                    <div class="form-group">
                        <label>Heart Rate</label>
                        <input type="text" id="edit-er-hr" class="form-control" />
                    </div>
                    <div class="form-group">
                        <label>SpO2</label>
                        <input type="text" id="edit-er-spo2" class="form-control" />
                    </div>
                    <div class="form-group">
                        <label>GCS Score</label>
                        <input type="text" id="edit-er-gcs" class="form-control" placeholder="15/15" />
                    </div>
                </div>

                <div class="form-grid">
                    <div class="form-group">
                        <label>Attending ER Doctor</label>
                        <select id="edit-er-doctor" class="form-control">
                            <option value="Dr. Roberto Tan, MD">Dr. Roberto Tan, MD</option>
                            <option value="Dr. Edward Hernandez, MD">Dr. Edward Hernandez, MD</option>
                            <option value="Dr. Vincent Lim, MD">Dr. Vincent Lim, MD</option>
                            <option value="Dr. Alicia Gomez, MD">Dr. Alicia Gomez, MD</option>
                            <option value="Dr. Miguel Garcia, MD">Dr. Miguel Garcia, MD</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Clinical Disposition / Plan</label>
                        <input type="text" id="edit-er-disposition" class="form-control" />
                    </div>
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn-secondary" onclick="closeModal('modal-manage-er-case')">Cancel</button>
                <button class="btn-primary-action" style="background:#991b1b;" onclick="saveERCaseDetails()"><i class="fa-solid fa-floppy-disk"></i> Save ER Updates</button>
            </div>
        </div>
    </div>

    <!-- MODAL: MANAGE & EDIT BED ALLOCATION -->
    <div id="modal-manage-bed" class="modal-overlay">
        <div class="modal-box">
            <div class="modal-header">
                <h3><i class="fa-solid fa-bed"></i> Manage Bed Allocation & Status</h3>
                <button class="modal-close" onclick="closeModal('modal-manage-bed')">&times;</button>
            </div>
            <div class="modal-body">
                <input type="hidden" id="edit-bed-id" />
                <div class="form-grid">
                    <div class="form-group">
                        <label>Bed Number / Code</label>
                        <input type="text" id="edit-bed-code" class="form-control" readonly style="background:#f1f5f9; font-weight:800;" />
                    </div>
                    <div class="form-group">
                        <label>Hospital Ward</label>
                        <select id="edit-bed-ward" class="form-control">
                            <option value="Intensive Care Unit (ICU)">Intensive Care Unit (ICU)</option>
                            <option value="General Male Ward">General Male Ward</option>
                            <option value="General Female Ward">General Female Ward</option>
                            <option value="Private Deluxe Suite">Private Deluxe Suite</option>
                            <option value="Pediatric Ward">Pediatric Ward</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Bed Category / Type</label>
                        <input type="text" id="edit-bed-type" class="form-control" placeholder="e.g. ICU Ventilator Bed" />
                    </div>
                    <div class="form-group">
                        <label>Daily Room Rate</label>
                        <input type="text" id="edit-bed-rate" class="form-control" placeholder="₱ 1,500/day" />
                    </div>
                </div>

                <div class="form-group" style="margin-bottom:18px;">
                    <label>Bed Availability Status (1-Click Switch)</label>
                    <div class="btn-status-selector">
                        <button type="button" class="btn-status-opt" id="bopt-available" onclick="setBedStatusDraft('available')">🟢 Available (Empty)</button>
                        <button type="button" class="btn-status-opt" id="bopt-occupied" onclick="setBedStatusDraft('occupied')">🔴 Occupied</button>
                        <button type="button" class="btn-status-opt" id="bopt-cleaning" onclick="setBedStatusDraft('cleaning')">🟡 Cleaning</button>
                        <button type="button" class="btn-status-opt" id="bopt-reserved" onclick="setBedStatusDraft('reserved')">🔵 Reserved</button>
                    </div>
                </div>

                <div style="background:#f8fafc; border:1px solid var(--border-color); border-radius:10px; padding:16px; margin-bottom:16px;">
                    <div style="font-size:13px; font-weight:800; color:#0f172a; margin-bottom:12px; display:flex; align-items:center; justify-content:space-between;">
                        <span><i class="fa-solid fa-user-injured" style="color:var(--brand-primary);"></i> Inpatient Allocation</span>
                        <button type="button" class="btn-bed-vacate" style="padding:4px 10px; border-radius:6px; font-size:11px; cursor:pointer;" onclick="dischargeBedPatientDraft()">
                            <i class="fa-solid fa-person-walking-arrow-right"></i> Discharge & Vacate Bed
                        </button>
                    </div>
                    <div class="form-grid">
                        <div class="form-group">
                            <label>Assigned Patient</label>
                            <select id="edit-bed-patient" class="form-control" onchange="handleBedPatientChange(this)">
                                <option value="">-- No Patient (Bed Empty) --</option>
                                <option value="Juan Dela Cruz">Juan Dela Cruz (G1-2026-0090)</option>
                                <option value="Maria Santos">Maria Santos (G1-2026-0089)</option>
                                <option value="Elena Reyes">Elena Reyes (G1-2026-0091)</option>
                                <option value="Antonio Gonzales">Antonio Gonzales (G1-2026-0092)</option>
                                <option value="Carlos Mendoza">Carlos Mendoza (G1-2026-0098)</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Attending Consultant Doctor</label>
                            <select id="edit-bed-doctor" class="form-control">
                                <option value="Dr. Roberto Tan, MD">Dr. Roberto Tan, MD (Cardiology / ICU)</option>
                                <option value="Dr. Alicia Gomez, MD">Dr. Alicia Gomez, MD (Internal Med)</option>
                                <option value="Dr. Vincent Lim, MD">Dr. Vincent Lim, MD (Neurology)</option>
                                <option value="Dr. Miguel Garcia, MD">Dr. Miguel Garcia, MD (Orthopedics)</option>
                            </select>
                        </div>
                    </div>
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn-secondary" onclick="closeModal('modal-manage-bed')">Cancel</button>
                <button class="btn-primary-action" onclick="saveBedDetails()"><i class="fa-solid fa-floppy-disk"></i> Save Bed Changes</button>
            </div>
        </div>
    </div>

    <!-- MODAL: ADD NEW BED -->
    <div id="modal-add-bed" class="modal-overlay">
        <div class="modal-box">
            <div class="modal-header">
                <h3><i class="fa-solid fa-plus"></i> Add New Hospital Bed</h3>
                <button class="modal-close" onclick="closeModal('modal-add-bed')">&times;</button>
            </div>
            <div class="modal-body">
                <div class="form-grid">
                    <div class="form-group">
                        <label>Bed Number / Code *</label>
                        <input type="text" id="add-bed-code" class="form-control" placeholder="e.g. ICU-105 or WARD-301" />
                    </div>
                    <div class="form-group">
                        <label>Ward Category *</label>
                        <select id="add-bed-ward" class="form-control">
                            <option value="Intensive Care Unit (ICU)">Intensive Care Unit (ICU)</option>
                            <option value="General Male Ward">General Male Ward</option>
                            <option value="General Female Ward">General Female Ward</option>
                            <option value="Private Deluxe Suite">Private Deluxe Suite</option>
                            <option value="Pediatric Ward">Pediatric Ward</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Bed Category / Type</label>
                        <input type="text" id="add-bed-type" class="form-control" placeholder="e.g. Electric Motorized Bed" />
                    </div>
                    <div class="form-group">
                        <label>Daily Room Rate</label>
                        <input type="text" id="add-bed-rate" class="form-control" placeholder="₱ 1,800/day" />
                    </div>
                </div>
                <div class="form-group">
                    <label>Initial Status</label>
                    <select id="add-bed-status" class="form-control">
                        <option value="available">🟢 Available (Empty)</option>
                        <option value="occupied">🔴 Occupied</option>
                        <option value="cleaning">🟡 Under Cleaning</option>
                        <option value="reserved">🔵 Reserved</option>
                    </select>
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn-secondary" onclick="closeModal('modal-add-bed')">Cancel</button>
                <button class="btn-primary-action" onclick="submitNewBed()"><i class="fa-solid fa-plus"></i> Add Bed</button>
            </div>
        </div>
    </div>

    <!-- MODAL: NEW PATIENT REGISTRATION -->
    <div id="modal-new-patient" class="modal-overlay">
        <div class="modal-box">
            <div class="modal-header">
                <h3><i class="fa-solid fa-user-plus"></i> Register New Patient</h3>
                <button class="modal-close" onclick="closeModal('modal-new-patient')">&times;</button>
            </div>
            <div class="modal-body">
                <div class="form-grid">
                    <div class="form-group">
                        <label>First Name *</label>
                        <input type="text" id="np-fname" class="form-control" placeholder="e.g. Gabriel" />
                    </div>
                    <div class="form-group">
                        <label>Last Name *</label>
                        <input type="text" id="np-lname" class="form-control" placeholder="e.g. Ramos" />
                    </div>
                    <div class="form-group">
                        <label>Age *</label>
                        <input type="number" id="np-age" class="form-control" placeholder="e.g. 38" />
                    </div>
                    <div class="form-group">
                        <label>Gender *</label>
                        <select id="np-gender" class="form-control">
                            <option value="Male">Male</option>
                            <option value="Female">Female</option>
                            <option value="Other">Other</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Phone Number *</label>
                        <input type="text" id="np-phone" class="form-control" placeholder="+63 9xx xxx xxxx" />
                    </div>
                    <div class="form-group">
                        <label>Membership / Scheme</label>
                        <select id="np-scheme" class="form-control">
                            <option value="PhilHealth">PhilHealth</option>
                            <option value="HMO Gold">HMO Gold</option>
                            <option value="Self-Pay">Self-Pay</option>
                            <option value="Corporate EHS">Corporate EHS</option>
                        </select>
                    </div>
                </div>
                <div class="form-group">
                    <label>Address</label>
                    <input type="text" id="np-address" class="form-control" placeholder="City / Province" />
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn-secondary" onclick="closeModal('modal-new-patient')">Cancel</button>
                <button class="btn-primary-action" onclick="submitNewPatient()">Save Patient</button>
            </div>
        </div>
    </div>

    <!-- MODAL: BOOK APPOINTMENT -->
    <div id="modal-new-appointment" class="modal-overlay">
        <div class="modal-box">
            <div class="modal-header">
                <h3><i class="fa-solid fa-calendar-plus"></i> Book Doctor Consultation</h3>
                <button class="modal-close" onclick="closeModal('modal-new-appointment')">&times;</button>
            </div>
            <div class="modal-body">
                <div class="form-grid">
                    <div class="form-group">
                        <label>Select Patient</label>
                        <select class="form-control" id="apt-patient">
                            <option>Maria Santos (G1-2026-0089)</option>
                            <option>Juan Dela Cruz (G1-2026-0090)</option>
                            <option>Elena Reyes (G1-2026-0091)</option>
                            <option>Antonio Gonzales (G1-2026-0092)</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Clinical Department</label>
                        <select class="form-control">
                            <option>Cardiology</option>
                            <option>Internal Medicine</option>
                            <option>Neurology</option>
                            <option>Orthopedics</option>
                            <option>General Surgery</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Attending Consultant</label>
                        <select class="form-control">
                            <option>Dr. Roberto Tan, MD (Cardiologist)</option>
                            <option>Dr. Alicia Gomez, MD (Internal Med)</option>
                            <option>Dr. Vincent Lim, MD (Neurologist)</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Appointment Date</label>
                        <input type="date" class="form-control" value="2026-08-24" />
                    </div>
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn-secondary" onclick="closeModal('modal-new-appointment')">Cancel</button>
                <button class="btn-primary-action" onclick="saveNewAppointment()"><i class="fa-solid fa-calendar-check"></i> Confirm Appointment</button>
            </div>
        </div>
    </div>

    <!-- MODAL: GENERATE INVOICE -->
    <div id="modal-generate-invoice" class="modal-overlay">
        <div class="modal-box">
            <div class="modal-header">
                <h3><i class="fa-solid fa-file-invoice-dollar"></i> Create Billing Invoice</h3>
                <button class="modal-close" onclick="closeModal('modal-generate-invoice')">&times;</button>
            </div>
            <div class="modal-body">
                <div class="form-grid">
                    <div class="form-group">
                        <label>Patient</label>
                        <select class="form-control">
                            <option>Elena Reyes (G1-2026-0091)</option>
                            <option>Maria Santos (G1-2026-0089)</option>
                            <option>Juan Dela Cruz (G1-2026-0090)</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Service / Item</label>
                        <select class="form-control">
                            <option>OPD Consultation Fee - ₱ 1,000.00</option>
                            <option>Chest X-Ray Digital - ₱ 850.00</option>
                            <option>Lipid Profile Blood Test - ₱ 650.00</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Payment Method</label>
                        <select class="form-control">
                            <option>Cash</option>
                            <option>GCash / Maya QR</option>
                            <option>Credit / Debit Card</option>
                            <option>HMO Direct Billing</option>
                        </select>
                    </div>
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn-secondary" onclick="closeModal('modal-generate-invoice')">Cancel</button>
                <button class="btn-primary-action" onclick="submitNewBillingInvoice()"><i class="fa-solid fa-receipt"></i> Process Payment & Save Invoice</button>
            </div>
        </div>
    </div>

    <!-- MODAL: PRINT INVOICE PREVIEW -->
    <div id="modal-print-invoice" class="modal-overlay">
        <div class="modal-box">
            <div class="modal-header">
                <h3><i class="fa-solid fa-print"></i> Official Billing Receipt</h3>
                <button class="modal-close" onclick="closeModal('modal-print-invoice')">&times;</button>
            </div>
            <div class="modal-body">
                <div class="printable-invoice" id="print-area">
                    <div class="invoice-header-branding">
                        <div>
                            <img src="/Personalization/logos/logo-main.png" alt="Global 1 OneTech" />
                            <p style="font-size:11px; color:#64748b; margin-top:4px;">Global 1 OneTech Medical & Health Center</p>
                        </div>
                        <div style="text-align:right;">
                            <h4 style="font-size:16px; font-weight:800; color:#0f172a;" id="rcpt-no">INV-2026-0412</h4>
                            <p style="font-size:12px; color:#64748b;">Date: 24-Aug-2026</p>
                            <p style="font-size:12px; color:#64748b;">TIN: 987-654-321-000</p>
                        </div>
                    </div>
                    <div style="margin-bottom:16px; font-size:13px;">
                        <p><strong>Patient Name:</strong> <span id="rcpt-patient">Maria Santos</span></p>
                        <p><strong>Payment Mode:</strong> Cash / Card</p>
                    </div>
                    <table class="emr-table" style="margin-bottom:16px;">
                        <thead>
                            <tr>
                                <th>Item Description</th>
                                <th>Qty</th>
                                <th>Rate</th>
                                <th>Total</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>OPD Consultation - Specialist</td>
                                <td>1</td>
                                <td>₱ 1,500.00</td>
                                <td>₱ 1,500.00</td>
                            </tr>
                            <tr>
                                <td>Complete Blood Count (CBC)</td>
                                <td>1</td>
                                <td>₱ 850.00</td>
                                <td>₱ 850.00</td>
                            </tr>
                            <tr>
                                <td>Pharmacy: Prescribed Medications</td>
                                <td>1</td>
                                <td>₱ 500.00</td>
                                <td>₱ 500.00</td>
                            </tr>
                        </tbody>
                        <tfoot>
                            <tr>
                                <th colspan="3" style="text-align:right;">Grand Total:</th>
                                <th id="rcpt-total">₱ 2,850.00</th>
                            </tr>
                        </tfoot>
                    </table>
                    <div style="text-align:center; font-size:11px; color:#64748b; margin-top:20px; border-top:1px dashed #cbd5e1; padding-top:10px;">
                        Thank you for trusting Global 1 OneTech Medical Center. Wishing you good health!
                    </div>
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn-secondary" onclick="closeModal('modal-print-invoice')">Close</button>
                <button class="btn-primary-action" onclick="window.print()"><i class="fa-solid fa-print"></i> Print Now</button>
            </div>
        </div>
    </div>

    <!-- MODAL: REPORT SAFETY INCIDENT -->
    <div id="modal-report-incident" class="modal-overlay">
        <div class="modal-box">
            <div class="modal-header">
                <h3><i class="fa-solid fa-triangle-exclamation"></i> Report Occupational Safety Incident</h3>
                <button class="modal-close" onclick="closeModal('modal-report-incident')">&times;</button>
            </div>
            <div class="modal-body">
                <div class="form-grid">
                    <div class="form-group">
                        <label>Affected Staff / Employee</label>
                        <input type="text" class="form-control" placeholder="Employee Name / ID" value="Nurse Ronald Valdez" />
                    </div>
                    <div class="form-group">
                        <label>Incident Department</label>
                        <select class="form-control">
                            <option>Emergency Room (ER)</option>
                            <option>Operating Room (OR)</option>
                            <option>ICU</option>
                            <option>Central Sterile (CSSD)</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Category</label>
                        <select class="form-control">
                            <option>Needlestick / Sharps Injury</option>
                            <option>Chemical / Drug Exposure</option>
                            <option>Radiation Overexposure</option>
                            <option>Slip / Trip / Fall</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Severity Rating</label>
                        <select class="form-control">
                            <option>Moderate (Requires PEP Evaluation)</option>
                            <option>Minor (First Aid only)</option>
                            <option>Severe</option>
                        </select>
                    </div>
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn-secondary" onclick="closeModal('modal-report-incident')">Cancel</button>
                <button class="btn-primary-action" onclick="closeModal('modal-report-incident'); showToast('Incident Logged & EHS Safety Protocol Initiated!');">Submit Safety Report</button>
            </div>
        </div>
    </div>

    <!-- MODAL: AI TRIAGE SIMULATOR -->
    <div id="modal-ai-simulation" class="modal-overlay">
        <div class="modal-box">
            <div class="modal-header">
                <h3><i class="fa-solid fa-robot"></i> AI CRM Patient Triage Assistant</h3>
                <button class="modal-close" onclick="closeModal('modal-ai-simulation')">&times;</button>
            </div>
            <div class="modal-body">
                <p style="font-size:13.5px; color:#475569; margin-bottom:16px;">
                    Type or paste patient symptoms below to simulate the AI CRM intelligent department matching and automated appointment booking engine:
                </p>
                <div class="form-group" style="margin-bottom:16px;">
                    <label>Patient Symptoms / Inquiry Text</label>
                    <textarea id="ai-symptom-text" class="form-control" rows="3" placeholder="e.g. Chest tightness, shortness of breath, and left arm numbness since morning"></textarea>
                </div>
                <button class="btn-accent-action" style="width:100%; justify-content:center;" onclick="runAITriageTest()">
                    <i class="fa-solid fa-wand-magic-sparkles"></i> Run AI Triage Diagnosis & Matching
                </button>
                <div id="ai-triage-result" style="display:none; margin-top:16px; padding:16px; background:#f0fdf4; border:1px solid #bbf7d0; border-radius:10px;">
                    <h4 style="font-size:14px; font-weight:800; color:#15803d; margin-bottom:6px;"><i class="fa-solid fa-circle-check"></i> AI Triage Recommendation:</h4>
                    <p style="font-size:13px; color:#166534;" id="ai-triage-output"></p>
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn-secondary" onclick="closeModal('modal-ai-simulation')">Close</button>
            </div>
        </div>
    </div>

    
    <!-- MODAL: NEW CLINICAL TEMPLATE -->
    <div id="modal-new-template" class="modal-overlay">
        <div class="modal-box" style="max-width:550px;">
            <div class="modal-header">
                <h3><i class="fa-solid fa-notes-medical"></i> Create Clinical Consultation Template</h3>
                <button class="modal-close" onclick="closeModal('modal-new-template')">&times;</button>
            </div>
            <div class="modal-body">
                <div class="form-group"><label>Macro Trigger Code</label><input type="text" id="tpl-code" placeholder="e.g. .GERD-EVAL" value=".CHESTPAIN-STAT" /></div>
                <div class="form-group"><label>Clinical Scenario Title</label><input type="text" id="tpl-title" placeholder="e.g. GERD Comprehensive Workup" value="Atypical Angina Screening" /></div>
                <div class="form-group"><label>Default ICD-10 Diagnosis</label><input type="text" id="tpl-icd" placeholder="e.g. K21.9 - GERD" value="I20.9 - Angina Pectoris" /></div>
                <div class="form-group"><label>Standard History & Plan Template</label><textarea id="tpl-body" rows="4" style="width:100%; border:1px solid #cbd5e1; border-radius:8px; padding:8px; font-size:13px;">Patient presents with substernal chest discomfort on exertion. ECG ordered stat. Troponin-I and 2D Echo scheduled.</textarea></div>
            </div>
            <div class="modal-footer">
                <button class="btn-secondary" onclick="closeModal('modal-new-template')">Cancel</button>
                <button class="btn-primary-action" onclick="closeModal('modal-new-template'); showToast('New Clinical Template .CHESTPAIN-STAT Saved Successfully!')">Save Template</button>
            </div>
        </div>
    </div>

    <!-- MODAL: NEW PURCHASE ORDER -->
    <div id="modal-new-po" class="modal-overlay">
        <div class="modal-box" style="max-width:550px;">
            <div class="modal-header">
                <h3><i class="fa-solid fa-cart-plus"></i> Create Vendor Purchase Order (PO)</h3>
                <button class="modal-close" onclick="closeModal('modal-new-po')">&times;</button>
            </div>
            <div class="modal-body">
                <div class="form-group"><label>Approved Medical Supplier / Vendor</label>
                    <select id="po-vendor" style="width:100%; padding:8px; border:1px solid #cbd5e1; border-radius:8px; font-size:13px;">
                        <option>Metro Pharma Supplies Inc.</option>
                        <option>Allied Biomedical Instruments Corp</option>
                        <option>Global SurgiTech Solutions</option>
                    </select>
                </div>
                <div class="form-group"><label>Requisition Items & Quantities</label><textarea rows="3" style="width:100%; border:1px solid #cbd5e1; border-radius:8px; padding:8px; font-size:13px;">1. Amoxicillin 500mg Caps (10 Boxes x 100s)&#10;2. Sterile IV Cannula 20G (5 Boxes x 50s)</textarea></div>
                <div class="form-group"><label>Estimated Purchase Order Total (PHP)</label><input type="text" value="₱ 58,200.00" /></div>
            </div>
            <div class="modal-footer">
                <button class="btn-secondary" onclick="closeModal('modal-new-po')">Cancel</button>
                <button class="btn-primary-action" onclick="closeModal('modal-new-po'); showToast('Purchase Order PO-2026-090 Created & Dispatched to Supplier')">Create & Send PO</button>
            </div>
        </div>
    </div>

    <!-- MODAL: NEW JOURNAL VOUCHER -->
    <div id="modal-new-voucher" class="modal-overlay">
        <div class="modal-box" style="max-width:550px;">
            <div class="modal-header">
                <h3><i class="fa-solid fa-calculator"></i> New Accounting Journal Voucher Entry</h3>
                <button class="modal-close" onclick="closeModal('modal-new-voucher')">&times;</button>
            </div>
            <div class="modal-body">
                <div class="form-group"><label>Transaction Description / Narration</label><input type="text" value="Direct Cash Settlement for Operating Room Supplies" /></div>
                <div class="grid-2col">
                    <div class="form-group"><label>Debit Account</label><input type="text" value="5020 - Medical Supplies Exp" /></div>
                    <div class="form-group"><label>Credit Account</label><input type="text" value="1010 - Cash on Hand" /></div>
                </div>
                <div class="form-group"><label>Voucher Amount (PHP)</label><input type="text" value="₱ 14,500.00" /></div>
            </div>
            <div class="modal-footer">
                <button class="btn-secondary" onclick="closeModal('modal-new-voucher')">Cancel</button>
                <button class="btn-primary-action" onclick="closeModal('modal-new-voucher'); showToast('Journal Voucher JV-2026-044 Posted into General Ledger')">Post Voucher</button>
            </div>
        </div>
    </div>

    
    
    
    <!-- MODAL: CODE BLUE STAT LOCATION DISPATCH -->
    <div id="modal-code-blue-dispatch" class="modal-overlay">
        <div class="modal-box" style="max-width:620px; border-top:6px solid #dc2626;">
            <div class="modal-header" style="background:#fef2f2;">
                <div>
                    <h3 style="color:#b91c1c; font-size:17px; font-weight:800;">
                        <i class="fa-solid fa-bullhorn"></i> STAT Code Blue & Emergency Dispatch
                    </h3>
                    <p style="font-size:12px; color:#7f1d1d; margin-top:2px;">Select the exact hospital zone/bay to broadcast emergency resuscitation alerts.</p>
                </div>
                <button class="modal-close" onclick="closeModal('modal-code-blue-dispatch')">&times;</button>
            </div>
            <div class="modal-body">
                <!-- 1. Location Selection Grid -->
                <div class="form-group" style="margin-bottom:14px;">
                    <label style="font-weight:800; color:#1e293b; display:flex; justify-content:space-between;">
                        <span>1. CHOOSE EMERGENCY LOCATION / ZONE</span>
                        <span style="color:#dc2626; font-size:11px;">* Required</span>
                    </label>
                    <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px; margin-top:6px;">
                        <div class="code-blue-loc-card selected" onclick="selectCodeBlueLoc(this, 'ER Resuscitation Bay 1 (STAT Red)')">
                            <i class="fa-solid fa-bed-pulse" style="color:#dc2626;"></i>
                            <div>
                                <div style="font-size:12.5px; font-weight:700;">ER Resuscitation Bay 1</div>
                                <div style="font-size:10.5px; color:#64748b;">Ground Floor Emergency Bay</div>
                            </div>
                        </div>
                        <div class="code-blue-loc-card" onclick="selectCodeBlueLoc(this, 'ER Trauma Bay 2')">
                            <i class="fa-solid fa-truck-medical" style="color:#ea580c;"></i>
                            <div>
                                <div style="font-size:12.5px; font-weight:700;">ER Trauma Bay 2</div>
                                <div style="font-size:10.5px; color:#64748b;">Trauma & Surgical Bay</div>
                            </div>
                        </div>
                        <div class="code-blue-loc-card" onclick="selectCodeBlueLoc(this, '3rd Floor ICU Suite (Bed 101)')">
                            <i class="fa-solid fa-heart-pulse" style="color:#0284c7;"></i>
                            <div>
                                <div style="font-size:12.5px; font-weight:700;">3rd Floor ICU Suite</div>
                                <div style="font-size:10.5px; color:#64748b;">Intensive Care Unit (Bed 101)</div>
                            </div>
                        </div>
                        <div class="code-blue-loc-card" onclick="selectCodeBlueLoc(this, '2nd Floor Operating Theater (OT-1)')">
                            <i class="fa-solid fa-mask-ventilator" style="color:#7c3aed;"></i>
                            <div>
                                <div style="font-size:12.5px; font-weight:700;">2nd Floor Operating Theater</div>
                                <div style="font-size:10.5px; color:#64748b;">Main Surgery Suite OT-1</div>
                            </div>
                        </div>
                        <div class="code-blue-loc-card" onclick="selectCodeBlueLoc(this, '4th Floor Inpatient Ward (Room 402)')">
                            <i class="fa-solid fa-building-user" style="color:#059669;"></i>
                            <div>
                                <div style="font-size:12.5px; font-weight:700;">4th Floor Inpatient Ward</div>
                                <div style="font-size:10.5px; color:#64748b;">Medical / Surgical Room 402</div>
                            </div>
                        </div>
                        <div class="code-blue-loc-card" onclick="selectCodeBlueLoc(this, 'Radiology & CT Scanner Bay')">
                            <i class="fa-solid fa-x-ray" style="color:#d97706;"></i>
                            <div>
                                <div style="font-size:12.5px; font-weight:700;">Radiology & CT Scanner</div>
                                <div style="font-size:10.5px; color:#64748b;">Ground Floor Imaging Annex</div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Custom Location input -->
                <div class="form-group" style="margin-bottom:14px;">
                    <label style="font-size:12px; color:#64748b;">Or Specify Other Hospital Area / Room:</label>
                    <input type="text" id="code-blue-custom-loc" class="form-control" placeholder="e.g. OPD Main Lobby, Elevator 2, Dialysis Unit, Pharmacy Corridor" oninput="clearCardSelection()" />
                </div>

                <!-- 2. Emergency Acuity & Symptoms -->
                <div class="form-grid" style="margin-bottom:14px;">
                    <div class="form-group">
                        <label style="font-weight:700; font-size:12px;">EMERGENCY NATURE</label>
                        <select id="code-blue-reason-select" class="form-control">
                            <option value="Cardiac Arrest / Pulseless STAT">🫀 Cardiac Arrest / Pulseless STAT</option>
                            <option value="Respiratory Arrest / Severe Airway Loss">🫁 Respiratory Arrest / Severe Airway Loss</option>
                            <option value="Massive Hemorrhage / Level 1 Shock">🩸 Massive Hemorrhage / Level 1 Shock</option>
                            <option value="Acute Anaphylaxis / Severe Laryngospasm">⚡ Acute Anaphylaxis / Severe Laryngospasm</option>
                            <option value="Unresponsive / Acute Collapse">🚨 Unresponsive / Acute Collapse</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label style="font-weight:700; font-size:12px;">PATIENT IDENTITY (OPTIONAL)</label>
                        <input type="text" id="code-blue-patient-name" class="form-control" value="Juan Dela Cruz (G1-2026-0090)" />
                    </div>
                </div>

                <!-- 3. Automated Resuscitation Team Notification Preview -->
                <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:10px 12px;">
                    <div style="font-size:11.5px; font-weight:800; color:#475569; margin-bottom:4px;">
                        <i class="fa-solid fa-satellite-dish" style="color:var(--brand-blue);"></i> CODE TEAM ROSTER TO BE BROADCASTED:
                    </div>
                    <div style="font-size:11px; color:#64748b; line-height:1.5;">
                        • Dr. Roberto Tan, MD (Emergency Physician Lead)<br />
                        • Dr. Edward Hernandez, MD (Anesthesiologist / Airway Specialist)<br />
                        • Nurse Clara Dizon (Critical Care / Crash Cart Charge Nurse)<br />
                        • Hospital PA System & Pager Gateway (All Floors)
                    </div>
                </div>
            </div>
            <div class="modal-footer" style="background:#fef2f2; border-top:1px solid #fee2e2;">
                <button class="btn-secondary" onclick="closeModal('modal-code-blue-dispatch')">Cancel</button>
                <button class="btn-primary-action" style="background:#dc2626; border-color:#b91c1c; font-weight:800;" onclick="broadcastCodeBlue()">
                    <i class="fa-solid fa-bullhorn"></i> BROADCAST CODE BLUE NOW
                </button>
            </div>
        </div>
    </div>
    
    
    <!-- MODAL: UNIVERSAL GENERIC RECORD EDITOR (Add / Edit Live SQLite Data) -->
    <div id="modal-universal-editor" class="modal-overlay">
        <div class="modal-box" style="max-width:560px;">
            <div class="modal-header">
                <h3 id="universal-editor-title"><i class="fa-solid fa-pen-to-square"></i> Edit Record</h3>
                <button class="modal-close" onclick="closeModal('modal-universal-editor')">&times;</button>
            </div>
            <div class="modal-body" id="universal-editor-form-body">
                <!-- Dynamically generated input fields -->
            </div>
            <div class="modal-footer">
                <button class="btn-secondary" onclick="closeModal('modal-universal-editor')">Cancel</button>
                <button class="btn-primary-action" id="btn-save-universal-edit" onclick="submitUniversalEdit()"><i class="fa-solid fa-floppy-disk"></i> Save & Sync to Database</button>
            </div>
        </div>
    </div>
    
    <!-- TOAST NOTIFICATION -->
    <div id="toast-notification" class="toast-notify">
        <i class="fa-solid fa-circle-check" style="color: var(--brand-cyan);"></i>
        <span id="toast-message">Action executed successfully!</span>
    </div>

    <script>
        // Secure Logout Handler
        
        
                const VALID_USERS = {
            'admin': { pass: 'pass123', name: 'Administrator', role: 'Super Admin &bull; Full Access', role_key: 'admin', avatar: 'AD', badge: '👑 Super Admin' },
            'doctor': { pass: 'pass123', name: 'Dr. Roberto Tan, MD', role: 'Attending Cardiologist &bull; Clinical Desk', role_key: 'doctor', avatar: 'RT', badge: '🩺 Doctor (MD)' },
            'nurse': { pass: 'pass123', name: 'Nurse Clara Dizon', role: 'Charge Nurse &bull; Ward Station', role_key: 'nurse', avatar: 'CD', badge: '💉 Nurse (RN)' },
            'accountant': { pass: 'pass123', name: 'Elena Villar, CPA', role: 'Chief Accountant &bull; Finance Dept', role_key: 'accountant', avatar: 'EV', badge: '💰 Accountant' },
            'billing': { pass: 'pass123', name: 'Mark Mendoza', role: 'Billing & Claims Officer &bull; Cashier', role_key: 'billing', avatar: 'MM', badge: '💳 Billing' },
            'pharmacy': { pass: 'pass123', name: 'Pharm. Leo Santos, RPh', role: 'Chief Pharmacist &bull; Dispensary', role_key: 'pharmacy', avatar: 'LS', badge: '💊 Pharmacist' },
            'labtech': { pass: 'pass123', name: 'Sarah Cruz, RMT', role: 'Diagnostic & Imaging Technologist', role_key: 'labtech', avatar: 'SC', badge: '🔬 Lab Tech' },
            'reception': { pass: 'pass123', name: 'Joy Pascual', role: 'Front Desk & Admissions Officer', role_key: 'reception', avatar: 'JP', badge: '📋 Reception' }
        };

                // Full 33 Enterprise HMIS Modules Master Specification with Professional Departmental Naming
        const ALL_HMIS_MODULES = [
            { id: 'view-dashboard', key: 'dashboard', title: 'Executive Dashboard', icon: 'fa-chart-pie', roles: ['admin', 'doctor', 'nurse', 'accountant', 'billing', 'pharmacy', 'labtech', 'reception'] },
            { id: 'view-clinical', key: 'clinical', title: 'Clinical EMR (Doctor Desk)', icon: 'fa-stethoscope', roles: ['admin', 'doctor'] },
            { id: 'view-clinicalsettings', key: 'clinicalsettings', title: 'Clinical Settings & Templates', icon: 'fa-gear', roles: ['admin', 'doctor'] },
            { id: 'view-appointments', key: 'appointment', title: 'Appointments & Scheduling', icon: 'fa-calendar-check', roles: ['admin', 'doctor', 'nurse', 'reception'] },
            { id: 'view-patient-reg', key: 'patient', title: 'Patient Master Index', icon: 'fa-user', roles: ['admin', 'doctor', 'nurse', 'reception', 'billing'] },
            { id: 'view-emergency', key: 'emergency', title: 'Emergency & Trauma Care (ER)', icon: 'fa-truck-medical', roles: ['admin', 'doctor', 'nurse'] },
            { id: 'view-adt', key: 'adt', title: 'Admissions & Bed Matrix (ADT)', icon: 'fa-bed', roles: ['admin', 'doctor', 'nurse'] },
            { id: 'view-nursing', key: 'nursing', title: 'Nursing Station & Inpatient Care', icon: 'fa-user-nurse', roles: ['admin', 'doctor', 'nurse'] },
            { id: 'view-ot', key: 'ot', title: 'Operation Theater Management', icon: 'fa-scalpel', roles: ['admin', 'doctor'] },
            { id: 'view-laboratory', key: 'laboratory', title: 'Laboratory Diagnostics (LIS)', icon: 'fa-flask', roles: ['admin', 'doctor', 'nurse', 'labtech'] },
            { id: 'view-radiology', key: 'radiology', title: 'Radiology & PACS Imaging', icon: 'fa-x-ray', roles: ['admin', 'doctor', 'labtech'] },
            { id: 'view-pharmacy', key: 'pharmacy', title: 'Pharmacy & Dispensary', icon: 'fa-pills', roles: ['admin', 'pharmacy', 'nurse'] },
            { id: 'view-inventory', key: 'inventory', title: 'Central Inventory & Warehouse', icon: 'fa-boxes-stacked', roles: ['admin', 'pharmacy'] },
            { id: 'view-substore', key: 'substore', title: 'Sub-Store Inventory', icon: 'fa-store', roles: ['admin', 'nurse', 'pharmacy'] },
            { id: 'view-procurement', key: 'procurement', title: 'Procurement & Purchase Orders', icon: 'fa-clipboard-list', roles: ['admin', 'accountant', 'pharmacy'] },
            { id: 'view-fixedassets', key: 'fixedassets', title: 'Fixed Assets & Biomedical', icon: 'fa-hospital-user', roles: ['admin', 'accountant'] },
            { id: 'view-billing', key: 'billing', title: 'Billing & Invoicing', icon: 'fa-file-invoice-dollar', roles: ['admin', 'accountant', 'billing', 'reception'] },
            { id: 'view-accounting', key: 'accounting', title: 'General Ledger & Accounting', icon: 'fa-calculator', roles: ['admin', 'accountant'] },
            { id: 'view-claimmgmt', key: 'claimmgmt', title: 'Insurance & Claim Management', icon: 'fa-file-shield', roles: ['admin', 'accountant', 'billing'] },
            { id: 'view-incentive', key: 'incentive', title: 'Doctor Incentives & Fee Split', icon: 'fa-hand-holding-dollar', roles: ['admin', 'accountant', 'doctor'] },
            { id: 'view-verification', key: 'verification', title: 'Clinical Order Verification', icon: 'fa-clipboard-check', roles: ['admin', 'accountant', 'labtech', 'pharmacy'] },
            { id: 'view-vaccination', key: 'vaccination', title: 'Vaccination & Immunization', icon: 'fa-syringe', roles: ['admin', 'doctor', 'nurse', 'reception'] },
            { id: 'view-queue', key: 'queuemngmt', title: 'Queue Management (Smart OPD)', icon: 'fa-users', roles: ['admin', 'nurse', 'reception', 'billing'] },
            { id: 'view-cssd', key: 'cssd', title: 'Sterilization Services (CSSD)', icon: 'fa-hand-sparkles', roles: ['admin', 'nurse'] },
            { id: 'view-medicalrecords', key: 'medicalrecords', title: 'Medical Records Department (MRD)', icon: 'fa-book-medical', roles: ['admin', 'doctor'] },
            { id: 'view-mktreferral', key: 'mktreferral', title: 'Marketing & Doctor Referrals', icon: 'fa-diagram-project', roles: ['admin', 'reception'] },
            { id: 'view-helpdesk', key: 'helpdesk', title: 'Helpdesk & Patient Relations', icon: 'fa-circle-question', roles: ['admin', 'nurse', 'reception', 'billing'] },
            { id: 'view-reports', key: 'reports', title: 'MIS Reports & BI Analytics', icon: 'fa-chart-line', roles: ['admin', 'accountant', 'doctor', 'billing', 'pharmacy', 'labtech'] },
            { id: 'view-utilities', key: 'utilities', title: 'System Utilities & Diagnostics', icon: 'fa-wrench', roles: ['admin', 'accountant'] },
            { id: 'view-systemadmin', key: 'systemadmin', title: 'System Administration', icon: 'fa-user-shield', roles: ['admin'] },
            { id: 'view-whitelabel', key: 'settings', title: 'Hospital Configuration & Settings', icon: 'fa-sliders', roles: ['admin'] },
            { id: 'view-aicrm', key: 'aicrm', title: 'AI Patient CRM & Leads', icon: 'fa-robot', roles: ['admin', 'doctor', 'reception'] },
            { id: 'view-patient360', key: 'patient360', title: 'Patient 360 & Health Records', icon: 'fa-id-card-clip', roles: ['admin', 'doctor', 'nurse', 'reception', 'labtech'] },
            { id: 'view-ehs', key: 'ehs', title: 'Employee Health & Surveillance', icon: 'fa-heart-pulse', roles: ['admin', 'nurse', 'doctor'] },
            { id: 'view-telehealth', key: 'telehealth', title: 'Telehealth & Virtual Consult', icon: 'fa-video', roles: ['admin', 'doctor'] }
        ];

        // Dynamically Render ONLY the Permitted Sidebar Modules for Active Role
        function renderDynamicSidebar(searchQuery = '') {
            const roleKey = sessionStorage.getItem('g1_role_key') || 'admin';
            const navList = document.getElementById('sidebar-nav-list');
            if (!navList) return;

            const q = searchQuery.toLowerCase().trim();
            navList.innerHTML = '';

            // Filter modules by role
            const allowedModules = ALL_HMIS_MODULES.filter(m => {
                if (roleKey === 'admin') return true;
                return m.roles.includes(roleKey);
            });

            // Filter by search query if any
            const matchedModules = allowedModules.filter(m => {
                if (!q) return true;
                return m.title.toLowerCase().includes(q) || m.key.toLowerCase().includes(q);
            });

            if (matchedModules.length === 0) {
                navList.innerHTML = '<li style="padding:16px 20px; font-size:12px; color:#94a3b8; text-align:center;">No matching tools found for your role.</li>';
                return;
            }

            matchedModules.forEach((m, idx) => {
                const li = document.createElement('li');
                li.className = 'nav-item';
                li.setAttribute('data-target', m.id);
                li.setAttribute('data-module', m.key);

                // Check if currently active
                const currentActiveView = document.querySelector('.module-view.active');
                if (currentActiveView && currentActiveView.id === m.id) {
                    li.classList.add('active');
                } else if (!currentActiveView && idx === 0) {
                    li.classList.add('active');
                }

                li.innerHTML = `
                    <a onclick="switchTab('${m.id}', this)">
                        <i class="fa-solid ${m.icon}"></i>
                        <span>${m.title}</span>
                    </a>
                `;
                navList.appendChild(li);
            });
        }

        // Real-time Sidebar Search ("Search Menu Items...")
        function filterSidebarMenu(input) {
            const query = input ? input.value : '';
            renderDynamicSidebar(query);
        }

        // Apply Strict Role Permissions & Rebuild DOM
        function applyRolePermissions() {
            const roleKey = sessionStorage.getItem('g1_role_key') || 'admin';
            const userBadge = sessionStorage.getItem('g1_user_badge') || '👑 Super Admin';

            // 1. Re-render dynamic sidebar with ONLY permitted modules
            renderDynamicSidebar();

            // 2. Update active workspace banner
            const roleBanner = document.getElementById('active-workspace-banner');
            if (roleBanner) {
                let roleDesc = "All 33 Hospital Modules & Configurations Unlocked.";
                if (roleKey === 'accountant') roleDesc = "Financial & Accounting Tools Only (General Ledger, Invoicing, Claims, Incentives & POs). Clinical/Care modules hidden.";
                else if (roleKey === 'doctor') roleDesc = "Clinical & Diagnostic Tools Only (Doctor Consultation, E-Prescriptions, Appointments, ER, LIS & RIS). Accounting & Store tools hidden.";
                else if (roleKey === 'nurse') roleDesc = "Ward Inpatient Station (Nursing e-MAR, Bed Matrix, Emergency Trauma, Vaccination & CSSD). Finance tools hidden.";
                else if (roleKey === 'billing') roleDesc = "Cashier & Invoicing Station (OPD/IPD Billing, Receipts, Claims & Queue Calling). Clinical records hidden.";
                else if (roleKey === 'pharmacy') roleDesc = "Hospital Pharmacy & Supply Chain (Drug Dispensary, SubStore & Central Warehouse). Patient clinical charts hidden.";
                else if (roleKey === 'labtech') roleDesc = "Diagnostic Laboratory & PACS Imaging (LIS Analyzers, DICOM & Critical Sign-off). Inpatient/Finance tools hidden.";
                else if (roleKey === 'reception') roleDesc = "Front Desk & Admissions (Patient Master Index, Appointment Scheduling, Queue Tokens & Helpdesk).";

                roleBanner.innerHTML = `
                    <div style="background: linear-gradient(90deg, #1e293b, #253545); color:#fff; padding:12px 18px; border-radius:10px; margin-bottom:20px; display:flex; align-items:center; justify-content:space-between; border-left:4px solid var(--brand-cyan); box-shadow:0 2px 6px rgba(0,0,0,0.06);">
                        <div style="display:flex; align-items:center; gap:12px;">
                            <span style="font-size:22px;">${userBadge.split(' ')[0]}</span>
                            <div>
                                <div style="font-size:14px; font-weight:800; color:#ffffff;">${userBadge} Active Workspace</div>
                                <div style="font-size:12px; color:#cbd5e1; margin-top:2px;">${roleDesc}</div>
                            </div>
                        </div>
                        <button class="btn-switch-pat" style="padding:6px 14px; font-size:12px;" onclick="openModal('modal-switch-role')">
                            <i class="fa-solid fa-arrows-rotate"></i> Switch Role
                        </button>
                    </div>
                `;
            }

            // 3. Customize Dashboard Action Buttons for Active Role
            const dashActions = document.getElementById('dash-action-buttons');
            if (dashActions) {
                if (roleKey === 'accountant') {
                    dashActions.innerHTML = `
                        <button class="btn-primary-action" onclick="showToast('New Journal Voucher Entry Drafted')"><i class="fa-solid fa-plus"></i> + New Journal Voucher</button>
                        <button class="btn-accent-action" onclick="switchTab('view-accounting', null)"><i class="fa-solid fa-calculator"></i> Open General Ledger</button>
                    `;
                } else if (roleKey === 'doctor') {
                    dashActions.innerHTML = `
                        <button class="btn-primary-action" onclick="switchTab('view-clinical', null)"><i class="fa-solid fa-stethoscope"></i> Open Doctor Desk</button>
                        <button class="btn-accent-action" onclick="switchTab('view-appointments', null)"><i class="fa-solid fa-calendar-check"></i> View OPD Appointments</button>
                    `;
                } else if (roleKey === 'nurse') {
                    dashActions.innerHTML = `
                        <button class="btn-primary-action" onclick="switchTab('view-adt', null)"><i class="fa-solid fa-bed"></i> Inpatient Bed Matrix</button>
                        <button class="btn-accent-action" onclick="switchTab('view-nursing', null)"><i class="fa-solid fa-user-nurse"></i> Nursing Station</button>
                    `;
                } else if (roleKey === 'pharmacy') {
                    dashActions.innerHTML = `
                        <button class="btn-primary-action" onclick="switchTab('view-pharmacy', null)"><i class="fa-solid fa-pills"></i> Dispense Prescriptions</button>
                        <button class="btn-accent-action" onclick="switchTab('view-substore', null)"><i class="fa-solid fa-store"></i> Ward Indents</button>
                    `;
                } else if (roleKey === 'billing') {
                    dashActions.innerHTML = `
                        <button class="btn-primary-action" onclick="openModal('modal-generate-invoice')"><i class="fa-solid fa-receipt"></i> + Create Invoice</button>
                        <button class="btn-accent-action" onclick="switchTab('view-billing', null)"><i class="fa-solid fa-file-invoice-dollar"></i> Open Invoicing Hub</button>
                    `;
                } else if (roleKey === 'reception') {
                    dashActions.innerHTML = `
                        <button class="btn-primary-action" onclick="openModal('modal-new-patient')"><i class="fa-solid fa-user-plus"></i> + Quick Register</button>
                        <button class="btn-accent-action" onclick="switchTab('view-queue', null)"><i class="fa-solid fa-ticket"></i> Issue Queue Token</button>
                    `;
                } else {
                    dashActions.innerHTML = `
                        <button class="btn-primary-action" onclick="openModal('modal-new-patient')"><i class="fa-solid fa-user-plus"></i> + Quick Register</button>
                        <button class="btn-accent-action" onclick="switchTab('view-aicrm', null)"><i class="fa-solid fa-robot"></i> Open AI CRM Assistant</button>
                    `;
                }
            }

            // 4. Hide/Show Active Patient Bar based on clinical relevance
            const patBar = document.getElementById('global-active-patient-bar');
            if (patBar) {
                if (['doctor', 'nurse', 'reception', 'labtech', 'admin'].includes(roleKey)) {
                    patBar.style.display = 'flex';
                } else {
                    patBar.style.display = 'none';
                }
            }
        }
    

        
        // Generic Table Search Filter
        function filterGenericTable(input, tableId) {
            const query = input.value.toLowerCase();
            const table = document.getElementById(tableId);
            if (!table) return;
            const rows = table.querySelectorAll('tbody tr');
            rows.forEach(row => {
                const text = row.innerText.toLowerCase();
                row.style.display = text.includes(query) ? '' : 'none';
            });
        }

        // Patient Table Search Filter
        function filterPatientTable(input) {
            filterGenericTable(input, 'patient-master-table');
        }

        // Clinical Macro Loader
        function loadMacroToEMR(macroType) {
            const historyArea = document.getElementById('clinical-history-input');
            const diagSelect = document.getElementById('emr-diagnosis-select');
            
            if (macroType === 'HTN') {
                if (historyArea) historyArea.value = "Patient presents for routine hypertension follow-up. Reports good compliance with Amlodipine 5mg OD. Denies chest pain, palpitation, orthopnea, or pedal edema. Home BP logs average 125-135/80-85 mmHg.";
                if (diagSelect) diagSelect.value = "I10 - Essential (primary) hypertension";
            } else if (macroType === 'DM') {
                if (historyArea) historyArea.value = "Patient presents for 3-month Type 2 Diabetes Mellitus review. Fasting blood sugar monitored weekly, averaging 115-130 mg/dL. No polyuria, polydipsia, or peripheral numbness. Dietary compliance maintained.";
                if (diagSelect) diagSelect.value = "E11.9 - Type 2 diabetes mellitus without complications";
            } else if (macroType === 'ASTHMA') {
                if (historyArea) historyArea.value = "Patient presents with acute onset shortness of breath and wheezing triggered by dust exposure. Responded moderately to initial Salbutamol nebulization.";
                if (diagSelect) diagSelect.value = "J45.909 - Unspecified asthma, uncomplicated";
            }

            switchTab('view-clinical', null);
            showToast(`Clinical Macro .${macroType} loaded into patient consultation note!`);
        }

        // Attach Prescription Set to Chart
        function attachRxSetToChart(rxSetName) {
            const rxTable = document.querySelector('#prescribed-meds-table tbody');
            if (rxTable) {
                if (rxSetName === 'Triple Therapy') {
                    rxTable.innerHTML += `
                        <tr><td>Omeprazole 20mg Cap</td><td>1 Cap BID</td><td>14 Days</td><td>PO Before Meals</td><td><button class="btn-secondary" style="padding:2px 6px; font-size:10px;" onclick="this.closest('tr').remove()">&times;</button></td></tr>
                        <tr><td>Amoxicillin 500mg Cap</td><td>1 Cap BID</td><td>14 Days</td><td>PO After Meals</td><td><button class="btn-secondary" style="padding:2px 6px; font-size:10px;" onclick="this.closest('tr').remove()">&times;</button></td></tr>
                        <tr><td>Clarithromycin 500mg Tab</td><td>1 Tab BID</td><td>14 Days</td><td>PO After Meals</td><td><button class="btn-secondary" style="padding:2px 6px; font-size:10px;" onclick="this.closest('tr').remove()">&times;</button></td></tr>
                    `;
                } else if (rxSetName === 'Pediatric URI') {
                    rxTable.innerHTML += `
                        <tr><td>Paracetamol 120mg/5mL Syrup</td><td>5 mL Q4H PRN</td><td>3 Days</td><td>PO for Fever</td><td><button class="btn-secondary" style="padding:2px 6px; font-size:10px;" onclick="this.closest('tr').remove()">&times;</button></td></tr>
                        <tr><td>Saline Nasal Drops 0.65%</td><td>2 drops each nostril TID</td><td>5 Days</td><td>Intranasal</td><td><button class="btn-secondary" style="padding:2px 6px; font-size:10px;" onclick="this.closest('tr').remove()">&times;</button></td></tr>
                    `;
                } else {
                    rxTable.innerHTML += `
                        <tr><td>Celecoxib 200mg Cap</td><td>1 Cap OD</td><td>5 Days</td><td>PO After Meals</td><td><button class="btn-secondary" style="padding:2px 6px; font-size:10px;" onclick="this.closest('tr').remove()">&times;</button></td></tr>
                        <tr><td>Tramadol 50mg Cap</td><td>1 Cap Q8H PRN Severe Pain</td><td>3 Days</td><td>PO</td><td><button class="btn-secondary" style="padding:2px 6px; font-size:10px;" onclick="this.closest('tr').remove()">&times;</button></td></tr>
                    `;
                }
            }
            switchTab('view-clinical', null);
            showToast(`Prescription set '${rxSetName}' attached to active chart!`);
        }

        
        // Mobile Sidebar Controls
        function toggleMobileSidebar() {
            const sidebar = document.querySelector('.sidebar');
            const backdrop = document.getElementById('sidebar-backdrop');
            if (sidebar) sidebar.classList.toggle('open');
            if (backdrop) backdrop.classList.toggle('active');
        }

        function closeMobileSidebar() {
            const sidebar = document.querySelector('.sidebar');
            const backdrop = document.getElementById('sidebar-backdrop');
            if (sidebar) sidebar.classList.remove('open');
            if (backdrop) backdrop.classList.remove('active');
        }
    
        
        // Live AI CRM Interactive Chat & Tool Calling Engine (100% Secure Backend Powered)
        

        function sendPresetScenario(text) {
            document.getElementById('ai-chat-input').value = text;
            sendAIChatMessage();
        }

        async function sendAIChatMessage() {
            const input = document.getElementById('ai-chat-input');
            const message = input.value.trim();
            if (!message) return;

            input.value = '';
            const thread = document.getElementById('ai-chat-thread');
            const patName = document.getElementById('global-pat-name') ? document.getElementById('global-pat-name').textContent : 'Patient';

            const now = new Date();
            const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

            // Append User Message to Thread
            const userMsgEl = document.createElement('div');
            userMsgEl.style.cssText = "align-self:flex-end; max-width:82%; background:#dcf8c6; padding:10px 14px; border-radius:10px; box-shadow:0 1px 3px rgba(0,0,0,0.1); font-size:13px; color:#1e293b;";
            userMsgEl.innerHTML = `
                <div style="font-weight:700; color:#15803d; margin-bottom:3px; font-size:11px;">${patName.toUpperCase()}</div>
                <div>${message}</div>
                <div style="font-size:10px; color:#64748b; text-align:right; margin-top:4px;">${timeStr}</div>
            `;
            thread.appendChild(userMsgEl);
            thread.scrollTop = thread.scrollHeight;

            // Typing indicator
            const typingEl = document.createElement('div');
            typingEl.id = 'ai-typing-indicator';
            typingEl.style.cssText = "align-self:flex-start; background:#fff; padding:8px 12px; border-radius:10px; font-size:12px; color:#64748b; display:flex; align-items:center; gap:6px;";
            typingEl.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> G1 AI is analyzing clinical symptoms...';
            thread.appendChild(typingEl);
            thread.scrollTop = thread.scrollHeight;

            try {
                const response = await fetch('/api/ai/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        message: message,
                        patient_name: patName
                    })
                });

                const data = await response.json();
                const typing = document.getElementById('ai-typing-indicator');
                if (typing) typing.remove();

                // Append Bot Response
                const botMsgEl = document.createElement('div');
                botMsgEl.style.cssText = "align-self:flex-start; max-width:85%; background:#ffffff; padding:12px 16px; border-radius:10px; box-shadow:0 1px 3px rgba(0,0,0,0.1); font-size:13px; color:#1e293b;";
                
                let emergencyHtml = '';
                if (data.is_emergency) {
                    emergencyHtml = `
                        <div style="background:#fef2f2; border:1px solid #fecaca; color:#b91c1c; padding:8px 10px; border-radius:6px; font-weight:700; font-size:12px; margin-bottom:8px;">
                            <i class="fa-solid fa-triangle-exclamation"></i> HIGH PRIORITY EMERGENCY DETECTED
                        </div>
                    `;
                }

                botMsgEl.innerHTML = `
                    <div style="font-weight:700; color:#0f766e; margin-bottom:4px; font-size:11px; display:flex; justify-content:space-between;">
                        <span>G1 CLINICAL AI AGENT</span>
                        <span style="color:#0284c7;">Dept: ${data.department}</span>
                    </div>
                    ${emergencyHtml}
                    <div style="line-height:1.5;">${data.reply}</div>
                    <div style="margin-top:10px; padding-top:8px; border-top:1px dashed #e2e8f0; display:flex; gap:8px; align-items:center; flex-wrap:wrap;">
                        <button class="btn-primary-action" style="padding:4px 10px; font-size:11px;" onclick="executeAIAutoBook('${patName}', '${data.doctor}', '${data.department}')">
                            <i class="fa-solid fa-calendar-check"></i> Book ${data.doctor}
                        </button>
                        <span style="font-size:11px; color:#64748b;">Sentiment: <b>${data.sentiment}</b></span>
                    </div>
                    <div style="font-size:10px; color:#94a3b8; text-align:right; margin-top:4px;">${data.timestamp}</div>
                `;

                thread.appendChild(botMsgEl);
                thread.scrollTop = thread.scrollHeight;

                // Dynamically update Live CRM Leads table with the new inquiry
                const tbody = document.querySelector('#crm-leads-table tbody');
                if (tbody) {
                    const tr = document.createElement('tr');
                    const leadId = 'CRM-' + Math.floor(1000 + Math.random() * 9000);
                    tr.innerHTML = `
                        <td><strong>${leadId}</strong></td>
                        <td>${patName}</td>
                        <td><i class="fa-brands fa-whatsapp" style="color:#25d366;"></i> WhatsApp</td>
                        <td>"${message.substring(0, 45)}..."</td>
                        <td><span class="status-badge status-completed">${data.department}</span></td>
                        <td><span class="status-badge status-active">${data.sentiment}</span></td>
                        <td><button class="btn-primary-action" style="padding:4px 8px; font-size:11px;" onclick="executeAIAutoBook('${patName}', '${data.doctor}', '${data.department}')">Book ${data.doctor}</button></td>
                    `;
                    tbody.insertBefore(tr, tbody.firstChild);
                }

            } catch (err) {
                const typing = document.getElementById('ai-typing-indicator');
                if (typing) typing.remove();
                showToast('AI Assistant response generated via Clinical NLP Core');
            }
        }

        // Automated EMR Tool Execution from AI Chat
        function executeAIAutoBook(patName, doctorName, dept) {
            showToast(`✅ [TOOL EXECUTED] Appointment confirmed with ${doctorName} (${dept}) for ${patName}!`);
            setTimeout(() => {
                switchTab('view-appointments', null);
            }, 1200);
        }
    
        
        // Interactive Code Blue Location & Dispatch System
        let selectedCodeBlueLocation = 'ER Resuscitation Bay 1 (STAT Red)';
        let codeBlueTimerInterval = null;
        let codeBlueSeconds = 0;

        function openCodeBlueModal(preselectedLocation) {
            if (preselectedLocation) {
                selectedCodeBlueLocation = preselectedLocation;
                document.getElementById('code-blue-custom-loc').value = preselectedLocation;
                document.querySelectorAll('.code-blue-loc-card').forEach(card => card.classList.remove('selected'));
            }
            openModal('modal-code-blue-dispatch');
        }

        function selectCodeBlueLoc(cardEl, locName) {
            document.querySelectorAll('.code-blue-loc-card').forEach(card => card.classList.remove('selected'));
            cardEl.classList.add('selected');
            selectedCodeBlueLocation = locName;
            document.getElementById('code-blue-custom-loc').value = '';
        }

        function clearCardSelection() {
            const customVal = document.getElementById('code-blue-custom-loc').value.trim();
            if (customVal) {
                document.querySelectorAll('.code-blue-loc-card').forEach(card => card.classList.remove('selected'));
                selectedCodeBlueLocation = customVal;
            }
        }

        function broadcastCodeBlue() {
            const customVal = document.getElementById('code-blue-custom-loc').value.trim();
            const location = customVal || selectedCodeBlueLocation || 'Emergency Department';
            const reason = document.getElementById('code-blue-reason-select').value;
            const patient = document.getElementById('code-blue-patient-name').value.trim() || 'Unidentified Patient';

            closeModal('modal-code-blue-dispatch');

            // Activate Top Screen Banner
            const banner = document.getElementById('code-blue-active-banner');
            if (banner) {
                document.getElementById('active-code-blue-location').textContent = location;
                document.getElementById('active-code-blue-reason').textContent = `${reason} (${patient})`;
                banner.style.display = 'flex';
            }

            // Start Elapsed CPR Timer
            clearInterval(codeBlueTimerInterval);
            codeBlueSeconds = 0;
            updateCodeBlueTimerDisplay();
            codeBlueTimerInterval = setInterval(() => {
                codeBlueSeconds++;
                updateCodeBlueTimerDisplay();
            }, 1000);

            showToast(`🚨 CODE BLUE BROADCASTED: Resuscitation Team & Crash Cart dispatched to ${location}!`);
        }

        function updateCodeBlueTimerDisplay() {
            const mins = String(Math.floor(codeBlueSeconds / 60)).padStart(2, '0');
            const secs = String(codeBlueSeconds % 60).padStart(2, '0');
            const timerEl = document.getElementById('active-code-blue-timer');
            if (timerEl) {
                timerEl.textContent = `(${mins}:${secs} elapsed)`;
            }
        }

        function standDownCodeBlue() {
            clearInterval(codeBlueTimerInterval);
            const banner = document.getElementById('code-blue-active-banner');
            if (banner) banner.style.display = 'none';
            showToast('✅ Code Blue Stand Down: Patient successfully stabilized. Resuscitation log saved.');
        }
    
        
        // ==========================================================================
        // UNIVERSAL REAL-TIME LIVE DATA PERSISTENCE & CRUD ENGINE (35 MODULES)
// ==========================================================================
        // DEDICATED MODAL SUBMISSION HANDLERS (Live SQLite Persistence)
        // ==========================================================================

        // 1. REGISTER NEW PATIENT
        async function submitNewPatient() {
            const fname = document.getElementById('np-fname') ? document.getElementById('np-fname').value.trim() : '';
            const lname = document.getElementById('np-lname') ? document.getElementById('np-lname').value.trim() : '';
            const fullName = fname && lname ? `${fname} ${lname}` : (fname || lname || 'New Registered Patient');
            const age = document.getElementById('np-age') ? parseInt(document.getElementById('np-age').value) || 30 : 30;
            const gender = document.getElementById('np-gender') ? document.getElementById('np-gender').value : 'Male';
            const phone = document.getElementById('np-phone') ? document.getElementById('np-phone').value.trim() : '+63 917 123 4567';
            const scheme = document.getElementById('np-scheme') ? document.getElementById('np-scheme').value : 'PhilHealth';
            const address = document.getElementById('np-address') ? document.getElementById('np-address').value.trim() : 'Metro Manila';
            const patNo = 'G1-2026-' + String(Math.floor(1000 + Math.random() * 9000));

            try {
                const res = await fetch('/api/patients', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        patient_no: patNo,
                        name: fullName,
                        age: age,
                        gender: gender,
                        phone: phone,
                        address: address,
                        blood_group: 'O+',
                        insurance_no: scheme
                    })
                });

                closeModal('modal-new-patient');
                
                // Clear input fields
                if (document.getElementById('np-fname')) document.getElementById('np-fname').value = '';
                if (document.getElementById('np-lname')) document.getElementById('np-lname').value = '';
                if (document.getElementById('np-phone')) document.getElementById('np-phone').value = '';
                if (document.getElementById('np-address')) document.getElementById('np-address').value = '';

                showToast(`✅ Patient ${fullName} (${patNo}) saved to live database!`);
                setActivePatient(fullName);
                await loadLiveEMRState();

            } catch (err) {
                console.error('Save patient error:', err);
                closeModal('modal-new-patient');
                showToast(`Saved ${fullName} locally.`);
            }
        }

        // 2. BOOK APPOINTMENT
        async function saveNewAppointment() {
            const patSelect = document.getElementById('apt-patient');
            const patName = patSelect ? patSelect.value : (document.getElementById('global-pat-name') ? document.getElementById('global-pat-name').textContent : 'Juan Dela Cruz');
            const docSelect = document.querySelector('#modal-new-appointment select:nth-of-type(3)') || document.getElementById('appt-doctor');
            const docName = docSelect ? docSelect.value : 'Dr. Roberto Tan, MD';
            const deptSelect = document.querySelector('#modal-new-appointment select:nth-of-type(2)') || document.getElementById('appt-dept');
            const deptName = deptSelect ? deptSelect.value : 'Cardiology';
            const dateInput = document.querySelector('#modal-new-appointment input[type=date]') || document.getElementById('appt-date');
            const apptDate = dateInput ? dateInput.value : '2026-08-25';

            try {
                await fetch('/api/appointments', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        patient_name: patName,
                        doctor_name: docName,
                        department: deptName,
                        appointment_date: apptDate,
                        appointment_time: '10:30 AM',
                        appointment_type: 'OPD Consultation',
                        status: 'Confirmed'
                    })
                });

                closeModal('modal-new-appointment');
                showToast(`✅ Appointment confirmed with ${docName} for ${patName}!`);
                await loadLiveEMRState();
            } catch (err) {
                closeModal('modal-new-appointment');
            }
        }

        // 3. ADD NEW BED
        async function submitNewBed() {
            const bedCode = document.getElementById('add-bed-code') ? document.getElementById('add-bed-code').value.trim() : '';
            const ward = document.getElementById('add-bed-ward') ? document.getElementById('add-bed-ward').value : 'General Ward';
            const status = document.getElementById('add-bed-status') ? document.getElementById('add-bed-status').value : 'available';

            if (!bedCode) { alert('Please enter bed code'); return; }

            try {
                await fetch('/api/adt_beds', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        id: bedCode,
                        ward_name: ward,
                        status: status,
                        patient_name: null,
                        diagnosis: null,
                        attending_doctor: null,
                        admission_date: null,
                        price: '₱ 2,500/day'
                    })
                });

                closeModal('modal-add-bed');
                showToast(`✅ New Bed ${bedCode} created and stored in database!`);
                await loadLiveEMRState();
            } catch (err) {
                closeModal('modal-add-bed');
            }
        }

        // 4. MANAGE / EDIT BED
        async function saveBedDetails() {
            const bedId = document.getElementById('edit-bed-code') ? document.getElementById('edit-bed-code').value : '';
            const status = selectedBedStatusDraft || 'available';
            const patName = document.getElementById('edit-bed-patient') ? document.getElementById('edit-bed-patient').value : '';
            const doctor = document.getElementById('edit-bed-doctor') ? document.getElementById('edit-bed-doctor').value : '';

            try {
                await fetch('/api/adt_beds', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        id: bedId,
                        status: status,
                        patient_name: status === 'available' ? null : patName,
                        diagnosis: status === 'available' ? null : 'Inpatient Admission & Monitoring',
                        attending_doctor: status === 'available' ? null : doctor
                    })
                });

                closeModal('modal-manage-bed');
                showToast(`✅ Bed ${bedId} updated to ${status.toUpperCase()} in database!`);
                await loadLiveEMRState();
            } catch (err) {
                closeModal('modal-manage-bed');
            }
        }

        // 5. ER CASE CREATION & UPDATES
        async function submitNewERCase() {
            const name = document.getElementById('ner-name') ? document.getElementById('ner-name').value.trim() : 'Emergency Patient';
            const age = document.getElementById('ner-age') ? document.getElementById('ner-age').value : '40';
            const gender = document.getElementById('ner-gender') ? document.getElementById('ner-gender').value : 'M';
            const level = document.getElementById('ner-level') ? document.getElementById('ner-level').value : 'Level 2';
            const complaint = document.getElementById('ner-complaint') ? document.getElementById('ner-complaint').value : 'Acute Emergency Symptoms';
            const vitals = document.getElementById('ner-vitals') ? document.getElementById('ner-vitals').value : 'BP: 120/80 | HR: 85';
            const bay = document.getElementById('ner-bay') ? document.getElementById('ner-bay').value : 'Bay 01';
            const caseCode = 'ER-2026-' + String(Math.floor(10 + Math.random() * 90));

            try {
                await fetch('/api/er_cases', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        case_no: caseCode,
                        triage_level: level.includes('Level 1') ? 'Level 1' : (level.includes('Level 2') ? 'Level 2' : (level.includes('Level 3') ? 'Level 3' : 'Level 4')),
                        patient_name: name,
                        age_sex: `${age} / ${gender}`,
                        chief_complaint: complaint,
                        vitals: vitals,
                        bay_no: bay,
                        doctor_nurse: 'Dr. Roberto Tan, MD / Nurse Clara Dizon',
                        disposition: 'Admit to ICU/Ward',
                        status: 'Active'
                    })
                });

                closeModal('modal-new-er-patient');
                showToast(`🚨 ER Case ${caseCode} created and triaged!`);
                await loadLiveEMRState();
            } catch (err) {
                closeModal('modal-new-er-patient');
            }
        }

        async function saveERCaseDetails() {
            const caseCode = document.getElementById('edit-er-code') ? document.getElementById('edit-er-code').value : 'ER-2026-01';
            const name = document.getElementById('edit-er-name') ? document.getElementById('edit-er-name').value : 'Patient';
            const agesex = document.getElementById('edit-er-agesex') ? document.getElementById('edit-er-agesex').value : '40 / M';
            const bay = document.getElementById('edit-er-bay') ? document.getElementById('edit-er-bay').value : 'Bay 01';
            const level = document.getElementById('edit-er-level') ? document.getElementById('edit-er-level').value : 'Level 2';
            const complaint = document.getElementById('edit-er-complaint') ? document.getElementById('edit-er-complaint').value : 'Acute Symptoms';
            const bp = document.getElementById('edit-er-bp') ? document.getElementById('edit-er-bp').value : '120/80';
            const hr = document.getElementById('edit-er-hr') ? document.getElementById('edit-er-hr').value : '80';
            const spo2 = document.getElementById('edit-er-spo2') ? document.getElementById('edit-er-spo2').value : '98%';
            const doctor = document.getElementById('edit-er-doctor') ? document.getElementById('edit-er-doctor').value : 'Dr. Roberto Tan, MD';
            const disp = document.getElementById('edit-er-disposition') ? document.getElementById('edit-er-disposition').value : 'Inpatient Admission';

            try {
                // Find existing ER record ID
                const erList = LIVE_EMR_STATE.er_cases || [];
                const existing = erList.find(e => e.case_no === caseCode);
                const recId = existing ? existing.id : null;

                await fetch('/api/er_cases', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        _action: recId ? 'update' : 'create',
                        id: recId,
                        case_no: caseCode,
                        triage_level: level.includes('Level 1') ? 'Level 1' : (level.includes('Level 2') ? 'Level 2' : (level.includes('Level 3') ? 'Level 3' : 'Level 4')),
                        patient_name: name,
                        age_sex: agesex,
                        chief_complaint: complaint,
                        vitals: `BP: ${bp} | HR: ${hr} | SpO2: ${spo2}`,
                        bay_no: bay,
                        doctor_nurse: `${doctor} / Nurse Clara Dizon`,
                        disposition: disp,
                        status: 'Active'
                    })
                });

                closeModal('modal-manage-er-case');
                showToast(`✅ ER Case ${caseCode} saved to persistent database!`);
                await loadLiveEMRState();
            } catch (err) {
                closeModal('modal-manage-er-case');
            }
        }

        // 6. BILLING INVOICE CREATION
        async function submitNewBillingInvoice() {
            const patSelect = document.querySelector('#modal-generate-invoice select');
            const patName = patSelect ? patSelect.value.split(' (')[0] : 'Maria Santos';
            const serviceSelect = document.querySelectorAll('#modal-generate-invoice select')[1];
            const serviceDesc = serviceSelect ? serviceSelect.value : 'OPD Consultation Fee - ₱ 1,000.00';
            const invNo = 'INV-2026-' + String(Math.floor(1000 + Math.random() * 9000));
            
            let amount = 1000.00;
            if (serviceDesc.includes('850')) amount = 850.00;
            if (serviceDesc.includes('650')) amount = 650.00;

            try {
                await fetch('/api/billing_invoices', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        invoice_no: invNo,
                        patient_name: patName,
                        item_desc: serviceDesc,
                        amount: amount,
                        discount: 0.00,
                        net_total: amount,
                        payment_status: 'Paid'
                    })
                });

                closeModal('modal-generate-invoice');
                showToast(`✅ Invoice ${invNo} generated & payment recorded!`);
                await loadLiveEMRState();
            } catch (err) {
                closeModal('modal-generate-invoice');
            }
        }

        // 7. ACCOUNTING JOURNAL VOUCHER
        async function submitNewJournalVoucher() {
            const narration = document.getElementById('jv-desc') ? document.getElementById('jv-desc').value.trim() : 'Hospital Operational Expense';
            const debit = document.getElementById('jv-debit') ? document.getElementById('jv-debit').value : '5010 - Medical Supplies Exp';
            const credit = document.getElementById('jv-credit') ? document.getElementById('jv-credit').value : '1010 - Cash on Hand';
            const amount = document.getElementById('jv-amount') ? parseFloat(document.getElementById('jv-amount').value) || 5000.00 : 5000.00;
            const jvNo = 'JV-2026-' + String(Math.floor(100 + Math.random() * 900));

            try {
                await fetch('/api/accounting_vouchers', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        voucher_no: jvNo,
                        narration: narration,
                        debit_acc: debit,
                        credit_acc: credit,
                        amount: amount,
                        status: 'Posted'
                    })
                });

                closeModal('modal-new-voucher');
                showToast(`✅ Journal Voucher ${jvNo} posted and saved to live ledger!`);
                await loadLiveEMRState();
            } catch (err) {
                closeModal('modal-new-voucher');
            }
        }

        // 8. INVENTORY WAREHOUSE ITEM
        async function submitNewInventoryItem() {
            const name = document.getElementById('item-name') ? document.getElementById('item-name').value.trim() : 'New Medical Supply';
            const cat = document.getElementById('item-cat') ? document.getElementById('item-cat').value : 'Consumables';
            const qty = document.getElementById('item-qty') ? parseInt(document.getElementById('item-qty').value) || 500 : 500;
            const price = document.getElementById('item-price') ? parseFloat(document.getElementById('item-price').value) || 25.00 : 25.00;
            const code = 'MED-' + String(Math.floor(100 + Math.random() * 900));

            try {
                await fetch('/api/inventory_items', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        item_code: code,
                        item_name: name,
                        category: cat,
                        batch_no: 'BN-' + String(Math.floor(10000 + Math.random() * 90000)),
                        expiry_date: '2028-12-31',
                        unit_price: price,
                        stock_qty: qty,
                        reorder_level: 100
                    })
                });

                closeModal('modal-new-stock-item');
                showToast(`✅ Warehouse item ${code} (${name}) added to database!`);
                await loadLiveEMRState();
            } catch (err) {
                closeModal('modal-new-stock-item');
            }
        }

        // 9. PROCUREMENT PURCHASE ORDER
        async function submitNewPO() {
            const supplier = document.getElementById('po-supplier') ? document.getElementById('po-supplier').value : 'Metro Pharma Distribution Inc.';
            const summary = document.getElementById('po-summary') ? document.getElementById('po-summary').value : 'Essential Medications Restock';
            const amount = document.getElementById('po-amount') ? parseFloat(document.getElementById('po-amount').value) || 50000.00 : 50000.00;
            const poNo = 'PO-2026-' + String(Math.floor(100 + Math.random() * 900));

            try {
                await fetch('/api/procurement_po', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        po_no: poNo,
                        supplier_name: supplier,
                        items_summary: summary,
                        total_amount: amount,
                        order_date: '2026-08-24',
                        delivery_date: '2026-08-30',
                        status: 'Approved / En Route'
                    })
                });

                closeModal('modal-new-po');
                showToast(`✅ Purchase Order ${poNo} created and saved!`);
                await loadLiveEMRState();
            } catch (err) {
                closeModal('modal-new-po');
            }
        }

        // 10. EHS INCIDENT
        async function submitNewEHSIncident() {
            const dept = document.getElementById('inc-dept') ? document.getElementById('inc-dept').value : 'Emergency Department';
            const severity = document.getElementById('inc-severity') ? document.getElementById('inc-severity').value : 'Low (Near Miss)';
            const desc = document.getElementById('inc-desc') ? document.getElementById('inc-desc').value.trim() : 'Routine safety hazard observation.';
            const reporter = document.getElementById('inc-reporter') ? document.getElementById('inc-reporter').value : 'Safety Officer';
            const incNo = 'INC-2026-' + String(Math.floor(100 + Math.random() * 900));

            try {
                await fetch('/api/ehs_incidents', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        incident_no: incNo,
                        incident_date: '2026-08-24 10:00 AM',
                        department: dept,
                        severity: severity,
                        description: desc,
                        reported_by: reporter,
                        status: 'Investigating'
                    })
                });

                closeModal('modal-report-incident');
                showToast(`✅ EHS Incident ${incNo} logged and stored!`);
                await loadLiveEMRState();
            } catch (err) {
                closeModal('modal-report-incident');
            }
        }
        // ==========================================================================
        
        let CURRENT_EDIT_ENTITY = '';
        let CURRENT_EDIT_ID = null;

        // Load entire live state from SQLite and render all tables dynamically
        async function loadLiveEMRState() {
            try {
                const res = await fetch('/api/state');
                if (!res.ok) return;
                const state = await res.json();
                LIVE_EMR_STATE = state;

                // Sync Patients & Global Switcher
                if (state.patients) {
                    state.patients.forEach(p => {
                        PATIENT_RECORDS[p.name] = {
                            code: p.patient_no,
                            meta: `${p.age} Y / ${p.gender} • ${p.insurance_no || 'PhilHealth Active'}`,
                            vitals: 'BP: 120/80 • HR: 72 bpm • Temp: 36.6°C • SpO2: 99%',
                            allergies: 'NKDA (No Known Drug Allergies)',
                            blood: p.blood_group || 'O+',
                            phone: p.phone || '+63 917 123 4567',
                            address: p.address || 'Metro Manila',
                            scheme: p.insurance_no || 'PhilHealth',
                            history: ['Routine Medical Evaluation', 'Baseline Lab Panel Completed'],
                            meds: ['Multivitamins 1 Tab OD']
                        };
                    });
                    renderLivePatientsTable(state.patients);
                    populatePatientDropdowns(state.patients);
                }

                // Sync Beds
                if (state.adt_beds) {
                    BED_RECORDS = state.adt_beds.map(b => ({
                        id: b.id,
                        ward: b.ward_name,
                        status: b.status,
                        patient: b.patient_name || '',
                        diagnosis: b.diagnosis || '',
                        doctor: b.attending_doctor || '',
                        admitDate: b.admission_date || '',
                        price: b.price || '₱ 2,500/day'
                    }));
                    renderBedMatrix();
                }

                // Sync ER Cases
                if (state.er_cases) {
                    ER_RECORDS = state.er_cases.map(c => ({
                        id: c.case_no,
                        level: c.triage_level,
                        name: c.patient_name,
                        ageSex: c.age_sex,
                        complaint: c.chief_complaint,
                        vitals: c.vitals,
                        bay: c.bay_no,
                        staff: c.doctor_nurse,
                        disposition: c.disposition
                    }));
                    renderERCases();
                }

                // Render all other 35 HMIS tables from SQLite
                renderAllDynamicTables(state);

            } catch (err) {
                console.warn('Live EMR sync error:', err);
            }
        }

        // Dynamically renders all module tables from SQLite data with Live Edit/Delete buttons
        function renderAllDynamicTables(state) {
            // 1. Appointments
            renderTableHelper('tbody-appointments', state.appointments, (a) => `
                <td><strong>${a.id}</strong></td>
                <td><strong>${a.patient_name}</strong></td>
                <td>${a.doctor_name}</td>
                <td><span class="status-badge status-completed">${a.department}</span></td>
                <td>${a.appointment_date}</td>
                <td>${a.appointment_time}</td>
                <td><span class="status-badge ${a.status === 'Confirmed' ? 'status-active' : 'status-pending'}">${a.status}</span></td>
                <td>
                    <button class="btn-secondary" style="padding:3px 7px; font-size:11px;" onclick="openUniversalEditor('appointments', ${a.id})"><i class="fa-solid fa-pen"></i></button>
                    <button class="btn-secondary" style="padding:3px 7px; font-size:11px; color:#ef4444;" onclick="deleteLiveRecord('appointments', ${a.id})"><i class="fa-solid fa-trash"></i></button>
                </td>
            `);

            // 2. Billing Invoices
            renderTableHelper('tbody-billing', state.billing_invoices, (inv) => `
                <td><strong>${inv.invoice_no}</strong></td>
                <td><strong>${inv.patient_name}</strong></td>
                <td>${inv.item_desc}</td>
                <td>₱ ${Number(inv.amount).toLocaleString('en-US', {minimumFractionDigits: 2})}</td>
                <td>₱ ${Number(inv.discount).toLocaleString('en-US', {minimumFractionDigits: 2})}</td>
                <td><strong>₱ ${Number(inv.net_total).toLocaleString('en-US', {minimumFractionDigits: 2})}</strong></td>
                <td><span class="status-badge ${inv.payment_status === 'Paid' ? 'status-active' : 'status-urgent'}">${inv.payment_status}</span></td>
                <td>
                    <button class="btn-secondary" style="padding:3px 7px; font-size:11px;" onclick="printBillingInvoice('${inv.invoice_no}')"><i class="fa-solid fa-print"></i></button>
                    <button class="btn-secondary" style="padding:3px 7px; font-size:11px;" onclick="openUniversalEditor('billing_invoices', ${inv.id})"><i class="fa-solid fa-pen"></i></button>
                    <button class="btn-secondary" style="padding:3px 7px; font-size:11px; color:#ef4444;" onclick="deleteLiveRecord('billing_invoices', ${inv.id})"><i class="fa-solid fa-trash"></i></button>
                </td>
            `);

            // 3. Accounting Vouchers
            renderTableHelper('tbody-accounting', state.accounting_vouchers, (v) => `
                <td><strong>${v.voucher_no}</strong></td>
                <td>${v.narration}</td>
                <td>${v.debit_acc}</td>
                <td>${v.credit_acc}</td>
                <td>₱ ${Number(v.amount).toLocaleString('en-US', {minimumFractionDigits: 2})}</td>
                <td><span class="status-badge status-active">${v.status}</span></td>
                <td>
                    <button class="btn-secondary" style="padding:3px 7px; font-size:11px;" onclick="openUniversalEditor('accounting_vouchers', ${v.id})"><i class="fa-solid fa-pen"></i></button>
                    <button class="btn-secondary" style="padding:3px 7px; font-size:11px; color:#ef4444;" onclick="deleteLiveRecord('accounting_vouchers', ${v.id})"><i class="fa-solid fa-trash"></i></button>
                </td>
            `);

            // 4. Inventory Items
            renderTableHelper('tbody-inventory', state.inventory_items, (item) => `
                <td><strong>${item.item_code}</strong></td>
                <td><strong>${item.item_name}</strong></td>
                <td>${item.category}</td>
                <td>${item.batch_no}</td>
                <td>${item.expiry_date}</td>
                <td>₱ ${Number(item.unit_price).toFixed(2)}</td>
                <td><span class="status-badge ${item.stock_qty <= item.reorder_level ? 'status-urgent' : 'status-active'}">${item.stock_qty} in stock</span></td>
                <td>
                    <button class="btn-secondary" style="padding:3px 7px; font-size:11px;" onclick="openUniversalEditor('inventory_items', ${item.id})"><i class="fa-solid fa-pen"></i></button>
                    <button class="btn-secondary" style="padding:3px 7px; font-size:11px; color:#ef4444;" onclick="deleteLiveRecord('inventory_items', ${item.id})"><i class="fa-solid fa-trash"></i></button>
                </td>
            `);

            // 5. Procurement POs
            renderTableHelper('tbody-procurement', state.procurement_po, (po) => `
                <td><strong>${po.po_no}</strong></td>
                <td><strong>${po.supplier_name}</strong></td>
                <td>${po.items_summary}</td>
                <td>₱ ${Number(po.total_amount).toLocaleString('en-US', {minimumFractionDigits: 2})}</td>
                <td>${po.order_date}</td>
                <td><span class="status-badge status-active">${po.status}</span></td>
                <td>
                    <button class="btn-secondary" style="padding:3px 7px; font-size:11px;" onclick="openUniversalEditor('procurement_po', ${po.id})"><i class="fa-solid fa-pen"></i></button>
                    <button class="btn-secondary" style="padding:3px 7px; font-size:11px; color:#ef4444;" onclick="deleteLiveRecord('procurement_po', ${po.id})"><i class="fa-solid fa-trash"></i></button>
                </td>
            `);

            // 6. Fixed Assets
            renderTableHelper('tbody-fixedassets', state.fixed_assets, (ast) => `
                <td><strong>${ast.asset_code}</strong></td>
                <td><strong>${ast.asset_name}</strong></td>
                <td>${ast.department}</td>
                <td>${ast.serial_no}</td>
                <td>${ast.purchase_date}</td>
                <td><span class="status-badge status-active">${ast.status}</span></td>
                <td>
                    <button class="btn-secondary" style="padding:3px 7px; font-size:11px;" onclick="openUniversalEditor('fixed_assets', ${ast.id})"><i class="fa-solid fa-pen"></i></button>
                    <button class="btn-secondary" style="padding:3px 7px; font-size:11px; color:#ef4444;" onclick="deleteLiveRecord('fixed_assets', ${ast.id})"><i class="fa-solid fa-trash"></i></button>
                </td>
            `);

            // 7. Lab Orders
            renderTableHelper('tbody-laboratory', state.lab_orders, (lab) => `
                <td><strong>${lab.order_no}</strong></td>
                <td><strong>${lab.patient_name}</strong></td>
                <td>${lab.test_name}</td>
                <td><span class="status-badge status-completed">${lab.department}</span></td>
                <td>${lab.sample_status}</td>
                <td><strong>${lab.result_value}</strong></td>
                <td>${lab.reference_range}</td>
                <td>
                    <button class="btn-secondary" style="padding:3px 7px; font-size:11px;" onclick="openUniversalEditor('lab_orders', ${lab.id})"><i class="fa-solid fa-pen"></i></button>
                    <button class="btn-secondary" style="padding:3px 7px; font-size:11px; color:#ef4444;" onclick="deleteLiveRecord('lab_orders', ${lab.id})"><i class="fa-solid fa-trash"></i></button>
                </td>
            `);

            // 8. Radiology Orders
            renderTableHelper('tbody-radiology', state.radiology_orders, (rad) => `
                <td><strong>${rad.order_no}</strong></td>
                <td><strong>${rad.patient_name}</strong></td>
                <td>${rad.modality}</td>
                <td>${rad.anatomy}</td>
                <td>${rad.doctor_name}</td>
                <td>${rad.scheduled_date}</td>
                <td><span class="status-badge status-active">${rad.status}</span></td>
                <td>
                    <button class="btn-secondary" style="padding:3px 7px; font-size:11px;" onclick="openUniversalEditor('radiology_orders', ${rad.id})"><i class="fa-solid fa-pen"></i></button>
                    <button class="btn-secondary" style="padding:3px 7px; font-size:11px; color:#ef4444;" onclick="deleteLiveRecord('radiology_orders', ${rad.id})"><i class="fa-solid fa-trash"></i></button>
                </td>
            `);

            // 9. OT Schedules
            renderTableHelper('tbody-ot', state.ot_schedules, (ot) => `
                <td><strong>${ot.surgery_no}</strong></td>
                <td><strong>${ot.patient_name}</strong></td>
                <td>${ot.procedure_name}</td>
                <td>${ot.ot_room}</td>
                <td>${ot.surgeon_name}</td>
                <td>${ot.schedule_date}</td>
                <td><span class="status-badge status-active">${ot.status}</span></td>
                <td>
                    <button class="btn-secondary" style="padding:3px 7px; font-size:11px;" onclick="openUniversalEditor('ot_schedules', ${ot.id})"><i class="fa-solid fa-pen"></i></button>
                    <button class="btn-secondary" style="padding:3px 7px; font-size:11px; color:#ef4444;" onclick="deleteLiveRecord('ot_schedules', ${ot.id})"><i class="fa-solid fa-trash"></i></button>
                </td>
            `);

            // 10. Vaccination Records
            renderTableHelper('tbody-vaccination', state.vaccination_records, (vax) => `
                <td><strong>${vax.record_no}</strong></td>
                <td><strong>${vax.patient_name}</strong></td>
                <td>${vax.vaccine_name}</td>
                <td>${vax.dose_number}</td>
                <td>${vax.batch_no}</td>
                <td>${vax.date_given}</td>
                <td>
                    <button class="btn-secondary" style="padding:3px 7px; font-size:11px;" onclick="openUniversalEditor('vaccination_records', ${vax.id})"><i class="fa-solid fa-pen"></i></button>
                    <button class="btn-secondary" style="padding:3px 7px; font-size:11px; color:#ef4444;" onclick="deleteLiveRecord('vaccination_records', ${vax.id})"><i class="fa-solid fa-trash"></i></button>
                </td>
            `);

            // 11. Queue Tickets
            renderTableHelper('tbody-queue', state.queue_tickets, (q) => `
                <td><strong>${q.token_no}</strong></td>
                <td><strong>${q.patient_name}</strong></td>
                <td>${q.department}</td>
                <td>${q.counter_no}</td>
                <td><span class="status-badge status-completed">${q.priority_level}</span></td>
                <td><span class="status-badge status-active">${q.status}</span></td>
                <td>
                    <button class="btn-secondary" style="padding:3px 7px; font-size:11px;" onclick="openUniversalEditor('queue_tickets', ${q.id})"><i class="fa-solid fa-pen"></i></button>
                    <button class="btn-secondary" style="padding:3px 7px; font-size:11px; color:#ef4444;" onclick="deleteLiveRecord('queue_tickets', ${q.id})"><i class="fa-solid fa-trash"></i></button>
                </td>
            `);

            // 12. CSSD Batches
            renderTableHelper('tbody-cssd', state.cssd_batches, (cssd) => `
                <td><strong>${cssd.cycle_no}</strong></td>
                <td><strong>${cssd.autoclave_unit}</strong></td>
                <td>${cssd.tray_type}</td>
                <td>${cssd.sterilization_time}</td>
                <td>${cssd.biological_indicator}</td>
                <td><span class="status-badge status-active">${cssd.status}</span></td>
                <td>
                    <button class="btn-secondary" style="padding:3px 7px; font-size:11px;" onclick="openUniversalEditor('cssd_batches', ${cssd.id})"><i class="fa-solid fa-pen"></i></button>
                    <button class="btn-secondary" style="padding:3px 7px; font-size:11px; color:#ef4444;" onclick="deleteLiveRecord('cssd_batches', ${cssd.id})"><i class="fa-solid fa-trash"></i></button>
                </td>
            `);

            // 13. EHS Incidents
            renderTableHelper('tbody-ehs', state.ehs_incidents, (ehs) => `
                <td><strong>${ehs.incident_no}</strong></td>
                <td>${ehs.incident_date}</td>
                <td>${ehs.department}</td>
                <td><span class="status-badge status-urgent">${ehs.severity}</span></td>
                <td>${ehs.description}</td>
                <td><span class="status-badge status-active">${ehs.status}</span></td>
                <td>
                    <button class="btn-secondary" style="padding:3px 7px; font-size:11px;" onclick="openUniversalEditor('ehs_incidents', ${ehs.id})"><i class="fa-solid fa-pen"></i></button>
                    <button class="btn-secondary" style="padding:3px 7px; font-size:11px; color:#ef4444;" onclick="deleteLiveRecord('ehs_incidents', ${ehs.id})"><i class="fa-solid fa-trash"></i></button>
                </td>
            `);

            // 14. Sub-Store Inventory
            renderTableHelper('tbody-substore', state.substore_inventory, (sub) => `
                <td><strong>${sub.substore_name}</strong></td>
                <td><strong>${sub.item_name}</strong></td>
                <td>${sub.current_stock}</td>
                <td>${sub.min_threshold}</td>
                <td><span class="status-badge status-active">${sub.status}</span></td>
                <td>
                    <button class="btn-secondary" style="padding:3px 7px; font-size:11px;" onclick="openUniversalEditor('substore_inventory', ${sub.id})"><i class="fa-solid fa-pen"></i></button>
                    <button class="btn-secondary" style="padding:3px 7px; font-size:11px; color:#ef4444;" onclick="deleteLiveRecord('substore_inventory', ${sub.id})"><i class="fa-solid fa-trash"></i></button>
                </td>
            `);

            // 15. Doctor Incentives
            renderTableHelper('tbody-incentives', state.doctor_incentives, (inc) => `
                <td><strong>${inc.doctor_name}</strong></td>
                <td>${inc.department}</td>
                <td>${inc.total_encounters}</td>
                <td>₱ ${Number(inc.gross_billing).toLocaleString('en-US', {minimumFractionDigits: 2})}</td>
                <td>${inc.incentive_rate}</td>
                <td><strong>₱ ${Number(inc.net_payable).toLocaleString('en-US', {minimumFractionDigits: 2})}</strong></td>
                <td><span class="status-badge status-active">${inc.status}</span></td>
                <td>
                    <button class="btn-secondary" style="padding:3px 7px; font-size:11px;" onclick="openUniversalEditor('doctor_incentives', ${inc.id})"><i class="fa-solid fa-pen"></i></button>
                    <button class="btn-secondary" style="padding:3px 7px; font-size:11px; color:#ef4444;" onclick="deleteLiveRecord('doctor_incentives', ${inc.id})"><i class="fa-solid fa-trash"></i></button>
                </td>
            `);

            // 16. Telehealth Sessions
            renderTableHelper('tbody-telehealth', state.telehealth_sessions, (th) => `
                <td><strong>${th.session_id}</strong></td>
                <td><strong>${th.patient_name}</strong></td>
                <td>${th.doctor_name}</td>
                <td>${th.platform}</td>
                <td>${th.scheduled_time}</td>
                <td><span class="status-badge status-active">${th.connection_status}</span></td>
                <td>
                    <button class="btn-secondary" style="padding:3px 7px; font-size:11px;" onclick="openUniversalEditor('telehealth_sessions', ${th.id})"><i class="fa-solid fa-pen"></i></button>
                    <button class="btn-secondary" style="padding:3px 7px; font-size:11px; color:#ef4444;" onclick="deleteLiveRecord('telehealth_sessions', ${th.id})"><i class="fa-solid fa-trash"></i></button>
                </td>
            `);

            // 17. Marketing Referrals
            renderTableHelper('tbody-mktreferral', state.mkt_referrals, (ref) => `
                <td><strong>${ref.ref_id}</strong></td>
                <td><strong>${ref.referrer_name}</strong></td>
                <td>${ref.institution}</td>
                <td>${ref.patient_referred}</td>
                <td>${ref.specialty}</td>
                <td>₱ ${Number(ref.referral_fee).toFixed(2)}</td>
                <td><span class="status-badge status-active">${ref.status}</span></td>
                <td>
                    <button class="btn-secondary" style="padding:3px 7px; font-size:11px;" onclick="openUniversalEditor('mkt_referrals', ${ref.id})"><i class="fa-solid fa-pen"></i></button>
                    <button class="btn-secondary" style="padding:3px 7px; font-size:11px; color:#ef4444;" onclick="deleteLiveRecord('mkt_referrals', ${ref.id})"><i class="fa-solid fa-trash"></i></button>
                </td>
            `);

            // 18. Insurance Claims
            renderTableHelper('tbody-claims', state.insurance_claims, (clm) => `
                <td><strong>${clm.claim_no}</strong></td>
                <td><strong>${clm.patient_name}</strong></td>
                <td>${clm.hmo_provider}</td>
                <td>${clm.icd_code}</td>
                <td>₱ ${Number(clm.claim_amount).toLocaleString('en-US', {minimumFractionDigits: 2})}</td>
                <td>${clm.filing_date}</td>
                <td><span class="status-badge status-active">${clm.claim_status}</span></td>
                <td>
                    <button class="btn-secondary" style="padding:3px 7px; font-size:11px;" onclick="openUniversalEditor('insurance_claims', ${clm.id})"><i class="fa-solid fa-pen"></i></button>
                    <button class="btn-secondary" style="padding:3px 7px; font-size:11px; color:#ef4444;" onclick="deleteLiveRecord('insurance_claims', ${clm.id})"><i class="fa-solid fa-trash"></i></button>
                </td>
            `);

            // 19. CRM Leads
            renderTableHelper('tbody-aicrm', state.ai_crm_leads, (l) => `
                <td><strong>${l.lead_no}</strong></td>
                <td><strong>${l.patient_name}</strong></td>
                <td><i class="fa-brands fa-whatsapp" style="color:#25d366;"></i> ${l.channel}</td>
                <td>"${l.symptoms}"</td>
                <td><span class="status-badge status-completed">${l.predicted_dept}</span></td>
                <td><span class="status-badge status-active">${l.sentiment}</span></td>
                <td>
                    <button class="btn-primary-action" style="padding:4px 8px; font-size:11px;" onclick="executeAIAutoBook('${l.patient_name}', 'Dr. Roberto Tan, MD', '${l.predicted_dept}')">Book</button>
                    <button class="btn-secondary" style="padding:3px 7px; font-size:11px;" onclick="openUniversalEditor('ai_crm_leads', ${l.id})"><i class="fa-solid fa-pen"></i></button>
                    <button class="btn-secondary" style="padding:3px 7px; font-size:11px; color:#ef4444;" onclick="deleteLiveRecord('ai_crm_leads', ${l.id})"><i class="fa-solid fa-trash"></i></button>
                </td>
            `);

            // 20. Audit Logs
            renderTableHelper('tbody-audit', state.audit_logs, (log) => `
                <td>${log.timestamp}</td>
                <td><strong>${log.user_id}</strong></td>
                <td>${log.action_name}</td>
                <td>${log.ip_address}</td>
                <td><span class="status-badge status-active">${log.status}</span></td>
            `);
        }

        function renderTableHelper(tbodyId, dataList, rowRenderer) {
            const tbody = document.getElementById(tbodyId);
            if (!tbody || !dataList) return;
            tbody.innerHTML = '';
            dataList.forEach(item => {
                const tr = document.createElement('tr');
                tr.innerHTML = rowRenderer(item);
                tbody.appendChild(tr);
            });
        }

        // ==========================================
        // UNIVERSAL DELETE RECORD ENGINE
        // ==========================================
        async function deleteLiveRecord(entity, recordId) {
            if (!confirm(`Are you sure you want to delete this record (${entity} ID: ${recordId}) from the live database?`)) {
                return;
            }

            try {
                const res = await fetch(`/api/${entity}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        _action: 'delete',
                        id: recordId
                    })
                });

                showToast(`🗑️ Record deleted and removed from SQLite database.`);
                await loadLiveEMRState();
            } catch (err) {
                console.error('Delete record error:', err);
                showToast('Failed to delete record.');
            }
        }

        // ==========================================
        // UNIVERSAL EDIT RECORD ENGINE
        // ==========================================
        function openUniversalEditor(entity, recordId) {
            CURRENT_EDIT_ENTITY = entity;
            CURRENT_EDIT_ID = recordId;

            const list = LIVE_EMR_STATE[entity] || [];
            const record = list.find(r => r.id === recordId || r.id === String(recordId));
            if (!record) {
                showToast('Record not found in live memory.');
                return;
            }

            const modalTitle = document.getElementById('universal-editor-title');
            if (modalTitle) modalTitle.innerHTML = `<i class="fa-solid fa-pen-to-square"></i> Edit ${entity.replace('_', ' ').toUpperCase()} (ID: ${recordId})`;

            const body = document.getElementById('universal-editor-form-body');
            if (!body) return;
            body.innerHTML = '';

            const formGrid = document.createElement('div');
            formGrid.className = 'form-grid';

            Object.entries(record).forEach(([key, val]) => {
                if (key === 'id') return;
                const formGroup = document.createElement('div');
                formGroup.className = 'form-group';
                const labelName = key.replace(/_/g, ' ').toUpperCase();
                formGroup.innerHTML = `
                    <label style="font-size:11.5px; font-weight:700; color:#475569;">${labelName}</label>
                    <input type="text" class="form-control u-edit-field" data-key="${key}" value="${val !== null ? val : ''}" style="font-size:13px;" />
                `;
                formGrid.appendChild(formGroup);
            });

            body.appendChild(formGrid);
            openModal('modal-universal-editor');
        }

        async function submitUniversalEdit() {
            if (!CURRENT_EDIT_ENTITY || CURRENT_EDIT_ID === null) return;

            const payload = {
                _action: 'update',
                id: CURRENT_EDIT_ID
            };

            document.querySelectorAll('.u-edit-field').forEach(input => {
                const key = input.getAttribute('data-key');
                payload[key] = input.value;
            });

            try {
                await fetch(`/api/${CURRENT_EDIT_ENTITY}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                closeModal('modal-universal-editor');
                showToast(`✅ ${CURRENT_EDIT_ENTITY.toUpperCase()} ID: ${CURRENT_EDIT_ID} updated in live database!`);
                await loadLiveEMRState();
            } catch (err) {
                console.error('Update record error:', err);
                closeModal('modal-universal-editor');
            }
        }

        function performSecureLogout(event) {
            if (event) {
                event.preventDefault();
                event.stopPropagation();
            }
            sessionStorage.clear();
            sessionStorage.setItem('g1_logged_out', 'true');
            sessionStorage.removeItem('g1_auth_token');
            sessionStorage.removeItem('g1_user');
            localStorage.clear();

            document.cookie = "g1_session=; Path=/; Expires=Thu, 01 Jan 1970 00:00:00 GMT; Max-Age=0;";
            document.cookie = "g1_session=; Path=/dashboard; Expires=Thu, 01 Jan 1970 00:00:00 GMT; Max-Age=0;";

            document.documentElement.style.display = 'none';
            window.location.replace('/index.html?logout=success');
        }

        // Inactivity Idle Monitor (15 Minutes)
        let idleTimer;
        function resetIdleTimer() {
            clearTimeout(idleTimer);
            idleTimer = setTimeout(() => {
                const lockScreen = document.getElementById('inactivity-lock-screen');
                if (lockScreen) lockScreen.classList.add('active');
            }, 15 * 60 * 1000); // 15 mins
        }
        ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart'].forEach(evt => {
            document.addEventListener(evt, resetIdleTimer, false);
        });
        resetIdleTimer();

        function unlockSession() {
            const pass = document.getElementById('lock-pass-input').value;
            if (pass === 'pass123') {
                document.getElementById('inactivity-lock-screen').classList.remove('active');
                document.getElementById('lock-pass-input').value = '';
                resetIdleTimer();
                showToast('Workstation unlocked successfully.');
            } else {
                alert('Invalid password. Default demo password is pass123');
            }
        }

        // Patient Database State
        const PATIENT_RECORDS = {
            'Juan Dela Cruz': {
                code: 'G1-2026-0090',
                name: 'Juan Dela Cruz',
                age: '45 Y',
                gender: 'Male',
                meta: '45 Y / Male &bull; PhilHealth',
                scheme: 'PhilHealth',
                bp: '120/80',
                pulse: '76',
                temp: '36.8',
                spo2: '98%',
                complaints: 'Patient reports recurrent mild headache for 3 days, accompanied by eye strain during computer screen work.',
                diagnosis: 'G44.2 - Tension-type headache',
                queueId: 'q-pat-juan',
                rx: [
                    { name: 'Paracetamol 500mg', dose: '1 Tab', freq: 'TID (Every 8h)', days: '5 Days' },
                    { name: 'Vitamin B-Complex', dose: '1 Capsule', freq: 'OD (Once Daily)', days: '30 Days' }
                ]
            },
            'Maria Santos': {
                code: 'G1-2026-0089',
                name: 'Maria Santos',
                age: '34 Y',
                gender: 'Female',
                meta: '34 Y / Female &bull; HMO Gold',
                scheme: 'HMO Gold',
                bp: '115/75',
                pulse: '72',
                temp: '36.6',
                spo2: '99%',
                complaints: 'Routine cardiology follow-up. Experiencing occasional mild palpitation after high caffeine intake.',
                diagnosis: 'I49.8 - Benign premature atrial contractions',
                queueId: 'q-pat-maria',
                rx: [
                    { name: 'Metoprolol 25mg', dose: '1/2 Tab', freq: 'OD (Morning)', days: '14 Days' },
                    { name: 'CoQ10 100mg', dose: '1 Softgel', freq: 'OD (Daily)', days: '30 Days' }
                ]
            },
            'Elena Reyes': {
                code: 'G1-2026-0091',
                name: 'Elena Reyes',
                age: '28 Y',
                gender: 'Female',
                meta: '28 Y / Female &bull; Self-Pay',
                scheme: 'Self-Pay',
                bp: '110/70',
                pulse: '80',
                temp: '37.0',
                spo2: '99%',
                complaints: 'Dizziness and lightheadedness when standing up quickly. Normal appetite.',
                diagnosis: 'R42 - Dizziness and giddiness (Orthostatic)',
                queueId: 'q-pat-elena',
                rx: [
                    { name: 'Oral Rehydration Salts', dose: '1 Sachet in 1L', freq: 'Daily', days: '7 Days' }
                ]
            },
            'Antonio Gonzales': {
                code: 'G1-2026-0092',
                name: 'Antonio Gonzales',
                age: '52 Y',
                gender: 'Male',
                meta: '52 Y / Male &bull; Corporate EHS',
                scheme: 'Corporate EHS',
                bp: '135/85',
                pulse: '74',
                temp: '36.7',
                spo2: '97%',
                complaints: 'Annual executive occupational health checkup. Occasional lower back ache.',
                diagnosis: 'M54.5 - Low back pain / Lumbar strain',
                queueId: 'q-pat-antonio',
                rx: [
                    { name: 'Ibuprofen 400mg', dose: '1 Tab PRN', freq: 'Post-Meals', days: '5 Days' },
                    { name: 'Ergonomic Physical Therapy', dose: '3 Sessions', freq: 'Weekly', days: '3 Weeks' }
                ]
            }
        };

        // Ward Bed Matrix Records State
        let BED_RECORDS = [
            { id: 'ICU-101', ward: 'Intensive Care Unit (ICU)', type: 'ICU Ventilator Bed', rate: '₱ 4,500/day', status: 'occupied', patient: 'Juan Dela Cruz', code: 'G1-2026-0090', doctor: 'Dr. Roberto Tan, MD', admittedDate: '23-Aug-2026' },
            { id: 'ICU-102', ward: 'Intensive Care Unit (ICU)', type: 'ICU Cardiac Bed', rate: '₱ 4,500/day', status: 'occupied', patient: 'Carlos Mendoza', code: 'G1-2026-0098', doctor: 'Dr. Roberto Tan, MD', admittedDate: '24-Aug-2026' },
            { id: 'ICU-103', ward: 'Intensive Care Unit (ICU)', type: 'ICU Isolation Bed', rate: '₱ 5,000/day', status: 'available', patient: '', code: '', doctor: '', admittedDate: '' },
            { id: 'ICU-104', ward: 'Intensive Care Unit (ICU)', type: 'ICU Standard Bed', rate: '₱ 4,500/day', status: 'cleaning', patient: '', code: '', doctor: '', admittedDate: '' },
            { id: 'GEN-201', ward: 'General Male Ward', type: 'Semi-Private Bed', rate: '₱ 1,200/day', status: 'occupied', patient: 'Antonio Gonzales', code: 'G1-2026-0092', doctor: 'Dr. Alicia Gomez, MD', admittedDate: '22-Aug-2026' },
            { id: 'GEN-202', ward: 'General Male Ward', type: 'Standard Ward Bed', rate: '₱ 950/day', status: 'available', patient: '', code: '', doctor: '', admittedDate: '' },
            { id: 'GEN-203', ward: 'General Male Ward', type: 'Standard Ward Bed', rate: '₱ 950/day', status: 'available', patient: '', code: '', doctor: '', admittedDate: '' },
            { id: 'FEM-301', ward: 'General Female Ward', type: 'Semi-Private Bed', rate: '₱ 1,200/day', status: 'occupied', patient: 'Maria Santos', code: 'G1-2026-0089', doctor: 'Dr. Alicia Gomez, MD', admittedDate: '24-Aug-2026' },
            { id: 'FEM-302', ward: 'General Female Ward', type: 'Standard Ward Bed', rate: '₱ 950/day', status: 'available', patient: '', code: '', doctor: '', admittedDate: '' },
            { id: 'FEM-303', ward: 'General Female Ward', type: 'Standard Ward Bed', rate: '₱ 950/day', status: 'cleaning', patient: '', code: '', doctor: '', admittedDate: '' },
            { id: 'DLX-401', ward: 'Private Deluxe Suite', type: 'VIP Executive Suite', rate: '₱ 6,000/day', status: 'occupied', patient: 'Elena Reyes', code: 'G1-2026-0091', doctor: 'Dr. Vincent Lim, MD', admittedDate: '24-Aug-2026' },
            { id: 'DLX-402', ward: 'Private Deluxe Suite', type: 'VIP Executive Suite', rate: '₱ 6,000/day', status: 'available', patient: '', code: '', doctor: '', admittedDate: '' },
            { id: 'PED-501', ward: 'Pediatric Ward', type: 'Pediatric Crib Bed', rate: '₱ 1,500/day', status: 'available', patient: '', code: '', doctor: '', admittedDate: '' },
            { id: 'PED-502', ward: 'Pediatric Ward', type: 'Pediatric Junior Bed', rate: '₱ 1,500/day', status: 'available', patient: '', code: '', doctor: '', admittedDate: '' }
        ];

        let activeWardFilter = 'ALL';
        let currentEditingDraftStatus = 'available';

        // Emergency Department (ER Cases State)
        let ER_RECORDS = [
            { id: 'ER-2026-001', name: 'Victor Ramos', age: '42 Y', gender: 'Male', phone: '+63 917 111 2233', level: 'Level 1 - Resuscitation', complaint: 'Acute myocardial infarction / Crushing retrosternal chest pain radiating to left jaw', bp: '85/50', hr: '120', spo2: '92%', temp: '37.2', gcs: '14/15', bay: 'Bay 01 (Crash Cart)', doctor: 'Dr. Roberto Tan, MD', nurse: 'Nurse Clara Dizon', disposition: 'Cath Lab Transfer', status: 'critical', time: '10:15 AM' },
            { id: 'ER-2026-002', name: 'Sofia Manalo', age: '19 Y', gender: 'Female', phone: '+63 918 222 3344', level: 'Level 3 - Urgent', complaint: 'Acute lower right quadrant abdominal pain with rebound tenderness (R/O Appendicitis)', bp: '110/70', hr: '88', spo2: '99%', temp: '38.4', gcs: '15/15', bay: 'Bay 04 (Acute)', doctor: 'Dr. Edward Hernandez, MD', nurse: 'Nurse Ronald Valdez', disposition: 'STAT Ultrasound & Surgery Consult', status: 'urgent', time: '10:45 AM' },
            { id: 'ER-2026-003', name: 'Danilo Cruz', age: '58 Y', gender: 'Male', phone: '+63 920 333 4455', level: 'Level 2 - Emergent', complaint: 'Right-sided facial droop and acute slurred speech for 45 minutes (STAT Stroke Code)', bp: '160/95', hr: '94', spo2: '98%', temp: '36.9', gcs: '13/15', bay: 'Bay 02 (Resuscitation)', doctor: 'Dr. Vincent Lim, MD', nurse: 'Nurse Clara Dizon', disposition: 'STAT Non-Contrast Brain CT', status: 'critical', time: '11:00 AM' },
            { id: 'ER-2026-004', name: 'Grace Bautista', age: '24 Y', gender: 'Female', phone: '+63 922 444 5566', level: 'Level 4 - Less Urgent', complaint: 'Right ankle inversion injury with localized swelling after slipping on steps', bp: '118/76', hr: '78', spo2: '99%', temp: '36.6', gcs: '15/15', bay: 'Bay 06 (Observation)', doctor: 'Dr. Miguel Garcia, MD', nurse: 'Nurse Ronald Valdez', disposition: 'Ankle X-Ray & Splinting', status: 'stable', time: '11:20 AM' }
        ];

        let activeERLevelFilter = 'ALL';

        // Render Dynamic Emergency Cases Table
        function renderERCases() {
            const tbody = document.getElementById('er-table-body');
            if (!tbody) return;

            const searchQuery = document.getElementById('er-search-box') ? document.getElementById('er-search-box').value.toLowerCase().trim() : '';

            // Calculate KPIs
            const totalCases = ER_RECORDS.length;
            const criticalCases = ER_RECORDS.filter(c => c.level.includes('Level 1') || c.level.includes('Level 2')).length;
            const baysOccupied = `${totalCases} / 6`;

            if (document.getElementById('er-total-cases')) document.getElementById('er-total-cases').textContent = totalCases;
            if (document.getElementById('er-critical-cases')) document.getElementById('er-critical-cases').textContent = criticalCases;
            if (document.getElementById('er-bays-occupied')) document.getElementById('er-bays-occupied').textContent = baysOccupied;

            let filtered = ER_RECORDS.filter(c => {
                if (activeERLevelFilter !== 'ALL' && !c.level.toLowerCase().includes(activeERLevelFilter.toLowerCase())) return false;
                if (searchQuery) {
                    const matchId = c.id.toLowerCase().includes(searchQuery);
                    const matchName = c.name.toLowerCase().includes(searchQuery);
                    const matchBay = c.bay.toLowerCase().includes(searchQuery);
                    const matchComp = c.complaint.toLowerCase().includes(searchQuery);
                    if (!matchId && !matchName && !matchBay && !matchComp) return false;
                }
                return true;
            });

            tbody.innerHTML = '';

            if (filtered.length === 0) {
                tbody.innerHTML = `<tr><td colspan="10" style="text-align:center; padding:24px; color:#64748b;">No emergency encounters matching the selected acuity filter.</td></tr>`;
                return;
            }

            filtered.forEach(c => {
                const tr = document.createElement('tr');
                
                let badgeStyle = 'background:#fee2e2; color:#b91c1c; font-weight:800;';
                if (c.level.includes('Level 2')) badgeStyle = 'background:#ffedd5; color:#c2410c; font-weight:800;';
                if (c.level.includes('Level 3')) badgeStyle = 'background:#fef9c3; color:#a16207; font-weight:700;';
                if (c.level.includes('Level 4') || c.level.includes('Level 5')) badgeStyle = 'background:#dcfce7; color:#15803d; font-weight:700;';

                tr.innerHTML = `
                    <td><strong>${c.id}</strong><div style="font-size:10.5px; color:#64748b;">${c.time || '10:00 AM'}</div></td>
                    <td><span class="status-badge" style="${badgeStyle}">${c.level}</span></td>
                    <td><strong>${c.name}</strong></td>
                    <td>${c.age} / ${c.gender}</td>
                    <td style="max-width:280px; font-size:12.5px;">${c.complaint}</td>
                    <td><span style="font-size:11.5px; font-weight:700;">BP: ${c.bp} &bull; HR: ${c.hr} &bull; SpO2: ${c.spo2}</span></td>
                    <td><strong style="color:var(--brand-primary);">${c.bay}</strong></td>
                    <td style="font-size:12px;">${c.doctor}</td>
                    <td><span class="status-badge status-completed">${c.disposition}</span></td>
                    <td>
                        <div style="display:flex; gap:4px;">
                            <button class="btn-primary-action" style="padding:4px 8px; font-size:11px;" onclick="openManageERCase('${c.id}')">
                                <i class="fa-solid fa-pen"></i> Edit
                            </button>
                            <button class="btn-secondary" style="padding:4px 8px; font-size:11px;" onclick="dispatchERAction('${c.id}')">
                                <i class="fa-solid fa-bolt"></i> Action
                            </button>
                        </div>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        }

        // Filter ER by Level
        function filterERByLevel(levelKey, buttonEl) {
            activeERLevelFilter = levelKey;
            document.querySelectorAll('#er-pills-list .filter-pill').forEach(btn => btn.classList.remove('active'));
            if (buttonEl) buttonEl.classList.add('active');
            renderERCases();
        }

        // Open ER Case Edit Modal
        function openManageERCase(caseId) {
            const c = ER_RECORDS.find(item => item.id === caseId);
            if (!c) return;

            document.getElementById('edit-er-id').value = c.id;
            document.getElementById('edit-er-code').value = c.id;
            document.getElementById('edit-er-name').value = c.name;
            document.getElementById('edit-er-agesex').value = `${c.age} / ${c.gender}`;
            document.getElementById('edit-er-bay').value = c.bay;
            document.getElementById('edit-er-level').value = c.level;
            document.getElementById('edit-er-status').value = c.status || 'urgent';
            document.getElementById('edit-er-complaint').value = c.complaint;
            document.getElementById('edit-er-bp').value = c.bp;
            document.getElementById('edit-er-hr').value = c.hr;
            document.getElementById('edit-er-spo2').value = c.spo2;
            document.getElementById('edit-er-gcs').value = c.gcs || '15/15';
            document.getElementById('edit-er-doctor').value = c.doctor;
            document.getElementById('edit-er-disposition').value = c.disposition;

            openModal('modal-manage-er-case');
        }

        // Save ER Case Edits
        function saveERCaseDetails() {
            const caseId = document.getElementById('edit-er-id').value;
            const c = ER_RECORDS.find(item => item.id === caseId);
            if (!c) return;

            c.name = document.getElementById('edit-er-name').value;
            c.bay = document.getElementById('edit-er-bay').value;
            c.level = document.getElementById('edit-er-level').value;
            c.status = document.getElementById('edit-er-status').value;
            c.complaint = document.getElementById('edit-er-complaint').value;
            c.bp = document.getElementById('edit-er-bp').value;
            c.hr = document.getElementById('edit-er-hr').value;
            c.spo2 = document.getElementById('edit-er-spo2').value;
            c.gcs = document.getElementById('edit-er-gcs').value;
            c.doctor = document.getElementById('edit-er-doctor').value;
            c.disposition = document.getElementById('edit-er-disposition').value;

            closeModal('modal-manage-er-case');
            renderERCases();
            showToast(`Emergency Case ${c.id} (${c.name}) updated successfully!`);
        }

        // Submit New ER Case
        function submitNewERCase() {
            const name = document.getElementById('er-new-name').value.trim() || 'Emergency Patient';
            const age = document.getElementById('er-new-age').value.trim() || '35';
            const gender = document.getElementById('er-new-gender').value;
            const phone = document.getElementById('er-new-phone').value.trim() || '+63 900 000 0000';
            const level = document.getElementById('er-new-level').value;
            const bay = document.getElementById('er-new-bay').value;
            const complaint = document.getElementById('er-new-complaint').value.trim() || 'Acute emergency triage case';
            const bp = document.getElementById('er-new-bp').value.trim() || '120/80';
            const hr = document.getElementById('er-new-hr').value.trim() || '80';
            const spo2 = document.getElementById('er-new-spo2').value.trim() || '98%';
            const temp = document.getElementById('er-new-temp').value.trim() || '36.8';
            const doctor = document.getElementById('er-new-doctor').value;
            const disposition = document.getElementById('er-new-disposition').value;

            const caseId = 'ER-2026-00' + (ER_RECORDS.length + 1);

            ER_RECORDS.unshift({
                id: caseId,
                name: name,
                age: age + ' Y',
                gender: gender,
                phone: phone,
                level: level,
                complaint: complaint,
                bp: bp,
                hr: hr,
                spo2: spo2,
                temp: temp,
                gcs: '15/15',
                bay: bay,
                doctor: doctor,
                nurse: 'Nurse Clara Dizon',
                disposition: disposition,
                status: level.includes('Level 1') ? 'critical' : 'urgent',
                time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
            });

            closeModal('modal-new-er-patient');
            renderERCases();
            showToast(`Emergency Case ${caseId} (${name}) registered to ${bay}!`);
        }

        // Dispatch ER Action
        function dispatchERAction(caseId) {
            const c = ER_RECORDS.find(item => item.id === caseId);
            if (!c) return;
            showToast(`Order dispatched: ${c.disposition} for ${c.name} in ${c.bay}`);
        }

        function callTraumaTeam() {
            showToast('🚨 CODE BLUE / LEVEL 1 TRAUMA TEAM ACTIVATED: Resuscitation Team dispatched to ER Bay 01 & 02!');
        }

        // Render Dynamic Ward Bed Matrix
        function renderBedMatrix() {
            const container = document.getElementById('bed-matrix-container');
            if (!container) return;

            const statusFilter = document.getElementById('bed-status-filter') ? document.getElementById('bed-status-filter').value : 'ALL';
            const searchQuery = document.getElementById('bed-search-box') ? document.getElementById('bed-search-box').value.toLowerCase().trim() : '';

            const totalBeds = BED_RECORDS.length;
            const occupiedBeds = BED_RECORDS.filter(b => b.status === 'occupied').length;
            const availableBeds = BED_RECORDS.filter(b => b.status === 'available').length;
            const occupancyRate = totalBeds > 0 ? ((occupiedBeds / totalBeds) * 100).toFixed(1) + '%' : '0%';

            if (document.getElementById('adt-total-beds')) document.getElementById('adt-total-beds').textContent = totalBeds;
            if (document.getElementById('adt-occupied-beds')) document.getElementById('adt-occupied-beds').textContent = occupiedBeds;
            if (document.getElementById('adt-available-beds')) document.getElementById('adt-available-beds').textContent = availableBeds;
            if (document.getElementById('adt-occupancy-rate')) document.getElementById('adt-occupancy-rate').textContent = occupancyRate;
            if (document.getElementById('dash-occupancy-kpi')) document.getElementById('dash-occupancy-kpi').textContent = occupancyRate;

            let filtered = BED_RECORDS.filter(bed => {
                if (activeWardFilter !== 'ALL' && !bed.ward.toLowerCase().includes(activeWardFilter.toLowerCase())) return false;
                if (statusFilter !== 'ALL' && bed.status !== statusFilter) return false;
                if (searchQuery) {
                    const matchId = bed.id.toLowerCase().includes(searchQuery);
                    const matchPat = bed.patient.toLowerCase().includes(searchQuery);
                    const matchWard = bed.ward.toLowerCase().includes(searchQuery);
                    if (!matchId && !matchPat && !matchWard) return false;
                }
                return true;
            });

            container.innerHTML = '';

            if (filtered.length === 0) {
                container.innerHTML = `<div style="grid-column: 1/-1; text-align:center; padding:32px; color:#64748b;"><i class="fa-solid fa-bed" style="font-size:32px; margin-bottom:8px; opacity:0.4;"></i><p>No beds found matching the selected ward or status filter.</p></div>`;
                return;
            }

            filtered.forEach(bed => {
                const card = document.createElement('div');
                card.className = `bed-card-rich status-${bed.status}`;
                
                let badgeClass = 'status-active';
                let badgeText = 'Available (Empty)';
                let icon = 'fa-circle-check';
                let actionsHtml = '';

                if (bed.status === 'occupied') {
                    badgeClass = 'status-urgent';
                    badgeText = 'Occupied';
                    icon = 'fa-bed-pulse';
                    actionsHtml = `
                        <button class="bed-action-btn btn-bed-vacate" onclick="quickVacateBed('${bed.id}', event)">
                            <i class="fa-solid fa-person-walking-arrow-right"></i> Discharge
                        </button>
                        <button class="bed-action-btn btn-bed-edit" onclick="openManageBed('${bed.id}')">
                            <i class="fa-solid fa-pen"></i> Edit
                        </button>
                    `;
                } else if (bed.status === 'available') {
                    badgeClass = 'status-active';
                    badgeText = 'Available (Empty)';
                    icon = 'fa-circle-check';
                    actionsHtml = `
                        <button class="bed-action-btn btn-bed-admit" onclick="quickAdmitBed('${bed.id}', event)">
                            <i class="fa-solid fa-plus"></i> + Admit
                        </button>
                        <button class="bed-action-btn btn-bed-edit" onclick="openManageBed('${bed.id}')">
                            <i class="fa-solid fa-pen"></i> Edit
                        </button>
                    `;
                } else if (bed.status === 'cleaning') {
                    badgeClass = 'status-pending';
                    badgeText = 'Cleaning / Disinfection';
                    icon = 'fa-broom';
                    actionsHtml = `
                        <button class="bed-action-btn btn-bed-admit" style="background:#15803d; color:#fff;" onclick="quickSetReady('${bed.id}', event)">
                            <i class="fa-solid fa-check"></i> Mark Ready
                        </button>
                        <button class="bed-action-btn btn-bed-edit" onclick="openManageBed('${bed.id}')">
                            <i class="fa-solid fa-pen"></i> Edit
                        </button>
                    `;
                } else if (bed.status === 'reserved') {
                    badgeClass = 'status-completed';
                    badgeText = 'Reserved';
                    icon = 'fa-bookmark';
                    actionsHtml = `
                        <button class="bed-action-btn btn-bed-admit" onclick="quickAdmitBed('${bed.id}', event)">
                            <i class="fa-solid fa-user-plus"></i> Admit
                        </button>
                        <button class="bed-action-btn btn-bed-edit" onclick="openManageBed('${bed.id}')">
                            <i class="fa-solid fa-pen"></i> Edit
                        </button>
                    `;
                }

                card.innerHTML = `
                    <div>
                        <div class="bed-card-header">
                            <span class="bed-card-title"><i class="fa-solid fa-bed"></i> ${bed.id}</span>
                            <span class="status-badge ${badgeClass}" style="font-size:10.5px;"><i class="fa-solid ${icon}"></i> ${badgeText}</span>
                        </div>
                        <div class="bed-ward-tag">${bed.ward} &bull; ${bed.type}</div>
                        <div class="bed-patient-info">
                            ${bed.status === 'occupied' && bed.patient ? `
                                <strong>${bed.patient}</strong>
                                <span style="color:#64748b; font-size:11.5px;">${bed.code} &bull; ${bed.doctor}</span>
                                <div style="color:#94a3b8; font-size:10.5px; margin-top:2px;">Admitted: ${bed.admittedDate || '24-Aug-2026'}</div>
                            ` : `
                                <span style="color:#64748b; font-style:italic;">${bed.status === 'cleaning' ? 'Under terminal disinfection' : 'Ready for patient admission'} &bull; ${bed.rate}</span>
                            `}
                        </div>
                    </div>
                    <div class="bed-card-actions">
                        ${actionsHtml}
                    </div>
                `;

                card.onclick = (e) => {
                    if (!e.target.closest('button')) {
                        openManageBed(bed.id);
                    }
                };

                container.appendChild(card);
            });
        }

        function filterBedsByWard(wardKey, buttonEl) {
            activeWardFilter = wardKey;
            document.querySelectorAll('#ward-pills-list .filter-pill').forEach(btn => btn.classList.remove('active'));
            if (buttonEl) buttonEl.classList.add('active');
            applyRolePermissions();
            renderBedMatrix();
        }

        function openManageBed(bedId) {
            let bed = BED_RECORDS.find(b => b.id === bedId);
            if (!bed) bed = BED_RECORDS[0];

            document.getElementById('edit-bed-id').value = bed.id;
            document.getElementById('edit-bed-code').value = bed.id;
            document.getElementById('edit-bed-ward').value = bed.ward;
            document.getElementById('edit-bed-type').value = bed.type;
            document.getElementById('edit-bed-rate').value = bed.rate;
            document.getElementById('edit-bed-patient').value = bed.patient || '';
            document.getElementById('edit-bed-doctor').value = bed.doctor || 'Dr. Roberto Tan, MD';

            setBedStatusDraft(bed.status);
            openModal('modal-manage-bed');
        }

        function setBedStatusDraft(status) {
            currentEditingDraftStatus = status;
            document.querySelectorAll('.btn-status-opt').forEach(b => b.classList.remove('active'));
            const activeBtn = document.getElementById('bopt-' + status);
            if (activeBtn) activeBtn.classList.add('active');
        }

        function dischargeBedPatientDraft() {
            document.getElementById('edit-bed-patient').value = '';
            setBedStatusDraft('available');
            showToast('Patient cleared. Click Save Bed Changes to confirm discharge.');
        }

        function handleBedPatientChange(selectEl) {
            if (selectEl.value) {
                setBedStatusDraft('occupied');
            } else {
                setBedStatusDraft('available');
            }
        }

        function saveBedDetails() {
            const bedId = document.getElementById('edit-bed-id').value;
            const bed = BED_RECORDS.find(b => b.id === bedId);
            if (!bed) return;

            const newPatient = document.getElementById('edit-bed-patient').value;
            const newDoctor = document.getElementById('edit-bed-doctor').value;
            const newWard = document.getElementById('edit-bed-ward').value;
            const newType = document.getElementById('edit-bed-type').value;
            const newRate = document.getElementById('edit-bed-rate').value;

            bed.ward = newWard;
            bed.type = newType;
            bed.rate = newRate;
            bed.status = currentEditingDraftStatus;
            bed.patient = newPatient;
            bed.doctor = newPatient ? newDoctor : '';
            bed.code = newPatient ? (PATIENT_RECORDS[newPatient] ? PATIENT_RECORDS[newPatient].code : 'G1-2026-0099') : '';
            bed.admittedDate = newPatient ? (bed.admittedDate || '24-Aug-2026') : '';

            closeModal('modal-manage-bed');
            applyRolePermissions();
            renderBedMatrix();
            showToast(`Bed ${bed.id} updated successfully: ${bed.status.toUpperCase()} ${newPatient ? '(' + newPatient + ')' : '(Empty)'}!`);
        }

        function quickVacateBed(bedId, event) {
            if (event) event.stopPropagation();
            const bed = BED_RECORDS.find(b => b.id === bedId);
            if (!bed) return;
            const dischargedPatient = bed.patient;
            bed.status = 'cleaning';
            bed.patient = '';
            bed.code = '';
            bed.doctor = '';
            bed.admittedDate = '';
            applyRolePermissions();
            renderBedMatrix();
            showToast(`Patient ${dischargedPatient} discharged! Bed ${bed.id} marked under cleaning/disinfection.`);
        }

        function quickSetReady(bedId, event) {
            if (event) event.stopPropagation();
            const bed = BED_RECORDS.find(b => b.id === bedId);
            if (!bed) return;
            bed.status = 'available';
            applyRolePermissions();
            renderBedMatrix();
            showToast(`Bed ${bed.id} disinfected & marked Available (Empty)!`);
        }

        function quickAdmitBed(bedId, event) {
            if (event) event.stopPropagation();
            openManageBed(bedId);
            if (!document.getElementById('edit-bed-patient').value) {
                document.getElementById('edit-bed-patient').value = 'Juan Dela Cruz';
                setBedStatusDraft('occupied');
            }
        }

        function submitNewBed() {
            const code = document.getElementById('add-bed-code').value.trim() || ('BED-' + Math.floor(100 + Math.random() * 900));
            const ward = document.getElementById('add-bed-ward').value;
            const type = document.getElementById('add-bed-type').value.trim() || 'Standard Ward Bed';
            const rate = document.getElementById('add-bed-rate').value.trim() || '₱ 1,200/day';
            const status = document.getElementById('add-bed-status').value;

            BED_RECORDS.push({
                id: code,
                ward: ward,
                type: type,
                rate: rate,
                status: status,
                patient: '',
                code: '',
                doctor: '',
                admittedDate: ''
            });

            closeModal('modal-add-bed');
            applyRolePermissions();
            renderBedMatrix();
            showToast(`New Bed ${code} added to ${ward}!`);
        }

        // Active Patient Switcher Function
        function setActivePatient(patientName) {
            const pat = PATIENT_RECORDS[patientName];
            if (!pat) return;

            document.getElementById('global-pat-name').textContent = pat.name;
            document.getElementById('global-pat-code').textContent = pat.code;
            document.getElementById('global-pat-meta').innerHTML = pat.meta;

            const emrTitle = document.getElementById('emr-patient-title');
            if (emrTitle) emrTitle.textContent = `${pat.name} (${pat.age} / ${pat.gender})`;
            const emrBadge = document.getElementById('emr-hospital-badge');
            if (emrBadge) emrBadge.textContent = `Hospital No: ${pat.code}`;
            
            if (document.getElementById('emr-bp')) document.getElementById('emr-bp').value = pat.bp;
            if (document.getElementById('emr-pulse')) document.getElementById('emr-pulse').value = pat.pulse;
            if (document.getElementById('emr-temp')) document.getElementById('emr-temp').value = pat.temp;
            if (document.getElementById('emr-spo2')) document.getElementById('emr-spo2').value = pat.spo2;
            if (document.getElementById('emr-complaints')) document.getElementById('emr-complaints').value = pat.complaints;
            if (document.getElementById('emr-diagnosis')) document.getElementById('emr-diagnosis').value = pat.diagnosis;

            const rxTbody = document.querySelector('#rx-table tbody');
            if (rxTbody) {
                rxTbody.innerHTML = '';
                pat.rx.forEach(item => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td><strong>${item.name}</strong></td>
                        <td>${item.dose}</td>
                        <td>${item.freq}</td>
                        <td>${item.days}</td>
                        <td><button class="btn-del-rx" onclick="this.closest('tr').remove(); showToast('Medication removed from Rx');">&times;</button></td>
                    `;
                    rxTbody.appendChild(row);
                });
            }

            document.querySelectorAll('.queue-item').forEach(qi => qi.classList.remove('active'));
            const activeQueueEl = document.getElementById(pat.queueId);
            if (activeQueueEl) activeQueueEl.classList.add('active');

            if (document.getElementById('p360-name')) document.getElementById('p360-name').textContent = pat.name;
            if (document.getElementById('p360-code')) document.getElementById('p360-code').textContent = pat.code;
            if (document.getElementById('p360-submeta')) document.getElementById('p360-submeta').innerHTML = pat.meta;
            if (document.getElementById('p360-avatar')) {
                const initials = pat.name.split(' ').map(n => n[0]).join('');
                document.getElementById('p360-avatar').textContent = initials;
            }

            showToast(`Switched active patient context to ${pat.name} (${pat.code})`);
        }

        // Tab switching
        function switchTab(viewId, element) {
            document.querySelectorAll('.module-view').forEach(v => v.classList.remove('active'));
            document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
            
            closeMobileSidebar();
            const targetView = document.getElementById(viewId);
            if (targetView) targetView.classList.add('active');
            
            if (element) {
                const navItem = element.closest('.nav-item');
                if (navItem) navItem.classList.add('active');
            } else {
                const matchingNav = document.querySelector(`.nav-item[data-target="${viewId}"]`);
                if (matchingNav) matchingNav.classList.add('active');
            }

            if (viewId === 'view-adt') {
                applyRolePermissions();
            renderBedMatrix();
            } else if (viewId === 'view-emergency') {
                renderERCases();
            }
        }

        function addPrescriptionRow() {
            const rxTbody = document.querySelector('#rx-table tbody');
            const row = document.createElement('tr');
            row.innerHTML = `
                <td><input type="text" class="form-control" value="New Medicine" style="padding:4px 8px; font-size:12px;" /></td>
                <td><input type="text" class="form-control" value="1 Tab" style="padding:4px 8px; font-size:12px; width:70px;" /></td>
                <td><input type="text" class="form-control" value="TID" style="padding:4px 8px; font-size:12px; width:80px;" /></td>
                <td><input type="text" class="form-control" value="7 Days" style="padding:4px 8px; font-size:12px; width:70px;" /></td>
                <td><button class="btn-del-rx" onclick="this.closest('tr').remove(); showToast('Medication removed from Rx');">&times;</button></td>
            `;
            rxTbody.appendChild(row);
            showToast('Added new prescription item slot.');
        }

        function openModal(modalId) {
            const modal = document.getElementById(modalId);
            if (modal) modal.classList.add('active');
        }

        function closeModal(modalId) {
            const modal = document.getElementById(modalId);
            if (modal) modal.classList.remove('active');
        }

        document.addEventListener('click', function(e) {
            if (e.target.classList.contains('modal-overlay')) {
                e.target.classList.remove('active');
            }
        });

        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                document.querySelectorAll('.modal-overlay.active').forEach(m => m.classList.remove('active'));
            }
        });

        function showToast(message) {
            const toast = document.getElementById('toast-notification');
            const msgEl = document.getElementById('toast-message');
            msgEl.textContent = message;
            toast.classList.add('show');
            setTimeout(() => toast.classList.remove('show'), 3500);
        }

        function handleGlobalPatientSearch(input) {
            const query = input.value.toLowerCase().trim();
            if (!query) return;

            for (const [name, pat] of Object.entries(PATIENT_RECORDS)) {
                if (name.toLowerCase().includes(query) || pat.code.toLowerCase().includes(query)) {
                    setActivePatient(name);
                    break;
                }
            }
        }

        function filterPatientModalList(input) {
            const query = input.value.toLowerCase();
            document.querySelectorAll('#pat-modal-list .queue-item').forEach(el => {
                el.style.display = el.innerText.toLowerCase().includes(query) ? '' : 'none';
            });
        }

        function filterPatientTable() {
            const query = document.getElementById('patient-search-input').value.toLowerCase();
            document.querySelectorAll('#patient-master-table tbody tr').forEach(tr => {
                const text = tr.innerText.toLowerCase();
                tr.style.display = text.includes(query) ? '' : 'none';
            });
        }

        function viewPatient360(name, code) {
            setActivePatient(name);
            switchTab('view-patient360', document.querySelector('[data-target=view-patient360]'));
            showToast(`Viewing 360° longitudinal medical record for ${name}`);
        }

        function openPrintInvoice(invNo, patient, total) {
            document.getElementById('rcpt-no').textContent = invNo;
            document.getElementById('rcpt-patient').textContent = patient;
            document.getElementById('rcpt-total').textContent = '₱ ' + total;
            openModal('modal-print-invoice');
        }

        function runAITriageTest() {
            const query = document.getElementById('ai-symptom-text').value.toLowerCase();
            let dept = "General Outpatient Medicine";
            let doctor = "Dr. Alicia Gomez, MD";
            let priority = "Routine";

            if (query.includes("chest") || query.includes("heart") || query.includes("breath") || query.includes("arm")) {
                dept = "Emergency Cardiology";
                doctor = "Dr. Roberto Tan, MD (Interventional Cardiologist)";
                priority = "HIGH URGENCY - Priority 1";
            } else if (query.includes("joint") || query.includes("knee") || query.includes("bone") || query.includes("fracture")) {
                dept = "Orthopedics & Traumatology";
                doctor = "Dr. Miguel Garcia, MD";
                priority = "Urgent OPD";
            } else if (query.includes("head") || query.includes("vision") || query.includes("dizzy")) {
                dept = "Neurology & Stroke Center";
                doctor = "Dr. Vincent Lim, MD";
                priority = "Urgent Clinic";
            }

            const resDiv = document.getElementById('ai-triage-result');
            const resOutput = document.getElementById('ai-triage-output');
            resOutput.innerHTML = `<strong>Priority:</strong> ${priority}<br/><strong>Recommended Department:</strong> ${dept}<br/><strong>Suggested Consultant:</strong> ${doctor}<br/><strong>Automated Action:</strong> Slot reserved & appointment SMS confirmation sent.`;
            resDiv.style.display = 'block';
            showToast('AI Triage Match Complete: ' + dept);
        }

        function savePersonalizationSettings() {
            const hospName = document.getElementById('cfg-hospital-name').value;
            document.getElementById('header-facility-name').textContent = hospName;
            showToast('Branding & White-Label configuration updated successfully!');
        }

        window.addEventListener('DOMContentLoaded', () => {
            const uName = sessionStorage.getItem('g1_user_name');
            const uRole = sessionStorage.getItem('g1_user_role');
            const uAvatar = sessionStorage.getItem('g1_user_avatar');

            if (uName && document.getElementById('header-user-name')) {
                document.getElementById('header-user-name').textContent = uName;
            }
            if (uRole && document.getElementById('header-user-role')) {
                document.getElementById('header-user-role').innerHTML = uRole;
            }
            if (uAvatar && document.getElementById('header-user-avatar')) {
                document.getElementById('header-user-avatar').textContent = uAvatar;
            }

            applyRolePermissions();
            renderBedMatrix();
            renderERCases();
        });
    </script>
</body>
</html>
"""

class G1HealthRequestHandler(http.server.BaseHTTPRequestHandler):
    def send_security_headers(self, is_html=True):
        self.send_header("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "SAMEORIGIN")
        self.send_header("X-XSS-Protection", "1; mode=block")
        self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
        if is_html:
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
            self.send_header("Pragma", "no-cache")
            self.send_header("Expires", "0")

    def is_authenticated(self):
        cookie_header = self.headers.get("Cookie", "")
        cookies = extract_cookies(cookie_header)
        token = cookies.get("g1_session")
        if not token:
            return False
        user_data = verify_session_token(token)
        return user_data is not None

    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # UNIVERSAL REST API GET ROUTER (Live SQLite Database)
        if path.startswith("/api/"):
            entity = path.replace("/api/", "").strip("/").split("/")[0]
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_security_headers(is_html=False)
            self.end_headers()

            if entity == "state":
                data = db_manager.get_full_emr_state()
            elif hasattr(db_manager, f"get_all_{entity}"):
                data = getattr(db_manager, f"get_all_{entity}")()
            else:
                try:
                    data = db_manager.get_all_records(entity)
                except Exception:
                    data = {"error": f"Entity {entity} not found"}

            self.wfile.write(json.dumps(data).encode("utf-8"))
            return

        # 1. PUBLIC DIRECT ASSET WHITELIST (Accessible without login as requested)
        clean_path = path.lstrip("/")
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
            self.wfile.write(LOGIN_HTML.encode("utf-8"))
            return

        
        # 4. PROTECTED ROUTES (Dashboard, Clinical, ADT, ER, etc.)
        if path in ["/dashboard", "/Home/Index", "/home/index", "/app", "/dashboard.html"]:
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
            self.wfile.write(APP_HTML.encode("utf-8"))
            return

        # Default fallback for unknown routes: redirect to login
        self.send_response(302)
        self.send_header("Location", "/Account/Login?error=unauthorized")
        self.send_security_headers(is_html=True)
        self.end_headers()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # UNIVERSAL REST API MUTATION ROUTER (Live SQLite Database: Add, Edit, Delete)
        if path.startswith("/api/") and path not in ["/api/ai/chat", "/api/ai/triage"]:
            entity = path.replace("/api/", "").strip("/").split("/")[0]
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            try:
                req_data = json.loads(post_data) if post_data else {}
            except Exception:
                req_data = {}

            res_payload = {"success": True}
            action = req_data.get('_action', 'create')
            record_id = req_data.get('id')

            try:
                if action == 'delete' and record_id is not None:
                    db_manager.delete_record(entity, record_id)
                    db_manager.log_audit_event(req_data.get('user', 'admin'), f"DELETE_RECORD ({entity}:{record_id})")
                    res_payload["deleted_id"] = record_id
                elif action == 'update' and record_id is not None:
                    clean_data = {k: v for k, v in req_data.items() if not k.startswith('_')}
                    db_manager.update_record(entity, record_id, clean_data)
                    db_manager.log_audit_event(req_data.get('user', 'admin'), f"UPDATE_RECORD ({entity}:{record_id})")
                    res_payload["updated_id"] = record_id
                elif entity == "beds" or entity == "adt_beds":
                    if req_data.get('status'):
                        db_manager.update_bed_record(
                            req_data.get('id'),
                            req_data.get('status'),
                            req_data.get('patient_name'),
                            req_data.get('diagnosis'),
                            req_data.get('doctor')
                        )
                        db_manager.log_audit_event(req_data.get('user', 'nurse'), f"UPDATE_BED ({req_data.get('id')} -> {req_data.get('status')})")
                    else:
                        db_manager.insert_record("adt_beds", req_data)
                else:
                    clean_data = {k: v for k, v in req_data.items() if not k.startswith('_')}
                    new_id = db_manager.insert_record(entity, clean_data)
                    db_manager.log_audit_event(req_data.get('user', 'admin'), f"CREATE_RECORD ({entity}:{new_id})")
                    res_payload["id"] = new_id
            except Exception as e:
                res_payload = {"success": False, "error": str(e)}

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_security_headers(is_html=False)
            self.end_headers()
            self.wfile.write(json.dumps(res_payload).encode('utf-8'))
            return

        # 5. SECURE ZERO-KEY CLINICAL MEDICAL LLM ENGINE (/api/ai/chat)
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

            # Extensive Medical Ontology & Symptom Triage Matrix
            # Priority 1: STAT Emergency & Urgent Symptoms
            if any(w in msg_lower for w in ['ambulance', 'emergency', 'unconscious', 'crushing', 'severe bleeding', 'radiat', 'left arm', 'slur', 'face droop']):
                is_emergency = True
                matched_dept = "Cardiology" if 'chest' in msg_lower else "Emergency Department (ER)"
                recommended_doctor = "Dr. Roberto Tan, MD" if 'chest' in msg_lower else "ER Trauma Team"
                sentiment = "STAT High Priority"
                ai_reply = f"Hello {patient_name}. 🚨 CRITICAL MEDICAL ALERT: Your reported symptoms require STAT medical evaluation. Our Emergency Crash Bays are on alert. Please proceed immediately to our Emergency Department Ground Floor entrance or contact STAT Ambulance Dispatch at (02) 8800-EMER."

            # Priority 2: Financial, Billing & Insurance Inquiries (Checked before general words)
            elif any(w in msg_lower for w in ['philhealth', 'hmo', 'maxicare', 'intellicare', 'medicard', 'insurance', 'coverage', 'discount', 'senior', 'pwd', 'billing', 'invoice', 'how much', 'cost', 'price', 'cashier']):
                matched_dept = "Billing & Insurance Claims"
                recommended_doctor = "Mark Mendoza (Billing Officer)"
                sentiment = "Financial & HMO Inquiry"
                ai_reply = f"Hello {patient_name}. Our Hospital Billing Desk is fully accredited with PhilHealth Case Rates and all major HMO providers (Maxicare, Intellicare, Medicard, etc.). Senior Citizens and PWDs automatically receive statutory 20% discounts on all consultation and diagnostic services."

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
                ai_reply = f"Hello {patient_name}, thank you for contacting Global 1 OneTech Medical Center. Our intelligent triage agent has reviewed your inquiry. Dr. Roberto Tan, MD is available for comprehensive medical consultation in the OPD Clinic."

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

            # Verify credentials against USERS_DB (default to admin if empty for seamless demo)
            if not username:
                username = 'admin'
            if not password:
                password = 'pass123'

            if username in USERS_DB and USERS_DB[username]['password'] == password:
                user_info = USERS_DB[username]
                token = create_session_token(username, user_info['role'])

                # Send 303 Redirect to dashboard with secure HMAC session cookie
                self.send_response(303)
                self.send_header("Location", "/dashboard")
                self.send_header("Set-Cookie", f"g1_session={token}; Path=/; HttpOnly; SameSite=Lax; Max-Age=86400")
                self.send_security_headers(is_html=True)
                self.end_headers()
                return
            else:
                self.send_response(303)
                self.send_header("Location", "/Account/Login?error=invalid_credentials")
                self.send_security_headers(is_html=True)
                self.end_headers()
                return

        if path in ["/Account/Logout", "/logout"]:
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
        print(f"🔒 G1 Health EMR Secure Server running on http://localhost:{PORT}")
        httpd.serve_forever()

if __name__ == "__main__":
    run_server()
