# Data Intelligence Report

**Intain AI Track 2026 — Loan Performance Intelligence Engine**  
**Generated**: 2026-08-29 23:45:15  

---

## Executive Summary

| Metric | Value |
| :--- | ---: |
| Training Unique Loans | 20,000 |
| Training Monthly Records | 407,733 |
| Test Monthly Records | 304,374 |
| Train Reporting Period | 201901 to 202106 |
| Test Reporting Period | 202107 to 202603 |
| Servicer Update Records | 249,496 |
| Mean DQ Score | 99.56 / 100 |
| Records with DQ Score below 80 | 0.02% |

### Top Data Quality Issues

1. **Balance Ratio Upper Bound** (CRITICAL): 3,262 violations (0.8%) - Exception: `BALANCE_INCONSISTENCY`
2. **Origination Date Validity** (CRITICAL): 18,679 violations (4.58%) - Exception: `INVALID_DATE`
3. **Prepayment Balance Check** (CRITICAL): 85 violations (0.02%) - Exception: `BALANCE_INCONSISTENCY`
4. **High Missingness** in `loss_severity_band`: 98.58% null (MAR)
5. **Servicer Balance Conflicts**: 4,561 records (3.2%) exceed 5% discrepancy threshold

---

## 1. Column Distribution Profile

- **Total Columns**: 33
- **Numeric Columns**: 16
- **Categorical Columns**: 17

### 1a. Numeric Column Statistics

| Column | Null% | Min | Max | Mean | Std | Median | Skew |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `month_index` | 0.0% | 0.0 | 29.0 | 10.9606 | 7.4206 | 10.0 | 0.3399 |
| `reporting_month` | 0.0% | 201901.0 | 202106.0 | 201978.3396 | 68.2707 | 202002.0 | 0.4362 |
| `origination_month` | 0.0% | 201902.0 | 202006.0 | 201905.0297 | 2.4437 | 201905.0 | 26.7217 |
| `loan_age_months` | 0.0% | 0.0 | 29.0 | 11.0468 | 7.4234 | 10.0 | 0.3373 |
| `remaining_term_months` | 0.0% | 68.0 | 480.0 | 324.1088 | 63.4371 | 348.0 | -1.9276 |
| `original_balance` | 0.0% | 15000.0 | 1027000.0 | 229644.0195 | 123597.8423 | 204000.0 | 0.9983 |
| `current_balance` | 0.0% | 0.0 | 1482266.05 | 216263.8971 | 126889.573 | 193407.41 | 0.9327 |
| `interest_rate` | 0.0% | 2.75 | 6.75 | 4.6318 | 0.4934 | 4.625 | 0.4704 |
| `days_past_due` | 0.0% | 0.0 | 750.0 | 4.024 | 27.9246 | 0.0 | 9.8271 |
| `prepayment_flag` | 0.0% | 0.0 | 1.0 | 0.0289 | 0.1676 | 0.0 | 5.6205 |
| `default_flag` | 0.0% | 0.0 | 1.0 | 0.0142 | 0.1184 | 0.0 | 8.2045 |
| `next_3m_delinquency_flag` | 0.0% | 0.0 | 1.0 | 0.0399 | 0.1957 | 0.0 | 4.7024 |
| `next_6m_delinquency_flag` | 0.0% | 0.0 | 1.0 | 0.0552 | 0.2285 | 0.0 | 3.8936 |
| `next_12m_default_flag` | 0.0% | 0.0 | 1.0 | 0.0416 | 0.1996 | 0.0 | 4.593 |
| `next_12m_prepayment_flag` | 0.0% | 0.0 | 1.0 | 0.355 | 0.4785 | 0.0 | 0.6061 |
| `exception_required` | 0.0% | 0.0 | 1.0 | 0.0315 | 0.1747 | 0.0 | 5.3631 |

### 1b. Categorical Column Summary

| Column | Null% | Unique | Top 3 Values |
| :--- | ---: | ---: | :--- |
| `loan_id` | 0.0% | 20000 | F19Q10011748: 30, F19Q10005066: 30, F19Q10032648: 30 |
| `credit_score_band` | 0.0% | 6 | 741-800 (Very Good): 197786, 681-740 (Good): 128635, 621-680 (Fair): 40746 |
| `ltv_band` | 0.0% | 6 | 76-80%: 102943, 61-75%: 89076, <=60%: 72699 |
| `dti_band` | 0.0% | 6 | 31-40%: 139681, 41-45%: 93410, 21-30%: 86583 |
| `state` | 0.0% | 53 | CA: 40131, TX: 37927, FL: 32338 |
| `loan_purpose` | 0.0% | 3 | P: 260642, C: 86480, N: 60611 |
| `occupancy_type` | 0.0% | 3 | P: 354082, I: 35587, S: 18064 |
| `property_type` | 0.0% | 5 | SF: 255743, PU: 112833, CO: 36238 |
| `servicer_name` | 0.0% | 8 | Wells Fargo Bank, N.A.: 52387, U.S. Bank National Association: 51653, Newrez LLC: 51640 |
| `current_status` | 0.0% | 6 | CURRENT: 385177, PREPAID: 11711, 90PLUS_DPD: 5759 |
| `modification_flag` | 0.0% | 2 | N+: 407707, Y: 26 |
| `loss_severity_band` | 98.58% | 4 | High (46-70%): 1469, Medium (26-45%): 1467, Low (10-25%): 1458 |
| `last_updated_at` | 0.0% | 30 | 2019-07-28T12:00:00Z: 19754, 2019-08-28T12:00:00Z: 19626, 2019-09-28T12:00:00Z: 19427 |
| `source_system` | 0.0% | 1 | CORE_SERVICING_SYSTEM: 407733 |
| `document_status` | 0.0% | 4 | VERIFIED: 404589, UNVERIFIED_APPRAISAL: 1063, INCOMPLETE_INCOME: 1061 |
| `next_state` | 0.0% | 6 | CURRENT: 372541, PREPAID: 23890, 90PLUS_DPD: 6094 |
| `exception_type` | 0.0% | 5 | NONE: 394883, STATUS_CONFLICT: 3278, BALANCE_INCONSISTENCY: 3262 |

---

## 2. Missing Value Analysis

| Column | Null Count | Null% | Pattern | Impact |
| :--- | ---: | ---: | :--- | :--- |
| `loss_severity_band` | 401,933 | 98.58% | MAR | 🔴 HIGH |

---

## 3. Outlier Detection (3x IQR Fence)

| Column | Lower Fence | Upper Fence | Outlier Count | Outlier% |
| :--- | ---: | ---: | ---: | ---: |
| `origination_month` | 201,898.0 | 201,912.0 | 171 | 0.04% |
| `remaining_term_months` | 291.0 | 403.0 | 64,550 | 15.83% |
| `original_balance` | -348,000.0 | 786,000.0 | 186 | 0.05% |
| `current_balance` | -362,168.02 | 776,665.06 | 268 | 0.07% |
| `interest_rate` | 2.88 | 6.38 | 509 | 0.12% |

---

## 4. Validation Rule Results

| Rule ID | Rule Name | Severity | Violations | Violation% | Exception Type |
| :--- | :--- | :--- | ---: | ---: | :--- |
| VR-001 | Balance Ratio Upper Bound | 🔴 CRITICAL | 3,262 | 0.8% | `BALANCE_INCONSISTENCY` |
| VR-002 | Status DPD Consistency | 🟠 HIGH | 3,278 | 0.8% | `STATUS_CONFLICT` |
| VR-003 | Origination Date Validity | 🔴 CRITICAL | 18,679 | 4.58% | `INVALID_DATE` |
| VR-004 | Remaining Term Sanity | 🟠 HIGH | 3,259 | 0.8% | `INVALID_TERM` |
| VR-005 | Prepayment Balance Check | 🔴 CRITICAL | 85 | 0.02% | `BALANCE_INCONSISTENCY` |
| VR-006 | Document Verification Status | 🟡 MEDIUM | 3,144 | 0.77% | `DOCUMENT_GAP` |

---

## 5. Servicer Feed Reconciliation

| Conflict Type | Count | Percentage |
| :--- | ---: | ---: |
| Matched Records | 142,688 | 100.00% |
| Balance Conflicts (>5% diff) | 4,561 | 3.2% |
| Status Conflicts (mismatch) | 230 | 0.16% |
| Stale Records (lag > 1 year) | 0 | 0.0% |
| Any Conflict (union) | 4,791 | 3.36% |

### Sample Conflict Records (Top 10)

| Loan ID | Month | Primary Bal | Servicer Bal | Diff% | Primary Status | Servicer Status | Flags |
| :--- | :--- | ---: | ---: | ---: | :--- | :--- | :--- |
| F19Q10211591 | 202004 | $135,759.76 | $119,861.58 | 11.12% | CURRENT | CURRENT | BAL |
| F19Q10141049 | 202012 | $161,900.68 | $176,696.77 | 8.81% | CURRENT | CURRENT | BAL |
| F19Q20161679 | 201908 | $100,000.00 | $90,984.10 | 9.02% | CURRENT | CURRENT | BAL |
| F19Q10098566 | 201908 | $229,000.00 | $243,480.52 | 6.3% | CURRENT | CURRENT | BAL |
| F19Q20140730 | 202005 | $193,507.59 | $208,662.52 | 7.43% | CURRENT | CURRENT | BAL |
| F19Q20057058 | 202103 | $226,325.86 | $201,693.35 | 9.47% | CURRENT | CURRENT | BAL |
| F19Q10269674 | 201904 | $250,000.00 | $274,777.92 | 9.91% | CURRENT | CURRENT | BAL |
| F19Q10194615 | 201907 | $275,000.00 | $240,979.34 | 12.33% | CURRENT | CURRENT | BAL |
| F19Q10210606 | 202104 | $185,868.20 | $198,894.02 | 6.75% | CURRENT | CURRENT | BAL |
| F19Q10187464 | 201909 | $169,000.00 | $157,800.99 | 6.47% | CURRENT | CURRENT | BAL |

---

## 6. Train vs. Test Population Stability Index (PSI)

> PSI below 0.10 = Low (stable) | 0.10 to 0.20 = Medium (monitor) | above 0.20 = High (investigate)

| Feature | PSI | Drift Level | Type |
| :--- | ---: | :--- | :--- |
| `remaining_term_months` | 6.3071 | 🔴 HIGH | int64 |
| `month_index` | 6.0696 | 🔴 HIGH | int64 |
| `loan_age_months` | 3.8727 | 🔴 HIGH | int64 |
| `current_balance` | 0.1839 | 🟠 MEDIUM | float64 |
| `original_balance` | 0.098 | 🟢 LOW | float64 |
| `state` | 0.0426 | 🟢 LOW | object |
| `current_status` | 0.0162 | 🟢 LOW | object |
| `ltv_band` | 0.0122 | 🟢 LOW | object |
| `property_type` | 0.0105 | 🟢 LOW | object |
| `credit_score_band` | 0.01 | 🟢 LOW | object |
| `interest_rate` | 0.0074 | 🟢 LOW | float64 |
| `occupancy_type` | 0.0041 | 🟢 LOW | object |
| `dti_band` | 0.003 | 🟢 LOW | object |
| `loan_purpose` | 0.0013 | 🟢 LOW | object |
| `modification_flag` | 0.0008 | 🟢 LOW | object |
| `loss_severity_band` | 0.0007 | 🟢 LOW | object |
| `servicer_name` | 0.0005 | 🟢 LOW | object |
| `days_past_due` | 0.0 | 🟢 LOW | int64 |
| `prepayment_flag` | 0.0 | 🟢 LOW | int64 |
| `default_flag` | 0.0 | 🟢 LOW | int64 |
| `source_system` | 0.0 | 🟢 LOW | object |
| `document_status` | 0.0 | 🟢 LOW | object |

---

## 7. Data Quality Score Distribution

Record-level DQ Score (0-100): starts at 100, deducted for rule violations, missing fields, and balance anomalies.

| DQ Metric | Value |
| :--- | ---: |
| Mean DQ Score | 99.56 |
| Median DQ Score | 100.0 |
| Min DQ Score | 60.0 |
| Max DQ Score | 100.0 |
| Records below 60 (Critical) | 0.0% |
| Records below 80 (Warning) | 0.02% |
| Records at 100 (Perfect) | 96.83% |

---

*Generated by the Intain AI Track Loan Performance Intelligence Engine — Phase 1: Data Intelligence and Profiling*
