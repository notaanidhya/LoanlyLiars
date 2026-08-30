# Model Explainability & Error Diagnostics Report

**Intain AI Track 2026 — Phase 4: TreeSHAP Attribution & Dual-Risk Analysis**  
**Generated**: 2026-08-30 19:35:37  

---

## 1. Executive Summary: Dual-Risk Dynamics & Operational Attribution

In structured finance and mortgage portfolio intelligence, risk modeling encompasses two distinct and competing hazards:

1. **Downside Credit Deterioration (Default & Delinquency)**: Borrowers unable to maintain debt service due to macro distress, leverage spikes, or payment shocks.
2. **Duration & Yield Risk (Prepayment / Refinance)**: Prime borrowers voluntarily refinancing when market interest rates drop, depriving investors of contracted yield streams.
3. **Operational & Reporting Anomalies ($S_{\text{anomaly}}$)**: Multivariate outliers and servicer discrepancies identified via unsupervised Isolation Forest and contractual validation rules.

This report details global TreeSHAP feature interactions, provides 20 reviewer-ready local case cards with full waterfall decompositions, stages vectorized top-3 drivers for final submission, and diagnoses error segments on the held-out validation cohort.

---

## 2. Global Model Explainability (TreeSHAP Beeswarm Summary)

TreeSHAP calculates the exact marginal contribution of each feature to the model's log-odds output across all possible feature coalitions.

### 2a. 12-Month Mortgage Default Risk Drivers

![Global Default SHAP](figures/shap_global_default_12m.png)

- **Primary Credit Drivers**: `dpd_3m_mean`, `dti_x_ltv`, `status_severity`, and `delinquency_velocity` exhibit the strongest upward pushes on default log-odds.
- **Protective Drivers**: High `credit_score_ord` and low `ltv_ord` strongly push default probabilities toward zero.

### 2b. 12-Month Voluntary Prepayment Drivers

![Global Prepayment SHAP](figures/shap_global_prepayment_12m.png)

- **Primary Refinance Drivers**: `prepayment_incentive` (the interest rate spread to current market average) and `credit_score_ord` dominate prepayment probability.
- **Dual-Risk Contrast**: Unlike default risk, prepayment risk is concentrated in **high-FICO, low-LTV** borrowers who can seamlessly qualify for refinancing.

### 2c. Unsupervised Isolation Forest Anomaly Drivers

![Global Isolation Forest SHAP](figures/shap_global_anomaly_iforest.png)

- **Directional Attribution**: For Isolation Forest, negative SHAP values indicate tree path compression (accelerating isolation). Key isolation drivers include multivariate interactions like `distress_score`, `age_x_rate`, and `rate_spread_to_market`.

---

## 3. Stratified Reviewer-Ready Case Cards (20 Local Waterfall Audits)

> Each audit card presents loan attributes, prescriptive reviewer action, continuous anomaly score, exact directional top drivers, and an embedded TreeSHAP waterfall chart.

### Case #01: Loan `F19Q20146209` (Period: `202209`)

- **Reviewer Action**: `MANUAL_AUDIT` | **Anomaly Score**: `0.8211` | **Exception**: `BALANCE_INCONSISTENCY`
- **Target Modeled**: `3-Month Delinquency Probability`
- **Top Directional TreeSHAP Drivers**:
  * `distress_score (+1.844)`
  * `maturity_pressure (+1.280)`
  * `dpd_3m_max (+0.547)`

![Waterfall Case 01](figures/waterfall_case_01.png)

- **Audit Recommendation**: *Critical risk surge or multi-rule breach. Auditor should recalculate balance ledger and audit collateral tape.*

---

### Case #02: Loan `F19Q10104351` (Period: `202208`)

- **Reviewer Action**: `MANUAL_AUDIT` | **Anomaly Score**: `0.7570` | **Exception**: `STATUS_CONFLICT`
- **Target Modeled**: `3-Month Delinquency Probability`
- **Top Directional TreeSHAP Drivers**:
  * `distress_score (+1.337)`
  * `maturity_pressure (+1.105)`
  * `days_past_due (+0.462)`

![Waterfall Case 02](figures/waterfall_case_02.png)

- **Audit Recommendation**: *Critical risk surge or multi-rule breach. Auditor should recalculate balance ledger and audit collateral tape.*

---

### Case #03: Loan `F19Q20197714` (Period: `202202`)

- **Reviewer Action**: `MANUAL_AUDIT` | **Anomaly Score**: `0.7570` | **Exception**: `BALANCE_INCONSISTENCY`
- **Target Modeled**: `3-Month Delinquency Probability`
- **Top Directional TreeSHAP Drivers**:
  * `distress_score (+1.504)`
  * `maturity_pressure (+1.166)`
  * `days_past_due (+0.448)`

![Waterfall Case 03](figures/waterfall_case_03.png)

- **Audit Recommendation**: *Critical risk surge or multi-rule breach. Auditor should recalculate balance ledger and audit collateral tape.*

---

### Case #04: Loan `F19Q10213219` (Period: `202209`)

- **Reviewer Action**: `MANUAL_AUDIT` | **Anomaly Score**: `0.7557` | **Exception**: `BALANCE_INCONSISTENCY`
- **Target Modeled**: `3-Month Delinquency Probability`
- **Top Directional TreeSHAP Drivers**:
  * `distress_score (+1.388)`
  * `maturity_pressure (+1.308)`
  * `days_past_due (+0.499)`

![Waterfall Case 04](figures/waterfall_case_04.png)

- **Audit Recommendation**: *Critical risk surge or multi-rule breach. Auditor should recalculate balance ledger and audit collateral tape.*

---

### Case #05: Loan `F19Q20134913` (Period: `202603`)

- **Reviewer Action**: `MANUAL_AUDIT` | **Anomaly Score**: `0.7293` | **Exception**: `BALANCE_INCONSISTENCY`
- **Target Modeled**: `3-Month Delinquency Probability`
- **Top Directional TreeSHAP Drivers**:
  * `distress_score (+1.580)`
  * `maturity_pressure (+1.118)`
  * `dpd_3m_max (+0.586)`

![Waterfall Case 05](figures/waterfall_case_05.png)

- **Audit Recommendation**: *Critical risk surge or multi-rule breach. Auditor should recalculate balance ledger and audit collateral tape.*

---

### Case #06: Loan `F19Q10133814` (Period: `202409`)

- **Reviewer Action**: `ESCALATE_DOC_REVIEW` | **Anomaly Score**: `0.4759` | **Exception**: `DOCUMENT_GAP`
- **Target Modeled**: `Isolation Forest Outlier Score`
- **Top Directional TreeSHAP Drivers**:
  * `maturity_pressure (-2.848)`
  * `distress_score (-2.571)`
  * `status_severity (-1.396)`

![Waterfall Case 06](figures/waterfall_case_06.png)

- **Audit Recommendation**: *Document verification defect detected. Request original note / title endorsement from originator.*

---

### Case #07: Loan `F19Q10133814` (Period: `202408`)

- **Reviewer Action**: `ESCALATE_DOC_REVIEW` | **Anomaly Score**: `0.4759` | **Exception**: `DOCUMENT_GAP`
- **Target Modeled**: `Isolation Forest Outlier Score`
- **Top Directional TreeSHAP Drivers**:
  * `maturity_pressure (-2.848)`
  * `distress_score (-2.571)`
  * `status_severity (-1.396)`

![Waterfall Case 07](figures/waterfall_case_07.png)

- **Audit Recommendation**: *Document verification defect detected. Request original note / title endorsement from originator.*

---

### Case #08: Loan `F19Q10240874` (Period: `202203`)

- **Reviewer Action**: `ESCALATE_DOC_REVIEW` | **Anomaly Score**: `0.4608` | **Exception**: `DOCUMENT_GAP`
- **Target Modeled**: `Isolation Forest Outlier Score`
- **Top Directional TreeSHAP Drivers**:
  * `maturity_pressure (-3.135)`
  * `distress_score (-2.711)`
  * `status_severity (-1.611)`

![Waterfall Case 08](figures/waterfall_case_08.png)

- **Audit Recommendation**: *Document verification defect detected. Request original note / title endorsement from originator.*

---

### Case #09: Loan `F19Q20235569` (Period: `202107`)

- **Reviewer Action**: `ESCALATE_DOC_REVIEW` | **Anomaly Score**: `0.4502` | **Exception**: `DOCUMENT_GAP`
- **Target Modeled**: `Isolation Forest Outlier Score`
- **Top Directional TreeSHAP Drivers**:
  * `maturity_pressure (-3.228)`
  * `distress_score (-2.851)`
  * `status_severity (-1.688)`

![Waterfall Case 09](figures/waterfall_case_09.png)

- **Audit Recommendation**: *Document verification defect detected. Request original note / title endorsement from originator.*

---

### Case #10: Loan `F19Q10133450` (Period: `202108`)

- **Reviewer Action**: `ESCALATE_DOC_REVIEW` | **Anomaly Score**: `0.4422` | **Exception**: `DOCUMENT_GAP`
- **Target Modeled**: `Isolation Forest Outlier Score`
- **Top Directional TreeSHAP Drivers**:
  * `maturity_pressure (-3.036)`
  * `distress_score (-2.768)`
  * `status_severity (-1.612)`

![Waterfall Case 10](figures/waterfall_case_10.png)

- **Audit Recommendation**: *Document verification defect detected. Request original note / title endorsement from originator.*

---

### Case #11: Loan `F19Q10087661` (Period: `202207`)

- **Reviewer Action**: `OVERRIDE_SERVICER` | **Anomaly Score**: `0.4096` | **Exception**: `NONE`
- **Target Modeled**: `Isolation Forest Outlier Score`
- **Top Directional TreeSHAP Drivers**:
  * `maturity_pressure (-2.885)`
  * `distress_score (-2.581)`
  * `status_severity (-1.419)`

![Waterfall Case 11](figures/waterfall_case_11.png)

- **Audit Recommendation**: *Servicer cross-source conflict confirmed. Apply primary ledger balance override.*

---

### Case #12: Loan `F19Q20014985` (Period: `202110`)

- **Reviewer Action**: `OVERRIDE_SERVICER` | **Anomaly Score**: `0.3744` | **Exception**: `NONE`
- **Target Modeled**: `Isolation Forest Outlier Score`
- **Top Directional TreeSHAP Drivers**:
  * `maturity_pressure (-3.421)`
  * `distress_score (-3.090)`
  * `status_severity (-1.799)`

![Waterfall Case 12](figures/waterfall_case_12.png)

- **Audit Recommendation**: *Servicer cross-source conflict confirmed. Apply primary ledger balance override.*

---

### Case #13: Loan `F19Q10267695` (Period: `202204`)

- **Reviewer Action**: `OVERRIDE_SERVICER` | **Anomaly Score**: `0.3679` | **Exception**: `NONE`
- **Target Modeled**: `Isolation Forest Outlier Score`
- **Top Directional TreeSHAP Drivers**:
  * `maturity_pressure (-3.457)`
  * `distress_score (-2.894)`
  * `status_severity (-1.733)`

![Waterfall Case 13](figures/waterfall_case_13.png)

- **Audit Recommendation**: *Servicer cross-source conflict confirmed. Apply primary ledger balance override.*

---

### Case #14: Loan `F19Q10087661` (Period: `202307`)

- **Reviewer Action**: `OVERRIDE_SERVICER` | **Anomaly Score**: `0.3669` | **Exception**: `NONE`
- **Target Modeled**: `Isolation Forest Outlier Score`
- **Top Directional TreeSHAP Drivers**:
  * `distress_score (-2.078)`
  * `maturity_pressure (-1.881)`
  * `status_severity (-1.513)`

![Waterfall Case 14](figures/waterfall_case_14.png)

- **Audit Recommendation**: *Servicer cross-source conflict confirmed. Apply primary ledger balance override.*

---

### Case #15: Loan `F19Q10267695` (Period: `202202`)

- **Reviewer Action**: `OVERRIDE_SERVICER` | **Anomaly Score**: `0.3636` | **Exception**: `NONE`
- **Target Modeled**: `Isolation Forest Outlier Score`
- **Top Directional TreeSHAP Drivers**:
  * `maturity_pressure (-3.331)`
  * `distress_score (-2.911)`
  * `status_severity (-1.733)`

![Waterfall Case 15](figures/waterfall_case_15.png)

- **Audit Recommendation**: *Servicer cross-source conflict confirmed. Apply primary ledger balance override.*

---

### Case #16: Loan `F19Q10086356` (Period: `202508`)

- **Reviewer Action**: `REQUEST_CURE` | **Anomaly Score**: `0.5555` | **Exception**: `INVALID_TERM`
- **Target Modeled**: `Isolation Forest Outlier Score`
- **Top Directional TreeSHAP Drivers**:
  * `maturity_pressure (-2.696)`
  * `distress_score (-2.326)`
  * `status_severity (-1.350)`

![Waterfall Case 16](figures/waterfall_case_16.png)

- **Audit Recommendation**: *Active delinquency roll or structural late payment. Request servicer cure plan.*

---

### Case #17: Loan `F19Q10086356` (Period: `202506`)

- **Reviewer Action**: `REQUEST_CURE` | **Anomaly Score**: `0.5555` | **Exception**: `INVALID_TERM`
- **Target Modeled**: `Isolation Forest Outlier Score`
- **Top Directional TreeSHAP Drivers**:
  * `maturity_pressure (-2.676)`
  * `distress_score (-2.304)`
  * `status_severity (-1.369)`

![Waterfall Case 17](figures/waterfall_case_17.png)

- **Audit Recommendation**: *Active delinquency roll or structural late payment. Request servicer cure plan.*

---

### Case #18: Loan `F19Q10086356` (Period: `202505`)

- **Reviewer Action**: `REQUEST_CURE` | **Anomaly Score**: `0.5555` | **Exception**: `INVALID_TERM`
- **Target Modeled**: `Isolation Forest Outlier Score`
- **Top Directional TreeSHAP Drivers**:
  * `maturity_pressure (-2.624)`
  * `distress_score (-2.281)`
  * `status_severity (-1.374)`

![Waterfall Case 18](figures/waterfall_case_18.png)

- **Audit Recommendation**: *Active delinquency roll or structural late payment. Request servicer cure plan.*

---

### Case #19: Loan `F19Q10086356` (Period: `202507`)

- **Reviewer Action**: `REQUEST_CURE` | **Anomaly Score**: `0.5555` | **Exception**: `INVALID_TERM`
- **Target Modeled**: `Isolation Forest Outlier Score`
- **Top Directional TreeSHAP Drivers**:
  * `maturity_pressure (-2.695)`
  * `distress_score (-2.335)`
  * `status_severity (-1.356)`

![Waterfall Case 19](figures/waterfall_case_19.png)

- **Audit Recommendation**: *Active delinquency roll or structural late payment. Request servicer cure plan.*

---

### Case #20: Loan `F19Q10086356` (Period: `202510`)

- **Reviewer Action**: `REQUEST_CURE` | **Anomaly Score**: `0.5555` | **Exception**: `INVALID_TERM`
- **Target Modeled**: `Isolation Forest Outlier Score`
- **Top Directional TreeSHAP Drivers**:
  * `maturity_pressure (-2.709)`
  * `distress_score (-2.376)`
  * `status_severity (-1.350)`

![Waterfall Case 20](figures/waterfall_case_20.png)

- **Audit Recommendation**: *Active delinquency roll or structural late payment. Request servicer cure plan.*

---

## 4. False Positive & False Negative Error Segment Diagnostics

Error segment profiling isolates where model predictions diverge from ground-truth outcomes on the untouched 15% validation slice.

### Target: `next_12m_default_flag` (Threshold @ 0.5)

| Metric | Value | Breakdown Count |
| :--- | ---: | :--- |
| **True Positives (TP)** | 350 | Correctly flagged high risk |
| **False Positives (FP)** | 7 | False alarms (model predicted 1, actual 0) |
| **False Negatives (FN)** | 75 | Missed risks (model predicted 0, actual 1) |
| **True Negatives (TN)** | 4,682 | Correctly cleared safe loans |
| **Precision** | 0.9804 | $\text{TP} / (\text{TP} + \text{FP})$ |
| **Recall** | 0.8235 | $\text{TP} / (\text{TP} + \text{FN})$ |
| **False Positive Rate** | 0.0015 | $\text{FP} / (\text{FP} + \text{TN})$ |
| **False Negative Rate** | 0.1765 | $\text{FN} / (\text{FN} + \text{TP})$ |

#### Top Distinguishing Divergences for `next_12m_default_flag`:

- **False Positive Segment Over-attribution (Why model predicted risk)**:
  * `status_severity`: +4.07$\sigma$ vs. True Negatives
  * `days_past_due`: +3.77$\sigma$ vs. True Negatives
  * `current_balance`: +0.97$\sigma$ vs. True Negatives
  * `prev_balance`: +0.97$\sigma$ vs. True Negatives
  * `original_balance`: +0.92$\sigma$ vs. True Negatives
- **False Negative Segment Under-attribution (Why model missed risk)**:
  * `days_past_due`: 2.30$\sigma$ vs. True Positives
  * `status_severity`: 1.23$\sigma$ vs. True Positives
  * `current_balance`: 0.34$\sigma$ vs. True Positives
  * `prev_balance`: 0.32$\sigma$ vs. True Positives
  * `dti_ord`: 0.31$\sigma$ vs. True Positives

### Target: `next_12m_prepayment_flag` (Threshold @ 0.5)

| Metric | Value | Breakdown Count |
| :--- | ---: | :--- |
| **True Positives (TP)** | 2,408 | Correctly flagged high risk |
| **False Positives (FP)** | 1 | False alarms (model predicted 1, actual 0) |
| **False Negatives (FN)** | 1 | Missed risks (model predicted 0, actual 1) |
| **True Negatives (TN)** | 4,977 | Correctly cleared safe loans |
| **Precision** | 0.9996 | $\text{TP} / (\text{TP} + \text{FP})$ |
| **Recall** | 0.9996 | $\text{TP} / (\text{TP} + \text{FN})$ |
| **False Positive Rate** | 0.0002 | $\text{FP} / (\text{FP} + \text{TN})$ |
| **False Negative Rate** | 0.0004 | $\text{FN} / (\text{FN} + \text{TP})$ |

#### Top Distinguishing Divergences for `next_12m_prepayment_flag`:

- **False Positive Segment Over-attribution (Why model predicted risk)**:
  * `loan_purpose_enc`: +1.94$\sigma$ vs. True Negatives
  * `property_type_enc`: +1.62$\sigma$ vs. True Negatives
  * `occupancy_type_enc`: +1.58$\sigma$ vs. True Negatives
  * `state_enc`: +1.45$\sigma$ vs. True Negatives
  * `interest_rate`: +1.41$\sigma$ vs. True Negatives
- **False Negative Segment Under-attribution (Why model missed risk)**:
  * `loan_age_months`: 0.85$\sigma$ vs. True Positives
  * `credit_score_ord`: 0.80$\sigma$ vs. True Positives
  * `property_type_enc`: -0.77$\sigma$ vs. True Positives
  * `servicer_name_enc`: 0.69$\sigma$ vs. True Positives
  * `loan_purpose_enc`: -0.56$\sigma$ vs. True Positives

### Target: `next_3m_delinquency_flag` (Threshold @ 0.5)

| Metric | Value | Breakdown Count |
| :--- | ---: | :--- |
| **True Positives (TP)** | 521 | Correctly flagged high risk |
| **False Positives (FP)** | 104 | False alarms (model predicted 1, actual 0) |
| **False Negatives (FN)** | 0 | Missed risks (model predicted 0, actual 1) |
| **True Negatives (TN)** | 6,164 | Correctly cleared safe loans |
| **Precision** | 0.8336 | $\text{TP} / (\text{TP} + \text{FP})$ |
| **Recall** | 1.0000 | $\text{TP} / (\text{TP} + \text{FN})$ |
| **False Positive Rate** | 0.0166 | $\text{FP} / (\text{FP} + \text{TN})$ |
| **False Negative Rate** | 0.0000 | $\text{FN} / (\text{FN} + \text{TP})$ |

#### Top Distinguishing Divergences for `next_3m_delinquency_flag`:

- **False Positive Segment Over-attribution (Why model predicted risk)**:
  * `days_past_due`: +1.45$\sigma$ vs. True Negatives
  * `status_severity`: +0.84$\sigma$ vs. True Negatives
  * `modification_flag_bin`: +0.55$\sigma$ vs. True Negatives
  * `interest_rate`: +0.37$\sigma$ vs. True Negatives
  * `prev_balance`: +0.33$\sigma$ vs. True Negatives
- **False Negative Segment Under-attribution (Why model missed risk)**:

---

## 5. Submission Readiness & Vectorized Driver Staging

- **Staged File**: `data/processed/phase4_shap_drivers_test.csv`
- **Total Rows Staged**: `92,586`
- **Null Value Rate**: `0.00%` across all driver columns

| Feature Column | Sample Top Values |
| :--- | :--- |
| `top_driver_1` | `age_x_rate, remaining_term_months, loan_purpose_enc` |
| `top_driver_2` | `age_x_rate, remaining_term_months, loan_purpose_enc` |
| `top_driver_3` | `age_x_rate, remaining_term_months, loan_purpose_enc` |

---

*Report generated by Intain AI Track — Phase 4: Model Explainability Engine*
