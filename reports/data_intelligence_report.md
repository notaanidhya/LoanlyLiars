# Data Intelligence Report

**Intain AI Track 2026 — Loan Performance Intelligence Engine**  
**Generated**: 2026-08-30 14:33:44  

---

## Executive Summary

| Metric | Value |
| :--- | ---: |
| Training Unique Loans | 20,000 |
| Training Monthly Records | 407,733 |
| Test Monthly Records | 304,374 |
| Train Reporting Period | 201901 to 202106 |
| Test Reporting Period | 202107 to 202603 |
| Servicer Update Records | 249,217 |
| Mean DQ Score | 99.3 / 100 |
| Records with DQ Score below 80 | 0.06% |

### Top Data Quality Issues

1. **Balance Ratio Upper Bound Check** (CRITICAL): 3,224 violations (0.79%) - Exception: `BALANCE_INCONSISTENCY`
2. **Origination Date Validity** (CRITICAL): 18,679 violations (4.58%) - Exception: `INVALID_DATE`
3. **Prepayment Balance Check** (CRITICAL): 74 violations (0.02%) - Exception: `BALANCE_INCONSISTENCY`
4. **High Missingness** in `next_12m_default_flag`: 35.45% null (MNAR (Potential Structural Gap))
5. **High Missingness** in `next_6m_delinquency_flag`: 18.02% null (MNAR (Potential Structural Gap))

---

## 1. Column Distribution Profile

### Numeric Features

| Column | Dtype | Null Count | Null% | Min | Median | Mean | Max | Std | Skew |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `month_index` | int64 | 0 | 0.0% | 0.0 | 10.0 | 10.9606 | 29.0 | 7.4206 | 0.3399 |
| `reporting_month` | int64 | 0 | 0.0% | 201901.0 | 202002.0 | 201978.3396 | 202106.0 | 68.2707 | 0.4362 |
| `origination_month` | int64 | 0 | 0.0% | 201902.0 | 201905.0 | 201905.0297 | 202006.0 | 2.4437 | 26.7217 |
| `loan_age_months` | int64 | 0 | 0.0% | 0.0 | 10.0 | 11.0468 | 29.0 | 7.4234 | 0.3373 |
| `remaining_term_months` | int64 | 0 | 0.0% | 68.0 | 348.0 | 324.139 | 480.0 | 63.4482 | -1.925 |
| `original_balance` | float64 | 0 | 0.0% | 15000.0 | 204000.0 | 229644.0195 | 1027000.0 | 123597.8423 | 0.9983 |
| `current_balance` | float64 | 0 | 0.0% | 0.0 | 193356.9 | 216255.9766 | 1209417.36 | 126910.4454 | 0.929 |
| `interest_rate` | float64 | 0 | 0.0% | 2.75 | 4.625 | 4.6318 | 6.75 | 0.4934 | 0.4704 |
| `days_past_due` | int64 | 0 | 0.0% | 0.0 | 0.0 | 4.0138 | 750.0 | 27.9195 | 9.84 |
| `prepayment_flag` | int64 | 0 | 0.0% | 0.0 | 0.0 | 0.0289 | 1.0 | 0.1676 | 5.6205 |
| `default_flag` | int64 | 0 | 0.0% | 0.0 | 0.0 | 0.0142 | 1.0 | 0.1184 | 8.2045 |
| `next_3m_delinquency_flag` | float64 | 36,201 | 8.88% | 0.0 | 0.0 | 0.0438 | 1.0 | 0.2046 | 4.46 |
| `next_6m_delinquency_flag` | float64 | 73,463 | 18.02% | 0.0 | 0.0 | 0.0674 | 1.0 | 0.2507 | 3.4514 |
| `next_12m_default_flag` | float64 | 144,528 | 35.45% | 0.0 | 0.0 | 0.0644 | 1.0 | 0.2455 | 3.549 |
| `next_12m_prepayment_flag` | float64 | 12,220 | 3.0% | 0.0 | 0.0 | 0.366 | 1.0 | 0.4817 | 0.5566 |
| `exception_required` | int64 | 0 | 0.0% | 0.0 | 0.0 | 0.0318 | 1.0 | 0.1755 | 5.3362 |

### Categorical Features

| Column | Dtype | Unique | Null Count | Null% | Top Values |
| :--- | :--- | ---: | ---: | ---: | :--- |
| `loan_id` | object | 20,000 | 0 | 0.0% | F19Q10016743: 30, F19Q10005066: 30, F19Q10005490: 30 |
| `credit_score_band` | object | 6 | 10,784 | 2.64% | 741-800 (Very Good): 192762, 681-740 (Good): 125136, 621-680 (Fair): 39345 |
| `ltv_band` | object | 6 | 0 | 0.0% | 76-80%: 102943, 61-75%: 89076, <=60%: 72699 |
| `dti_band` | object | 6 | 10,605 | 2.6% | 31-40%: 136276, 41-45%: 91053, 21-30%: 84253 |
| `state` | object | 53 | 8,620 | 2.11% | CA: 39379, TX: 37190, FL: 31519 |
| `loan_purpose` | object | 3 | 8,109 | 1.99% | P: 255544, C: 84554, N: 59526 |
| `occupancy_type` | object | 3 | 0 | 0.0% | P: 354082, I: 35587, S: 18064 |
| `property_type` | object | 5 | 0 | 0.0% | SF: 255743, PU: 112833, CO: 36238 |
| `servicer_name` | object | 8 | 0 | 0.0% | Pennymac Loan Services, LLC: 51623, Wells Fargo Bank, N.A.: 51257, Newrez LLC: 51139 |
| `current_status` | object | 6 | 0 | 0.0% | CURRENT: 385197, PREPAID: 11708, 90PLUS_DPD: 5753 |
| `modification_flag` | object | 2 | 0 | 0.0% | N+: 407707, Y: 26 |
| `loss_severity_band` | object | 4 | 401,933 | 98.58% | Low (10-25%): 1495, Medium (26-45%): 1487, Severe (>70%): 1416 |
| `last_updated_at` | object | 30 | 0 | 0.0% | 2019-07-28T12:00:00Z: 19754, 2019-08-28T12:00:00Z: 19626, 2019-09-28T12:00:00Z: 19427 |
| `source_system` | object | 1 | 0 | 0.0% | CORE_SERVICING_SYSTEM: 407733 |
| `document_status` | object | 4 | 0 | 0.0% | VERIFIED: 404475, INCOMPLETE_INCOME: 1130, UNVERIFIED_APPRAISAL: 1069 |
| `next_state` | object | 6 | 52 | 0.01% | CURRENT: 372489, PREPAID: 23890, 90PLUS_DPD: 6094 |
| `exception_type` | object | 5 | 0 | 0.0% | NONE: 394765, DOCUMENT_GAP: 3258, INVALID_TERM: 3250 |

---

## 2. Missingness Analysis (MCAR / MAR Patterns)

| Column | Null Count | Null% | Classification | Impact | Description |
| :--- | ---: | ---: | :--- | :--- | :--- |
| `loss_severity_band` | 401,933 | 98.58% | **MAR (Mechanistic)** | 🟢 INFORMATIONAL | Null in 100% of non-default records; populated exclusively upon default (expected behavior) |
| `next_12m_default_flag` | 144,528 | 35.45% | **MNAR (Potential Structural Gap)** | 🔴 HIGH | High missingness (35.45%) requires feature engineering imputation |
| `next_6m_delinquency_flag` | 73,463 | 18.02% | **MNAR (Potential Structural Gap)** | 🔴 HIGH | High missingness (18.02%) requires feature engineering imputation |
| `next_3m_delinquency_flag` | 36,201 | 8.88% | **MCAR (Random)** | 🟠 MEDIUM | Nulls uniformly distributed without target condition |
| `next_12m_prepayment_flag` | 12,220 | 3.0% | **MCAR (Random)** | 🟠 MEDIUM | Nulls uniformly distributed without target condition |
| `credit_score_band` | 10,784 | 2.64% | **MAR (Conditional)** | 🟠 MEDIUM | Missingness rate is 6.5% for Investment vs 2.3% for Primary occupancy |
| `dti_band` | 10,605 | 2.6% | **MCAR (Random)** | 🟠 MEDIUM | Nulls uniformly distributed without target condition |
| `state` | 8,620 | 2.11% | **MCAR (Random)** | 🟠 MEDIUM | Nulls uniformly distributed without target condition |
| `loan_purpose` | 8,109 | 1.99% | **MCAR (Random)** | 🟠 MEDIUM | Nulls uniformly distributed without target condition |
| `next_state` | 52 | 0.01% | **MCAR (Random)** | 🟢 LOW | Nulls uniformly distributed without target condition |

---

## 3. Extreme Outliers (3x IQR Fence)

| Feature | Lower Fence | Upper Fence | Outlier Count | Outlier% |
| :--- | ---: | ---: | ---: | ---: |
| `original_balance` | -348,000.0 | 786,000.0 | 186 | 0.046% |
| `current_balance` | -362,052.16 | 776,445.76 | 274 | 0.067% |
| `interest_rate` | 2.88 | 6.38 | 509 | 0.125% |
| `days_past_due` | 0.0 | 0.0 | 14,064 | 3.449% |

---

## 4. Deterministic Business & Accounting Rule Violations

| Rule ID | Rule Name | Severity | Exception Type | Violations | Violation% |
| :--- | :--- | :--- | :--- | ---: | ---: |
| `VR-001` | Balance Ratio Upper Bound Check | 🔴 CRITICAL | `BALANCE_INCONSISTENCY` | 3,224 | 0.79% |
| `VR-002` | Status DPD Consistency | 🟠 HIGH | `STATUS_CONFLICT` | 3,236 | 0.79% |
| `VR-003` | Origination Date Validity | 🔴 CRITICAL | `INVALID_DATE` | 18,679 | 4.58% |
| `VR-004` | Remaining Term Sanity Check | 🟠 HIGH | `INVALID_TERM` | 3,342 | 0.82% |
| `VR-005` | Prepayment Balance Check | 🔴 CRITICAL | `BALANCE_INCONSISTENCY` | 74 | 0.02% |
| `VR-006` | Document Verification Status | 🟡 MEDIUM | `DOCUMENT_GAP` | 3,258 | 0.8% |
| `VR-007` | Servicer Feed Reconciliation | 🟠 HIGH | `SERVICER_CONFLICT` | 0 | 0.0% |
| `VR-008` | Feed Staleness Check | 🟡 MEDIUM | `STALE_RECORD` | 0 | 0.0% |

---

## 5. Cross-Source Servicer Conflict Reconciliation

- Total Matched Records: **142,888**
- Balance Discrepancies (>5%): **4,531** (3.17%)
- Status Discrepancies: **223** (0.16%)
- Stale Feed Records: **0** (0.0%)

## 6. Train vs. Test Population Stability Index (PSI)

> PSI below 0.10 = Low (stable) | 0.10 to 0.20 = Medium (monitor) | above 0.20 = High (investigate)

| Feature | PSI | Drift Level | Type |
| :--- | ---: | :--- | :--- |
| `remaining_term_months` | 6.3044 | 🔴 HIGH | int64 |
| `month_index` | 6.0696 | 🔴 HIGH | int64 |
| `loan_age_months` | 3.8727 | 🔴 HIGH | int64 |
| `current_balance` | 0.184 | 🟠 MEDIUM | float64 |
| `original_balance` | 0.098 | 🟢 LOW | float64 |
| `state` | 0.0425 | 🟢 LOW | object |
| `current_status` | 0.0162 | 🟢 LOW | object |
| `ltv_band` | 0.0122 | 🟢 LOW | object |
| `property_type` | 0.0105 | 🟢 LOW | object |
| `credit_score_band` | 0.0101 | 🟢 LOW | object |
| `interest_rate` | 0.0074 | 🟢 LOW | float64 |
| `occupancy_type` | 0.0041 | 🟢 LOW | object |
| `dti_band` | 0.0031 | 🟢 LOW | object |
| `loan_purpose` | 0.0013 | 🟢 LOW | object |
| `loss_severity_band` | 0.0012 | 🟢 LOW | object |
| `servicer_name` | 0.0009 | 🟢 LOW | object |
| `modification_flag` | 0.0008 | 🟢 LOW | object |
| `days_past_due` | 0.0 | 🟢 LOW | int64 |
| `prepayment_flag` | 0.0 | 🟢 LOW | int64 |
| `default_flag` | 0.0 | 🟢 LOW | int64 |
| `document_status` | 0.0 | 🟢 LOW | object |

---

## 7. Multicollinearity & Bivariate Correlation Analysis

> Highlights highly dependent feature pairs (|r| >= 0.70) to inform regularization and model interpretability.

| Feature 1 | Feature 2 | Pearson r | Spearman rho | Collinearity Level |
| :--- | :--- | ---: | ---: | :--- |
| `reporting_month` | `loan_age_months` | **0.9215** | 0.9805 | 🔴 HIGH_COLLINEARITY |
| `original_balance` | `current_balance` | **0.9037** | 0.9078 | 🔴 HIGH_COLLINEARITY |
| `next_3m_delinquency_flag` | `next_6m_delinquency_flag` | **0.8413** | 0.8413 | 🟠 MODERATE_COLLINEARITY |
| `days_past_due` | `default_flag` | **0.8373** | 0.6477 | 🟠 MODERATE_COLLINEARITY |
| `next_6m_delinquency_flag` | `next_12m_default_flag` | **0.7193** | 0.7193 | 🟠 MODERATE_COLLINEARITY |
| `reporting_month` | `remaining_term_months` | **-0.1294** | -0.7154 | 🟠 MODERATE_COLLINEARITY |
| `loan_age_months` | `remaining_term_months` | **-0.1419** | -0.7299 | 🟠 MODERATE_COLLINEARITY |

---

## 8. Data Quality Score Distribution

Record-level DQ Score (0-100): starts at 100, deducted for rule violations, missing fields, and balance anomalies.

| DQ Metric | Value |
| :--- | ---: |
| Mean DQ Score | 99.3 |
| Median DQ Score | 100.0 |
| Min DQ Score | 55.0 |
| Max DQ Score | 100.0 |
| Records below 60 (Critical) | 0.0% |
| Records below 80 (Warning) | 0.06% |
| Records at 100 (Perfect) | 91.79% |

---

*Generated by the Intain AI Track Loan Performance Intelligence Engine — Phase 1: Data Intelligence and Profiling*
