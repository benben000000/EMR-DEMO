# Antigravity Agent Workspace Guidelines: Enterprise Hospital EMR

## 1. Personalization & White-Labeling Protocol
- When asked to customize branding, logos, hospital names, contact details, or themes, **ALWAYS check the `/Personalization` directory first**:
  - `Personalization/hospital-info/hospital-config.json` (Hospital name, phone, email, address, PAN)
  - `Personalization/theme/theme.json` and `Personalization/theme/theme.css` (Brand colors, UI tokens)
  - `Personalization/logos/` (`logo-main.png`, `logo-white.png`, `logo-phrm.png`, `favicon.ico`, `watermark.png`)
  - `Personalization/print-headers/` (`invoice-header.png`, `lab-header.png`, `discharge-header.png`)
- **Zero Hardcoded Hospital Logic**: Never use `if (hospitalName == "...")` in code. Use dynamic parameter lookups in `CORE_CFG_Parameters`.

## 2. Frontend Refactoring Guidelines
- Target decoupled, modern SPA architecture with CSS custom properties (`--brand-primary`, `--sidebar-bg`, etc.).
- Never modify DOM elements with jQuery in Angular components; use reactive state and Angular services.
- Ensure dual calendar compatibility (Gregorian AD and Nepali Bikram Sambat BS) through `NepaliCalendarService`.

## 3. Backend & API Guidelines
- Register all new domain services in `Code/Websites/HospitalEMR/DependencyInjection/HospitalServicesExtensions.cs`.
- All API controllers must inherit from `CommonController`, enforce JWT Bearer auth, and return `HospitalHTTPResponse<T>`.
- Register new EF entities in `HospitalEMR.ServerModel` and `HospitalEMR.DalLayer`.

## 4. Database Safety Rules
- Wrap data manipulation in transactions with error handling.
- Verify `OBJECTPROPERTY(..., 'TableHasIdentity') = 1` before invoking `DBCC CHECKIDENT`.
