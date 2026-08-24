# Workspace Rules: Refactoring, Personalization & SaaS Development

These rules apply to all AI coding assistants operating within this repository. Follow these guidelines during any refactoring, feature addition, or white-labeling task.

---

## 1. 🎨 Personalization & White-Labeling Rules

### Rule 1.1: Always Consult the `/Personalization` Directory First
Whenever tasked with updating branding, logos, themes, contact information, print headers, or preparing the software for a specific hospital or demo:
- **Inspect `/Personalization/`**:
  - `Personalization/hospital-info/hospital-config.json` -> Hospital name, address, phone, email, PAN/Tax ID.
  - `Personalization/theme/theme.json` and `Personalization/theme/theme.css` -> Brand colors, navbar/sidebar colors, typography.
  - `Personalization/logos/` -> `logo-main.png`, `logo-white.png`, `logo-phrm.png`, `favicon.ico`, `watermark.png`.
  - `Personalization/print-headers/` -> `invoice-header.png`, `lab-header.png`, `discharge-header.png`.

### Rule 1.2: Zero Hardcoded Hospital Logic (Strictly Forbidden)
- **NEVER** write conditional statements based on hospital names (e.g., `if (hospitalName == "Fishtail")` or `if (name.Contains("CMH"))`).
- **NEVER** create hospital-specific subdirectories inside feature modules (e.g., do NOT create `discharge-summary/templates/HospitalABC/`).
- **ALWAYS** use parameter-driven configuration stored in database `CORE_CFG_Parameters` (e.g., `CustomerHeader`, `TenantBrandConfig`, `DynamicTemplates`).

### Rule 1.3: Dynamic CSS Variables & Theming
- Do not use hardcoded hex colors for primary UI elements.
- Bind colors to CSS Custom Properties:
  ```css
  --brand-primary
  --brand-secondary
  --brand-accent
  --sidebar-bg
  --sidebar-text
  --navbar-bg
  --navbar-text
  ```

---

## 2. ⚡ Frontend Refactoring & Architecture Guidelines

### Rule 2.1: Modern Modular SPA Principles
- Maintain decoupled feature modules under `wwwroot/DanpheApp/src/app/` (or modernized standalone components in target Angular/React/Vite).
- Ensure every feature module has dedicated `shared/` services (`bl.service.ts`, `dl.service.ts`, `endpoint.service.ts`) encapsulating HTTP operations.
- Avoid passing raw untyped objects; define TypeScript interfaces/models in `<feature>/shared/<model>.model.ts`.

### Rule 2.2: Dual Calendar (Gregorian AD & Bikram Sambat BS) Safety
- DanpheEMR operates with dual calendar systems (English AD and Nepali BS).
- Always use `NepaliCalendarService` / `nepali-dates` for date conversion. Do not mutate raw JavaScript `Date` objects directly when handling BS fiscal dates.

### Rule 2.3: Reusable Data Grids & Modals
- Use standard `DanpheGridComponent` or the modernized table component with built-in export (Excel/PDF), filtering, search, and pagination.
- Avoid modifying global DOM elements directly via jQuery; use Angular reactive state and Angular CDK / Headless UI patterns.

---

## 3. 🛡️ Backend & API Guidelines

### Rule 3.1: Service Registration & Dependency Injection
- Whenever creating a new domain service, register it in `Code/Websites/DanpheEMR/DependencyInjection/DanpheServicesExtensions.cs` using `services.AddTransient<ITargetService, TargetService>();`.
- Do not bloat `Startup.cs` directly.

### Rule 3.2: API Controller Standards
- All domain controllers must inherit from `CommonController` to gain access to configuration, tenant connection strings, and audit helpers.
- Decorate endpoints with `[Authorize(AuthenticationSchemes = JwtBearerDefaults.AuthenticationScheme)]`.
- Always wrap response payloads in `DanpheHTTPResponse<T>` (`Status = "OK" | "Failed"`, `Results = data`, `ErrorMessage = message`).

### Rule 3.3: Data Access & EF DbContext Partitioning
- Place new Entity Framework models in `DanpheEMR.ServerModel/<Domain>Models/`.
- Register new `DbSet<T>` in the appropriate `DanpheEMR.DalLayer/<Domain>DbContext.cs`.
- Ensure table names strictly match SQL schema mappings (e.g. `[Table("PAT_Patient")]`).

---

## 4. 🗄️ Database & Cleanliness Rules

### Rule 4.1: Clean Schema & Transaction Safety
- All SQL scripts modifying data must be wrapped in `BEGIN TRY ... BEGIN TRANSACTION ... COMMIT ... END TRY BEGIN CATCH ... ROLLBACK ... END CATCH`.
- When deleting or reseeding tables, always check:
  ```sql
  IF OBJECT_ID('[TableName]', 'U') IS NOT NULL
  BEGIN
      DELETE FROM [TableName];
      IF OBJECTPROPERTY(OBJECT_ID('[TableName]'), 'TableHasIdentity') = 1
          DBCC CHECKIDENT ('[TableName]', RESEED, 0) WITH NO_INFOMSGS;
  END
  ```
- Use `sp_MSforeachtable "ALTER TABLE ? NOCHECK CONSTRAINT all"` before mass data operations, and `sp_MSforeachtable "ALTER TABLE ? WITH CHECK CHECK CONSTRAINT all"` after.
