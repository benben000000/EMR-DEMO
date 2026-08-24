import os

def build_suite():
    LOGIN_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate" />
    <meta http-equiv="Pragma" content="no-cache" />
    <meta http-equiv="Expires" content="0" />
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
            width: 1080px;
            max-width: 96vw;
            min-height: 660px;
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
            margin-bottom: 26px;
        }

        .hero-tagline b { color: var(--brand-cyan); }

        .feature-list {
            list-style: none;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }

        .feature-item {
            display: flex;
            align-items: center;
            gap: 12px;
            font-size: 13.5px;
            font-weight: 600;
            color: #f8fafc;
            background: rgba(255, 255, 255, 0.05);
            padding: 9px 14px;
            border-radius: 8px;
            border-left: 3.5px solid var(--brand-cyan);
            backdrop-filter: blur(8px);
        }

        .feature-item i { color: var(--brand-cyan); font-size: 14px; width: 18px; text-align: center; }

        .hero-footer {
            font-size: 12px;
            color: #94a3b8;
            margin-top: 24px;
        }

        .hero-footer a { color: var(--brand-cyan); text-decoration: none; font-weight: 600; }

        .form-panel {
            flex: 1;
            padding: 40px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            background: #ffffff;
        }

        .form-logo { text-align: center; margin-bottom: 16px; }
        .form-logo img { max-height: 42px; }

        .form-header { text-align: center; margin-bottom: 18px; }
        .form-header h2 { font-size: 22px; font-weight: 800; color: #1e293b; }
        .form-header p { font-size: 12.5px; color: #64748b; margin-top: 4px; }

        .security-alert {
            padding: 10px 14px;
            border-radius: 8px;
            font-size: 12.5px;
            font-weight: 600;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .alert-success { background: #dcfce7; color: #15803d; border: 1px solid #86efac; }
        .alert-danger { background: #fee2e2; color: #b91c1c; border: 1px solid #fca5a5; }

        .input-group { margin-bottom: 14px; }
        .input-group label { display: block; font-size: 12.5px; font-weight: 700; color: #334155; margin-bottom: 5px; }

        .input-wrapper { position: relative; display: flex; align-items: center; }
        .input-wrapper i { position: absolute; left: 14px; color: #94a3b8; font-size: 14px; }

        .input-wrapper input {
            width: 100%;
            padding: 11px 14px 11px 40px;
            border: 1.5px solid #e2e8f0;
            border-radius: 10px;
            font-size: 13.5px;
            color: #1e293b;
            outline: none;
            transition: all 0.2s;
        }

        .input-wrapper input:focus {
            border-color: var(--brand-primary);
            box-shadow: 0 0 0 3px rgba(37, 53, 69, 0.12);
        }

        .btn-submit {
            width: 100%;
            padding: 12px;
            background-color: var(--brand-primary);
            color: #ffffff;
            border: none;
            border-radius: 10px;
            font-size: 14.5px;
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
        }

        .role-switcher-bar {
            margin-top: 16px;
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            padding: 12px;
            font-size: 12px;
        }

        .role-switcher-title {
            font-weight: 800;
            color: #475569;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .role-pills {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 6px;
        }

        .role-pill-btn {
            background: #ffffff;
            border: 1px solid #cbd5e1;
            border-radius: 6px;
            padding: 6px 4px;
            font-size: 11px;
            font-weight: 700;
            cursor: pointer;
            color: #334155;
            text-align: center;
            transition: all 0.15s;
        }

        .role-pill-btn:hover {
            background: var(--brand-primary);
            color: #ffffff;
            border-color: var(--brand-primary);
        }

        @media (max-width: 768px) {
            .auth-container { flex-direction: column; }
            .hero-panel, .form-panel { padding: 24px; }
            .role-pills { grid-template-columns: repeat(2, 1fr); }
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
                    Full-Spectrum <b>33-Module Hospital Management Solution</b> with Departmental Role-Based Access Control.
                </p>
                <ul class="feature-list">
                    <li class="feature-item">
                        <i class="fa-solid fa-shield-halved"></i>
                        <span>Departmental RBAC (Doctor, Nurse, Accountant, Pharmacy, Admin)</span>
                    </li>
                    <li class="feature-item">
                        <i class="fa-solid fa-calculator"></i>
                        <span>Accounting, Billing, Claims, Fixed Assets & Incentives</span>
                    </li>
                    <li class="feature-item">
                        <i class="fa-solid fa-bed"></i>
                        <span>Dynamic Ward Bed Matrix & Emergency Trauma Triage</span>
                    </li>
                    <li class="feature-item">
                        <i class="fa-solid fa-boxes-packing"></i>
                        <span>Pharmacy, Central Inventory, Procurement & SubStore</span>
                    </li>
                    <li class="feature-item">
                        <i class="fa-solid fa-robot"></i>
                        <span>AI CRM & Longitudinal Patient 360 Information System</span>
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
                <button type="submit" class="btn-submit" id="btn-login-submit" style="margin-top: 10px;">
                    <span>Sign In to Dashboard</span>
                    <i class="fa-solid fa-arrow-right"></i>
                </button>

                <!-- 8 Interactive Role Selectors -->
                <div class="role-switcher-bar">
                    <div class="role-switcher-title">
                        <span><i class="fa-solid fa-id-badge"></i> Select Department Role:</span>
                        <span style="color:#64748b; font-size:11px;">1-Click Fill</span>
                    </div>
                    <div class="role-pills">
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
                sessionStorage.setItem('g1_role_key', matched.role_key);
                sessionStorage.setItem('g1_user_name', matched.name);
                sessionStorage.setItem('g1_user_role', matched.role);
                sessionStorage.setItem('g1_user_avatar', matched.avatar);
                sessionStorage.setItem('g1_user_badge', matched.badge);
                localStorage.setItem('g1_user', userInp);

                document.cookie = "g1_session=sess_" + userInp + "_" + Date.now() + "; Path=/; Max-Age=86400; SameSite=Lax;";

                setTimeout(() => {
                    window.location.replace('/dashboard.html');
                }, 100);
                return false;
            } else {
                alertBox.innerHTML = `
                    <div class="security-alert alert-danger">
                        <i class="fa-solid fa-triangle-exclamation"></i>
                        <span>Invalid credentials. Use demo accounts (e.g. <b>admin</b>, <b>doctor</b>, <b>accountant</b>, <b>nurse</b>) with password <b>pass123</b>.</span>
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
                if (container) {
                    container.innerHTML = `
                        <div class="security-alert alert-danger">
                            <i class="fa-solid fa-shield-halved"></i>
                            <span>Authentication required. Please sign in to access clinical records.</span>
                        </div>
                    `;
                }
            }
        });

        function setRoleCredentials(user, pass) {
            document.getElementById('username').value = user;
            document.getElementById('password').value = pass;
        }
    </script>
</body>
</html>
"""
    print("Login HTML built.")

build_suite()
