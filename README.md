# G1 Health EMR

> **Smart Healthcare Management Solution**  
> Powered by [Global 1 OneTech](https://global1onetech.com/)

---

## 🔑 Access & Demo Credentials

Once the system is launched, access the portal in your browser:

- **Login URL**: `http://localhost:5000/Account/Login`
- **Username**: `admin`
- **Password**: `pass123`

---

## 🚀 How to Run and Access

### 1. Prerequisites
- **Operating System**: Windows 10 / 11 / Windows Server
- **IDE**: Visual Studio 2019 / 2022 (with *.NET Desktop and Web Development* workload)
- **Framework**: .NET Framework 4.6.1 Developer Pack
- **Database**: Microsoft SQL Server 2016+ (or SQL Server Express)
- **Frontend**: Node.js (v10.x – v12.x) & npm

---

### 2. Setup Steps

#### Step 1: Restore Databases
1. Open SQL Server Management Studio (SSMS).
2. Extract and restore `Database/2. EMR-Db/DanpheInternationalDB/Dev_DanpheEMR_INT1.zip` as database **`DEV_DanpheEMR_INT`**.
3. Execute `Database/1. Admin-Db/1. DanpheAdmin_CompleteDB.sql` to create database **`DanpheAdmin`**.
4. Verify connection strings in `Code/Websites/DanpheEMR/appsettings.json`.

#### Step 2: Build Frontend
Navigate to the Angular directory and build the client bundle:
```bash
cd Code/Websites/DanpheEMR/wwwroot/DanpheApp
npm install
npm run build
```

#### Step 3: Launch Application
1. Open `Code/Solutions/DanpheEMR.sln` in Visual Studio.
2. Set `DanpheEMR` as the Startup Project.
3. Press **`F5`** (or `Ctrl + F5`) to run via IIS Express / Kestrel.
4. Navigate to `http://localhost:5000` and sign in with the credentials above.
