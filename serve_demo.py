#!/usr/bin/env python3
"""
G1 Health EMR - macOS Demo Runner & Web Server
Powered by Global 1 OneTech (https://global1onetech.com/)
"""

import http.server
import socketserver
import urllib.parse
import os
import mimetypes
import json

PORT = 5000
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "Code/Websites/DanpheEMR"))
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

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
            --bg-slate: #0f172a;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Nunito', 'Inter', sans-serif;
        }

        body {
            background-color: #f1f5f9;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow-x: hidden;
        }

        .auth-container {
            display: flex;
            width: 1000px;
            max-width: 95vw;
            min-height: 600px;
            background: #ffffff;
            border-radius: 16px;
            box-shadow: 0 20px 40px -15px rgba(15, 23, 42, 0.15), 0 0 0 1px rgba(15, 23, 42, 0.05);
            overflow: hidden;
        }

        .hero-panel {
            flex: 1.1;
            background: linear-gradient(135deg, #1b2838 0%, #253545 100%);
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
            top: -50%;
            right: -50%;
            width: 100%;
            height: 100%;
            background: radial-gradient(circle, rgba(0, 255, 161, 0.12) 0%, transparent 70%);
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
            margin-bottom: 12px;
            color: #ffffff;
        }

        .hero-tagline {
            font-size: 15px;
            color: #cbd5e1;
            line-height: 1.6;
            margin-bottom: 32px;
        }

        .hero-tagline b {
            color: var(--brand-cyan);
        }

        .feature-list {
            list-style: none;
            display: flex;
            flex-direction: column;
            gap: 14px;
        }

        .feature-item {
            display: flex;
            align-items: center;
            gap: 12px;
            font-size: 14px;
            font-weight: 600;
            color: #f8fafc;
            background: rgba(255, 255, 255, 0.06);
            padding: 10px 14px;
            border-radius: 8px;
            border-left: 3px solid var(--brand-cyan);
            backdrop-filter: blur(8px);
        }

        .feature-item i {
            color: var(--brand-cyan);
            font-size: 16px;
        }

        .hero-footer {
            font-size: 12px;
            color: #94a3b8;
            margin-top: 32px;
        }

        .hero-footer a {
            color: var(--brand-cyan);
            text-decoration: none;
            font-weight: 600;
        }

        .form-panel {
            flex: 1;
            padding: 48px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            background: #ffffff;
        }

        .form-logo {
            text-align: center;
            margin-bottom: 32px;
        }

        .form-logo img {
            max-height: 48px;
        }

        .form-header {
            text-align: center;
            margin-bottom: 28px;
        }

        .form-header h2 {
            font-size: 22px;
            font-weight: 700;
            color: #1e293b;
        }

        .form-header p {
            font-size: 13px;
            color: #64748b;
            margin-top: 4px;
        }

        .input-group {
            margin-bottom: 20px;
        }

        .input-group label {
            display: block;
            font-size: 13px;
            font-weight: 600;
            color: #334155;
            margin-bottom: 6px;
        }

        .input-wrapper {
            position: relative;
            display: flex;
            align-items: center;
        }

        .input-wrapper i {
            position: absolute;
            left: 14px;
            color: #94a3b8;
            font-size: 15px;
        }

        .input-wrapper input {
            width: 100%;
            padding: 12px 14px 12px 42px;
            border: 1.5px solid #e2e8f0;
            border-radius: 8px;
            font-size: 14px;
            color: #1e293b;
            outline: none;
            transition: all 0.2s;
        }

        .input-wrapper input:focus {
            border-color: var(--brand-primary);
            box-shadow: 0 0 0 3px rgba(37, 53, 69, 0.1);
        }

        .form-options {
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-size: 13px;
            margin-bottom: 24px;
        }

        .remember-me {
            display: flex;
            align-items: center;
            gap: 6px;
            color: #475569;
            cursor: pointer;
        }

        .forgot-link {
            color: var(--brand-primary);
            text-decoration: none;
            font-weight: 600;
        }

        .btn-submit {
            width: 100%;
            padding: 13px;
            background-color: var(--brand-primary);
            color: #ffffff;
            border: none;
            border-radius: 8px;
            font-size: 15px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }

        .btn-submit:hover {
            background-color: var(--brand-primary-hover);
            color: var(--brand-cyan);
            transform: translateY(-1px);
            box-shadow: 0 8px 16px -4px rgba(37, 53, 69, 0.3);
        }

        .demo-credentials-badge {
            margin-top: 24px;
            background: #f8fafc;
            border: 1px dashed #cbd5e1;
            border-radius: 8px;
            padding: 10px 14px;
            font-size: 12px;
            color: #475569;
            text-align: center;
        }

        .demo-credentials-badge code {
            background: #e2e8f0;
            padding: 2px 6px;
            border-radius: 4px;
            font-weight: 700;
            color: #0f172a;
        }

        @media (max-width: 768px) {
            .auth-container {
                flex-direction: column;
            }
            .hero-panel {
                padding: 32px;
            }
            .form-panel {
                padding: 32px;
            }
        }
    </style>
</head>
<body>
    <div class="auth-container">
        <!-- Hero Section -->
        <div class="hero-panel">
            <div>
                <img src="/Personalization/logos/logo-main.png" alt="Global 1 OneTech" class="brand-logo-hero" />
                <h1 class="hero-title">G1 Health EMR</h1>
                <p class="hero-tagline">
                    A Smart <b>Healthcare Management Solution</b> powered by Global 1 OneTech.
                </p>
                <ul class="feature-list">
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
                    <li class="feature-item">
                        <i class="fa-solid fa-heart-pulse"></i>
                        <span>Employee Health & Safety (EHS)</span>
                    </li>
                </ul>
            </div>
            <div class="hero-footer">
                &copy; 2026 <a href="https://global1onetech.com/" target="_blank">Global 1 OneTech</a> &bull; All Rights Reserved.
            </div>
        </div>

        <!-- Form Section -->
        <div class="form-panel">
            <div class="form-logo">
                <img src="/Personalization/logos/logo-main.png" alt="Global 1 OneTech" />
            </div>
            <div class="form-header">
                <h2>Sign in to G1 Health EMR</h2>
                <p>Enter your system credentials to continue</p>
            </div>
            <form action="/login" method="POST">
                <div class="input-group">
                    <label for="username">Username</label>
                    <div class="input-wrapper">
                        <i class="fa-solid fa-user"></i>
                        <input type="text" id="username" name="username" value="admin" required />
                    </div>
                </div>
                <div class="input-group">
                    <label for="password">Password</label>
                    <div class="input-wrapper">
                        <i class="fa-solid fa-lock"></i>
                        <input type="password" id="password" name="password" value="pass123" required />
                    </div>
                </div>
                <div class="form-options">
                    <label class="remember-me">
                        <input type="checkbox" name="remember" checked />
                        <span>Remember me</span>
                    </label>
                    <a href="#" class="forgot-link">Forgot password?</a>
                </div>
                <button type="submit" class="btn-submit">
                    <span>Sign In to Dashboard</span>
                    <i class="fa-solid fa-arrow-right"></i>
                </button>
                <div class="demo-credentials-badge">
                    Demo Access: User: <code>admin</code> | Password: <code>pass123</code>
                </div>
            </form>
        </div>
    </div>
</body>
</html>
"""

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Dashboard - G1 Health EMR (Global 1 OneTech)</title>
    <link rel="icon" href="/Personalization/logos/favicon.ico" />
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&family=Inter:wght@400;500;600;700&display=swap" />
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" />
    <style>
        :root {
            --brand-primary: #253545;
            --brand-primary-hover: #1b2838;
            --brand-cyan: #00ffa1;
            --brand-accent: #00bfa5;
            --sidebar-bg: #1b2838;
            --sidebar-text: #f8fafc;
            --card-bg: #ffffff;
            --bg-page: #f8fafc;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Nunito', 'Inter', sans-serif;
        }

        body {
            background-color: var(--bg-page);
            display: flex;
            min-height: 100vh;
            overflow-x: hidden;
        }

        /* Sidebar */
        .sidebar {
            width: 260px;
            background: var(--sidebar-bg);
            color: var(--sidebar-text);
            display: flex;
            flex-direction: column;
            flex-shrink: 0;
            border-right: 1px solid rgba(255, 255, 255, 0.05);
        }

        .sidebar-brand {
            padding: 20px;
            background: rgba(0, 0, 0, 0.2);
            display: flex;
            align-items: center;
            gap: 12px;
            border-bottom: 2px solid var(--brand-cyan);
        }

        .sidebar-brand img {
            max-height: 38px;
            filter: brightness(0) invert(1);
        }

        .nav-menu {
            list-style: none;
            padding: 16px 0;
            display: flex;
            flex-direction: column;
            gap: 4px;
        }

        .nav-section-title {
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: #64748b;
            padding: 12px 24px 6px;
            font-weight: 700;
        }

        .nav-item a {
            display: flex;
            align-items: center;
            gap: 14px;
            padding: 12px 24px;
            color: #cbd5e1;
            text-decoration: none;
            font-size: 14px;
            font-weight: 600;
            transition: all 0.2s;
        }

        .nav-item a:hover {
            background: rgba(255, 255, 255, 0.06);
            color: #ffffff;
        }

        .nav-item.active a {
            background: #253545;
            color: #ffffff;
            border-left: 4px solid var(--brand-cyan);
        }

        .nav-item i {
            font-size: 16px;
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
            font-size: 10px;
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
            overflow-y: auto;
        }

        .top-navbar {
            height: 64px;
            background: var(--brand-primary);
            color: #ffffff;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 28px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }

        .top-navbar .facility-title {
            font-size: 16px;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .top-navbar .facility-title span {
            color: var(--brand-cyan);
        }

        .user-profile {
            display: flex;
            align-items: center;
            gap: 14px;
        }

        .user-avatar {
            width: 36px;
            height: 36px;
            background: rgba(255, 255, 255, 0.1);
            border: 1.5px solid var(--brand-cyan);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 14px;
            color: var(--brand-cyan);
        }

        .btn-logout {
            color: #cbd5e1;
            text-decoration: none;
            font-size: 13px;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 6px;
            padding: 6px 12px;
            border-radius: 6px;
            background: rgba(0, 0, 0, 0.2);
            transition: all 0.2s;
        }

        .btn-logout:hover {
            color: #ff6b6b;
            background: rgba(255, 0, 0, 0.1);
        }

        .content-area {
            padding: 32px 28px;
        }

        .page-header {
            margin-bottom: 28px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .page-header h1 {
            font-size: 24px;
            font-weight: 800;
            color: #1e293b;
        }

        .page-header p {
            font-size: 14px;
            color: #64748b;
            margin-top: 4px;
        }

        /* Stats Grid */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 20px;
            margin-bottom: 32px;
        }

        .stat-card {
            background: #ffffff;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
            display: flex;
            align-items: center;
            gap: 16px;
            border-left: 4px solid var(--brand-primary);
        }

        .stat-card.cyan {
            border-left-color: var(--brand-cyan);
        }

        .stat-card.teal {
            border-left-color: var(--brand-accent);
        }

        .stat-icon {
            width: 48px;
            height: 48px;
            border-radius: 10px;
            background: #f1f5f9;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            color: var(--brand-primary);
        }

        .stat-content h3 {
            font-size: 24px;
            font-weight: 800;
            color: #0f172a;
        }

        .stat-content p {
            font-size: 13px;
            color: #64748b;
            font-weight: 600;
        }

        /* Modules Grid */
        .modules-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 24px;
        }

        .module-card {
            background: #ffffff;
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }

        .module-card-header {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 12px;
        }

        .module-card-header i {
            font-size: 22px;
            color: var(--brand-primary);
        }

        .module-card-header h3 {
            font-size: 17px;
            font-weight: 700;
            color: #1e293b;
        }

        .module-card p {
            font-size: 13px;
            color: #64748b;
            line-height: 1.5;
            margin-bottom: 20px;
        }

        .btn-module {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 9px 16px;
            background: var(--brand-primary);
            color: #ffffff;
            text-decoration: none;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 700;
            width: fit-content;
            transition: all 0.2s;
        }

        .btn-module:hover {
            background: var(--brand-primary-hover);
            color: var(--brand-cyan);
        }
    </style>
</head>
<body>
    <!-- Sidebar -->
    <aside class="sidebar">
        <div class="sidebar-brand">
            <img src="/Personalization/logos/logo-main.png" alt="G1 Health EMR" />
        </div>
        <ul class="nav-menu">
            <li class="nav-section-title">Core Operations</li>
            <li class="nav-item active"><a href="/dashboard"><i class="fa-solid fa-chart-pie"></i><span>Dashboard</span></a></li>
            <li class="nav-item"><a href="#"><i class="fa-solid fa-user-plus"></i><span>Patient Registration</span></a></li>
            <li class="nav-item"><a href="#"><i class="fa-solid fa-calendar-check"></i><span>Appointments</span></a></li>
            <li class="nav-item"><a href="#"><i class="fa-solid fa-file-invoice-dollar"></i><span>Billing & Invoicing</span></a></li>
            
            <li class="nav-section-title">Clinical & Diagnostic</li>
            <li class="nav-item"><a href="#"><i class="fa-solid fa-stethoscope"></i><span>Clinical EMR</span></a></li>
            <li class="nav-item"><a href="#"><i class="fa-solid fa-flask-vial"></i><span>Laboratory</span></a></li>
            <li class="nav-item"><a href="#"><i class="fa-solid fa-x-ray"></i><span>Radiology</span></a></li>
            <li class="nav-item"><a href="#"><i class="fa-solid fa-pills"></i><span>Pharmacy & Inventory</span></a></li>

            <li class="nav-section-title">Smart Cloud Extensions</li>
            <li class="nav-item"><a href="#"><i class="fa-solid fa-robot"></i><span>AI CRM & Leads</span><span class="badge-new">NEW</span></a></li>
            <li class="nav-item"><a href="#"><i class="fa-solid fa-id-card-clip"></i><span>Patient 360 (PIS)</span><span class="badge-new">NEW</span></a></li>
            <li class="nav-item"><a href="#"><i class="fa-solid fa-heart-pulse"></i><span>Employee Health (EHS)</span><span class="badge-new">NEW</span></a></li>
            
            <li class="nav-section-title">Administration</li>
            <li class="nav-item"><a href="#"><i class="fa-solid fa-sliders"></i><span>White-Label Settings</span></a></li>
        </ul>
    </aside>

    <!-- Main Content -->
    <div class="main-wrapper">
        <header class="top-navbar">
            <div class="facility-title">
                <i class="fa-solid fa-hospital"></i>
                <span>Global 1 OneTech Medical & Health Center</span>
            </div>
            <div class="user-profile">
                <div class="user-avatar">AD</div>
                <div>
                    <div style="font-size: 13px; font-weight: 700;">Administrator</div>
                    <div style="font-size: 11px; color: #94a3b8;">Super Admin</div>
                </div>
                <a href="/Account/Login" class="btn-logout">
                    <i class="fa-solid fa-right-from-bracket"></i>
                    <span>Sign Out</span>
                </a>
            </div>
        </header>

        <main class="content-area">
            <div class="page-header">
                <div>
                    <h1>Executive Healthcare Dashboard</h1>
                    <p>Welcome to G1 Health EMR &bull; Powered by Global 1 OneTech</p>
                </div>
            </div>

            <!-- Stats Grid -->
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
                        <h3>92%</h3>
                        <p>Inpatient Bed Occupancy</p>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon"><i class="fa-solid fa-robot"></i></div>
                    <div class="stat-content">
                        <h3>32</h3>
                        <p>AI CRM Active Inquiries</p>
                    </div>
                </div>
            </div>

            <!-- Major Modules Grid -->
            <div class="modules-grid">
                <div class="module-card">
                    <div>
                        <div class="module-card-header">
                            <i class="fa-solid fa-robot" style="color: var(--brand-accent);"></i>
                            <h3>AI CRM & Patient Engagement</h3>
                        </div>
                        <p>Omnichannel patient intake, AI-driven symptom triage, automated discharge follow-ups, and WhatsApp appointment reminders.</p>
                    </div>
                    <a href="#" class="btn-module">Open AI CRM Console <i class="fa-solid fa-arrow-right"></i></a>
                </div>

                <div class="module-card">
                    <div>
                        <div class="module-card-header">
                            <i class="fa-solid fa-id-card-clip" style="color: var(--brand-primary);"></i>
                            <h3>Patient 360 Information System</h3>
                        </div>
                        <p>Longitudinal clinical timeline, digital patient vault, laboratory test results, prescription histories, and family record linking.</p>
                    </div>
                    <a href="#" class="btn-module">View Patient 360 <i class="fa-solid fa-arrow-right"></i></a>
                </div>

                <div class="module-card">
                    <div>
                        <div class="module-card-header">
                            <i class="fa-solid fa-heart-pulse" style="color: #ef4444;"></i>
                            <h3>Employee Health & Safety (EHS)</h3>
                        </div>
                        <p>Hospital staff health surveillance, occupational immunization tracking, needlestick incident reporting, and dosimetry monitoring.</p>
                    </div>
                    <a href="#" class="btn-module">Open EHS Module <i class="fa-solid fa-arrow-right"></i></a>
                </div>
            </div>
        </main>
    </div>
</body>
</html>
"""

class G1HealthRequestHandler(http.server.BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path in ["/", "/Account/Login", "/account/login"]:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(LOGIN_HTML.encode("utf-8"))
            return

        if path in ["/dashboard", "/Home/Index", "/home/index"]:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(DASHBOARD_HTML.encode("utf-8"))
            return

        # Serve static assets from PROJECT_ROOT
        clean_path = path.lstrip("/")
        file_path = os.path.join(PROJECT_ROOT, clean_path)
        if not os.path.exists(file_path):
            file_path = os.path.join(BASE_DIR, "wwwroot", clean_path)

        if os.path.isfile(file_path):
            self.send_response(200)
            mime, _ = mimetypes.guess_type(file_path)
            self.send_header("Content-Type", mime or "application/octet-stream")
            self.end_headers()
            with open(file_path, "rb") as f:
                self.wfile.write(f.read())
            return

        self.send_response(404)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Not Found")

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path in ["/login", "/Account/Login"]:
            self.send_response(303)
            self.send_header("Location", "/dashboard")
            self.end_headers()
            return

def run_server():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), G1HealthRequestHandler) as httpd:
        print(f"G1 Health EMR Server running on http://localhost:{PORT}")
        httpd.serve_forever()

if __name__ == "__main__":
    run_server()
