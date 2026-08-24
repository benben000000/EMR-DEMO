# Personalization & Branding Assets Folder

Welcome to the **Personalization & White-Labeling** folder for this project. 

Whenever you want to rebrand, customize, or prepare the EMR for a client/hospital, place your assets and configuration files in this directory. The AI assistant is instructed via workspace rules to look into this directory first to automatically integrate logos, themes, contact details, and print headers across the codebase.

---

## 📁 Directory Structure & File Map

```
/Personalization/
├── logos/
│   ├── logo-main.png           # Primary hospital logo (Used in top navbar, headers, login)
│   ├── logo-white.png          # Inverted/White logo (Used on dark backgrounds/sidebars)
│   ├── logo-phrm.png           # Pharmacy/Dispensary logo (Optional, falls back to logo-main)
│   ├── favicon.ico             # Browser favicon icon (32x32 or 16x16)
│   └── watermark.png           # Faded watermark logo (Used for background of bill prints)
│
├── print-headers/
│   ├── invoice-header.png      # Header banner image for billing/invoices (Optional)
│   ├── lab-header.png          # Header banner image for lab test reports (Optional)
│   └── discharge-header.png    # Header banner image for discharge summaries (Optional)
│
├── theme/
│   ├── theme.json              # Primary, secondary, accent colors, and font definitions
│   └── theme.css               # CSS variable overrides (Optional)
│
└── hospital-info/
    └── hospital-config.json    # Hospital name, address, contact, tax/PAN, licenses
```

---

## 📄 File Details & Templates

### 1. `hospital-info/hospital-config.json`
Fill out your hospital or clinic information below:

```json
{
  "TenantCode": "MY_HOSPITAL",
  "HospitalName": "Grand Care Specialty Hospital & Research Center",
  "ShortName": "GrandCare",
  "Tagline": "Excellence in Healthcare & Patient Wellbeing",
  "Contact": {
    "Address": "452 Healthcare Boulevard, Medical District",
    "City": "Kathmandu",
    "Country": "Nepal",
    "Phone": "+977-1-4567890, +977-1-4567891",
    "Email": "info@grandcarehospital.com",
    "Website": "https://www.grandcarehospital.com",
    "TaxRegistrationNumber": "PAN-601234567"
  },
  "PrintSettings": {
    "InvoiceHeaderNote": "Government Approved Multi-Specialty Hospital",
    "InvoiceFooterNote": "Wishing you a speedy recovery! Valid for tax deduction as per local regulations.",
    "ShowWatermarkOnPrint": true
  }
}
```

### 2. `theme/theme.json`
Define your brand colors and font preferences:

```json
{
  "PrimaryColor": "#1e40af",
  "PrimaryHoverColor": "#1d4ed8",
  "SecondaryColor": "#0f172a",
  "AccentColor": "#0d9488",
  "SuccessColor": "#16a34a",
  "WarningColor": "#d97706",
  "DangerColor": "#dc2626",
  "SidebarBgColor": "#0f172a",
  "SidebarTextColor": "#f8fafc",
  "NavbarBgColor": "#ffffff",
  "NavbarTextColor": "#1e293b",
  "FontFamily": "Inter, Roboto, sans-serif"
}
```

---

## 🚀 How the AI Integrates These Files

When you prompt the AI with:
> *"Apply the personalization from `/Personalization`"* or *"Update the branding"*

The AI automatically:
1. **Copies & registers logos**: Maps `logo-main.png`, `logo-white.png`, `favicon.ico`, and `watermark.png` to active assets.
2. **Injects theme variables**: Applies CSS custom properties (`--brand-primary`, `--brand-secondary`, etc.) into the frontend.
3. **Updates Database Parameters**: Syncs `CustomerHeader`, `HospitalName`, `Contact`, and print settings into `CORE_CFG_Parameters`.
4. **Updates Login & Main UI**: Refreshes Login.cshtml and AppMain.html with your branding.
