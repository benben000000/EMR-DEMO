#!/usr/bin/env python3
"""
G1 Health EMR - macOS Full-Feature Interactive Application & Demo Runner
Powered by Global 1 OneTech (https://global1onetech.com/)
All modules clickable with live interactive state, modals, data tables, and print previews.
"""

import http.server
import socketserver
import urllib.parse
import os
import mimetypes
import json

PORT = 5000
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
BASE_DIR = os.path.abspath(os.path.join(PROJECT_ROOT, "Code/Websites/DanpheEMR"))

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
            min-height: 620px;
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
            padding: 48px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            background: #ffffff;
        }

        .form-logo { text-align: center; margin-bottom: 28px; }
        .form-logo img { max-height: 50px; }

        .form-header { text-align: center; margin-bottom: 28px; }
        .form-header h2 { font-size: 24px; font-weight: 800; color: #1e293b; }
        .form-header p { font-size: 13px; color: #64748b; margin-top: 4px; }

        .input-group { margin-bottom: 20px; }
        .input-group label { display: block; font-size: 13px; font-weight: 700; color: #334155; margin-bottom: 6px; }

        .input-wrapper { position: relative; display: flex; align-items: center; }
        .input-wrapper i { position: absolute; left: 14px; color: #94a3b8; font-size: 15px; }

        .input-wrapper input {
            width: 100%;
            padding: 13px 14px 13px 42px;
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
            margin-bottom: 24px;
        }

        .remember-me { display: flex; align-items: center; gap: 6px; color: #475569; cursor: pointer; }
        .forgot-link { color: var(--brand-primary); text-decoration: none; font-weight: 700; }

        .btn-submit {
            width: 100%;
            padding: 14px;
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
            .auth-container { flex-direction: column; }
            .hero-panel, .form-panel { padding: 32px; }
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
                <p>Enter system credentials to launch executive demo</p>
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
                <button type="submit" class="btn-submit" id="btn-login-submit">
                    <span>Sign In to Dashboard</span>
                    <i class="fa-solid fa-arrow-right"></i>
                </button>
                <div class="demo-credentials-badge">
                    Default Credentials: <code>admin</code> / <code>pass123</code>
                </div>
            </form>
        </div>
    </div>
</body>
</html>
"""

# Load complete single-page application with all modules working
APP_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>G1 Health EMR - Global 1 OneTech Hospital Suite</title>
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
            padding: 18px 20px;
            background: rgba(0, 0, 0, 0.25);
            display: flex;
            align-items: center;
            gap: 12px;
            border-bottom: 2px solid var(--brand-cyan);
        }

        .sidebar-brand img {
            max-height: 38px;
            width: auto;
            filter: brightness(0) invert(1);
        }

        .nav-menu-wrapper {
            flex: 1;
            overflow-y: auto;
            padding: 12px 0;
        }

        .nav-menu {
            list-style: none;
            display: flex;
            flex-direction: column;
            gap: 2px;
        }

        .nav-section-title {
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: #64748b;
            padding: 14px 24px 6px;
            font-weight: 800;
        }

        .nav-item a {
            display: flex;
            align-items: center;
            gap: 14px;
            padding: 11px 24px;
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

        .top-navbar {
            height: 64px;
            background: var(--brand-primary);
            color: #ffffff;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 28px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            border-bottom: 2px solid var(--brand-cyan);
            flex-shrink: 0;
        }

        .top-navbar .facility-title {
            font-size: 15px;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 10px;
            letter-spacing: 0.2px;
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
            font-weight: 800;
            font-size: 13px;
            color: var(--brand-cyan);
        }

        .btn-logout {
            color: #cbd5e1;
            text-decoration: none;
            font-size: 12.5px;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 6px;
            padding: 6px 12px;
            border-radius: 6px;
            background: rgba(0, 0, 0, 0.25);
            transition: all 0.2s;
        }

        .btn-logout:hover {
            color: #ff6b6b;
            background: rgba(255, 0, 0, 0.15);
        }

        .content-area {
            flex: 1;
            overflow-y: auto;
            padding: 28px;
        }

        /* Modules Views */
        .module-view {
            display: none;
            animation: fadeIn 0.25s ease-in-out;
        }

        .module-view.active {
            display: block;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(4px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* Section Headings */
        .view-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 24px;
            padding-bottom: 16px;
            border-bottom: 1px solid var(--border-color);
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
            padding: 16px 20px;
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

        .search-box input:focus {
            border-color: var(--brand-primary);
        }

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
            padding: 13px 18px;
            border-bottom: 1px solid var(--border-color);
            color: #1e293b;
        }

        .emr-table tbody tr:hover {
            background-color: #f8fafc;
        }

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
            grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
            gap: 20px;
            margin-bottom: 28px;
        }

        .stat-card {
            background: #ffffff;
            border-radius: 12px;
            padding: 22px;
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

        /* Form Inputs */
        .form-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
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

        .form-control:focus {
            border-color: var(--brand-primary);
        }

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

        .modal-overlay.active {
            display: flex;
        }

        .modal-box {
            background: #ffffff;
            border-radius: 16px;
            width: 700px;
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

        .modal-body {
            padding: 24px;
        }

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

        .invoice-header-branding img {
            max-height: 52px;
        }

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
    </style>
</head>
<body>
    <!-- Sidebar -->
    <aside class="sidebar">
        <div class="sidebar-brand">
            <img src="/Personalization/logos/logo-main.png" alt="G1 Health EMR" />
        </div>
        <div class="nav-menu-wrapper">
            <ul class="nav-menu">
                <li class="nav-section-title">Core Operations</li>
                <li class="nav-item active" data-target="view-dashboard">
                    <a onclick="switchTab('view-dashboard', this)"><i class="fa-solid fa-chart-pie"></i><span>Dashboard</span></a>
                </li>
                <li class="nav-item" data-target="view-patient-reg">
                    <a onclick="switchTab('view-patient-reg', this)"><i class="fa-solid fa-user-plus"></i><span>Patient Registration</span></a>
                </li>
                <li class="nav-item" data-target="view-appointments">
                    <a onclick="switchTab('view-appointments', this)"><i class="fa-solid fa-calendar-check"></i><span>Appointments</span></a>
                </li>
                <li class="nav-item" data-target="view-billing">
                    <a onclick="switchTab('view-billing', this)"><i class="fa-solid fa-file-invoice-dollar"></i><span>Billing & Invoicing</span></a>
                </li>
                
                <li class="nav-section-title">Clinical & Diagnostic</li>
                <li class="nav-item" data-target="view-clinical">
                    <a onclick="switchTab('view-clinical', this)"><i class="fa-solid fa-stethoscope"></i><span>Clinical EMR (Doctor)</span></a>
                </li>
                <li class="nav-item" data-target="view-laboratory">
                    <a onclick="switchTab('view-laboratory', this)"><i class="fa-solid fa-flask-vial"></i><span>Laboratory</span></a>
                </li>
                <li class="nav-item" data-target="view-radiology">
                    <a onclick="switchTab('view-radiology', this)"><i class="fa-solid fa-x-ray"></i><span>Radiology & PACS</span></a>
                </li>
                <li class="nav-item" data-target="view-pharmacy">
                    <a onclick="switchTab('view-pharmacy', this)"><i class="fa-solid fa-pills"></i><span>Pharmacy & Inventory</span></a>
                </li>

                <li class="nav-section-title">Smart Cloud Extensions</li>
                <li class="nav-item" data-target="view-aicrm">
                    <a onclick="switchTab('view-aicrm', this)"><i class="fa-solid fa-robot"></i><span>AI CRM & Leads</span><span class="badge-new">NEW</span></a>
                </li>
                <li class="nav-item" data-target="view-patient360">
                    <a onclick="switchTab('view-patient360', this)"><i class="fa-solid fa-id-card-clip"></i><span>Patient 360 (PIS)</span><span class="badge-new">NEW</span></a>
                </li>
                <li class="nav-item" data-target="view-ehs">
                    <a onclick="switchTab('view-ehs', this)"><i class="fa-solid fa-heart-pulse"></i><span>Employee Health (EHS)</span><span class="badge-new">NEW</span></a>
                </li>
                
                <li class="nav-section-title">Administration</li>
                <li class="nav-item" data-target="view-whitelabel">
                    <a onclick="switchTab('view-whitelabel', this)"><i class="fa-solid fa-sliders"></i><span>White-Label Settings</span></a>
                </li>
            </ul>
        </div>
    </aside>

    <!-- Main Wrapper -->
    <div class="main-wrapper">
        <header class="top-navbar">
            <div class="facility-title">
                <i class="fa-solid fa-hospital" style="color: var(--brand-cyan);"></i>
                <span id="header-facility-name">Global 1 OneTech Medical & Health Center</span>
            </div>
            <div class="user-profile">
                <div class="user-avatar">AD</div>
                <div>
                    <div style="font-size: 13px; font-weight: 700;">Administrator</div>
                    <div style="font-size: 11px; color: #cbd5e1;">Global 1 OneTech Super Admin</div>
                </div>
                <a href="/Account/Login" class="btn-logout">
                    <i class="fa-solid fa-right-from-bracket"></i>
                    <span>Sign Out</span>
                </a>
            </div>
        </header>

        <main class="content-area">
            
            <!-- 1. DASHBOARD VIEW -->
            <section id="view-dashboard" class="module-view active">
                <div class="view-header">
                    <div>
                        <h1>Executive Healthcare Dashboard</h1>
                        <p>Welcome to G1 Health EMR &bull; Powered by Global 1 OneTech</p>
                    </div>
                    <div>
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
                            <h3>92%</h3>
                            <p>Inpatient Bed Occupancy</p>
                        </div>
                    </div>
                    <div class="stat-card blue">
                        <div class="stat-icon"><i class="fa-solid fa-robot"></i></div>
                        <div class="stat-content">
                            <h3>32</h3>
                            <p>AI CRM Inquiries</p>
                        </div>
                    </div>
                </div>

                <div class="grid-2col">
                    <div class="card-box">
                        <div class="card-box-header">
                            <h3><i class="fa-solid fa-user-clock" style="color: var(--brand-primary);"></i> Recent Patient Registrations</h3>
                            <a href="javascript:void(0)" onclick="switchTab('view-patient-reg', document.querySelector('[data-target=view-patient-reg]'))" style="font-size: 12px; font-weight:700; color:var(--brand-primary); text-decoration:none;">View All &rarr;</a>
                        </div>
                        <table class="emr-table">
                            <thead>
                                <tr>
                                    <th>Hospital No</th>
                                    <th>Patient Name</th>
                                    <th>Age/Sex</th>
                                    <th>Contact</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td><strong>G1-2026-0089</strong></td>
                                    <td>Maria Santos</td>
                                    <td>34 Y / F</td>
                                    <td>+63 917 555 1234</td>
                                    <td><span class="status-badge status-active">Registered</span></td>
                                </tr>
                                <tr>
                                    <td><strong>G1-2026-0090</strong></td>
                                    <td>Juan Dela Cruz</td>
                                    <td>45 Y / M</td>
                                    <td>+63 920 444 8901</td>
                                    <td><span class="status-badge status-completed">In Consultation</span></td>
                                </tr>
                                <tr>
                                    <td><strong>G1-2026-0091</strong></td>
                                    <td>Elena Reyes</td>
                                    <td>28 Y / F</td>
                                    <td>+63 918 333 7654</td>
                                    <td><span class="status-badge status-pending">In Triage</span></td>
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
                                    <td><button class="btn-primary-action" style="padding:4px 10px; font-size:11px;" onclick="showToast('AI Auto-Booked with Dr. Lim (Neurology)')">Auto-Book</button></td>
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
                <div class="view-header">
                    <div>
                        <h1>Patient Registration & Demographics</h1>
                        <p>Register new outpatients/inpatients and manage master patient indexing (EMPI)</p>
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
                        <div style="font-size: 13px; color: var(--text-muted);">
                            Showing <strong>4</strong> registered patients
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
                                    <button class="btn-primary-action" style="padding: 5px 10px; font-size: 12px;" onclick="viewPatient360('Maria Santos', 'G1-2026-0089')">
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
                                    <button class="btn-primary-action" style="padding: 5px 10px; font-size: 12px;" onclick="viewPatient360('Juan Dela Cruz', 'G1-2026-0090')">
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
                                    <button class="btn-primary-action" style="padding: 5px 10px; font-size: 12px;" onclick="viewPatient360('Elena Reyes', 'G1-2026-0091')">
                                        <i class="fa-solid fa-id-card"></i> 360° View
                                    </button>
                                </td>
                            </tr>
                            <tr>
                                <td><strong>G1-2026-0092</strong></td>
                                <td>Antonio Gonzales</td>
                                <td>52 Y / Male</td>
                                <td>+63 919 222 9988</td>
                                <td>Pasig City, Manila</td>
                                <td><span class="status-badge status-completed">Corporate EHS</span></td>
                                <td>
                                    <button class="btn-primary-action" style="padding: 5px 10px; font-size: 12px;" onclick="viewPatient360('Antonio Gonzales', 'G1-2026-0092')">
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

                <div class="grid-3col">
                    <div class="stat-card">
                        <div class="stat-icon"><i class="fa-solid fa-user-doctor"></i></div>
                        <div class="stat-content">
                            <h3>14</h3>
                            <p>Doctors on Duty Today</p>
                        </div>
                    </div>
                    <div class="stat-card cyan">
                        <div class="stat-icon"><i class="fa-solid fa-calendar-check"></i></div>
                        <div class="stat-content">
                            <h3>58</h3>
                            <p>Completed Consultations</p>
                        </div>
                    </div>
                    <div class="stat-card teal">
                        <div class="stat-icon"><i class="fa-solid fa-clock"></i></div>
                        <div class="stat-content">
                            <h3>26</h3>
                            <p>Waiting in OPD Queue</p>
                        </div>
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
                        <tbody>
                            <tr>
                                <td>09:00 AM</td>
                                <td>Maria Santos</td>
                                <td>Dr. Roberto Tan, MD</td>
                                <td>Cardiology</td>
                                <td><span class="status-badge status-completed">Completed</span></td>
                                <td><button class="btn-secondary" style="padding:4px 8px; font-size:12px;" onclick="showToast('Opening Doctor E-Prescription Slip...')">View Rx</button></td>
                            </tr>
                            <tr>
                                <td>10:30 AM</td>
                                <td>Juan Dela Cruz</td>
                                <td>Dr. Alicia Gomez, MD</td>
                                <td>Internal Medicine</td>
                                <td><span class="status-badge status-active">In Consultation</span></td>
                                <td><button class="btn-primary-action" style="padding:4px 8px; font-size:12px;" onclick="switchTab('view-clinical', document.querySelector('[data-target=view-clinical]'))">Open Desk</button></td>
                            </tr>
                            <tr>
                                <td>11:15 AM</td>
                                <td>Elena Reyes</td>
                                <td>Dr. Vincent Lim, MD</td>
                                <td>Neurology</td>
                                <td><span class="status-badge status-pending">Waiting in Room 204</span></td>
                                <td><button class="btn-primary-action" style="padding:4px 8px; font-size:12px;" onclick="showToast('Calling Patient to Doctor Chamber...')">Call Patient</button></td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </section>

            <!-- 4. BILLING & INVOICING VIEW -->
            <section id="view-billing" class="module-view">
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
                        <tbody>
                            <tr>
                                <td><strong>INV-2026-0412</strong></td>
                                <td>24-Aug-2026 10:15 AM</td>
                                <td>Maria Santos</td>
                                <td>₱ 2,850.00</td>
                                <td>Credit Card / HMO</td>
                                <td><span class="status-badge status-completed">Paid</span></td>
                                <td>
                                    <button class="btn-primary-action" style="padding: 4px 10px; font-size: 12px;" onclick="openPrintInvoice('INV-2026-0412', 'Maria Santos', '2,850.00')">
                                        <i class="fa-solid fa-print"></i> Print Receipt
                                    </button>
                                </td>
                            </tr>
                            <tr>
                                <td><strong>INV-2026-0413</strong></td>
                                <td>24-Aug-2026 11:00 AM</td>
                                <td>Juan Dela Cruz</td>
                                <td>₱ 1,450.00</td>
                                <td>Cash / PhilHealth</td>
                                <td><span class="status-badge status-completed">Paid</span></td>
                                <td>
                                    <button class="btn-primary-action" style="padding: 4px 10px; font-size: 12px;" onclick="openPrintInvoice('INV-2026-0413', 'Juan Dela Cruz', '1,450.00')">
                                        <i class="fa-solid fa-print"></i> Print Receipt
                                    </button>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </section>

            <!-- 5. CLINICAL EMR VIEW -->
            <section id="view-clinical" class="module-view">
                <div class="view-header">
                    <div>
                        <h1>Doctor Consultation Desk (Clinical EMR)</h1>
                        <p>Record clinical encounters, ICD-10 diagnoses, vital signs, and prescribe electronic medications</p>
                    </div>
                    <div>
                        <button class="btn-accent-action" onclick="showToast('Electronic Prescription Signed & Synced to Pharmacy Counter!')">
                            <i class="fa-solid fa-signature"></i> Sign & Send e-Prescription
                        </button>
                    </div>
                </div>

                <div class="grid-2col">
                    <div class="card-box">
                        <div class="card-box-header">
                            <h3><i class="fa-solid fa-user-tag" style="color:var(--brand-primary);"></i> Active Patient: Juan Dela Cruz (45 Y / M)</h3>
                            <span class="status-badge status-active">Hospital No: G1-2026-0090</span>
                        </div>
                        <div class="form-grid">
                            <div class="form-group">
                                <label>Blood Pressure (mmHg)</label>
                                <input type="text" class="form-control" value="120/80" />
                            </div>
                            <div class="form-group">
                                <label>Pulse Rate (bpm)</label>
                                <input type="text" class="form-control" value="76" />
                            </div>
                            <div class="form-group">
                                <label>Temperature (°C)</label>
                                <input type="text" class="form-control" value="36.8" />
                            </div>
                            <div class="form-group">
                                <label>SpO2 (%)</label>
                                <input type="text" class="form-control" value="98%" />
                            </div>
                        </div>
                        <div class="form-group" style="margin-bottom:14px;">
                            <label>Chief Complaints & Subjective History</label>
                            <textarea class="form-control" rows="3">Patient reports recurrent mild headache for 3 days, accompanied by eye strain during computer screen work.</textarea>
                        </div>
                        <div class="form-group">
                            <label>ICD-10 Primary Diagnosis</label>
                            <input type="text" class="form-control" value="G44.2 - Tension-type headache" />
                        </div>
                    </div>

                    <div class="card-box">
                        <div class="card-box-header">
                            <h3><i class="fa-solid fa-pills" style="color:var(--brand-accent);"></i> Electronic Prescription Builder</h3>
                        </div>
                        <table class="emr-table" style="margin-bottom:16px;">
                            <thead>
                                <tr>
                                    <th>Medicine Name</th>
                                    <th>Dosage</th>
                                    <th>Frequency</th>
                                    <th>Days</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td><strong>Paracetamol 500mg</strong></td>
                                    <td>1 Tab</td>
                                    <td>TID (Every 8h)</td>
                                    <td>5 Days</td>
                                </tr>
                                <tr>
                                    <td><strong>Vitamin B-Complex</strong></td>
                                    <td>1 Capsule</td>
                                    <td>OD (Once Daily)</td>
                                    <td>30 Days</td>
                                </tr>
                            </tbody>
                        </table>
                        <button class="btn-primary-action" style="width:100%; justify-content:center;" onclick="showToast('Added Medicine to Prescription List')">
                            <i class="fa-solid fa-plus"></i> Add Another Medication
                        </button>
                    </div>
                </div>
            </section>

            <!-- 6. LABORATORY VIEW -->
            <section id="view-laboratory" class="module-view">
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
                        <tbody>
                            <tr>
                                <td><strong>LAB-9041</strong></td>
                                <td>Maria Santos</td>
                                <td>Complete Blood Count (CBC) + ESR</td>
                                <td><span class="status-badge status-completed">Collected</span></td>
                                <td>WBC: 6.8 | Hb: 13.2 | Plt: 240k</td>
                                <td><button class="btn-accent-action" style="padding:4px 10px; font-size:12px;" onclick="showToast('Pathology Report Verified and Published to Patient 360 Portal')"><i class="fa-solid fa-circle-check"></i> Verified</button></td>
                            </tr>
                            <tr>
                                <td><strong>LAB-9042</strong></td>
                                <td>Juan Dela Cruz</td>
                                <td>Lipid Profile & Fasting Blood Sugar</td>
                                <td><span class="status-badge status-active">Processing</span></td>
                                <td>FBS: 98 mg/dL | Chol: 185 mg/dL</td>
                                <td><button class="btn-primary-action" style="padding:4px 10px; font-size:12px;" onclick="showToast('Verification Complete')">Verify Result</button></td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </section>

            <!-- 7. RADIOLOGY VIEW -->
            <section id="view-radiology" class="module-view">
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
                        <tbody>
                            <tr>
                                <td><strong>RAD-3021</strong></td>
                                <td>Antonio Gonzales</td>
                                <td><span class="status-badge status-completed">Digital X-Ray</span></td>
                                <td>Chest PA View</td>
                                <td>Normal cardiothoracic ratio, clear lung fields.</td>
                                <td><button class="btn-primary-action" style="padding:4px 10px; font-size:12px;" onclick="showToast('Opening DICOM Web Viewer...')"><i class="fa-solid fa-eye"></i> View DICOM</button></td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </section>

            <!-- 8. PHARMACY VIEW -->
            <section id="view-pharmacy" class="module-view">
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

            <!-- 9. AI CRM VIEW (NEW) -->
            <section id="view-aicrm" class="module-view">
                <div class="view-header">
                    <div>
                        <h1>AI CRM & Intelligent Patient Engagement</h1>
                        <p>Omnichannel lead intake, AI clinical triage, automated WhatsApp discharge follow-ups</p>
                    </div>
                    <div>
                        <button class="btn-accent-action" onclick="openModal('modal-ai-simulation')">
                            <i class="fa-solid fa-wand-magic-sparkles"></i> Launch AI Triage Simulator
                        </button>
                    </div>
                </div>

                <div class="grid-3col">
                    <div class="stat-card cyan">
                        <div class="stat-icon"><i class="fa-brands fa-whatsapp"></i></div>
                        <div class="stat-content">
                            <h3>142</h3>
                            <p>Automated WhatsApp Check-ins Sent</p>
                        </div>
                    </div>
                    <div class="stat-card teal">
                        <div class="stat-icon"><i class="fa-solid fa-bullseye"></i></div>
                        <div class="stat-content">
                            <h3>94.8%</h3>
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

                <div class="table-card">
                    <div class="table-toolbar">
                        <h3 style="font-size: 15px; font-weight: 700;">Live Patient Inquiries & AI Follow-Up Pipeline</h3>
                    </div>
                    <table class="emr-table">
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

            <!-- 10. PATIENT 360 VIEW (PIS) -->
            <section id="view-patient360" class="module-view">
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
                                MS
                            </div>
                            <div>
                                <h2 style="font-size:20px; font-weight:800; color:#0f172a;" id="p360-name">Maria Santos</h2>
                                <p style="font-size:13px; color:#64748b;">Hospital No: <strong id="p360-code">G1-2026-0089</strong> &bull; 34 Y / Female &bull; Blood Group: B+ &bull; HMO: Gold Care</p>
                            </div>
                        </div>
                        <div>
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

            <!-- 11. EMPLOYEE HEALTH & SAFETY (EHS) VIEW -->
            <section id="view-ehs" class="module-view">
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
                        <tbody>
                            <tr>
                                <td><strong>EHS-INC-0012</strong></td>
                                <td>Nurse Clara Dizon</td>
                                <td>Operating Room (OR)</td>
                                <td>Needlestick Sharp Injury</td>
                                <td><span class="status-badge status-urgent">Moderate</span></td>
                                <td><span class="status-badge status-completed">PEP Day 1 Initiated</span></td>
                                <td><span class="status-badge status-active">Under Monitoring</span></td>
                            </tr>
                            <tr>
                                <td><strong>EHS-INC-0011</strong></td>
                                <td>Tech Marco Cruz</td>
                                <td>Radiology / CT Scan</td>
                                <td>Minor Contrast Splash</td>
                                <td><span class="status-badge status-completed">Minor</span></td>
                                <td>Eye Flush Completed</td>
                                <td><span class="status-badge status-completed">Resolved & Closed</span></td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </section>

            <!-- 12. WHITE-LABEL & PERSONALIZATION SETTINGS -->
            <section id="view-whitelabel" class="module-view">
                <div class="view-header">
                    <div>
                        <h1>White-Label & Personalization Settings</h1>
                        <p>Customize tenant brand name, contact details, tax numbers, and primary UI color tokens</p>
                    </div>
                    <div>
                        <button class="btn-accent-action" onclick="savePersonalizationSettings()">
                            <i class="fa-solid fa-floppy-disk"></i> Save & Apply Changes
                        </button>
                    </div>
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

        </main>
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
                <button class="btn-primary-action" onclick="closeModal('modal-new-appointment'); showToast('Appointment Booked & SMS Reminder Scheduled!');">Confirm Appointment</button>
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
                <button class="btn-primary-action" onclick="closeModal('modal-generate-invoice'); showToast('Invoice Generated & Receipt Printed!');">Process Payment & Print</button>
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

    <!-- TOAST NOTIFICATION -->
    <div id="toast-notification" class="toast-notify">
        <i class="fa-solid fa-circle-check" style="color: var(--brand-cyan);"></i>
        <span id="toast-message">Action executed successfully!</span>
    </div>

    <script>
        // Tab switching
        function switchTab(viewId, element) {
            document.querySelectorAll('.module-view').forEach(v => v.classList.remove('active'));
            document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
            
            const targetView = document.getElementById(viewId);
            if (targetView) targetView.classList.add('active');
            
            if (element) {
                const navItem = element.closest('.nav-item');
                if (navItem) navItem.classList.add('active');
            }
        }

        // Modal Controls
        function openModal(modalId) {
            const modal = document.getElementById(modalId);
            if (modal) modal.classList.add('active');
        }

        function closeModal(modalId) {
            const modal = document.getElementById(modalId);
            if (modal) modal.classList.remove('active');
        }

        // Toast Feedback
        function showToast(message) {
            const toast = document.getElementById('toast-notification');
            const msgEl = document.getElementById('toast-message');
            msgEl.textContent = message;
            toast.classList.add('show');
            setTimeout(() => toast.classList.remove('show'), 3500);
        }

        // Patient Registration
        function submitNewPatient() {
            const fname = document.getElementById('np-fname').value || 'New';
            const lname = document.getElementById('np-lname').value || 'Patient';
            const age = document.getElementById('np-age').value || '30';
            const gender = document.getElementById('np-gender').value || 'Male';
            const phone = document.getElementById('np-phone').value || '+63 900 000 0000';
            const scheme = document.getElementById('np-scheme').value || 'Self-Pay';
            const address = document.getElementById('np-address').value || 'Metro Manila';
            
            const code = 'G1-2026-00' + Math.floor(100 + Math.random() * 900);
            
            const tbody = document.querySelector('#patient-master-table tbody');
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><strong>${code}</strong></td>
                <td>${fname} ${lname}</td>
                <td>${age} Y / ${gender}</td>
                <td>${phone}</td>
                <td>${address}</td>
                <td><span class="status-badge status-active">${scheme}</span></td>
                <td>
                    <button class="btn-primary-action" style="padding: 5px 10px; font-size: 12px;" onclick="viewPatient360('${fname} ${lname}', '${code}')">
                        <i class="fa-solid fa-id-card"></i> 360° View
                    </button>
                </td>
            `;
            tbody.prepend(tr);
            closeModal('modal-new-patient');
            showToast(`Patient ${fname} ${lname} registered with Hospital No ${code}!`);
        }

        // Search Filter
        function filterPatientTable() {
            const query = document.getElementById('patient-search-input').value.toLowerCase();
            document.querySelectorAll('#patient-master-table tbody tr').forEach(tr => {
                const text = tr.innerText.toLowerCase();
                tr.style.display = text.includes(query) ? '' : 'none';
            });
        }

        // Patient 360 View Jump
        function viewPatient360(name, code) {
            document.getElementById('p360-name').textContent = name;
            document.getElementById('p360-code').textContent = code;
            switchTab('view-patient360', document.querySelector('[data-target=view-patient360]'));
            showToast(`Viewing 360° longitudinal medical record for ${name}`);
        }

        // Print Invoice Dialog
        function openPrintInvoice(invNo, patient, total) {
            document.getElementById('rcpt-no').textContent = invNo;
            document.getElementById('rcpt-patient').textContent = patient;
            document.getElementById('rcpt-total').textContent = '₱ ' + total;
            openModal('modal-print-invoice');
        }

        // AI Triage Simulator
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

        // White-Label Settings Save
        function savePersonalizationSettings() {
            const hospName = document.getElementById('cfg-hospital-name').value;
            document.getElementById('header-facility-name').textContent = hospName;
            showToast('Branding & White-Label configuration updated successfully!');
        }
    </script>
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

        if path in ["/dashboard", "/Home/Index", "/home/index", "/app"]:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(APP_HTML.encode("utf-8"))
            return

        # Static assets
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
        if parsed.path in ["/login", "/Account/Login", "/account/login"]:
            self.send_response(303)
            self.send_header("Location", "/dashboard")
            self.end_headers()
            return

def run_server():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), G1HealthRequestHandler) as httpd:
        print(f"G1 Health EMR Full Application running on http://localhost:{PORT}")
        httpd.serve_forever()

if __name__ == "__main__":
    run_server()
