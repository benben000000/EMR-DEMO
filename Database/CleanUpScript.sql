/*
================================================================================
 DanpheEMR Database Cleanup Script
 Purpose: Cleans transactional and test data while preserving master/config data
 Features:
   - Disables FK constraints & triggers safely to prevent cascade/order conflicts
   - Disables specified non-clustered/unique indexes
   - Safely deletes data and reseeds identity columns (only when applicable)
   - Restores/rebuilds indexes, re-enables triggers, and re-checks constraints
   - Error handling with automatic constraint & trigger re-enabling
================================================================================
*/

SET NOCOUNT ON;

PRINT '[START] DanpheEMR Database Cleanup Script initialized.';

-- Step 1: Disable all Foreign Key constraints and Triggers across the database
PRINT '[INFO] Disabling all foreign key constraints and triggers...';
EXEC sp_MSforeachtable "ALTER TABLE ? NOCHECK CONSTRAINT all";
EXEC sp_MSforeachtable "ALTER TABLE ? DISABLE TRIGGER all";

-- Step 2: Disable specific indexes
PRINT '[INFO] Disabling specific unique/non-clustered indexes...';
IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'UK_BillingCounterName_Type' AND object_id = OBJECT_ID('[BIL_CFG_Counter]'))
    ALTER INDEX [UK_BillingCounterName_Type] ON [BIL_CFG_Counter] DISABLE;
IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'UK_BIL_CFG_FiscalYears' AND object_id = OBJECT_ID('[BIL_CFG_FiscalYears]'))
    ALTER INDEX [UK_BIL_CFG_FiscalYears] ON [BIL_CFG_FiscalYears] DISABLE;
IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'UQ__CLN_EyeS__D7A3AA55BC800205' AND object_id = OBJECT_ID('[CLN_EyeScanImages]'))
    ALTER INDEX [UQ__CLN_EyeS__D7A3AA55BC800205] ON [CLN_EyeScanImages] DISABLE;
IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'UQ__CLN_MST___4D3AA1DF8A330DC6' AND object_id = OBJECT_ID('[CLN_MST_EYE]'))
    ALTER INDEX [UQ__CLN_MST___4D3AA1DF8A330DC6] ON [CLN_MST_EYE] DISABLE;
IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'UQ__CLN_PAT___D7A3AA5567EF1EDE' AND object_id = OBJECT_ID('[CLN_PAT_Images]'))
    ALTER INDEX [UQ__CLN_PAT___D7A3AA5567EF1EDE] ON [CLN_PAT_Images] DISABLE;
IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'UniqueOperatiONName' AND object_id = OBJECT_ID('[MR_MST_OperatiONType]'))
    ALTER INDEX [UniqueOperatiONName] ON [MR_MST_OperatiONType] DISABLE;
IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'UK_Membership_Community' AND object_id = OBJECT_ID('[PAT_CFG_MembershipType]'))
    ALTER INDEX [UK_Membership_Community] ON [PAT_CFG_MembershipType] DISABLE;
IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'UQ__PAT_Pati__D7A3AA55F0F539DA' AND object_id = OBJECT_ID('[PAT_PatientFiles]'))
    ALTER INDEX [UQ__PAT_Pati__D7A3AA55F0F539DA] ON [PAT_PatientFiles] DISABLE;
IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_TblPatInsuranceInfo_PatientId' AND object_id = OBJECT_ID('[PAT_PatientInsuranceInfo]'))
    ALTER INDEX [IX_TblPatInsuranceInfo_PatientId] ON [PAT_PatientInsuranceInfo] DISABLE;
IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'UK_PHRM_CFG_FiscalYear' AND object_id = OBJECT_ID('[PHRM_CFG_FiscalYears]'))
    ALTER INDEX [UK_PHRM_CFG_FiscalYear] ON [PHRM_CFG_FiscalYears] DISABLE;
IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'Unique_Gov_Lab_ReportItem_Name' AND object_id = OBJECT_ID('[Lab_Mst_Gov_Report_Items]'))
    ALTER INDEX [Unique_Gov_Lab_ReportItem_Name] ON [Lab_Mst_Gov_Report_Items] DISABLE;
IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'Unique_Gov_Lab_ReportItem_SerialNumber' AND object_id = OBJECT_ID('[Lab_Mst_Gov_Report_Items]'))
    ALTER INDEX [Unique_Gov_Lab_ReportItem_SerialNumber] ON [Lab_Mst_Gov_Report_Items] DISABLE;
IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_TblBilDeposit_VisitId' AND object_id = OBJECT_ID('[BIL_TXN_Deposit]'))
    ALTER INDEX [IX_TblBilDeposit_VisitId] ON [BIL_TXN_Deposit] DISABLE;
IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_TblPatientBedInfo_VisitId' AND object_id = OBJECT_ID('[ADT_TXN_PatientBedInfo]'))
    ALTER INDEX [IX_TblPatientBedInfo_VisitId] ON [ADT_TXN_PatientBedInfo] DISABLE;
IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_BIL_BillingTransaction_CreatedOn' AND object_id = OBJECT_ID('[BIL_TXN_BillingTransaction]'))
    ALTER INDEX [IX_BIL_BillingTransaction_CreatedOn] ON [BIL_TXN_BillingTransaction] DISABLE;
IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_TblBilTxn_FiscalYearId_InvoiceNo' AND object_id = OBJECT_ID('[BIL_TXN_BillingTransaction]'))
    ALTER INDEX [IX_TblBilTxn_FiscalYearId_InvoiceNo] ON [BIL_TXN_BillingTransaction] DISABLE;
IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_TblVisit_HasInsurance_VisitDate' AND object_id = OBJECT_ID('[PAT_PatientVisits]'))
    ALTER INDEX [IX_TblVisit_HasInsurance_VisitDate] ON [PAT_PatientVisits] DISABLE;
IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_TblVisit_PatientId' AND object_id = OBJECT_ID('[PAT_PatientVisits]'))
    ALTER INDEX [IX_TblVisit_PatientId] ON [PAT_PatientVisits] DISABLE;
IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_TblVisits_ClaimCode' AND object_id = OBJECT_ID('[PAT_PatientVisits]'))
    ALTER INDEX [IX_TblVisits_ClaimCode] ON [PAT_PatientVisits] DISABLE;
IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_INCTV_TXN_IncentiveFractionItem_BillingTransactionItemId' AND object_id = OBJECT_ID('[INCTV_TXN_IncentiveFractionItem]'))
    ALTER INDEX [IX_INCTV_TXN_IncentiveFractionItem_BillingTransactionItemId] ON [INCTV_TXN_IncentiveFractionItem] DISABLE;
IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_INCTV_TXN_IncentiveFractionItem_IncentiveReceiverId' AND object_id = OBJECT_ID('[INCTV_TXN_IncentiveFractionItem]'))
    ALTER INDEX [IX_INCTV_TXN_IncentiveFractionItem_IncentiveReceiverId] ON [INCTV_TXN_IncentiveFractionItem] DISABLE;
IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'UK_IncentiveFractionItems' AND object_id = OBJECT_ID('[INCTV_TXN_IncentiveFractionItem]'))
    ALTER INDEX [UK_IncentiveFractionItems] ON [INCTV_TXN_IncentiveFractionItem] DISABLE;
IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_TblAdmission_IsInsurancePatient' AND object_id = OBJECT_ID('[ADT_PatientAdmission]'))
    ALTER INDEX [IX_TblAdmission_IsInsurancePatient] ON [ADT_PatientAdmission] DISABLE;
IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_TblAdmission_VisitId_PatientId' AND object_id = OBJECT_ID('[ADT_PatientAdmission]'))
    ALTER INDEX [IX_TblAdmission_VisitId_PatientId] ON [ADT_PatientAdmission] DISABLE;

BEGIN TRY
    BEGIN TRANSACTION;

    PRINT '[INFO] Deleting data from transactional tables and resetting identity seeds...';

    -- Clean table: [__MigrationHistory]
    IF OBJECT_ID('[__MigrationHistory]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [__MigrationHistory];
        IF OBJECTPROPERTY(OBJECT_ID('[__MigrationHistory]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[__MigrationHistory]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [ACC_Bill_LedgerMapping]
    IF OBJECT_ID('[ACC_Bill_LedgerMapping]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [ACC_Bill_LedgerMapping];
        IF OBJECTPROPERTY(OBJECT_ID('[ACC_Bill_LedgerMapping]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[ACC_Bill_LedgerMapping]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [ACC_FiscalYear_Log]
    IF OBJECT_ID('[ACC_FiscalYear_Log]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [ACC_FiscalYear_Log];
        IF OBJECTPROPERTY(OBJECT_ID('[ACC_FiscalYear_Log]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[ACC_FiscalYear_Log]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [ACC_InvoiceData]
    IF OBJECT_ID('[ACC_InvoiceData]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [ACC_InvoiceData];
        IF OBJECTPROPERTY(OBJECT_ID('[ACC_InvoiceData]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[ACC_InvoiceData]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [ACC_LedgerBalanceHistory]
    IF OBJECT_ID('[ACC_LedgerBalanceHistory]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [ACC_LedgerBalanceHistory];
        IF OBJECTPROPERTY(OBJECT_ID('[ACC_LedgerBalanceHistory]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[ACC_LedgerBalanceHistory]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [ACC_Log_EditVoucher]
    IF OBJECT_ID('[ACC_Log_EditVoucher]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [ACC_Log_EditVoucher];
        IF OBJECTPROPERTY(OBJECT_ID('[ACC_Log_EditVoucher]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[ACC_Log_EditVoucher]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [ACC_Map_TxnItemCostCenterItem]
    IF OBJECT_ID('[ACC_Map_TxnItemCostCenterItem]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [ACC_Map_TxnItemCostCenterItem];
        IF OBJECTPROPERTY(OBJECT_ID('[ACC_Map_TxnItemCostCenterItem]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[ACC_Map_TxnItemCostCenterItem]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [ACC_ReverseTransaction]
    IF OBJECT_ID('[ACC_ReverseTransaction]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [ACC_ReverseTransaction];
        IF OBJECTPROPERTY(OBJECT_ID('[ACC_ReverseTransaction]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[ACC_ReverseTransaction]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [ACC_Transaction_History]
    IF OBJECT_ID('[ACC_Transaction_History]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [ACC_Transaction_History];
        IF OBJECTPROPERTY(OBJECT_ID('[ACC_Transaction_History]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[ACC_Transaction_History]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [ACC_TransactionItemDetail]
    IF OBJECT_ID('[ACC_TransactionItemDetail]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [ACC_TransactionItemDetail];
        IF OBJECTPROPERTY(OBJECT_ID('[ACC_TransactionItemDetail]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[ACC_TransactionItemDetail]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [ACC_TransactionItems]
    IF OBJECT_ID('[ACC_TransactionItems]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [ACC_TransactionItems];
        IF OBJECTPROPERTY(OBJECT_ID('[ACC_TransactionItems]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[ACC_TransactionItems]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [ACC_Transactions]
    IF OBJECT_ID('[ACC_Transactions]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [ACC_Transactions];
        IF OBJECTPROPERTY(OBJECT_ID('[ACC_Transactions]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[ACC_Transactions]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [ACC_TXN_Bank_Reconciliation]
    IF OBJECT_ID('[ACC_TXN_Bank_Reconciliation]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [ACC_TXN_Bank_Reconciliation];
        IF OBJECTPROPERTY(OBJECT_ID('[ACC_TXN_Bank_Reconciliation]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[ACC_TXN_Bank_Reconciliation]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [ACC_TXN_Link]
    IF OBJECT_ID('[ACC_TXN_Link]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [ACC_TXN_Link];
        IF OBJECTPROPERTY(OBJECT_ID('[ACC_TXN_Link]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[ACC_TXN_Link]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [ACC_TXN_Payment]
    IF OBJECT_ID('[ACC_TXN_Payment]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [ACC_TXN_Payment];
        IF OBJECTPROPERTY(OBJECT_ID('[ACC_TXN_Payment]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[ACC_TXN_Payment]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [ADT_BabyBirthDetails]
    IF OBJECT_ID('[ADT_BabyBirthDetails]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [ADT_BabyBirthDetails];
        IF OBJECTPROPERTY(OBJECT_ID('[ADT_BabyBirthDetails]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[ADT_BabyBirthDetails]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [ADT_BedReservation]
    IF OBJECT_ID('[ADT_BedReservation]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [ADT_BedReservation];
        IF OBJECTPROPERTY(OBJECT_ID('[ADT_BedReservation]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[ADT_BedReservation]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [ADT_DeathDeatils]
    IF OBJECT_ID('[ADT_DeathDeatils]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [ADT_DeathDeatils];
        IF OBJECTPROPERTY(OBJECT_ID('[ADT_DeathDeatils]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[ADT_DeathDeatils]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [ADT_DischargeCancel]
    IF OBJECT_ID('[ADT_DischargeCancel]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [ADT_DischargeCancel];
        IF OBJECTPROPERTY(OBJECT_ID('[ADT_DischargeCancel]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[ADT_DischargeCancel]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [ADT_DischargeSummary]
    IF OBJECT_ID('[ADT_DischargeSummary]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [ADT_DischargeSummary];
        IF OBJECTPROPERTY(OBJECT_ID('[ADT_DischargeSummary]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[ADT_DischargeSummary]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [ADT_DischargeSummaryMedication]
    IF OBJECT_ID('[ADT_DischargeSummaryMedication]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [ADT_DischargeSummaryMedication];
        IF OBJECTPROPERTY(OBJECT_ID('[ADT_DischargeSummaryMedication]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[ADT_DischargeSummaryMedication]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [ADT_MAP_BedFeaturesMap]
    IF OBJECT_ID('[ADT_MAP_BedFeaturesMap]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [ADT_MAP_BedFeaturesMap];
        IF OBJECTPROPERTY(OBJECT_ID('[ADT_MAP_BedFeaturesMap]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[ADT_MAP_BedFeaturesMap]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [ADT_PatientCertificate]
    IF OBJECT_ID('[ADT_PatientCertificate]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [ADT_PatientCertificate];
        IF OBJECTPROPERTY(OBJECT_ID('[ADT_PatientCertificate]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[ADT_PatientCertificate]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [BedInformationModels]
    IF OBJECT_ID('[BedInformationModels]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [BedInformationModels];
        IF OBJECTPROPERTY(OBJECT_ID('[BedInformationModels]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[BedInformationModels]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [BIL_BillItemRequisition]
    IF OBJECT_ID('[BIL_BillItemRequisition]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [BIL_BillItemRequisition];
        IF OBJECTPROPERTY(OBJECT_ID('[BIL_BillItemRequisition]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[BIL_BillItemRequisition]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [BIL_CFG_BillItemPrice]
    IF OBJECT_ID('[BIL_CFG_BillItemPrice]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [BIL_CFG_BillItemPrice];
        IF OBJECTPROPERTY(OBJECT_ID('[BIL_CFG_BillItemPrice]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[BIL_CFG_BillItemPrice]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [BIL_CFG_BillItemPrice_History]
    IF OBJECT_ID('[BIL_CFG_BillItemPrice_History]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [BIL_CFG_BillItemPrice_History];
        IF OBJECTPROPERTY(OBJECT_ID('[BIL_CFG_BillItemPrice_History]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[BIL_CFG_BillItemPrice_History]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [BIL_CFG_Counter]
    IF OBJECT_ID('[BIL_CFG_Counter]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [BIL_CFG_Counter];
        IF OBJECTPROPERTY(OBJECT_ID('[BIL_CFG_Counter]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[BIL_CFG_Counter]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [BIL_CFG_FiscalYears]
    IF OBJECT_ID('[BIL_CFG_FiscalYears]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [BIL_CFG_FiscalYears];
        IF OBJECTPROPERTY(OBJECT_ID('[BIL_CFG_FiscalYears]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[BIL_CFG_FiscalYears]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [BIL_CFG_Packages]
    IF OBJECT_ID('[BIL_CFG_Packages]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [BIL_CFG_Packages];
        IF OBJECTPROPERTY(OBJECT_ID('[BIL_CFG_Packages]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[BIL_CFG_Packages]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [BIL_CFG_PriceCategory]
    IF OBJECT_ID('[BIL_CFG_PriceCategory]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [BIL_CFG_PriceCategory];
        IF OBJECTPROPERTY(OBJECT_ID('[BIL_CFG_PriceCategory]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[BIL_CFG_PriceCategory]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [BIL_History_BillingTransactionItems]
    IF OBJECT_ID('[BIL_History_BillingTransactionItems]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [BIL_History_BillingTransactionItems];
        IF OBJECTPROPERTY(OBJECT_ID('[BIL_History_BillingTransactionItems]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[BIL_History_BillingTransactionItems]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [BIL_Temp_ItemsMapping]
    IF OBJECT_ID('[BIL_Temp_ItemsMapping]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [BIL_Temp_ItemsMapping];
        IF OBJECTPROPERTY(OBJECT_ID('[BIL_Temp_ItemsMapping]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[BIL_Temp_ItemsMapping]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [BIL_TXN_CashHandover]
    IF OBJECT_ID('[BIL_TXN_CashHandover]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [BIL_TXN_CashHandover];
        IF OBJECTPROPERTY(OBJECT_ID('[BIL_TXN_CashHandover]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[BIL_TXN_CashHandover]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [BIL_TXN_Settlements]
    IF OBJECT_ID('[BIL_TXN_Settlements]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [BIL_TXN_Settlements];
        IF OBJECTPROPERTY(OBJECT_ID('[BIL_TXN_Settlements]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[BIL_TXN_Settlements]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [CLN_ActiveMedicals]
    IF OBJECT_ID('[CLN_ActiveMedicals]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [CLN_ActiveMedicals];
        IF OBJECTPROPERTY(OBJECT_ID('[CLN_ActiveMedicals]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[CLN_ActiveMedicals]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [CLN_Allergies]
    IF OBJECT_ID('[CLN_Allergies]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [CLN_Allergies];
        IF OBJECTPROPERTY(OBJECT_ID('[CLN_Allergies]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[CLN_Allergies]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [CLN_Diagnosis]
    IF OBJECT_ID('[CLN_Diagnosis]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [CLN_Diagnosis];
        IF OBJECTPROPERTY(OBJECT_ID('[CLN_Diagnosis]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[CLN_Diagnosis]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [CLN_EYE_Ablation_Profile]
    IF OBJECT_ID('[CLN_EYE_Ablation_Profile]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [CLN_EYE_Ablation_Profile];
        IF OBJECTPROPERTY(OBJECT_ID('[CLN_EYE_Ablation_Profile]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[CLN_EYE_Ablation_Profile]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [CLN_EYE_Laser_DataEntry]
    IF OBJECT_ID('[CLN_EYE_Laser_DataEntry]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [CLN_EYE_Laser_DataEntry];
        IF OBJECTPROPERTY(OBJECT_ID('[CLN_EYE_Laser_DataEntry]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[CLN_EYE_Laser_DataEntry]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [CLN_EYE_LasikRST]
    IF OBJECT_ID('[CLN_EYE_LasikRST]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [CLN_EYE_LasikRST];
        IF OBJECTPROPERTY(OBJECT_ID('[CLN_EYE_LasikRST]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[CLN_EYE_LasikRST]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [CLN_EYE_OperationNotes]
    IF OBJECT_ID('[CLN_EYE_OperationNotes]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [CLN_EYE_OperationNotes];
        IF OBJECTPROPERTY(OBJECT_ID('[CLN_EYE_OperationNotes]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[CLN_EYE_OperationNotes]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [CLN_EYE_ORA]
    IF OBJECT_ID('[CLN_EYE_ORA]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [CLN_EYE_ORA];
        IF OBJECTPROPERTY(OBJECT_ID('[CLN_EYE_ORA]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[CLN_EYE_ORA]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [CLN_EYE_Pachymetry]
    IF OBJECT_ID('[CLN_EYE_Pachymetry]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [CLN_EYE_Pachymetry];
        IF OBJECTPROPERTY(OBJECT_ID('[CLN_EYE_Pachymetry]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[CLN_EYE_Pachymetry]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [CLN_EYE_PreOP_Pachymetry]
    IF OBJECT_ID('[CLN_EYE_PreOP_Pachymetry]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [CLN_EYE_PreOP_Pachymetry];
        IF OBJECTPROPERTY(OBJECT_ID('[CLN_EYE_PreOP_Pachymetry]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[CLN_EYE_PreOP_Pachymetry]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [CLN_EYE_Refraction]
    IF OBJECT_ID('[CLN_EYE_Refraction]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [CLN_EYE_Refraction];
        IF OBJECTPROPERTY(OBJECT_ID('[CLN_EYE_Refraction]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[CLN_EYE_Refraction]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [CLN_EYE_Smile_Incisions]
    IF OBJECT_ID('[CLN_EYE_Smile_Incisions]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [CLN_EYE_Smile_Incisions];
        IF OBJECTPROPERTY(OBJECT_ID('[CLN_EYE_Smile_Incisions]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[CLN_EYE_Smile_Incisions]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [CLN_EYE_Smile_Setting]
    IF OBJECT_ID('[CLN_EYE_Smile_Setting]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [CLN_EYE_Smile_Setting];
        IF OBJECTPROPERTY(OBJECT_ID('[CLN_EYE_Smile_Setting]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[CLN_EYE_Smile_Setting]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [CLN_EYE_VisuMax]
    IF OBJECT_ID('[CLN_EYE_VisuMax]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [CLN_EYE_VisuMax];
        IF OBJECTPROPERTY(OBJECT_ID('[CLN_EYE_VisuMax]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[CLN_EYE_VisuMax]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [CLN_EYE_Wavefront]
    IF OBJECT_ID('[CLN_EYE_Wavefront]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [CLN_EYE_Wavefront];
        IF OBJECTPROPERTY(OBJECT_ID('[CLN_EYE_Wavefront]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[CLN_EYE_Wavefront]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [CLN_EyeScanImages]
    IF OBJECT_ID('[CLN_EyeScanImages]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [CLN_EyeScanImages];
        IF OBJECTPROPERTY(OBJECT_ID('[CLN_EyeScanImages]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[CLN_EyeScanImages]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [CLN_FamilyHistory]
    IF OBJECT_ID('[CLN_FamilyHistory]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [CLN_FamilyHistory];
        IF OBJECTPROPERTY(OBJECT_ID('[CLN_FamilyHistory]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[CLN_FamilyHistory]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [CLN_HomeMedications]
    IF OBJECT_ID('[CLN_HomeMedications]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [CLN_HomeMedications];
        IF OBJECTPROPERTY(OBJECT_ID('[CLN_HomeMedications]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[CLN_HomeMedications]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [CLN_KV_PatientClinical_Info]
    IF OBJECT_ID('[CLN_KV_PatientClinical_Info]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [CLN_KV_PatientClinical_Info];
        IF OBJECTPROPERTY(OBJECT_ID('[CLN_KV_PatientClinical_Info]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[CLN_KV_PatientClinical_Info]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [CLN_MedicationPrescription]
    IF OBJECT_ID('[CLN_MedicationPrescription]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [CLN_MedicationPrescription];
        IF OBJECTPROPERTY(OBJECT_ID('[CLN_MedicationPrescription]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[CLN_MedicationPrescription]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [CLN_MST_EYE]
    IF OBJECT_ID('[CLN_MST_EYE]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [CLN_MST_EYE];
        IF OBJECTPROPERTY(OBJECT_ID('[CLN_MST_EYE]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[CLN_MST_EYE]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [CLN_MST_PrescriptionSlip]
    IF OBJECT_ID('[CLN_MST_PrescriptionSlip]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [CLN_MST_PrescriptionSlip];
        IF OBJECTPROPERTY(OBJECT_ID('[CLN_MST_PrescriptionSlip]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[CLN_MST_PrescriptionSlip]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [CLN_Notes_Emergency]
    IF OBJECT_ID('[CLN_Notes_Emergency]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [CLN_Notes_Emergency];
        IF OBJECTPROPERTY(OBJECT_ID('[CLN_Notes_Emergency]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[CLN_Notes_Emergency]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [CLN_Notes_FreeText]
    IF OBJECT_ID('[CLN_Notes_FreeText]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [CLN_Notes_FreeText];
        IF OBJECTPROPERTY(OBJECT_ID('[CLN_Notes_FreeText]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[CLN_Notes_FreeText]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [CLN_Notes_Objective]
    IF OBJECT_ID('[CLN_Notes_Objective]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [CLN_Notes_Objective];
        IF OBJECTPROPERTY(OBJECT_ID('[CLN_Notes_Objective]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[CLN_Notes_Objective]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [CLN_Notes_PrescriptionNote]
    IF OBJECT_ID('[CLN_Notes_PrescriptionNote]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [CLN_Notes_PrescriptionNote];
        IF OBJECTPROPERTY(OBJECT_ID('[CLN_Notes_PrescriptionNote]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[CLN_Notes_PrescriptionNote]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [CLN_Notes_Procedure]
    IF OBJECT_ID('[CLN_Notes_Procedure]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [CLN_Notes_Procedure];
        IF OBJECTPROPERTY(OBJECT_ID('[CLN_Notes_Procedure]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[CLN_Notes_Procedure]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [CLN_Notes_Progress]
    IF OBJECT_ID('[CLN_Notes_Progress]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [CLN_Notes_Progress];
        IF OBJECTPROPERTY(OBJECT_ID('[CLN_Notes_Progress]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[CLN_Notes_Progress]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [CLN_Notes_Subjective]
    IF OBJECT_ID('[CLN_Notes_Subjective]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [CLN_Notes_Subjective];
        IF OBJECTPROPERTY(OBJECT_ID('[CLN_Notes_Subjective]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[CLN_Notes_Subjective]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [CLN_PastMedicals]
    IF OBJECT_ID('[CLN_PastMedicals]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [CLN_PastMedicals];
        IF OBJECTPROPERTY(OBJECT_ID('[CLN_PastMedicals]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[CLN_PastMedicals]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [CLN_PAT_Images]
    IF OBJECT_ID('[CLN_PAT_Images]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [CLN_PAT_Images];
        IF OBJECTPROPERTY(OBJECT_ID('[CLN_PAT_Images]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[CLN_PAT_Images]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [CLN_PatientNotes]
    IF OBJECT_ID('[CLN_PatientNotes]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [CLN_PatientNotes];
        IF OBJECTPROPERTY(OBJECT_ID('[CLN_PatientNotes]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[CLN_PatientNotes]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [CLN_PatientVisit_Notes]
    IF OBJECT_ID('[CLN_PatientVisit_Notes]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [CLN_PatientVisit_Notes];
        IF OBJECTPROPERTY(OBJECT_ID('[CLN_PatientVisit_Notes]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[CLN_PatientVisit_Notes]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [CLN_PatientVisitProcedure]
    IF OBJECT_ID('[CLN_PatientVisitProcedure]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [CLN_PatientVisitProcedure];
        IF OBJECTPROPERTY(OBJECT_ID('[CLN_PatientVisitProcedure]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[CLN_PatientVisitProcedure]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [CLN_PrescriptionSlip_Acceptance]
    IF OBJECT_ID('[CLN_PrescriptionSlip_Acceptance]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [CLN_PrescriptionSlip_Acceptance];
        IF OBJECTPROPERTY(OBJECT_ID('[CLN_PrescriptionSlip_Acceptance]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[CLN_PrescriptionSlip_Acceptance]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [CLN_PrescriptionSlip_AdviceDiagnosis]
    IF OBJECT_ID('[CLN_PrescriptionSlip_AdviceDiagnosis]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [CLN_PrescriptionSlip_AdviceDiagnosis];
        IF OBJECTPROPERTY(OBJECT_ID('[CLN_PrescriptionSlip_AdviceDiagnosis]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[CLN_PrescriptionSlip_AdviceDiagnosis]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [CLN_PrescriptionSlip_Dilate]
    IF OBJECT_ID('[CLN_PrescriptionSlip_Dilate]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [CLN_PrescriptionSlip_Dilate];
        IF OBJECTPROPERTY(OBJECT_ID('[CLN_PrescriptionSlip_Dilate]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[CLN_PrescriptionSlip_Dilate]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [CLN_PrescriptionSlip_FinalClass]
    IF OBJECT_ID('[CLN_PrescriptionSlip_FinalClass]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [CLN_PrescriptionSlip_FinalClass];
        IF OBJECTPROPERTY(OBJECT_ID('[CLN_PrescriptionSlip_FinalClass]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[CLN_PrescriptionSlip_FinalClass]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [CLN_PrescriptionSlip_History]
    IF OBJECT_ID('[CLN_PrescriptionSlip_History]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [CLN_PrescriptionSlip_History];
        IF OBJECTPROPERTY(OBJECT_ID('[CLN_PrescriptionSlip_History]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[CLN_PrescriptionSlip_History]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [CLN_PrescriptionSlip_IOP]
    IF OBJECT_ID('[CLN_PrescriptionSlip_IOP]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [CLN_PrescriptionSlip_IOP];
        IF OBJECTPROPERTY(OBJECT_ID('[CLN_PrescriptionSlip_IOP]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[CLN_PrescriptionSlip_IOP]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [CLN_PrescriptionSlip_Plup]
    IF OBJECT_ID('[CLN_PrescriptionSlip_Plup]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [CLN_PrescriptionSlip_Plup];
        IF OBJECTPROPERTY(OBJECT_ID('[CLN_PrescriptionSlip_Plup]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[CLN_PrescriptionSlip_Plup]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [CLN_PrescriptionSlip_Retinoscopy]
    IF OBJECT_ID('[CLN_PrescriptionSlip_Retinoscopy]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [CLN_PrescriptionSlip_Retinoscopy];
        IF OBJECTPROPERTY(OBJECT_ID('[CLN_PrescriptionSlip_Retinoscopy]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[CLN_PrescriptionSlip_Retinoscopy]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [CLN_PrescriptionSlip_TBUT]
    IF OBJECT_ID('[CLN_PrescriptionSlip_TBUT]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [CLN_PrescriptionSlip_TBUT];
        IF OBJECTPROPERTY(OBJECT_ID('[CLN_PrescriptionSlip_TBUT]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[CLN_PrescriptionSlip_TBUT]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [CLN_PrescriptionSlip_VaUnaided]
    IF OBJECT_ID('[CLN_PrescriptionSlip_VaUnaided]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [CLN_PrescriptionSlip_VaUnaided];
        IF OBJECTPROPERTY(OBJECT_ID('[CLN_PrescriptionSlip_VaUnaided]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[CLN_PrescriptionSlip_VaUnaided]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [CLN_ReferralSource]
    IF OBJECT_ID('[CLN_ReferralSource]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [CLN_ReferralSource];
        IF OBJECTPROPERTY(OBJECT_ID('[CLN_ReferralSource]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[CLN_ReferralSource]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [CLN_SocialHistory]
    IF OBJECT_ID('[CLN_SocialHistory]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [CLN_SocialHistory];
        IF OBJECTPROPERTY(OBJECT_ID('[CLN_SocialHistory]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[CLN_SocialHistory]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [CORE_Notification]
    IF OBJECT_ID('[CORE_Notification]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [CORE_Notification];
        IF OBJECTPROPERTY(OBJECT_ID('[CORE_Notification]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[CORE_Notification]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [CSSD_TXN_ItemTransaction]
    IF OBJECT_ID('[CSSD_TXN_ItemTransaction]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [CSSD_TXN_ItemTransaction];
        IF OBJECTPROPERTY(OBJECT_ID('[CSSD_TXN_ItemTransaction]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[CSSD_TXN_ItemTransaction]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [CLN_SurgicalHistory]
    IF OBJECT_ID('[CLN_SurgicalHistory]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [CLN_SurgicalHistory];
        IF OBJECTPROPERTY(OBJECT_ID('[CLN_SurgicalHistory]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[CLN_SurgicalHistory]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [DanpheAudit]
    IF OBJECT_ID('[DanpheAudit]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [DanpheAudit];
        IF OBJECTPROPERTY(OBJECT_ID('[DanpheAudit]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[DanpheAudit]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [DanpheLogInInformation]
    IF OBJECT_ID('[DanpheLogInInformation]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [DanpheLogInInformation];
        IF OBJECTPROPERTY(OBJECT_ID('[DanpheLogInInformation]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[DanpheLogInInformation]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [DOC_TXN_VisitSummary]
    IF OBJECT_ID('[DOC_TXN_VisitSummary]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [DOC_TXN_VisitSummary];
        IF OBJECTPROPERTY(OBJECT_ID('[DOC_TXN_VisitSummary]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[DOC_TXN_VisitSummary]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [EMP_EmployeePreferences]
    IF OBJECT_ID('[EMP_EmployeePreferences]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [EMP_EmployeePreferences];
        IF OBJECTPROPERTY(OBJECT_ID('[EMP_EmployeePreferences]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[EMP_EmployeePreferences]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [ER_DischargeSummary]
    IF OBJECT_ID('[ER_DischargeSummary]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [ER_DischargeSummary];
        IF OBJECTPROPERTY(OBJECT_ID('[ER_DischargeSummary]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[ER_DischargeSummary]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [ER_FileUploads]
    IF OBJECT_ID('[ER_FileUploads]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [ER_FileUploads];
        IF OBJECTPROPERTY(OBJECT_ID('[ER_FileUploads]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[ER_FileUploads]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [ER_ModeOfArrival]
    IF OBJECT_ID('[ER_ModeOfArrival]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [ER_ModeOfArrival];
        IF OBJECTPROPERTY(OBJECT_ID('[ER_ModeOfArrival]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[ER_ModeOfArrival]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [ER_Patient]
    IF OBJECT_ID('[ER_Patient]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [ER_Patient];
        IF OBJECTPROPERTY(OBJECT_ID('[ER_Patient]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[ER_Patient]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [ER_Patient_Cases]
    IF OBJECT_ID('[ER_Patient_Cases]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [ER_Patient_Cases];
        IF OBJECTPROPERTY(OBJECT_ID('[ER_Patient_Cases]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[ER_Patient_Cases]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [FRC_FractionCalculation]
    IF OBJECT_ID('[FRC_FractionCalculation]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [FRC_FractionCalculation];
        IF OBJECTPROPERTY(OBJECT_ID('[FRC_FractionCalculation]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[FRC_FractionCalculation]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [INCTV_TXN_PaymentInfo]
    IF OBJECT_ID('[INCTV_TXN_PaymentInfo]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [INCTV_TXN_PaymentInfo];
        IF OBJECTPROPERTY(OBJECT_ID('[INCTV_TXN_PaymentInfo]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[INCTV_TXN_PaymentInfo]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [INS_InsuranceBalanceAmount_History]
    IF OBJECT_ID('[INS_InsuranceBalanceAmount_History]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [INS_InsuranceBalanceAmount_History];
        IF OBJECTPROPERTY(OBJECT_ID('[INS_InsuranceBalanceAmount_History]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[INS_InsuranceBalanceAmount_History]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [INS_TXN_PatientInsurancePackages]
    IF OBJECT_ID('[INS_TXN_PatientInsurancePackages]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [INS_TXN_PatientInsurancePackages];
        IF OBJECTPROPERTY(OBJECT_ID('[INS_TXN_PatientInsurancePackages]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[INS_TXN_PatientInsurancePackages]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [INV_AssetConditionCheckList]
    IF OBJECT_ID('[INV_AssetConditionCheckList]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [INV_AssetConditionCheckList];
        IF OBJECTPROPERTY(OBJECT_ID('[INV_AssetConditionCheckList]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[INV_AssetConditionCheckList]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [INV_AssetFaultHistory]
    IF OBJECT_ID('[INV_AssetFaultHistory]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [INV_AssetFaultHistory];
        IF OBJECTPROPERTY(OBJECT_ID('[INV_AssetFaultHistory]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[INV_AssetFaultHistory]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [INV_AssetInsurance]
    IF OBJECT_ID('[INV_AssetInsurance]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [INV_AssetInsurance];
        IF OBJECTPROPERTY(OBJECT_ID('[INV_AssetInsurance]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[INV_AssetInsurance]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [INV_AssetLocationHistory]
    IF OBJECT_ID('[INV_AssetLocationHistory]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [INV_AssetLocationHistory];
        IF OBJECTPROPERTY(OBJECT_ID('[INV_AssetLocationHistory]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[INV_AssetLocationHistory]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [INV_AssetServiceHistory]
    IF OBJECT_ID('[INV_AssetServiceHistory]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [INV_AssetServiceHistory];
        IF OBJECTPROPERTY(OBJECT_ID('[INV_AssetServiceHistory]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[INV_AssetServiceHistory]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [INV_MST_Donation]
    IF OBJECT_ID('[INV_MST_Donation]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [INV_MST_Donation];
        IF OBJECTPROPERTY(OBJECT_ID('[INV_MST_Donation]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[INV_MST_Donation]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [INV_MST_Stock]
    IF OBJECT_ID('[INV_MST_Stock]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [INV_MST_Stock];
        IF OBJECTPROPERTY(OBJECT_ID('[INV_MST_Stock]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[INV_MST_Stock]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [INV_MST_Vendor]
    IF OBJECT_ID('[INV_MST_Vendor]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [INV_MST_Vendor];
        IF OBJECTPROPERTY(OBJECT_ID('[INV_MST_Vendor]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[INV_MST_Vendor]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [INV_Quotation]
    IF OBJECT_ID('[INV_Quotation]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [INV_Quotation];
        IF OBJECTPROPERTY(OBJECT_ID('[INV_Quotation]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[INV_Quotation]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [INV_QuotationItems]
    IF OBJECT_ID('[INV_QuotationItems]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [INV_QuotationItems];
        IF OBJECTPROPERTY(OBJECT_ID('[INV_QuotationItems]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[INV_QuotationItems]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [INV_QuotationUploadedFiles]
    IF OBJECT_ID('[INV_QuotationUploadedFiles]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [INV_QuotationUploadedFiles];
        IF OBJECTPROPERTY(OBJECT_ID('[INV_QuotationUploadedFiles]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[INV_QuotationUploadedFiles]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [INV_RequestForQuotation]
    IF OBJECT_ID('[INV_RequestForQuotation]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [INV_RequestForQuotation];
        IF OBJECTPROPERTY(OBJECT_ID('[INV_RequestForQuotation]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[INV_RequestForQuotation]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [INV_RequestForQuotationItems]
    IF OBJECT_ID('[INV_RequestForQuotationItems]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [INV_RequestForQuotationItems];
        IF OBJECTPROPERTY(OBJECT_ID('[INV_RequestForQuotationItems]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[INV_RequestForQuotationItems]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [INV_RequestForQuotationVendors]
    IF OBJECT_ID('[INV_RequestForQuotationVendors]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [INV_RequestForQuotationVendors];
        IF OBJECTPROPERTY(OBJECT_ID('[INV_RequestForQuotationVendors]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[INV_RequestForQuotationVendors]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [INV_TXN_AssetDepreciation]
    IF OBJECT_ID('[INV_TXN_AssetDepreciation]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [INV_TXN_AssetDepreciation];
        IF OBJECTPROPERTY(OBJECT_ID('[INV_TXN_AssetDepreciation]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[INV_TXN_AssetDepreciation]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [INV_TXN_FixedAssetDispatch]
    IF OBJECT_ID('[INV_TXN_FixedAssetDispatch]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [INV_TXN_FixedAssetDispatch];
        IF OBJECTPROPERTY(OBJECT_ID('[INV_TXN_FixedAssetDispatch]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[INV_TXN_FixedAssetDispatch]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [INV_TXN_FixedAssetDispatchItems]
    IF OBJECT_ID('[INV_TXN_FixedAssetDispatchItems]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [INV_TXN_FixedAssetDispatchItems];
        IF OBJECTPROPERTY(OBJECT_ID('[INV_TXN_FixedAssetDispatchItems]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[INV_TXN_FixedAssetDispatchItems]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [INV_TXN_FixedAssetRequisition]
    IF OBJECT_ID('[INV_TXN_FixedAssetRequisition]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [INV_TXN_FixedAssetRequisition];
        IF OBJECTPROPERTY(OBJECT_ID('[INV_TXN_FixedAssetRequisition]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[INV_TXN_FixedAssetRequisition]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [INV_TXN_FixedAssetRequisitionItems]
    IF OBJECT_ID('[INV_TXN_FixedAssetRequisitionItems]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [INV_TXN_FixedAssetRequisitionItems];
        IF OBJECTPROPERTY(OBJECT_ID('[INV_TXN_FixedAssetRequisitionItems]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[INV_TXN_FixedAssetRequisitionItems]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [INV_TXN_FixedAssetReturn]
    IF OBJECT_ID('[INV_TXN_FixedAssetReturn]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [INV_TXN_FixedAssetReturn];
        IF OBJECTPROPERTY(OBJECT_ID('[INV_TXN_FixedAssetReturn]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[INV_TXN_FixedAssetReturn]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [INV_TXN_FixedAssetReturnItems]
    IF OBJECT_ID('[INV_TXN_FixedAssetReturnItems]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [INV_TXN_FixedAssetReturnItems];
        IF OBJECTPROPERTY(OBJECT_ID('[INV_TXN_FixedAssetReturnItems]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[INV_TXN_FixedAssetReturnItems]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [INV_TXN_FixedAssetStock]
    IF OBJECT_ID('[INV_TXN_FixedAssetStock]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [INV_TXN_FixedAssetStock];
        IF OBJECTPROPERTY(OBJECT_ID('[INV_TXN_FixedAssetStock]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[INV_TXN_FixedAssetStock]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [INV_TXN_GoodsReceipt]
    IF OBJECT_ID('[INV_TXN_GoodsReceipt]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [INV_TXN_GoodsReceipt];
        IF OBJECTPROPERTY(OBJECT_ID('[INV_TXN_GoodsReceipt]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[INV_TXN_GoodsReceipt]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [INV_TXN_PurchaseOrder]
    IF OBJECT_ID('[INV_TXN_PurchaseOrder]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [INV_TXN_PurchaseOrder];
        IF OBJECTPROPERTY(OBJECT_ID('[INV_TXN_PurchaseOrder]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[INV_TXN_PurchaseOrder]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [INV_TXN_PurchaseOrderItems]
    IF OBJECT_ID('[INV_TXN_PurchaseOrderItems]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [INV_TXN_PurchaseOrderItems];
        IF OBJECTPROPERTY(OBJECT_ID('[INV_TXN_PurchaseOrderItems]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[INV_TXN_PurchaseOrderItems]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [INV_TXN_PurchaseRequest]
    IF OBJECT_ID('[INV_TXN_PurchaseRequest]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [INV_TXN_PurchaseRequest];
        IF OBJECTPROPERTY(OBJECT_ID('[INV_TXN_PurchaseRequest]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[INV_TXN_PurchaseRequest]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [INV_TXN_PurchaseRequestItems]
    IF OBJECT_ID('[INV_TXN_PurchaseRequestItems]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [INV_TXN_PurchaseRequestItems];
        IF OBJECTPROPERTY(OBJECT_ID('[INV_TXN_PurchaseRequestItems]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[INV_TXN_PurchaseRequestItems]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [INV_TXN_RequisitionForPO]
    IF OBJECT_ID('[INV_TXN_RequisitionForPO]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [INV_TXN_RequisitionForPO];
        IF OBJECTPROPERTY(OBJECT_ID('[INV_TXN_RequisitionForPO]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[INV_TXN_RequisitionForPO]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [INV_TXN_RequisitionItemsForPO]
    IF OBJECT_ID('[INV_TXN_RequisitionItemsForPO]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [INV_TXN_RequisitionItemsForPO];
        IF OBJECTPROPERTY(OBJECT_ID('[INV_TXN_RequisitionItemsForPO]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[INV_TXN_RequisitionItemsForPO]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [INV_TXN_ReturnToVendor]
    IF OBJECT_ID('[INV_TXN_ReturnToVendor]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [INV_TXN_ReturnToVendor];
        IF OBJECTPROPERTY(OBJECT_ID('[INV_TXN_ReturnToVendor]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[INV_TXN_ReturnToVendor]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [INV_TXN_ReturnToVendorItems]
    IF OBJECT_ID('[INV_TXN_ReturnToVendorItems]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [INV_TXN_ReturnToVendorItems];
        IF OBJECTPROPERTY(OBJECT_ID('[INV_TXN_ReturnToVendorItems]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[INV_TXN_ReturnToVendorItems]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [INV_TXN_StoreStock]
    IF OBJECT_ID('[INV_TXN_StoreStock]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [INV_TXN_StoreStock];
        IF OBJECTPROPERTY(OBJECT_ID('[INV_TXN_StoreStock]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[INV_TXN_StoreStock]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [INV_TXN_WriteOffItems]
    IF OBJECT_ID('[INV_TXN_WriteOffItems]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [INV_TXN_WriteOffItems];
        IF OBJECTPROPERTY(OBJECT_ID('[INV_TXN_WriteOffItems]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[INV_TXN_WriteOffItems]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [IRD_Log]
    IF OBJECT_ID('[IRD_Log]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [IRD_Log];
        IF OBJECTPROPERTY(OBJECT_ID('[IRD_Log]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[IRD_Log]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [MAT_FileUploads]
    IF OBJECT_ID('[MAT_FileUploads]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [MAT_FileUploads];
        IF OBJECTPROPERTY(OBJECT_ID('[MAT_FileUploads]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[MAT_FileUploads]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [MAT_MaternityANC]
    IF OBJECT_ID('[MAT_MaternityANC]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [MAT_MaternityANC];
        IF OBJECTPROPERTY(OBJECT_ID('[MAT_MaternityANC]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[MAT_MaternityANC]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [MAT_Patient]
    IF OBJECT_ID('[MAT_Patient]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [MAT_Patient];
        IF OBJECTPROPERTY(OBJECT_ID('[MAT_Patient]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[MAT_Patient]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [MAT_Register]
    IF OBJECT_ID('[MAT_Register]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [MAT_Register];
        IF OBJECTPROPERTY(OBJECT_ID('[MAT_Register]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[MAT_Register]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [MAT_TXN_PatientPayments]
    IF OBJECT_ID('[MAT_TXN_PatientPayments]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [MAT_TXN_PatientPayments];
        IF OBJECTPROPERTY(OBJECT_ID('[MAT_TXN_PatientPayments]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[MAT_TXN_PatientPayments]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [MR_MST_OperationType]
    IF OBJECT_ID('[MR_MST_OperationType]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [MR_MST_OperationType];
        IF OBJECTPROPERTY(OBJECT_ID('[MR_MST_OperationType]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[MR_MST_OperationType]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [MR_RecordSummary]
    IF OBJECT_ID('[MR_RecordSummary]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [MR_RecordSummary];
        IF OBJECTPROPERTY(OBJECT_ID('[MR_RecordSummary]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[MR_RecordSummary]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [MR_TXN_Inpatient_Diagnosis]
    IF OBJECT_ID('[MR_TXN_Inpatient_Diagnosis]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [MR_TXN_Inpatient_Diagnosis];
        IF OBJECTPROPERTY(OBJECT_ID('[MR_TXN_Inpatient_Diagnosis]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[MR_TXN_Inpatient_Diagnosis]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [NewItemHAMS]
    IF OBJECT_ID('[NewItemHAMS]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [NewItemHAMS];
        IF OBJECTPROPERTY(OBJECT_ID('[NewItemHAMS]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[NewItemHAMS]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [OT_TXN_BookingDetails]
    IF OBJECT_ID('[OT_TXN_BookingDetails]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [OT_TXN_BookingDetails];
        IF OBJECTPROPERTY(OBJECT_ID('[OT_TXN_BookingDetails]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[OT_TXN_BookingDetails]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [OT_TXN_CheckListInfo]
    IF OBJECT_ID('[OT_TXN_CheckListInfo]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [OT_TXN_CheckListInfo];
        IF OBJECTPROPERTY(OBJECT_ID('[OT_TXN_CheckListInfo]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[OT_TXN_CheckListInfo]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [OT_TXN_OtTeamsInfo]
    IF OBJECT_ID('[OT_TXN_OtTeamsInfo]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [OT_TXN_OtTeamsInfo];
        IF OBJECTPROPERTY(OBJECT_ID('[OT_TXN_OtTeamsInfo]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[OT_TXN_OtTeamsInfo]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [OT_TXN_Summary]
    IF OBJECT_ID('[OT_TXN_Summary]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [OT_TXN_Summary];
        IF OBJECTPROPERTY(OBJECT_ID('[OT_TXN_Summary]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[OT_TXN_Summary]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [PAT_Appointment]
    IF OBJECT_ID('[PAT_Appointment]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [PAT_Appointment];
        IF OBJECTPROPERTY(OBJECT_ID('[PAT_Appointment]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[PAT_Appointment]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [PAT_CFG_MembershipType]
    IF OBJECT_ID('[PAT_CFG_MembershipType]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [PAT_CFG_MembershipType];
        IF OBJECTPROPERTY(OBJECT_ID('[PAT_CFG_MembershipType]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[PAT_CFG_MembershipType]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [PAT_HealthCardInfo]
    IF OBJECT_ID('[PAT_HealthCardInfo]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [PAT_HealthCardInfo];
        IF OBJECTPROPERTY(OBJECT_ID('[PAT_HealthCardInfo]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[PAT_HealthCardInfo]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [PAT_PatientAddress]
    IF OBJECT_ID('[PAT_PatientAddress]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [PAT_PatientAddress];
        IF OBJECTPROPERTY(OBJECT_ID('[PAT_PatientAddress]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[PAT_PatientAddress]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [PAT_PatientFiles]
    IF OBJECT_ID('[PAT_PatientFiles]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [PAT_PatientFiles];
        IF OBJECTPROPERTY(OBJECT_ID('[PAT_PatientFiles]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[PAT_PatientFiles]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [PAT_PatientInsuranceInfo]
    IF OBJECT_ID('[PAT_PatientInsuranceInfo]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [PAT_PatientInsuranceInfo];
        IF OBJECTPROPERTY(OBJECT_ID('[PAT_PatientInsuranceInfo]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[PAT_PatientInsuranceInfo]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [PAT_PatientKinOrEmergencyContacts]
    IF OBJECT_ID('[PAT_PatientKinOrEmergencyContacts]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [PAT_PatientKinOrEmergencyContacts];
        IF OBJECTPROPERTY(OBJECT_ID('[PAT_PatientKinOrEmergencyContacts]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[PAT_PatientKinOrEmergencyContacts]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [PAT_SSU_Information]
    IF OBJECT_ID('[PAT_SSU_Information]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [PAT_SSU_Information];
        IF OBJECTPROPERTY(OBJECT_ID('[PAT_SSU_Information]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[PAT_SSU_Information]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [PHRM_BIL_Transaction]
    IF OBJECT_ID('[PHRM_BIL_Transaction]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [PHRM_BIL_Transaction];
        IF OBJECTPROPERTY(OBJECT_ID('[PHRM_BIL_Transaction]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[PHRM_BIL_Transaction]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [PHRM_BIL_TransactionItem]
    IF OBJECT_ID('[PHRM_BIL_TransactionItem]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [PHRM_BIL_TransactionItem];
        IF OBJECTPROPERTY(OBJECT_ID('[PHRM_BIL_TransactionItem]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[PHRM_BIL_TransactionItem]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [PHRM_CFG_FiscalYears]
    IF OBJECT_ID('[PHRM_CFG_FiscalYears]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [PHRM_CFG_FiscalYears];
        IF OBJECTPROPERTY(OBJECT_ID('[PHRM_CFG_FiscalYears]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[PHRM_CFG_FiscalYears]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [PHRM_Deposit]
    IF OBJECT_ID('[PHRM_Deposit]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [PHRM_Deposit];
        IF OBJECTPROPERTY(OBJECT_ID('[PHRM_Deposit]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[PHRM_Deposit]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [PHRM_ExpiryDate_BatchNo_History]
    IF OBJECT_ID('[PHRM_ExpiryDate_BatchNo_History]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [PHRM_ExpiryDate_BatchNo_History];
        IF OBJECTPROPERTY(OBJECT_ID('[PHRM_ExpiryDate_BatchNo_History]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[PHRM_ExpiryDate_BatchNo_History]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [PHRM_FiscalYearStock]
    IF OBJECT_ID('[PHRM_FiscalYearStock]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [PHRM_FiscalYearStock];
        IF OBJECTPROPERTY(OBJECT_ID('[PHRM_FiscalYearStock]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[PHRM_FiscalYearStock]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [PHRM_History_Item]
    IF OBJECT_ID('[PHRM_History_Item]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [PHRM_History_Item];
        IF OBJECTPROPERTY(OBJECT_ID('[PHRM_History_Item]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[PHRM_History_Item]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [PHRM_History_StockBatchExpiry]
    IF OBJECT_ID('[PHRM_History_StockBatchExpiry]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [PHRM_History_StockBatchExpiry];
        IF OBJECTPROPERTY(OBJECT_ID('[PHRM_History_StockBatchExpiry]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[PHRM_History_StockBatchExpiry]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [PHRM_History_StockMRP]
    IF OBJECT_ID('[PHRM_History_StockMRP]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [PHRM_History_StockMRP];
        IF OBJECTPROPERTY(OBJECT_ID('[PHRM_History_StockMRP]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[PHRM_History_StockMRP]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [PHRM_NarcoticSaleRecord]
    IF OBJECT_ID('[PHRM_NarcoticSaleRecord]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [PHRM_NarcoticSaleRecord];
        IF OBJECTPROPERTY(OBJECT_ID('[PHRM_NarcoticSaleRecord]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[PHRM_NarcoticSaleRecord]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [PHRM_Prescription]
    IF OBJECT_ID('[PHRM_Prescription]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [PHRM_Prescription];
        IF OBJECTPROPERTY(OBJECT_ID('[PHRM_Prescription]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[PHRM_Prescription]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [PHRM_PrescriptionItems]
    IF OBJECT_ID('[PHRM_PrescriptionItems]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [PHRM_PrescriptionItems];
        IF OBJECTPROPERTY(OBJECT_ID('[PHRM_PrescriptionItems]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[PHRM_PrescriptionItems]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [PHRM_Requisition]
    IF OBJECT_ID('[PHRM_Requisition]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [PHRM_Requisition];
        IF OBJECTPROPERTY(OBJECT_ID('[PHRM_Requisition]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[PHRM_Requisition]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [PHRM_RequisitionItems]
    IF OBJECT_ID('[PHRM_RequisitionItems]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [PHRM_RequisitionItems];
        IF OBJECTPROPERTY(OBJECT_ID('[PHRM_RequisitionItems]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[PHRM_RequisitionItems]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [PHRM_ReturnToSupplier]
    IF OBJECT_ID('[PHRM_ReturnToSupplier]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [PHRM_ReturnToSupplier];
        IF OBJECTPROPERTY(OBJECT_ID('[PHRM_ReturnToSupplier]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[PHRM_ReturnToSupplier]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [PHRM_ReturnToSupplierItems]
    IF OBJECT_ID('[PHRM_ReturnToSupplierItems]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [PHRM_ReturnToSupplierItems];
        IF OBJECTPROPERTY(OBJECT_ID('[PHRM_ReturnToSupplierItems]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[PHRM_ReturnToSupplierItems]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [PHRM_SaleItems]
    IF OBJECT_ID('[PHRM_SaleItems]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [PHRM_SaleItems];
        IF OBJECTPROPERTY(OBJECT_ID('[PHRM_SaleItems]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[PHRM_SaleItems]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [PHRM_SaleItemsReturn]
    IF OBJECT_ID('[PHRM_SaleItemsReturn]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [PHRM_SaleItemsReturn];
        IF OBJECTPROPERTY(OBJECT_ID('[PHRM_SaleItemsReturn]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[PHRM_SaleItemsReturn]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [PHRM_Stock]
    IF OBJECT_ID('[PHRM_Stock]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [PHRM_Stock];
        IF OBJECTPROPERTY(OBJECT_ID('[PHRM_Stock]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[PHRM_Stock]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [PHRM_StockManage]
    IF OBJECT_ID('[PHRM_StockManage]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [PHRM_StockManage];
        IF OBJECTPROPERTY(OBJECT_ID('[PHRM_StockManage]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[PHRM_StockManage]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [PHRM_StockTxnItems]
    IF OBJECT_ID('[PHRM_StockTxnItems]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [PHRM_StockTxnItems];
        IF OBJECTPROPERTY(OBJECT_ID('[PHRM_StockTxnItems]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[PHRM_StockTxnItems]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [PHRM_StockTxnItems_MRPHistory]
    IF OBJECT_ID('[PHRM_StockTxnItems_MRPHistory]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [PHRM_StockTxnItems_MRPHistory];
        IF OBJECTPROPERTY(OBJECT_ID('[PHRM_StockTxnItems_MRPHistory]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[PHRM_StockTxnItems_MRPHistory]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [PHRM_StoreDispatchItems]
    IF OBJECT_ID('[PHRM_StoreDispatchItems]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [PHRM_StoreDispatchItems];
        IF OBJECTPROPERTY(OBJECT_ID('[PHRM_StoreDispatchItems]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[PHRM_StoreDispatchItems]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [PHRM_StoreRequisition]
    IF OBJECT_ID('[PHRM_StoreRequisition]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [PHRM_StoreRequisition];
        IF OBJECTPROPERTY(OBJECT_ID('[PHRM_StoreRequisition]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[PHRM_StoreRequisition]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [PHRM_StoreRequisitionItems]
    IF OBJECT_ID('[PHRM_StoreRequisitionItems]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [PHRM_StoreRequisitionItems];
        IF OBJECTPROPERTY(OBJECT_ID('[PHRM_StoreRequisitionItems]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[PHRM_StoreRequisitionItems]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [PHRM_TXN_DispensaryStock]
    IF OBJECT_ID('[PHRM_TXN_DispensaryStock]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [PHRM_TXN_DispensaryStock];
        IF OBJECTPROPERTY(OBJECT_ID('[PHRM_TXN_DispensaryStock]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[PHRM_TXN_DispensaryStock]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [PHRM_TXN_DispensaryStockTransaction]
    IF OBJECT_ID('[PHRM_TXN_DispensaryStockTransaction]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [PHRM_TXN_DispensaryStockTransaction];
        IF OBJECTPROPERTY(OBJECT_ID('[PHRM_TXN_DispensaryStockTransaction]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[PHRM_TXN_DispensaryStockTransaction]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [PHRM_TXN_Invoice]
    IF OBJECT_ID('[PHRM_TXN_Invoice]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [PHRM_TXN_Invoice];
        IF OBJECTPROPERTY(OBJECT_ID('[PHRM_TXN_Invoice]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[PHRM_TXN_Invoice]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [PHRM_TXN_InvoiceItems]
    IF OBJECT_ID('[PHRM_TXN_InvoiceItems]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [PHRM_TXN_InvoiceItems];
        IF OBJECTPROPERTY(OBJECT_ID('[PHRM_TXN_InvoiceItems]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[PHRM_TXN_InvoiceItems]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [PHRM_TXN_InvoiceReturn]
    IF OBJECT_ID('[PHRM_TXN_InvoiceReturn]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [PHRM_TXN_InvoiceReturn];
        IF OBJECTPROPERTY(OBJECT_ID('[PHRM_TXN_InvoiceReturn]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[PHRM_TXN_InvoiceReturn]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [PHRM_TXN_InvoiceReturnItems]
    IF OBJECT_ID('[PHRM_TXN_InvoiceReturnItems]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [PHRM_TXN_InvoiceReturnItems];
        IF OBJECTPROPERTY(OBJECT_ID('[PHRM_TXN_InvoiceReturnItems]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[PHRM_TXN_InvoiceReturnItems]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [PHRM_TXN_Settlement]
    IF OBJECT_ID('[PHRM_TXN_Settlement]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [PHRM_TXN_Settlement];
        IF OBJECTPROPERTY(OBJECT_ID('[PHRM_TXN_Settlement]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[PHRM_TXN_Settlement]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [PHRM_TXN_Stock]
    IF OBJECT_ID('[PHRM_TXN_Stock]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [PHRM_TXN_Stock];
        IF OBJECTPROPERTY(OBJECT_ID('[PHRM_TXN_Stock]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[PHRM_TXN_Stock]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [PHRM_TXN_StockTransaction]
    IF OBJECT_ID('[PHRM_TXN_StockTransaction]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [PHRM_TXN_StockTransaction];
        IF OBJECTPROPERTY(OBJECT_ID('[PHRM_TXN_StockTransaction]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[PHRM_TXN_StockTransaction]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [PHRM_TXN_StoreStock]
    IF OBJECT_ID('[PHRM_TXN_StoreStock]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [PHRM_TXN_StoreStock];
        IF OBJECTPROPERTY(OBJECT_ID('[PHRM_TXN_StoreStock]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[PHRM_TXN_StoreStock]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [PHRM_TXN_SupplierLedger]
    IF OBJECT_ID('[PHRM_TXN_SupplierLedger]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [PHRM_TXN_SupplierLedger];
        IF OBJECTPROPERTY(OBJECT_ID('[PHRM_TXN_SupplierLedger]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[PHRM_TXN_SupplierLedger]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [PHRM_TXN_SupplierLedgerTransaction]
    IF OBJECT_ID('[PHRM_TXN_SupplierLedgerTransaction]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [PHRM_TXN_SupplierLedgerTransaction];
        IF OBJECTPROPERTY(OBJECT_ID('[PHRM_TXN_SupplierLedgerTransaction]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[PHRM_TXN_SupplierLedgerTransaction]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [PHRM_WriteOff]
    IF OBJECT_ID('[PHRM_WriteOff]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [PHRM_WriteOff];
        IF OBJECTPROPERTY(OBJECT_ID('[PHRM_WriteOff]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[PHRM_WriteOff]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [PHRM_WriteOffItems]
    IF OBJECT_ID('[PHRM_WriteOffItems]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [PHRM_WriteOffItems];
        IF OBJECTPROPERTY(OBJECT_ID('[PHRM_WriteOffItems]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[PHRM_WriteOffItems]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [PROLL_AttendanceDailyTimeRecord]
    IF OBJECT_ID('[PROLL_AttendanceDailyTimeRecord]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [PROLL_AttendanceDailyTimeRecord];
        IF OBJECTPROPERTY(OBJECT_ID('[PROLL_AttendanceDailyTimeRecord]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[PROLL_AttendanceDailyTimeRecord]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [PROLL_DailyMuster]
    IF OBJECT_ID('[PROLL_DailyMuster]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [PROLL_DailyMuster];
        IF OBJECTPROPERTY(OBJECT_ID('[PROLL_DailyMuster]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[PROLL_DailyMuster]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [PROLL_EmpLeave]
    IF OBJECT_ID('[PROLL_EmpLeave]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [PROLL_EmpLeave];
        IF OBJECTPROPERTY(OBJECT_ID('[PROLL_EmpLeave]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[PROLL_EmpLeave]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [SCH_EmpDayWiseAvailability]
    IF OBJECT_ID('[SCH_EmpDayWiseAvailability]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [SCH_EmpDayWiseAvailability];
        IF OBJECTPROPERTY(OBJECT_ID('[SCH_EmpDayWiseAvailability]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[SCH_EmpDayWiseAvailability]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [SCH_EmployeeSchedules]
    IF OBJECT_ID('[SCH_EmployeeSchedules]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [SCH_EmployeeSchedules];
        IF OBJECTPROPERTY(OBJECT_ID('[SCH_EmployeeSchedules]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[SCH_EmployeeSchedules]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [SCH_MAP_EmployeeShift]
    IF OBJECT_ID('[SCH_MAP_EmployeeShift]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [SCH_MAP_EmployeeShift];
        IF OBJECTPROPERTY(OBJECT_ID('[SCH_MAP_EmployeeShift]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[SCH_MAP_EmployeeShift]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [TBL_BillItem_Temp]
    IF OBJECT_ID('[TBL_BillItem_Temp]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [TBL_BillItem_Temp];
        IF OBJECTPROPERTY(OBJECT_ID('[TBL_BillItem_Temp]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[TBL_BillItem_Temp]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [Temp_LabNewPrice]
    IF OBJECT_ID('[Temp_LabNewPrice]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [Temp_LabNewPrice];
        IF OBJECTPROPERTY(OBJECT_ID('[Temp_LabNewPrice]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[Temp_LabNewPrice]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [Temp10]
    IF OBJECT_ID('[Temp10]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [Temp10];
        IF OBJECTPROPERTY(OBJECT_ID('[Temp10]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[Temp10]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [tempRange]
    IF OBJECT_ID('[tempRange]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [tempRange];
        IF OBJECTPROPERTY(OBJECT_ID('[tempRange]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[tempRange]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [TXN_EmpDueAmount]
    IF OBJECT_ID('[TXN_EmpDueAmount]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [TXN_EmpDueAmount];
        IF OBJECTPROPERTY(OBJECT_ID('[TXN_EmpDueAmount]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[TXN_EmpDueAmount]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [TXN_Sms]
    IF OBJECT_ID('[TXN_Sms]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [TXN_Sms];
        IF OBJECTPROPERTY(OBJECT_ID('[TXN_Sms]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[TXN_Sms]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [TXN_Verification]
    IF OBJECT_ID('[TXN_Verification]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [TXN_Verification];
        IF OBJECTPROPERTY(OBJECT_ID('[TXN_Verification]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[TXN_Verification]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [WardInformationModels]
    IF OBJECT_ID('[WardInformationModels]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [WardInformationModels];
        IF OBJECTPROPERTY(OBJECT_ID('[WardInformationModels]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[WardInformationModels]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [WARD_Transaction]
    IF OBJECT_ID('[WARD_Transaction]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [WARD_Transaction];
        IF OBJECTPROPERTY(OBJECT_ID('[WARD_Transaction]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[WARD_Transaction]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [WARD_Stock]
    IF OBJECT_ID('[WARD_Stock]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [WARD_Stock];
        IF OBJECTPROPERTY(OBJECT_ID('[WARD_Stock]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[WARD_Stock]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [WARD_RequisitionItems]
    IF OBJECT_ID('[WARD_RequisitionItems]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [WARD_RequisitionItems];
        IF OBJECTPROPERTY(OBJECT_ID('[WARD_RequisitionItems]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[WARD_RequisitionItems]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [WARD_Requisition]
    IF OBJECT_ID('[WARD_Requisition]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [WARD_Requisition];
        IF OBJECTPROPERTY(OBJECT_ID('[WARD_Requisition]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[WARD_Requisition]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [WARD_INV_ConsumptionReceipt]
    IF OBJECT_ID('[WARD_INV_ConsumptionReceipt]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [WARD_INV_ConsumptionReceipt];
        IF OBJECTPROPERTY(OBJECT_ID('[WARD_INV_ConsumptionReceipt]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[WARD_INV_ConsumptionReceipt]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [WARD_InternalConsumptionItems]
    IF OBJECT_ID('[WARD_InternalConsumptionItems]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [WARD_InternalConsumptionItems];
        IF OBJECTPROPERTY(OBJECT_ID('[WARD_InternalConsumptionItems]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[WARD_InternalConsumptionItems]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [WARD_InternalConsumption]
    IF OBJECT_ID('[WARD_InternalConsumption]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [WARD_InternalConsumption];
        IF OBJECTPROPERTY(OBJECT_ID('[WARD_InternalConsumption]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[WARD_InternalConsumption]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [WARD_DispatchItems]
    IF OBJECT_ID('[WARD_DispatchItems]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [WARD_DispatchItems];
        IF OBJECTPROPERTY(OBJECT_ID('[WARD_DispatchItems]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[WARD_DispatchItems]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [WARD_Dispatch]
    IF OBJECT_ID('[WARD_Dispatch]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [WARD_Dispatch];
        IF OBJECTPROPERTY(OBJECT_ID('[WARD_Dispatch]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[WARD_Dispatch]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [WARD_Consumption]
    IF OBJECT_ID('[WARD_Consumption]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [WARD_Consumption];
        IF OBJECTPROPERTY(OBJECT_ID('[WARD_Consumption]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[WARD_Consumption]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [VACC_Vaccines]
    IF OBJECT_ID('[VACC_Vaccines]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [VACC_Vaccines];
        IF OBJECTPROPERTY(OBJECT_ID('[VACC_Vaccines]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[VACC_Vaccines]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [VACC_PatientVaccineDetail]
    IF OBJECT_ID('[VACC_PatientVaccineDetail]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [VACC_PatientVaccineDetail];
        IF OBJECTPROPERTY(OBJECT_ID('[VACC_PatientVaccineDetail]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[VACC_PatientVaccineDetail]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [PHRM_StoreStock]
    IF OBJECT_ID('[PHRM_StoreStock]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [PHRM_StoreStock];
        IF OBJECTPROPERTY(OBJECT_ID('[PHRM_StoreStock]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[PHRM_StoreStock]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [LAB_TXN_TestComponentResult]
    IF OBJECT_ID('[LAB_TXN_TestComponentResult]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [LAB_TXN_TestComponentResult];
        IF OBJECTPROPERTY(OBJECT_ID('[LAB_TXN_TestComponentResult]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[LAB_TXN_TestComponentResult]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [LAB_TXN_LabReports]
    IF OBJECT_ID('[LAB_TXN_LabReports]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [LAB_TXN_LabReports];
        IF OBJECTPROPERTY(OBJECT_ID('[LAB_TXN_LabReports]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[LAB_TXN_LabReports]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [LAB_BarCode]
    IF OBJECT_ID('[LAB_BarCode]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [LAB_BarCode];
        IF OBJECTPROPERTY(OBJECT_ID('[LAB_BarCode]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[LAB_BarCode]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [LAB_TestRequisition]
    IF OBJECT_ID('[LAB_TestRequisition]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [LAB_TestRequisition];
        IF OBJECTPROPERTY(OBJECT_ID('[LAB_TestRequisition]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[LAB_TestRequisition]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [AllAbnormalDataTable]
    IF OBJECT_ID('[AllAbnormalDataTable]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [AllAbnormalDataTable];
        IF OBJECTPROPERTY(OBJECT_ID('[AllAbnormalDataTable]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[AllAbnormalDataTable]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [Lab_Mst_Gov_Report_Items]
    IF OBJECT_ID('[Lab_Mst_Gov_Report_Items]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [Lab_Mst_Gov_Report_Items];
        IF OBJECTPROPERTY(OBJECT_ID('[Lab_Mst_Gov_Report_Items]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[Lab_Mst_Gov_Report_Items]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [LAB_LabTestsWithCorrectedCategory]
    IF OBJECT_ID('[LAB_LabTestsWithCorrectedCategory]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [LAB_LabTestsWithCorrectedCategory];
        IF OBJECTPROPERTY(OBJECT_ID('[LAB_LabTestsWithCorrectedCategory]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[LAB_LabTestsWithCorrectedCategory]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [PAT_PatientGurantorInfo]
    IF OBJECT_ID('[PAT_PatientGurantorInfo]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [PAT_PatientGurantorInfo];
        IF OBJECTPROPERTY(OBJECT_ID('[PAT_PatientGurantorInfo]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[PAT_PatientGurantorInfo]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [PAT_PatientMembership]
    IF OBJECT_ID('[PAT_PatientMembership]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [PAT_PatientMembership];
        IF OBJECTPROPERTY(OBJECT_ID('[PAT_PatientMembership]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[PAT_PatientMembership]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [BIL_TXN_InvoiceReturnItems]
    IF OBJECT_ID('[BIL_TXN_InvoiceReturnItems]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [BIL_TXN_InvoiceReturnItems];
        IF OBJECTPROPERTY(OBJECT_ID('[BIL_TXN_InvoiceReturnItems]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[BIL_TXN_InvoiceReturnItems]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [BIL_TXN_InvoiceReturn]
    IF OBJECT_ID('[BIL_TXN_InvoiceReturn]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [BIL_TXN_InvoiceReturn];
        IF OBJECTPROPERTY(OBJECT_ID('[BIL_TXN_InvoiceReturn]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[BIL_TXN_InvoiceReturn]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [BIL_TXN_Deposit]
    IF OBJECT_ID('[BIL_TXN_Deposit]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [BIL_TXN_Deposit];
        IF OBJECTPROPERTY(OBJECT_ID('[BIL_TXN_Deposit]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[BIL_TXN_Deposit]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [TXN_EmpCashTransaction]
    IF OBJECT_ID('[TXN_EmpCashTransaction]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [TXN_EmpCashTransaction];
        IF OBJECTPROPERTY(OBJECT_ID('[TXN_EmpCashTransaction]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[TXN_EmpCashTransaction]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [BIL_TXN_Denomination]
    IF OBJECT_ID('[BIL_TXN_Denomination]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [BIL_TXN_Denomination];
        IF OBJECTPROPERTY(OBJECT_ID('[BIL_TXN_Denomination]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[BIL_TXN_Denomination]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [ACC_Ledger_Mapping]
    IF OBJECT_ID('[ACC_Ledger_Mapping]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [ACC_Ledger_Mapping];
        IF OBJECTPROPERTY(OBJECT_ID('[ACC_Ledger_Mapping]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[ACC_Ledger_Mapping]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [BIL_MST_Handover]
    IF OBJECT_ID('[BIL_MST_Handover]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [BIL_MST_Handover];
        IF OBJECTPROPERTY(OBJECT_ID('[BIL_MST_Handover]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[BIL_MST_Handover]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [UpdatedBillItemPriceTable]
    IF OBJECT_ID('[UpdatedBillItemPriceTable]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [UpdatedBillItemPriceTable];
        IF OBJECTPROPERTY(OBJECT_ID('[UpdatedBillItemPriceTable]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[UpdatedBillItemPriceTable]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [BIL_TEMP_CFGBillItemPrice_7Sept]
    IF OBJECT_ID('[BIL_TEMP_CFGBillItemPrice_7Sept]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [BIL_TEMP_CFGBillItemPrice_7Sept];
        IF OBJECTPROPERTY(OBJECT_ID('[BIL_TEMP_CFGBillItemPrice_7Sept]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[BIL_TEMP_CFGBillItemPrice_7Sept]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [RAD_PatientImagingReport]
    IF OBJECT_ID('[RAD_PatientImagingReport]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [RAD_PatientImagingReport];
        IF OBJECTPROPERTY(OBJECT_ID('[RAD_PatientImagingReport]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[RAD_PatientImagingReport]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [RAD_PatientImagingRequisition]
    IF OBJECT_ID('[RAD_PatientImagingRequisition]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [RAD_PatientImagingRequisition];
        IF OBJECTPROPERTY(OBJECT_ID('[RAD_PatientImagingRequisition]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[RAD_PatientImagingRequisition]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [ADT_TXN_PatientBedInfo]
    IF OBJECT_ID('[ADT_TXN_PatientBedInfo]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [ADT_TXN_PatientBedInfo];
        IF OBJECTPROPERTY(OBJECT_ID('[ADT_TXN_PatientBedInfo]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[ADT_TXN_PatientBedInfo]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [ADT_PatientAdmission]
    IF OBJECT_ID('[ADT_PatientAdmission]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [ADT_PatientAdmission];
        IF OBJECTPROPERTY(OBJECT_ID('[ADT_PatientAdmission]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[ADT_PatientAdmission]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [CLN_InputOutput]
    IF OBJECT_ID('[CLN_InputOutput]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [CLN_InputOutput];
        IF OBJECTPROPERTY(OBJECT_ID('[CLN_InputOutput]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[CLN_InputOutput]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [CLN_PatientVitals]
    IF OBJECT_ID('[CLN_PatientVitals]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [CLN_PatientVitals];
        IF OBJECTPROPERTY(OBJECT_ID('[CLN_PatientVitals]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[CLN_PatientVitals]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [CLN_Notes]
    IF OBJECT_ID('[CLN_Notes]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [CLN_Notes];
        IF OBJECTPROPERTY(OBJECT_ID('[CLN_Notes]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[CLN_Notes]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [INCTV_TXN_IncentiveFractionItem]
    IF OBJECT_ID('[INCTV_TXN_IncentiveFractionItem]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [INCTV_TXN_IncentiveFractionItem];
        IF OBJECTPROPERTY(OBJECT_ID('[INCTV_TXN_IncentiveFractionItem]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[INCTV_TXN_IncentiveFractionItem]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [TXN_PrintInformation]
    IF OBJECT_ID('[TXN_PrintInformation]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [TXN_PrintInformation];
        IF OBJECTPROPERTY(OBJECT_ID('[TXN_PrintInformation]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[TXN_PrintInformation]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [BIL_SYNC_BillingAccounting]
    IF OBJECT_ID('[BIL_SYNC_BillingAccounting]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [BIL_SYNC_BillingAccounting];
        IF OBJECTPROPERTY(OBJECT_ID('[BIL_SYNC_BillingAccounting]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[BIL_SYNC_BillingAccounting]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [PHRM_PurchaseOrder]
    IF OBJECT_ID('[PHRM_PurchaseOrder]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [PHRM_PurchaseOrder];
        IF OBJECTPROPERTY(OBJECT_ID('[PHRM_PurchaseOrder]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[PHRM_PurchaseOrder]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [PHRM_PurchaseOrderItems]
    IF OBJECT_ID('[PHRM_PurchaseOrderItems]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [PHRM_PurchaseOrderItems];
        IF OBJECTPROPERTY(OBJECT_ID('[PHRM_PurchaseOrderItems]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[PHRM_PurchaseOrderItems]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [PHRM_GoodsReceipt]
    IF OBJECT_ID('[PHRM_GoodsReceipt]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [PHRM_GoodsReceipt];
        IF OBJECTPROPERTY(OBJECT_ID('[PHRM_GoodsReceipt]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[PHRM_GoodsReceipt]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [PHRM_GoodsReceiptItems]
    IF OBJECT_ID('[PHRM_GoodsReceiptItems]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [PHRM_GoodsReceiptItems];
        IF OBJECTPROPERTY(OBJECT_ID('[PHRM_GoodsReceiptItems]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[PHRM_GoodsReceiptItems]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [PHRM_DispensaryStock]
    IF OBJECT_ID('[PHRM_DispensaryStock]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [PHRM_DispensaryStock];
        IF OBJECTPROPERTY(OBJECT_ID('[PHRM_DispensaryStock]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[PHRM_DispensaryStock]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [INV_FiscalYearStock]
    IF OBJECT_ID('[INV_FiscalYearStock]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [INV_FiscalYearStock];
        IF OBJECTPROPERTY(OBJECT_ID('[INV_FiscalYearStock]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[INV_FiscalYearStock]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [INV_TXN_StockTransaction]
    IF OBJECT_ID('[INV_TXN_StockTransaction]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [INV_TXN_StockTransaction];
        IF OBJECTPROPERTY(OBJECT_ID('[INV_TXN_StockTransaction]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[INV_TXN_StockTransaction]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [WARD_INV_Transaction]
    IF OBJECT_ID('[WARD_INV_Transaction]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [WARD_INV_Transaction];
        IF OBJECTPROPERTY(OBJECT_ID('[WARD_INV_Transaction]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[WARD_INV_Transaction]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [INV_TEMP_TXN_NewStockTxn]
    IF OBJECT_ID('[INV_TEMP_TXN_NewStockTxn]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [INV_TEMP_TXN_NewStockTxn];
        IF OBJECTPROPERTY(OBJECT_ID('[INV_TEMP_TXN_NewStockTxn]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[INV_TEMP_TXN_NewStockTxn]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [INV_TXN_DispatchItems]
    IF OBJECT_ID('[INV_TXN_DispatchItems]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [INV_TXN_DispatchItems];
        IF OBJECTPROPERTY(OBJECT_ID('[INV_TXN_DispatchItems]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[INV_TXN_DispatchItems]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [INV_TXN_RequisitionItems]
    IF OBJECT_ID('[INV_TXN_RequisitionItems]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [INV_TXN_RequisitionItems];
        IF OBJECTPROPERTY(OBJECT_ID('[INV_TXN_RequisitionItems]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[INV_TXN_RequisitionItems]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [INV_TXN_Requisition]
    IF OBJECT_ID('[INV_TXN_Requisition]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [INV_TXN_Requisition];
        IF OBJECTPROPERTY(OBJECT_ID('[INV_TXN_Requisition]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[INV_TXN_Requisition]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [WARD_INV_Stock]
    IF OBJECT_ID('[WARD_INV_Stock]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [WARD_INV_Stock];
        IF OBJECTPROPERTY(OBJECT_ID('[WARD_INV_Stock]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[WARD_INV_Stock]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [WARD_INV_Consumption]
    IF OBJECT_ID('[WARD_INV_Consumption]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [WARD_INV_Consumption];
        IF OBJECTPROPERTY(OBJECT_ID('[WARD_INV_Consumption]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[WARD_INV_Consumption]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [INV_TXN_GoodsReceiptItems]
    IF OBJECT_ID('[INV_TXN_GoodsReceiptItems]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [INV_TXN_GoodsReceiptItems];
        IF OBJECTPROPERTY(OBJECT_ID('[INV_TXN_GoodsReceiptItems]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[INV_TXN_GoodsReceiptItems]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [INV_TXN_Stock]
    IF OBJECT_ID('[INV_TXN_Stock]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [INV_TXN_Stock];
        IF OBJECTPROPERTY(OBJECT_ID('[INV_TXN_Stock]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[INV_TXN_Stock]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [ACC_Ledger_2076_77_2]
    IF OBJECT_ID('[ACC_Ledger_2076_77_2]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [ACC_Ledger_2076_77_2];
        IF OBJECTPROPERTY(OBJECT_ID('[ACC_Ledger_2076_77_2]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[ACC_Ledger_2076_77_2]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [ACC_LedgerCharak$]
    IF OBJECT_ID('[ACC_LedgerCharak$]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [ACC_LedgerCharak$];
        IF OBJECTPROPERTY(OBJECT_ID('[ACC_LedgerCharak$]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[ACC_LedgerCharak$]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [PAT_NeighbourhoodCardDetail]
    IF OBJECT_ID('[PAT_NeighbourhoodCardDetail]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [PAT_NeighbourhoodCardDetail];
        IF OBJECTPROPERTY(OBJECT_ID('[PAT_NeighbourhoodCardDetail]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[PAT_NeighbourhoodCardDetail]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [PAT_PatientVisits]
    IF OBJECT_ID('[PAT_PatientVisits]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [PAT_PatientVisits];
        IF OBJECTPROPERTY(OBJECT_ID('[PAT_PatientVisits]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[PAT_PatientVisits]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [PAT_Patient]
    IF OBJECT_ID('[PAT_Patient]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [PAT_Patient] WHERE [PatientId] > 0;
        IF OBJECTPROPERTY(OBJECT_ID('[PAT_Patient]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[PAT_Patient]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    -- Clean table: [BIL_TXN_BillingTransaction]
    IF OBJECT_ID('[BIL_TXN_BillingTransaction]', 'U') IS NOT NULL
    BEGIN
        DELETE FROM [BIL_TXN_BillingTransaction];
        IF OBJECTPROPERTY(OBJECT_ID('[BIL_TXN_BillingTransaction]'), 'TableHasIdentity') = 1
            DBCC CHECKIDENT ('[BIL_TXN_BillingTransaction]', RESEED, 0) WITH NO_INFOMSGS;
    END;

    COMMIT TRANSACTION;
    PRINT '[SUCCESS] Transaction committed successfully.';
END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0
        ROLLBACK TRANSACTION;

    PRINT '[ERROR] An error occurred during database cleanup:';
    PRINT 'Error Number: ' + CAST(ERROR_NUMBER() AS VARCHAR(10));
    PRINT 'Error Line:   ' + CAST(ERROR_LINE() AS VARCHAR(10));
    PRINT 'Error Msg:    ' + ERROR_MESSAGE();
END CATCH;

-- Step 3: Rebuild specific indexes
PRINT '[INFO] Rebuilding disabled indexes...';
IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'UK_BillingCounterName_Type' AND object_id = OBJECT_ID('[BIL_CFG_Counter]'))
    ALTER INDEX [UK_BillingCounterName_Type] ON [BIL_CFG_Counter] REBUILD;
IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'UK_BIL_CFG_FiscalYears' AND object_id = OBJECT_ID('[BIL_CFG_FiscalYears]'))
    ALTER INDEX [UK_BIL_CFG_FiscalYears] ON [BIL_CFG_FiscalYears] REBUILD;
IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'UQ__CLN_EyeS__D7A3AA55BC800205' AND object_id = OBJECT_ID('[CLN_EyeScanImages]'))
    ALTER INDEX [UQ__CLN_EyeS__D7A3AA55BC800205] ON [CLN_EyeScanImages] REBUILD;
IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'UQ__CLN_MST___4D3AA1DF8A330DC6' AND object_id = OBJECT_ID('[CLN_MST_EYE]'))
    ALTER INDEX [UQ__CLN_MST___4D3AA1DF8A330DC6] ON [CLN_MST_EYE] REBUILD;
IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'UQ__CLN_PAT___D7A3AA5567EF1EDE' AND object_id = OBJECT_ID('[CLN_PAT_Images]'))
    ALTER INDEX [UQ__CLN_PAT___D7A3AA5567EF1EDE] ON [CLN_PAT_Images] REBUILD;
IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'UniqueOperatiONName' AND object_id = OBJECT_ID('[MR_MST_OperatiONType]'))
    ALTER INDEX [UniqueOperatiONName] ON [MR_MST_OperatiONType] REBUILD;
IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'UK_Membership_Community' AND object_id = OBJECT_ID('[PAT_CFG_MembershipType]'))
    ALTER INDEX [UK_Membership_Community] ON [PAT_CFG_MembershipType] REBUILD;
IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'UQ__PAT_Pati__D7A3AA55F0F539DA' AND object_id = OBJECT_ID('[PAT_PatientFiles]'))
    ALTER INDEX [UQ__PAT_Pati__D7A3AA55F0F539DA] ON [PAT_PatientFiles] REBUILD;
IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_TblPatInsuranceInfo_PatientId' AND object_id = OBJECT_ID('[PAT_PatientInsuranceInfo]'))
    ALTER INDEX [IX_TblPatInsuranceInfo_PatientId] ON [PAT_PatientInsuranceInfo] REBUILD;
IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'UK_PHRM_CFG_FiscalYear' AND object_id = OBJECT_ID('[PHRM_CFG_FiscalYears]'))
    ALTER INDEX [UK_PHRM_CFG_FiscalYear] ON [PHRM_CFG_FiscalYears] REBUILD;
IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'Unique_Gov_Lab_ReportItem_Name' AND object_id = OBJECT_ID('[Lab_Mst_Gov_Report_Items]'))
    ALTER INDEX [Unique_Gov_Lab_ReportItem_Name] ON [Lab_Mst_Gov_Report_Items] REBUILD;
IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'Unique_Gov_Lab_ReportItem_SerialNumber' AND object_id = OBJECT_ID('[Lab_Mst_Gov_Report_Items]'))
    ALTER INDEX [Unique_Gov_Lab_ReportItem_SerialNumber] ON [Lab_Mst_Gov_Report_Items] REBUILD;
IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_TblBilDeposit_VisitId' AND object_id = OBJECT_ID('[BIL_TXN_Deposit]'))
    ALTER INDEX [IX_TblBilDeposit_VisitId] ON [BIL_TXN_Deposit] REBUILD;
IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_TblPatientBedInfo_VisitId' AND object_id = OBJECT_ID('[ADT_TXN_PatientBedInfo]'))
    ALTER INDEX [IX_TblPatientBedInfo_VisitId] ON [ADT_TXN_PatientBedInfo] REBUILD;
IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_BIL_BillingTransaction_CreatedOn' AND object_id = OBJECT_ID('[BIL_TXN_BillingTransaction]'))
    ALTER INDEX [IX_BIL_BillingTransaction_CreatedOn] ON [BIL_TXN_BillingTransaction] REBUILD;
IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_TblBilTxn_FiscalYearId_InvoiceNo' AND object_id = OBJECT_ID('[BIL_TXN_BillingTransaction]'))
    ALTER INDEX [IX_TblBilTxn_FiscalYearId_InvoiceNo] ON [BIL_TXN_BillingTransaction] REBUILD;
IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_TblVisit_HasInsurance_VisitDate' AND object_id = OBJECT_ID('[PAT_PatientVisits]'))
    ALTER INDEX [IX_TblVisit_HasInsurance_VisitDate] ON [PAT_PatientVisits] REBUILD;
IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_TblVisit_PatientId' AND object_id = OBJECT_ID('[PAT_PatientVisits]'))
    ALTER INDEX [IX_TblVisit_PatientId] ON [PAT_PatientVisits] REBUILD;
IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_TblVisits_ClaimCode' AND object_id = OBJECT_ID('[PAT_PatientVisits]'))
    ALTER INDEX [IX_TblVisits_ClaimCode] ON [PAT_PatientVisits] REBUILD;
IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_INCTV_TXN_IncentiveFractionItem_BillingTransactionItemId' AND object_id = OBJECT_ID('[INCTV_TXN_IncentiveFractionItem]'))
    ALTER INDEX [IX_INCTV_TXN_IncentiveFractionItem_BillingTransactionItemId] ON [INCTV_TXN_IncentiveFractionItem] REBUILD;
IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_INCTV_TXN_IncentiveFractionItem_IncentiveReceiverId' AND object_id = OBJECT_ID('[INCTV_TXN_IncentiveFractionItem]'))
    ALTER INDEX [IX_INCTV_TXN_IncentiveFractionItem_IncentiveReceiverId] ON [INCTV_TXN_IncentiveFractionItem] REBUILD;
IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'UK_IncentiveFractionItems' AND object_id = OBJECT_ID('[INCTV_TXN_IncentiveFractionItem]'))
    ALTER INDEX [UK_IncentiveFractionItems] ON [INCTV_TXN_IncentiveFractionItem] REBUILD;
IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_TblAdmission_IsInsurancePatient' AND object_id = OBJECT_ID('[ADT_PatientAdmission]'))
    ALTER INDEX [IX_TblAdmission_IsInsurancePatient] ON [ADT_PatientAdmission] REBUILD;
IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_TblAdmission_VisitId_PatientId' AND object_id = OBJECT_ID('[ADT_PatientAdmission]'))
    ALTER INDEX [IX_TblAdmission_VisitId_PatientId] ON [ADT_PatientAdmission] REBUILD;

-- Step 4: Re-enable triggers and Foreign Key constraints
PRINT '[INFO] Re-enabling all triggers and constraints...';
EXEC sp_MSforeachtable "ALTER TABLE ? ENABLE TRIGGER all";
EXEC sp_MSforeachtable "ALTER TABLE ? WITH CHECK CHECK CONSTRAINT all";

PRINT '[COMPLETE] DanpheEMR Database Cleanup finished.';
GO
