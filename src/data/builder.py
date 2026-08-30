import json
import os
import random
import numpy as np
import pandas as pd
from tqdm import tqdm

RANDOM_SEED = 42
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

SERVICERS = [
    "Rocket Mortgage, LLC",
    "Wells Fargo Bank, N.A.",
    "JPMorgan Chase Bank, N.A.",
    "Pennymac Loan Services, LLC",
    "Nationstar Mortgage LLC (Mr. Cooper)",
    "Newrez LLC",
    "Freedom Mortgage Corporation",
    "U.S. Bank National Association"
]

def categorize_credit_score(score):
    if pd.isna(score) or score == '' or score == '9999':
        return 'Unknown'
    try:
        s = float(score)
        if s <= 620: return '<=620 (Poor)'
        elif s <= 680: return '621-680 (Fair)'
        elif s <= 740: return '681-740 (Good)'
        elif s <= 800: return '741-800 (Very Good)'
        else: return '801+ (Exceptional)'
    except:
        return 'Unknown'

def categorize_ltv(ltv):
    if pd.isna(ltv) or ltv == '' or ltv == '999':
        return 'Unknown'
    try:
        v = float(ltv)
        if v <= 60: return '<=60%'
        elif v <= 75: return '61-75%'
        elif v <= 80: return '76-80%'
        elif v <= 90: return '81-90%'
        elif v <= 95: return '91-95%'
        else: return '>95%'
    except:
        return 'Unknown'

def categorize_dti(dti):
    if pd.isna(dti) or dti == '' or dti == '999':
        return 'Unknown'
    try:
        v = float(dti)
        if v <= 20: return '<=20%'
        elif v <= 30: return '21-30%'
        elif v <= 40: return '31-40%'
        elif v <= 45: return '41-45%'
        elif v <= 50: return '46-50%'
        else: return '>50%'
    except:
        return 'Unknown'

def parse_dpd(status_str):
    if pd.isna(status_str) or status_str == '' or status_str == 'XX':
        return 0
    s = str(status_str).strip()
    if s in ['00', '0']:
        return 0
    elif s in ['01', '1']:
        return 30
    elif s in ['02', '2']:
        return 60
    elif s in ['03', '3']:
        return 90
    elif s in ['RA', 'REO']: 
        return 180
    else:
        try:
            return int(s) * 30
        except:
            return 0

def map_current_status(dpd, zero_code):
    if zero_code in ['01', 1]: 
        return 'PREPAID'
    elif zero_code in ['02', '03', '09', '15', 2, 3, 9, 15]: 
        return 'DEFAULT'
    elif dpd == 0:
        return 'CURRENT'
    elif dpd == 30:
        return '30DPD'
    elif dpd == 60:
        return '60DPD'
    else:
        return '90PLUS_DPD'

def build_data_pack(
    raw_orig_path='data/raw/sample_orig_2019.txt',
    raw_perf_path='data/raw/sample_perf_2019.txt',
    output_dir='data/processed',
    max_loans=20000
):
    os.makedirs(output_dir, exist_ok=True)
    print('=' * 70)
    print('STEP 1: Parsing Origination Data...')
    print('=' * 70)

    orig_dict = {}
    with open(raw_orig_path, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split('|')
            if len(parts) < 22:
                continue
            loan_id = parts[19]
            if not loan_id:
                continue
            
            credit_score = parts[0]
            first_pay_date = parts[1]
            maturity_date = parts[3]
            occupancy = parts[7]
            cltv = parts[8]
            dti = parts[9]
            orig_upb = parts[10]
            ltv = parts[11]
            orig_rate = parts[12]
            channel = parts[13]
            state = parts[16]
            prop_type = parts[17]
            purpose = parts[20]
            orig_term = parts[21]
            num_borrowers = parts[22] if len(parts) > 22 else '1'
            
            servicer = SERVICERS[hash(loan_id) % len(SERVICERS)]

            # Inject realistic MCAR & MAR missingness patterns for Data Profiling evaluation
            f_score_band = categorize_credit_score(credit_score)
            f_dti_band = categorize_dti(dti)
            f_state = state if state else "CA"
            f_purpose = purpose if purpose else "P"

            # MAR: Missing credit score conditioned on investor/cash-out risk cohorts
            mar_p = 0.06 if (occupancy == 'I' or purpose == 'C') else 0.015
            if random.random() < mar_p:
                f_score_band = np.nan

            # MCAR: Random missingness across general demographic/loan profile fields
            if random.random() < 0.025:
                f_dti_band = np.nan
            if random.random() < 0.020:
                f_state = np.nan
            if random.random() < 0.020:
                f_purpose = np.nan

            orig_dict[loan_id] = {
                "loan_id": loan_id,
                "credit_score": float(credit_score) if credit_score and credit_score != '9999' else np.nan,
                "credit_score_band": f_score_band,
                "origination_month": first_pay_date,
                "maturity_date": maturity_date,
                "occupancy_type": occupancy if occupancy in ['P', 'S', 'I'] else 'P',
                "cltv": float(cltv) if cltv and cltv != '999' else np.nan,
                "dti": float(dti) if dti and dti != '999' else np.nan,
                "dti_band": f_dti_band,
                "original_balance": float(orig_upb) if orig_upb else 0.0,
                "ltv": float(ltv) if ltv and ltv != '999' else np.nan,
                "ltv_band": categorize_ltv(ltv),
                "original_rate": float(orig_rate) if orig_rate else 4.5,
                "channel": channel if channel else "R",
                "state": f_state,
                "property_type": prop_type if prop_type else "SF",
                "loan_purpose": f_purpose,
                "original_term_months": int(orig_term) if orig_term else 360,
                "num_borrowers": int(num_borrowers) if num_borrowers.isdigit() else 1,
                "servicer_name": servicer,
                "vintage": "2019Q1"
            }

    print(f"Loaded {len(orig_dict):,} loans from origination file.")

    all_loan_ids = list(orig_dict.keys())
    selected_loan_ids = set(all_loan_ids[:max_loans])
    print(f"Selected {len(selected_loan_ids):,} loans for performance extraction.")

    print("\n" + "=" * 70)
    print("STEP 2: Ingesting & Grouping Monthly Performance Records...")
    print("=" * 70)

    perf_records_by_loan = {lid: [] for lid in selected_loan_ids}
    with open(raw_perf_path, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split('|')
            if len(parts) < 6:
                continue
            loan_id = parts[0]
            if loan_id not in selected_loan_ids:
                continue
            
            reporting_month = parts[1]
            actual_upb = parts[2]
            delinq_status = parts[3]
            loan_age = parts[4]
            rem_term = parts[5]
            mod_flag = parts[7] if len(parts) > 7 else 'N'
            zero_code = parts[8] if len(parts) > 8 else ''
            zero_date = parts[9] if len(parts) > 9 else ''
            curr_rate = parts[10] if len(parts) > 10 and parts[10] else ''

            perf_records_by_loan[loan_id].append({
                "reporting_month": reporting_month,
                "current_balance": float(actual_upb) if actual_upb else 0.0,
                "delinq_raw": delinq_status,
                "loan_age_months": int(loan_age) if loan_age and loan_age.isdigit() else 0,
                "remaining_term_months": int(rem_term) if rem_term and rem_term.isdigit() else 360,
                "modification_flag": "Y" if mod_flag == "Y" else "N+",
                "zero_balance_code": zero_code.strip() if zero_code else '',
                "zero_balance_date": zero_date.strip() if zero_date else '',
                "interest_rate": float(curr_rate) if curr_rate else orig_dict[loan_id]["original_rate"],
            })

    print("Computing forward-looking targets and anomalies...")

    all_rows = []
    servicer_update_rows = []

    for loan_id in tqdm(selected_loan_ids, desc="Processing Loan Timelines"):
        records = perf_records_by_loan[loan_id]
        if not records:
            continue
        
        records.sort(key=lambda x: x["reporting_month"])
        orig_info = orig_dict[loan_id]
        n = len(records)

        dpd_list = [parse_dpd(r["delinq_raw"]) for r in records]
        status_list = [map_current_status(dpd_list[i], records[i]["zero_balance_code"]) for i in range(n)]


        for i in range(n):
            rec = records[i]
            rep_month = rec["reporting_month"]
            month_idx = i
            dpd = dpd_list[i]
            curr_status = status_list[i]
            
            # Target 1: Next 3 months delinquency (>= 30 DPD) with Right-Censoring
            next_3m_dpds = dpd_list[i+1 : min(i+4, n)]
            if any(d >= 30 for d in next_3m_dpds):
                next_3m_delinq = 1
            elif i + 3 < n:
                next_3m_delinq = 0
            else:
                next_3m_delinq = np.nan

            # Target 2: Next 6 months delinquency (>= 30 DPD) with Right-Censoring
            next_6m_dpds = dpd_list[i+1 : min(i+7, n)]
            if any(d >= 30 for d in next_6m_dpds):
                next_6m_delinq = 1
            elif i + 6 < n:
                next_6m_delinq = 0
            else:
                next_6m_delinq = np.nan

            # Target 3: Next 12 months default (90+ DPD or default zero code) with Right-Censoring
            next_12m_records = records[i+1 : min(i+13, n)]
            next_12m_dpds = dpd_list[i+1 : min(i+13, n)]
            next_12m_zero = [r["zero_balance_code"] for r in next_12m_records]
            
            has_default = (
                any(d >= 90 for d in next_12m_dpds) or 
                any(z in ["02", "03", "09", "15"] for z in next_12m_zero)
            )
            if has_default:
                next_12m_default = 1
            elif i + 12 < n:
                next_12m_default = 0
            else:
                next_12m_default = np.nan

            # Target 4: Next 12 months prepayment (zero balance code == 01) with Right-Censoring
            has_prepay = any(z == "01" for z in next_12m_zero)
            if has_prepay:
                next_12m_prepay = 1
            elif i + 12 < n:
                next_12m_prepay = 0
            else:
                next_12m_prepay = np.nan

            # Target 5: Next state (month i+1 status)
            if i + 1 < n:
                next_state = status_list[i+1]
            elif rec["zero_balance_code"] == "01":
                next_state = "PREPAID"
            elif dpd >= 90 or rec["zero_balance_code"] in ["02", "03", "09", "15"]:
                next_state = "DEFAULT"
            else:
                next_state = np.nan

            # Performance flags
            prepayment_flag = 1 if rec["zero_balance_code"] == "01" else 0
            default_flag = 1 if (dpd >= 90 or rec["zero_balance_code"] in ["02", "03", "09", "15"]) else 0
            
            loss_severity_band = "None"
            if default_flag:
                loss_severity_band = random.choice(["Low (10-25%)", "Medium (26-45%)", "High (46-70%)", "Severe (>70%)"])

            # Exception & Anomaly Injection for Task 1 & Task 4 evaluation
            exception_required = 0
            exception_type = "NONE"

            rand_val = random.random()
            current_bal = rec["current_balance"]
            orig_bal = orig_info["original_balance"]
            doc_status = "VERIFIED"
            rem_term_val = rec["remaining_term_months"]

            if rand_val < 0.008:
                current_bal = round(orig_bal * random.uniform(1.25, 1.75), 2)
                exception_required = 1
                exception_type = "BALANCE_INCONSISTENCY"
            elif rand_val < 0.016:
                dpd = 90
                curr_status = "CURRENT"
                exception_required = 1
                exception_type = "STATUS_CONFLICT"
            elif rand_val < 0.024:
                doc_status = random.choice(["MISSING_NOTE", "INCOMPLETE_INCOME", "UNVERIFIED_APPRAISAL"])
                exception_required = 1
                exception_type = "DOCUMENT_GAP"
            elif rand_val < 0.032:
                rem_term_val = 450
                exception_required = 1
                exception_type = "INVALID_TERM"

            row = {
                "loan_id": loan_id,
                "month_index": month_idx,
                "reporting_month": rep_month,
                "origination_month": orig_info["origination_month"],
                "loan_age_months": rec["loan_age_months"],
                "remaining_term_months": rem_term_val,
                "original_balance": orig_bal,
                "current_balance": round(current_bal, 2),
                "interest_rate": rec["interest_rate"],
                "credit_score_band": orig_info["credit_score_band"],
                "ltv_band": orig_info["ltv_band"],
                "dti_band": orig_info["dti_band"],
                "state": orig_info["state"],
                "loan_purpose": orig_info["loan_purpose"],
                "occupancy_type": orig_info["occupancy_type"],
                "property_type": orig_info["property_type"],
                "servicer_name": orig_info["servicer_name"],
                "current_status": curr_status,
                "days_past_due": dpd,
                "modification_flag": rec["modification_flag"],
                "prepayment_flag": prepayment_flag,
                "default_flag": default_flag,
                "loss_severity_band": loss_severity_band,
                "last_updated_at": f"{rep_month[:4]}-{rep_month[4:]}-28T12:00:00Z",
                "source_system": "CORE_SERVICING_SYSTEM",
                "document_status": doc_status,
                "next_3m_delinquency_flag": next_3m_delinq,
                "next_6m_delinquency_flag": next_6m_delinq,
                "next_12m_default_flag": next_12m_default,
                "next_12m_prepayment_flag": next_12m_prepay,
                "next_state": next_state,
                "exception_required": exception_required,
                "exception_type": exception_type
            }
            all_rows.append(row)

            # Secondary Servicer Feed Generation
            if random.random() < 0.35:
                servicer_bal = current_bal
                servicer_status = curr_status
                servicer_dpd = dpd
                is_stale = False
                
                conflict_rand = random.random()
                if conflict_rand < 0.05:
                    servicer_bal = round(current_bal * random.uniform(0.85, 1.15), 2)
                elif conflict_rand < 0.08:
                    servicer_dpd = max(0, dpd - 30)
                    servicer_status = map_current_status(servicer_dpd, '')
                elif conflict_rand < 0.10:
                    is_stale = True

                year = int(rep_month[:4])
                m = int(rep_month[4:])
                update_ts = f"{year}-{m:02d}-25T08:30:00Z"
                if is_stale:
                    update_ts = f"{year - 1}-12-15T08:30:00Z"

                servicer_update_rows.append({
                    "loan_id": loan_id,
                    "reporting_month": rep_month,
                    "servicer_name": orig_info["servicer_name"],
                    "servicer_reported_balance": servicer_bal,
                    "servicer_reported_status": servicer_status,
                    "servicer_days_past_due": servicer_dpd,
                    "servicer_update_timestamp": update_ts,
                    "source_system": "SERVICER_PORTAL_FEED"
                })

    df_all = pd.DataFrame(all_rows)
    print(f"\nTotal generated monthly records: {len(df_all):,}")

    print("\n" + "=" * 70)
    print("STEP 3: Splitting into Train & Test (Time-Aware)...")
    print("=" * 70)

    train_mask = df_all["reporting_month"] <= "202106"
    test_mask = df_all["reporting_month"] > "202106"

    df_train = df_all[train_mask].copy()
    df_test_full = df_all[test_mask].copy()

    target_cols = [
        "next_3m_delinquency_flag", "next_6m_delinquency_flag", 
        "next_12m_default_flag", "next_12m_prepayment_flag", 
        "next_state", "exception_required", "exception_type"
    ]
    df_test = df_test_full.drop(columns=target_cols).copy()

    print(f"Train records: {len(df_train):,} (<= 2021-06)")
    print(f"Test records:  {len(df_test):,} (> 2021-06)")

    train_path = os.path.join(output_dir, "loan_monthly_performance_train.csv")
    test_path = os.path.join(output_dir, "loan_monthly_performance_test.csv")
    test_truth_path = os.path.join(output_dir, "loan_monthly_performance_test_ground_truth.csv")

    df_train.to_csv(train_path, index=False)
    df_test.to_csv(test_path, index=False)
    df_test_full.to_csv(test_truth_path, index=False)
    print(f"Saved: {train_path}")
    print(f"Saved: {test_path}")

    print("\n" + "=" * 70)
    print("STEP 4: Generating Static Attributes File...")
    print("=" * 70)

    static_rows = []
    for lid in selected_loan_ids:
        info = orig_dict[lid]
        static_rows.append({
            "loan_id": lid,
            "original_balance": info["original_balance"],
            "origination_month": info["origination_month"],
            "original_term_months": info["original_term_months"],
            "credit_score_band": info["credit_score_band"],
            "ltv_band": info["ltv_band"],
            "dti_band": info["dti_band"],
            "state": info["state"],
            "loan_purpose": info["loan_purpose"],
            "occupancy_type": info["occupancy_type"],
            "property_type": info["property_type"],
            "servicer_name": info["servicer_name"],
            "vintage": info["vintage"]
        })
    df_static = pd.DataFrame(static_rows)
    static_path = os.path.join(output_dir, "loan_static_attributes.csv")
    df_static.to_csv(static_path, index=False)
    print(f"Saved: {static_path} ({len(df_static):,} loans)")

    print("\n" + "=" * 70)
    print("STEP 5: Generating Servicer Updates File...")
    print("=" * 70)

    df_servicer = pd.DataFrame(servicer_update_rows)
    servicer_path = os.path.join(output_dir, "servicer_updates.csv")
    df_servicer.to_csv(servicer_path, index=False)
    print(f"Saved: {servicer_path} ({len(df_servicer):,} updates)")

    print("\n" + "=" * 70)
    print("STEP 6: Generating Validation Rules JSON...")
    print("=" * 70)

    validation_rules = {
        "rules": [
            {
                "rule_id": "VR-001",
                "rule_name": "Balance Ratio Upper Bound Check",
                "description": "Current balance must not exceed 115% of original balance unless positive modification is recorded.",
                "condition": "current_balance <= original_balance * 1.15 or modification_flag == 'Y'",
                "severity": "CRITICAL",
                "exception_type": "BALANCE_INCONSISTENCY"
            },
            {
                "rule_id": "VR-002",
                "rule_name": "Status DPD Consistency",
                "description": "If days_past_due > 0, current_status must not be CURRENT.",
                "condition": "not (days_past_due > 0 and current_status == 'CURRENT')",
                "severity": "HIGH",
                "exception_type": "STATUS_CONFLICT"
            },
            {
                "rule_id": "VR-003",
                "rule_name": "Origination Date Validity",
                "description": "Reporting month must be equal to or greater than origination month.",
                "condition": "reporting_month >= origination_month",
                "severity": "CRITICAL",
                "exception_type": "INVALID_DATE"
            },
            {
                "rule_id": "VR-004",
                "rule_name": "Remaining Term Sanity Check",
                "description": "Remaining term months must be between 0 and 360.",
                "condition": "remaining_term_months >= 0 and remaining_term_months <= 360",
                "severity": "HIGH",
                "exception_type": "INVALID_TERM"
            },
            {
                "rule_id": "VR-005",
                "rule_name": "Prepayment Balance Check",
                "description": "If prepayment_flag == 1 or current_status == 'PREPAID', current_balance must be 0.00.",
                "condition": "not (current_status == 'PREPAID' and current_balance > 0)",
                "severity": "CRITICAL",
                "exception_type": "BALANCE_INCONSISTENCY"
            },
            {
                "rule_id": "VR-006",
                "rule_name": "Document Verification Status",
                "description": "Document status must be VERIFIED or PENDING; missing notes require manual audit.",
                "condition": "document_status == 'VERIFIED'",
                "severity": "MEDIUM",
                "exception_type": "DOCUMENT_GAP"
            },
            {
                "rule_id": "VR-007",
                "rule_name": "Servicer Feed Reconciliation",
                "description": "Primary balance and servicer reported balance must match within 5% tolerance.",
                "condition": "abs(current_balance - servicer_reported_balance) / (original_balance + 1e-5) <= 0.05",
                "severity": "HIGH",
                "exception_type": "SERVICER_CONFLICT"
            },
            {
                "rule_id": "VR-008",
                "rule_name": "Feed Staleness Check",
                "description": "Last updated timestamp must not lag reporting month by more than 60 days.",
                "condition": "days_between(reporting_month, last_updated_at) <= 60",
                "severity": "MEDIUM",
                "exception_type": "STALE_RECORD"
            }
        ]
    }
    rules_path = os.path.join(output_dir, "validation_rules.json")
    with open(rules_path, 'w', encoding='utf-8') as f:
        json.dump(validation_rules, f, indent=2)
    print(f"Saved: {rules_path}")

    print("\n" + "=" * 70)
    print("STEP 7: Generating Macro Scenarios CSV...")
    print("=" * 70)

    macro_scenarios = pd.DataFrame([
        {
            "scenario_name": "Base",
            "description": "Current macroeconomic conditions baseline trajectory",
            "interest_rate_shock_bps": 0,
            "unemployment_rate_shock_pct": 0.0,
            "hpa_shock_pct": 2.5,
            "default_hazard_multiplier": 1.0,
            "prepayment_hazard_multiplier": 1.0
        },
        {
            "scenario_name": "Adverse_Credit",
            "description": "Severe economic contraction, rising rates, and falling property values",
            "interest_rate_shock_bps": 150,
            "unemployment_rate_shock_pct": 3.5,
            "hpa_shock_pct": -10.0,
            "default_hazard_multiplier": 2.3,
            "prepayment_hazard_multiplier": 0.65
        },
        {
            "scenario_name": "High_Prepayment",
            "description": "Aggressive monetary easing, mortgage rate drops driving refi wave",
            "interest_rate_shock_bps": -150,
            "unemployment_rate_shock_pct": -0.5,
            "hpa_shock_pct": 6.0,
            "default_hazard_multiplier": 0.85,
            "prepayment_hazard_multiplier": 2.75
        }
    ])
    macro_path = os.path.join(output_dir, "macro_scenarios.csv")
    macro_scenarios.to_csv(macro_path, index=False)
    print(f"Saved: {macro_path}")

    print("\n" + "=" * 70)
    print("STEP 8: Generating Data Dictionary...")
    print("=" * 70)

    data_dict_content = """# Loan Performance Intelligence Engine — Data Dictionary

## 1. Overview
Plain-English field definitions for feature understanding, deterministic validation rules, and grounding the LLM Reviewer Copilot.

---

### 2. Primary Dataset Fields

| Field Name | Type | Description | Valid Values / Domain |
| :--- | :--- | :--- | :--- |
| `loan_id` | String | Unique loan sequence identifier | Freddie Mac loan ID (e.g. `F19Q10000056`) |
| `month_index` | Integer | Sequence index of the reporting cycle for this loan | `0, 1, 2, ...` |
| `reporting_month` | String | Monthly reporting period in YYYYMM format | `201902` to `202204` |
| `origination_month` | String | First scheduled payment month | `YYYYMM` (e.g. `201903`) |
| `loan_age_months` | Integer | Number of months elapsed since loan origination | `0` to `360` |
| `remaining_term_months` | Integer | Months remaining until legal loan maturity | `0` to `360` |
| `original_balance` | Float | Original unpaid principal balance (UPB) | `$10,000` to `$1,000,000` |
| `current_balance` | Float | Actual current unpaid principal balance | `$0.00` to `$1,000,000` |
| `interest_rate` | Float | Current note interest rate (percentage) | `2.0%` to `10.0%` |
| `credit_score_band` | Categorical | FICO credit score tier at origination | `<=620 (Poor)`, `621-680 (Fair)`, `681-740 (Good)`, `741-800 (Very Good)`, `801+ (Exceptional)` |
| `ltv_band` | Categorical | Loan-to-Value tier at origination | `<=60%`, `61-75%`, `76-80%`, `81-90%`, `91-95%`, `>95%` |
| `dti_band` | Categorical | Debt-to-Income tier at origination | `<=20%`, `21-30%`, `31-40%`, `41-45%`, `46-50%`, `>50%` |
| `state` | String | US State of mortgaged collateral | 2-letter state code (e.g. `CA`, `TX`, `NY`) |
| `loan_purpose` | Categorical | Loan origination purpose | `P` (Purchase), `C` (Cash-out Refi), `N` (No Cash-out Refi) |
| `occupancy_type` | Categorical | Occupancy status of property | `P` (Primary Residence), `S` (Second Home), `I` (Investment) |
| `property_type` | Categorical | Real estate property structure | `SF` (Single Family), `CO` (Condo), `PU` (PUD), `MH` (Manufactured) |
| `servicer_name` | String | Primary servicing institution | e.g. `Rocket Mortgage`, `Wells Fargo`, `Pennymac` |
| `current_status` | Categorical | Current monthly payment status | `CURRENT`, `30DPD`, `60DPD`, `90PLUS_DPD`, `DEFAULT`, `PREPAID` |
| `days_past_due` | Integer | Days delinquent on payment | `0, 30, 60, 90, 120, 180+` |
| `modification_flag` | String | Indicates loan restructuring/modification | `Y`, `N` |
| `prepayment_flag` | Integer | Binary indicator for full loan payoff | `0`, `1` |
| `default_flag` | Integer | Binary indicator for loan default/foreclosure | `0`, `1` |
| `loss_severity_band` | Categorical | Estimated loss severity tier upon default | `None`, `Low (10-25%)`, `Medium (26-45%)`, `High (46-70%)`, `Severe (>70%)` |
| `last_updated_at` | String | Timestamp of last system update | ISO 8601 UTC timestamp |
| `source_system` | String | Upstream origination/servicing feed | `CORE_SERVICING_SYSTEM` |
| `document_status` | Categorical | Loan file audit completeness | `VERIFIED`, `MISSING_NOTE`, `INCOMPLETE_INCOME`, `UNVERIFIED_APPRAISAL` |

---

### 3. Prediction Targets

| Target Field | Type | Horizon | Description |
| :--- | :--- | :--- | :--- |
| `next_3m_delinquency_flag` | Binary | 3 Months | 1 if loan becomes 30+ DPD within 3 months |
| `next_6m_delinquency_flag` | Binary | 6 Months | 1 if loan becomes 30+ DPD within 6 months |
| `next_12m_default_flag` | Binary | 12 Months | 1 if loan enters 90+ DPD or default within 12 months |
| `next_12m_prepayment_flag` | Binary | 12 Months | 1 if loan prepays in full within 12 months |
| `next_state` | Categorical | 1 Month | Status next month (`CURRENT`, `30DPD`, `60DPD`, `90PLUS_DPD`, `DEFAULT`, `PREPAID`) |
| `exception_required` | Binary | Instant | 1 if record contains data anomaly or conflict |
| `exception_type` | Categorical | Instant | `BALANCE_INCONSISTENCY`, `STATUS_CONFLICT`, `DOCUMENT_GAP`, `INVALID_TERM`, `SERVICER_CONFLICT`, `STALE_RECORD`, `NONE` |
"""
    dict_path = os.path.join(output_dir, "data_dictionary.md")
    with open(dict_path, 'w', encoding='utf-8') as f:
        f.write(data_dict_content.strip())
    print(f"Saved: {dict_path}")

    print("\n" + "=" * 70)
    print("STEP 9: Generating Submission Template...")
    print("=" * 70)

    template_rows = []
    for _, row in df_test.head(100).iterrows():
        template_rows.append({
            "loan_id": row["loan_id"],
            "month_index": row["month_index"],
            "next_3m_delinquency_prob": 0.05,
            "next_6m_delinquency_prob": 0.08,
            "next_12m_default_prob": 0.02,
            "next_12m_prepayment_prob": 0.15,
            "next_state": "CURRENT",
            "exception_required": 0,
            "exception_type": "NONE",
            "anomaly_score": 0.05,
            "top_driver_1": "dti_band",
            "top_driver_2": "credit_score_band",
            "top_driver_3": "loan_age_months",
            "action": "PASS",
            "confidence": "HIGH"
        })
    df_template = pd.DataFrame(template_rows)
    template_path = os.path.join(output_dir, "submission_template.csv")
    df_template.to_csv(template_path, index=False)
    print(f"Saved: {template_path}")

    print("\n" + "=" * 70)
    print("PHASE 0 DATA PACK GENERATION COMPLETE!")
    print(f"All 8 required files generated successfully in '{output_dir}/'")
    print("=" * 70)

if __name__ == '__main__':
    build_data_pack()
