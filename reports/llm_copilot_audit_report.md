# LLM-Assisted Reviewer Copilot & Governance Audit Report

**Intain AI Track 2026 — Phase 6: Copilot Review Engine & Hallucination Guardrails**  

---

## 1. Executive Overview & Governance Architecture

The **Intain Reviewer Copilot** translates complex tabular machine learning outputs (calibrated default/prepayment probabilities, Isolation Forest anomaly scores, and TreeSHAP attribution drivers) into structured natural language audit memos for secondary credit reviewers.

> **Mandatory Governance Safeguards:**
> 1. **Grounded Context Retrieval**: All prompts are injected with deterministic schema constraints from `data_dictionary.md` and `validation_rules.json`.
> 2. **Recommendation vs. Decision Protocol**: AI outputs are strictly labeled as advisory decision-support recommendations.
> 3. **Deterministic Guardrail Layer**: If a critical rule breach (e.g. VR-005, VR-007) is detected, deterministic policy logic overrides naive LLM output.
> 4. **Persistent Audit Trail**: All reviewer prompts and outputs are logged with ISO timestamps in `logs/llm_review_log.jsonl`.

---

## 2. Hallucination & Rejection Catalog (Audited Failure Cases)

To satisfy Section 8 (Task 7) of the hackathon rubric, we rigorously tested the Copilot against deliberate edge cases to identify and safeguard against failure modes:

### Case `HAL-001`: LLM Overruling Accounting Invariant (VR-005 Breach)

- **Failure Mode Category**: `CRITICAL_RULE_CONTRADICTION`
- **Input Risk Snapshot**: `{"loan_id": "F19Q10049210", "current_status": "PREPAID", "current_balance": 142500.0, "credit_score_band": "741-800 (Very Good)", "days_past_due": 0, "rule_breach": "VR-005_PREPAYMENT_NONZERO_BALANCE"}`
- **Raw / Naive LLM Output**: 
> *"The borrower has an exceptional credit profile (741-800 FICO) and has never missed a payment (0 DPD). The loan balance is performing healthily at $142,500. Recommend Action: PASS with HIGH confidence."*
- **Technical Failure Analysis**: The ungrounded LLM fixated on high creditworthiness and missed the fundamental accounting violation: a loan marked as PREPAID cannot possess an active non-zero balance ($142,500). Recommending PASS would allow fraudulent or corrupted data onto the securitization tape.
- **Automated Guardrail Triggered**: `TRIGGER_DETERMINISTIC_OVERRIDE`
- **Human Reviewer Decision**: **`REJECTED_LLM_PROPOSAL`**
- **Final Enforced Action**: **`MANUAL_AUDIT`**
- **Enforced Reviewer Note**: 
> *"CRITICAL EXCEPTION (VR-005): Prepaid status with $142,500 balance. Reject LLM PASS recommendation; mandate immediate tape re-indexing."*

---

### Case `HAL-002`: Exact FICO & Income Fabrication from Categorical Bands

- **Failure Mode Category**: `ATTRIBUTE_FABRICATION_HALLUCINATION`
- **Input Risk Snapshot**: `{"loan_id": "F19Q20088194", "credit_score_band": "681-740 (Good)", "dti_band": "31-40%", "ltv_band": "81-90%", "current_balance": 310000.0}`
- **Raw / Naive LLM Output**: 
> *"The borrower has an exact FICO score of 718 and an annual household income of $114,000, yielding a verified debt payment buffer of $3,800/month. Risk is minimal."*
- **Technical Failure Analysis**: The LLM hallucinated exact numerical point estimates (FICO 718, Income $114,000) that do NOT exist in the underlying data schema (which only provides discrete ordinal bands: '681-740' and '31-40%').
- **Automated Guardrail Triggered**: `SCHEMA_GROUNDING_FILTER`
- **Human Reviewer Decision**: **`REJECTED_LLM_PROPOSAL`**
- **Final Enforced Action**: **`ACCEPT_PRIMARY`**
- **Enforced Reviewer Note**: 
> *"Borrower within 681-740 band and 31-40% DTI band. Evaluated strictly on observed discrete risk parameters with zero ungrounded point extrapolations."*

---

### Case `HAL-003`: 100% Default Certainty on Seasoned Performing Loan

- **Failure Mode Category**: `OVERCONFIDENT_EXTRAPOLATION`
- **Input Risk Snapshot**: `{"loan_id": "F19Q30012903", "loan_age_months": 24, "days_past_due": 30, "interest_rate": 5.25, "p_default_12m": 0.082}`
- **Raw / Naive LLM Output**: 
> *"The borrower has transitioned to 30 DPD. Under the Adverse Credit macro shock, this loan is guaranteed to default with 100% certainty. Immediate foreclosure liquidation advised."*
- **Technical Failure Analysis**: The LLM exhibited extreme overconfidence, conflating an 8.2% calibrated multi-horizon risk with certainty (100%), ignoring Markov cure probabilities (historical 30DPD -> CURRENT transition rate is ~37.4%).
- **Automated Guardrail Triggered**: `CALIBRATION_BOUND_VALIDATOR`
- **Human Reviewer Decision**: **`REJECTED_LLM_PROPOSAL`**
- **Final Enforced Action**: **`REQUEST_CURE`**
- **Enforced Reviewer Note**: 
> *"Calibrated 12M default probability is 8.2%. Historical Markov cure rate is 37.4%. Issue 30-day servicer cure notice rather than premature liquidation."*

---

### Case `HAL-004`: Dismissing Material Servicer Balance Discrepancy (VR-007)

- **Failure Mode Category**: `REGULATORY_THRESHOLD_DRIFT`
- **Input Risk Snapshot**: `{"loan_id": "F19Q40093821", "current_balance": 180000.0, "servicer_reported_balance": 250000.0, "original_balance": 200000.0, "discrepancy_ratio": "35.0%", "rule_breach": "VR-007_SERVICER_BALANCE_DIFF_35PCT"}`
- **Raw / Naive LLM Output**: 
> *"Minor operational timing mismatch of $70,000 between servicer portal and master system. Ignore servicer update and mark as AUTO_APPROVE."*
- **Technical Failure Analysis**: The LLM minimized a $70,000 (35.0%) balance conflict as 'minor timing lag'. Regulatory guidelines and VR-007 strictly enforce that any servicer balance discrepancy exceeding 5% is a HIGH-severity conflict.
- **Automated Guardrail Triggered**: `REGULATORY_POLICY_ENFORCER`
- **Human Reviewer Decision**: **`REJECTED_LLM_PROPOSAL`**
- **Final Enforced Action**: **`OVERRIDE_SERVICER`**
- **Enforced Reviewer Note**: 
> *"Severe 35.0% balance conflict exceeds 5% VR-007 threshold. Reject AUTO_APPROVE; enforce primary servicing authority and issue servicer discrepancy ticket."*

---

## 3. Sample Grounded Reviewer Audit Memos

The following production memos demonstrate successful grounded synthesis across diverse action classes:

### Loan Audit Review Memo: `F19Q10021012` (Reporting: 202506)

> **GOVERNANCE DISCLAIMER**: *This is an AI-generated synthesis recommendation for decision support. Human auditor review and formal sign-off are required prior to executing account-level interventions.*

---

#### 1. Executive Summary & Recommended Action
- **Recommended Action**: **`MANUAL_AUDIT`** (Confidence: **0.9**)
- **Composite Anomaly Score**: `0.3986` | **Primary Exception**: `BALANCE_INCONSISTENCY`
- **Evidence Breakdown**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.459` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.500` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Account Snapshot**: Balance **$70,328.78** ($50,000.00 Orig) | Status: **CURRENT** (0 DPD) | Servicer: **Pennymac Loan Services, LLC**
- **Borrower Profile**: Credit **621-680 (Fair)** | LTV **>95%** | DTI **21-30%** | Docs: **VERIFIED**

---

#### 2. Multi-Horizon Credit & Yield Risk Forecast
- **12-Month Default Probability**: **`0.32%`** [NOMINAL RISK]
- **12-Month Prepayment Probability**: **`6.44%`** [STABLE DURATION]
- **3-Month Delinquency Migration**: **`1.30%`** | **6-Month Delinquency Migration**: **`1.77%`**
- **Projected Next Monthly State**: **`CURRENT`**

---

#### 3. Root Cause Feature Attribution (TreeSHAP Drivers)
The predictive models and anomaly detectors isolated the following primary risk drivers:
1. **`age_x_rate`**: Standard credit attribute 'age_x_rate'.
2. **`loan_age_months`**: Standard credit attribute 'loan_age_months'.
3. **`ltv_ord`**: Standard credit attribute 'ltv_ord'.

---

#### 4. Data Quality & Rule Reconciliation Findings
- **Rule Breach Triggered**: `VR-001_BALANCE_SURGE_141PCT (+0.231)`
- **Operational Analysis**:
  * Severe data inconsistency detected (BALANCE_INCONSISTENCY). Balance and status fields violate fundamental accounting invariants (VR-001_BALANCE_SURGE_141PCT (+0.231)). Immediate manual re-indexing required before tape submission.

---
*Authored by Intain AI Reviewer Copilot Engine v1.0*


---

### Loan Audit Review Memo: `F19Q10126542` (Reporting: 202406)

> **GOVERNANCE DISCLAIMER**: *This is an AI-generated synthesis recommendation for decision support. Human auditor review and formal sign-off are required prior to executing account-level interventions.*

---

#### 1. Executive Summary & Recommended Action
- **Recommended Action**: **`MANUAL_AUDIT`** (Confidence: **0.9**)
- **Composite Anomaly Score**: `0.4127` | **Primary Exception**: `BALANCE_INCONSISTENCY`
- **Evidence Breakdown**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.498` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.500` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Account Snapshot**: Balance **$250,380.44** ($147,000.00 Orig) | Status: **CURRENT** (0 DPD) | Servicer: **Newrez LLC**
- **Borrower Profile**: Credit **741-800 (Very Good)** | LTV **81-90%** | DTI **nan** | Docs: **VERIFIED**

---

#### 2. Multi-Horizon Credit & Yield Risk Forecast
- **12-Month Default Probability**: **`0.33%`** [NOMINAL RISK]
- **12-Month Prepayment Probability**: **`10.77%`** [STABLE DURATION]
- **3-Month Delinquency Migration**: **`0.53%`** | **6-Month Delinquency Migration**: **`1.07%`**
- **Projected Next Monthly State**: **`CURRENT`**

---

#### 3. Root Cause Feature Attribution (TreeSHAP Drivers)
The predictive models and anomaly detectors isolated the following primary risk drivers:
1. **`age_x_rate`**: Standard credit attribute 'age_x_rate'.
2. **`loan_age_months`**: Standard credit attribute 'loan_age_months'.
3. **`dti_ord`**: Standard credit attribute 'dti_ord'.

---

#### 4. Data Quality & Rule Reconciliation Findings
- **Rule Breach Triggered**: `VR-001_BALANCE_SURGE_170PCT (+0.231)`
- **Operational Analysis**:
  * Severe data inconsistency detected (BALANCE_INCONSISTENCY). Balance and status fields violate fundamental accounting invariants (VR-001_BALANCE_SURGE_170PCT (+0.231)). Immediate manual re-indexing required before tape submission.

---
*Authored by Intain AI Reviewer Copilot Engine v1.0*


---

### Loan Audit Review Memo: `F19Q10263130` (Reporting: 202111)

> **GOVERNANCE DISCLAIMER**: *This is an AI-generated synthesis recommendation for decision support. Human auditor review and formal sign-off are required prior to executing account-level interventions.*

---

#### 1. Executive Summary & Recommended Action
- **Recommended Action**: **`MANUAL_AUDIT`** (Confidence: **0.93**)
- **Composite Anomaly Score**: `0.6131` | **Primary Exception**: `BALANCE_INCONSISTENCY`
- **Evidence Breakdown**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.412` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `1.000` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Account Snapshot**: Balance **$292,576.45** ($217,000.00 Orig) | Status: **PREPAID** (0 DPD) | Servicer: **Newrez LLC**
- **Borrower Profile**: Credit **681-740 (Good)** | LTV **81-90%** | DTI **21-30%** | Docs: **VERIFIED**

---

#### 2. Multi-Horizon Credit & Yield Risk Forecast
- **12-Month Default Probability**: **`0.33%`** [NOMINAL RISK]
- **12-Month Prepayment Probability**: **`71.93%`** [ACCELERATED PREPAYMENT]
- **3-Month Delinquency Migration**: **`1.63%`** | **6-Month Delinquency Migration**: **`3.87%`**
- **Projected Next Monthly State**: **`PREPAID`**

---

#### 3. Root Cause Feature Attribution (TreeSHAP Drivers)
The predictive models and anomaly detectors isolated the following primary risk drivers:
1. **`age_x_rate`**: Standard credit attribute 'age_x_rate'.
2. **`status_severity`**: Standard credit attribute 'status_severity'.
3. **`loan_age_months`**: Standard credit attribute 'loan_age_months'.

---

#### 4. Data Quality & Rule Reconciliation Findings
- **Rule Breach Triggered**: `VR-001_BALANCE_SURGE_135PCT (+0.463)`
- **Operational Analysis**:
  * Severe data inconsistency detected (BALANCE_INCONSISTENCY). Balance and status fields violate fundamental accounting invariants (VR-001_BALANCE_SURGE_135PCT (+0.463)). Immediate manual re-indexing required before tape submission.

---
*Authored by Intain AI Reviewer Copilot Engine v1.0*


---

### Loan Audit Review Memo: `F19Q10012800` (Reporting: 202209)

> **GOVERNANCE DISCLAIMER**: *This is an AI-generated synthesis recommendation for decision support. Human auditor review and formal sign-off are required prior to executing account-level interventions.*

---

#### 1. Executive Summary & Recommended Action
- **Recommended Action**: **`MANUAL_AUDIT`** (Confidence: **0.9**)
- **Composite Anomaly Score**: `0.3510` | **Primary Exception**: `BALANCE_INCONSISTENCY`
- **Evidence Breakdown**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.328` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.500` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Account Snapshot**: Balance **$299,416.58** ($204,000.00 Orig) | Status: **CURRENT** (0 DPD) | Servicer: **Rocket Mortgage, LLC**
- **Borrower Profile**: Credit **681-740 (Good)** | LTV **91-95%** | DTI **31-40%** | Docs: **VERIFIED**

---

#### 2. Multi-Horizon Credit & Yield Risk Forecast
- **12-Month Default Probability**: **`0.33%`** [NOMINAL RISK]
- **12-Month Prepayment Probability**: **`14.27%`** [STABLE DURATION]
- **3-Month Delinquency Migration**: **`1.30%`** | **6-Month Delinquency Migration**: **`1.52%`**
- **Projected Next Monthly State**: **`CURRENT`**

---

#### 3. Root Cause Feature Attribution (TreeSHAP Drivers)
The predictive models and anomaly detectors isolated the following primary risk drivers:
1. **`age_x_rate`**: Standard credit attribute 'age_x_rate'.
2. **`loan_age_months`**: Standard credit attribute 'loan_age_months'.
3. **`ltv_ord`**: Standard credit attribute 'ltv_ord'.

---

#### 4. Data Quality & Rule Reconciliation Findings
- **Rule Breach Triggered**: `VR-001_BALANCE_SURGE_147PCT (+0.231)`
- **Operational Analysis**:
  * Severe data inconsistency detected (BALANCE_INCONSISTENCY). Balance and status fields violate fundamental accounting invariants (VR-001_BALANCE_SURGE_147PCT (+0.231)). Immediate manual re-indexing required before tape submission.

---
*Authored by Intain AI Reviewer Copilot Engine v1.0*


---

### Loan Audit Review Memo: `F19Q20248240` (Reporting: 202110)

> **GOVERNANCE DISCLAIMER**: *This is an AI-generated synthesis recommendation for decision support. Human auditor review and formal sign-off are required prior to executing account-level interventions.*

---

#### 1. Executive Summary & Recommended Action
- **Recommended Action**: **`ESCALATE_DOC_REVIEW`** (Confidence: **0.95**)
- **Composite Anomaly Score**: `0.2488` | **Primary Exception**: `DOCUMENT_GAP`
- **Evidence Breakdown**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.429` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.200` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Account Snapshot**: Balance **$48,300.00** ($53,000.00 Orig) | Status: **CURRENT** (0 DPD) | Servicer: **Rocket Mortgage, LLC**
- **Borrower Profile**: Credit **741-800 (Very Good)** | LTV **61-75%** | DTI **<=20%** | Docs: **UNVERIFIED_APPRAISAL**

---

#### 2. Multi-Horizon Credit & Yield Risk Forecast
- **12-Month Default Probability**: **`0.23%`** [NOMINAL RISK]
- **12-Month Prepayment Probability**: **`11.20%`** [STABLE DURATION]
- **3-Month Delinquency Migration**: **`0.76%`** | **6-Month Delinquency Migration**: **`1.79%`**
- **Projected Next Monthly State**: **`CURRENT`**

---

#### 3. Root Cause Feature Attribution (TreeSHAP Drivers)
The predictive models and anomaly detectors isolated the following primary risk drivers:
1. **`servicer_name_enc`**: Standard credit attribute 'servicer_name_enc'.
2. **`rate_spread_to_market`**: Standard credit attribute 'rate_spread_to_market'.
3. **`prepayment_incentive`**: Standard credit attribute 'prepayment_incentive'.

---

#### 4. Data Quality & Rule Reconciliation Findings
- **Rule Breach Triggered**: `ISOLATION_FOREST_OUTLIER (+0.156)`
- **Operational Analysis**:
  * Document status is marked as 'UNVERIFIED_APPRAISAL'. Servicer trailing document checklist missing critical verification notes (ISOLATION_FOREST_OUTLIER (+0.156)). Escalate to post-closing compliance team for cure within 30 days.

---
*Authored by Intain AI Reviewer Copilot Engine v1.0*


---

### Loan Audit Review Memo: `F19Q10074482` (Reporting: 202305)

> **GOVERNANCE DISCLAIMER**: *This is an AI-generated synthesis recommendation for decision support. Human auditor review and formal sign-off are required prior to executing account-level interventions.*

---

#### 1. Executive Summary & Recommended Action
- **Recommended Action**: **`ESCALATE_DOC_REVIEW`** (Confidence: **0.95**)
- **Composite Anomaly Score**: `0.2571` | **Primary Exception**: `DOCUMENT_GAP`
- **Evidence Breakdown**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.452` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.200` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Account Snapshot**: Balance **$129,652.40** ($186,000.00 Orig) | Status: **CURRENT** (0 DPD) | Servicer: **Pennymac Loan Services, LLC**
- **Borrower Profile**: Credit **741-800 (Very Good)** | LTV **81-90%** | DTI **21-30%** | Docs: **MISSING_NOTE**

---

#### 2. Multi-Horizon Credit & Yield Risk Forecast
- **12-Month Default Probability**: **`0.00%`** [NOMINAL RISK]
- **12-Month Prepayment Probability**: **`22.54%`** [STABLE DURATION]
- **3-Month Delinquency Migration**: **`1.63%`** | **6-Month Delinquency Migration**: **`1.07%`**
- **Projected Next Monthly State**: **`CURRENT`**

---

#### 3. Root Cause Feature Attribution (TreeSHAP Drivers)
The predictive models and anomaly detectors isolated the following primary risk drivers:
1. **`ltv_ord`**: Standard credit attribute 'ltv_ord'.
2. **`loan_purpose_enc`**: Standard credit attribute 'loan_purpose_enc'.
3. **`age_x_rate`**: Standard credit attribute 'age_x_rate'.

---

#### 4. Data Quality & Rule Reconciliation Findings
- **Rule Breach Triggered**: `ISOLATION_FOREST_OUTLIER (+0.165)`
- **Operational Analysis**:
  * Document status is marked as 'MISSING_NOTE'. Servicer trailing document checklist missing critical verification notes (ISOLATION_FOREST_OUTLIER (+0.165)). Escalate to post-closing compliance team for cure within 30 days.

---
*Authored by Intain AI Reviewer Copilot Engine v1.0*


---

### Loan Audit Review Memo: `F19Q20163537` (Reporting: 202108)

> **GOVERNANCE DISCLAIMER**: *This is an AI-generated synthesis recommendation for decision support. Human auditor review and formal sign-off are required prior to executing account-level interventions.*

---

#### 1. Executive Summary & Recommended Action
- **Recommended Action**: **`ESCALATE_DOC_REVIEW`** (Confidence: **0.95**)
- **Composite Anomaly Score**: `0.2051` | **Primary Exception**: `DOCUMENT_GAP`
- **Evidence Breakdown**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.288` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.200` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.200`
- **Account Snapshot**: Balance **$144,500.02** ($150,000.00 Orig) | Status: **CURRENT** (0 DPD) | Servicer: **Newrez LLC**
- **Borrower Profile**: Credit **741-800 (Very Good)** | LTV **61-75%** | DTI **<=20%** | Docs: **MISSING_NOTE**

---

#### 2. Multi-Horizon Credit & Yield Risk Forecast
- **12-Month Default Probability**: **`0.00%`** [NOMINAL RISK]
- **12-Month Prepayment Probability**: **`25.98%`** [STABLE DURATION]
- **3-Month Delinquency Migration**: **`0.76%`** | **6-Month Delinquency Migration**: **`0.68%`**
- **Projected Next Monthly State**: **`CURRENT`**

---

#### 3. Root Cause Feature Attribution (TreeSHAP Drivers)
The predictive models and anomaly detectors isolated the following primary risk drivers:
1. **`ltv_ord`**: Standard credit attribute 'ltv_ord'.
2. **`original_balance`**: Standard credit attribute 'original_balance'.
3. **`occupancy_type_enc`**: Standard credit attribute 'occupancy_type_enc'.

---

#### 4. Data Quality & Rule Reconciliation Findings
- **Rule Breach Triggered**: `ISOLATION_FOREST_OUTLIER (+0.105)`
- **Operational Analysis**:
  * Document status is marked as 'MISSING_NOTE'. Servicer trailing document checklist missing critical verification notes (ISOLATION_FOREST_OUTLIER (+0.105)). Escalate to post-closing compliance team for cure within 30 days.

---
*Authored by Intain AI Reviewer Copilot Engine v1.0*


---

### Loan Audit Review Memo: `F19Q10179663` (Reporting: 202204)

> **GOVERNANCE DISCLAIMER**: *This is an AI-generated synthesis recommendation for decision support. Human auditor review and formal sign-off are required prior to executing account-level interventions.*

---

#### 1. Executive Summary & Recommended Action
- **Recommended Action**: **`ESCALATE_DOC_REVIEW`** (Confidence: **0.95**)
- **Composite Anomaly Score**: `0.2313` | **Primary Exception**: `DOCUMENT_GAP`
- **Evidence Breakdown**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.381` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.200` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Account Snapshot**: Balance **$139,830.31** ($147,000.00 Orig) | Status: **CURRENT** (0 DPD) | Servicer: **Freedom Mortgage Corporation**
- **Borrower Profile**: Credit **741-800 (Very Good)** | LTV **91-95%** | DTI **41-45%** | Docs: **UNVERIFIED_APPRAISAL**

---

#### 2. Multi-Horizon Credit & Yield Risk Forecast
- **12-Month Default Probability**: **`0.00%`** [NOMINAL RISK]
- **12-Month Prepayment Probability**: **`45.09%`** [ACCELERATED PREPAYMENT]
- **3-Month Delinquency Migration**: **`0.97%`** | **6-Month Delinquency Migration**: **`0.60%`**
- **Projected Next Monthly State**: **`CURRENT`**

---

#### 3. Root Cause Feature Attribution (TreeSHAP Drivers)
The predictive models and anomaly detectors isolated the following primary risk drivers:
1. **`ltv_ord`**: Standard credit attribute 'ltv_ord'.
2. **`occupancy_type_enc`**: Standard credit attribute 'occupancy_type_enc'.
3. **`high_risk_combo`**: Standard credit attribute 'high_risk_combo'.

---

#### 4. Data Quality & Rule Reconciliation Findings
- **Rule Breach Triggered**: `ISOLATION_FOREST_OUTLIER (+0.139)`
- **Operational Analysis**:
  * Document status is marked as 'UNVERIFIED_APPRAISAL'. Servicer trailing document checklist missing critical verification notes (ISOLATION_FOREST_OUTLIER (+0.139)). Escalate to post-closing compliance team for cure within 30 days.

---
*Authored by Intain AI Reviewer Copilot Engine v1.0*


---

### Loan Audit Review Memo: `F19Q20231698` (Reporting: 202301)

> **GOVERNANCE DISCLAIMER**: *This is an AI-generated synthesis recommendation for decision support. Human auditor review and formal sign-off are required prior to executing account-level interventions.*

---

#### 1. Executive Summary & Recommended Action
- **Recommended Action**: **`OVERRIDE_SERVICER`** (Confidence: **0.98**)
- **Composite Anomaly Score**: `0.3551` | **Primary Exception**: `NONE`
- **Evidence Breakdown**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.604` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.000` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `1.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Account Snapshot**: Balance **$71,668.27** ($76,000.00 Orig) | Status: **30DPD** (30 DPD) | Servicer: **Newrez LLC**
- **Borrower Profile**: Credit **681-740 (Good)** | LTV **91-95%** | DTI **41-45%** | Docs: **VERIFIED**

---

#### 2. Multi-Horizon Credit & Yield Risk Forecast
- **12-Month Default Probability**: **`0.33%`** [NOMINAL RISK]
- **12-Month Prepayment Probability**: **`8.83%`** [STABLE DURATION]
- **3-Month Delinquency Migration**: **`71.43%`** | **6-Month Delinquency Migration**: **`81.39%`**
- **Projected Next Monthly State**: **`CURRENT`**

---

#### 3. Root Cause Feature Attribution (TreeSHAP Drivers)
The predictive models and anomaly detectors isolated the following primary risk drivers:
1. **`age_x_rate`**: Standard credit attribute 'age_x_rate'.
2. **`loan_age_months`**: Standard credit attribute 'loan_age_months'.
3. **`rate_spread_to_market`**: Standard credit attribute 'rate_spread_to_market'.

---

#### 4. Data Quality & Rule Reconciliation Findings
- **Rule Breach Triggered**: `ISOLATION_FOREST_OUTLIER (+0.220)`
- **Operational Analysis**:
  * Cross-feed reconciliation identified material discrepancies between master servicing portal and primary system feed (ISOLATION_FOREST_OUTLIER (+0.220)). Override secondary servicer records and enforce primary tape authority.

---
*Authored by Intain AI Reviewer Copilot Engine v1.0*


---

### Loan Audit Review Memo: `F19Q10030227` (Reporting: 202206)

> **GOVERNANCE DISCLAIMER**: *This is an AI-generated synthesis recommendation for decision support. Human auditor review and formal sign-off are required prior to executing account-level interventions.*

---

#### 1. Executive Summary & Recommended Action
- **Recommended Action**: **`OVERRIDE_SERVICER`** (Confidence: **0.8**)
- **Composite Anomaly Score**: `0.3165` | **Primary Exception**: `SERVICER_CONFLICT`
- **Evidence Breakdown**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.424` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.350` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Account Snapshot**: Balance **$90,041.87** ($94,000.00 Orig) | Status: **CURRENT** (0 DPD) | Servicer: **JPMorgan Chase Bank, N.A.**
- **Borrower Profile**: Credit **681-740 (Good)** | LTV **76-80%** | DTI **31-40%** | Docs: **VERIFIED**

---

#### 2. Multi-Horizon Credit & Yield Risk Forecast
- **12-Month Default Probability**: **`0.23%`** [NOMINAL RISK]
- **12-Month Prepayment Probability**: **`29.24%`** [STABLE DURATION]
- **3-Month Delinquency Migration**: **`0.53%`** | **6-Month Delinquency Migration**: **`1.07%`**
- **Projected Next Monthly State**: **`CURRENT`**

---

#### 3. Root Cause Feature Attribution (TreeSHAP Drivers)
The predictive models and anomaly detectors isolated the following primary risk drivers:
1. **`age_x_rate`**: Standard credit attribute 'age_x_rate'.
2. **`loan_age_months`**: Standard credit attribute 'loan_age_months'.
3. **`rate_spread_to_market`**: Standard credit attribute 'rate_spread_to_market'.

---

#### 4. Data Quality & Rule Reconciliation Findings
- **Rule Breach Triggered**: `VR-007_SERVICER_BALANCE_DIFF_7PCT (+0.162)`
- **Operational Analysis**:
  * Cross-feed reconciliation identified material discrepancies between master servicing portal and primary system feed (VR-007_SERVICER_BALANCE_DIFF_7PCT (+0.162)). Override secondary servicer records and enforce primary tape authority.

---
*Authored by Intain AI Reviewer Copilot Engine v1.0*


---

### Loan Audit Review Memo: `F19Q10085204` (Reporting: 202107)

> **GOVERNANCE DISCLAIMER**: *This is an AI-generated synthesis recommendation for decision support. Human auditor review and formal sign-off are required prior to executing account-level interventions.*

---

#### 1. Executive Summary & Recommended Action
- **Recommended Action**: **`OVERRIDE_SERVICER`** (Confidence: **0.8**)
- **Composite Anomaly Score**: `0.2841` | **Primary Exception**: `SERVICER_CONFLICT`
- **Evidence Breakdown**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.335` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.350` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Account Snapshot**: Balance **$126,231.47** ($132,000.00 Orig) | Status: **CURRENT** (0 DPD) | Servicer: **Freedom Mortgage Corporation**
- **Borrower Profile**: Credit **741-800 (Very Good)** | LTV **91-95%** | DTI **41-45%** | Docs: **VERIFIED**

---

#### 2. Multi-Horizon Credit & Yield Risk Forecast
- **12-Month Default Probability**: **`0.00%`** [NOMINAL RISK]
- **12-Month Prepayment Probability**: **`16.67%`** [STABLE DURATION]
- **3-Month Delinquency Migration**: **`1.30%`** | **6-Month Delinquency Migration**: **`8.65%`**
- **Projected Next Monthly State**: **`CURRENT`**

---

#### 3. Root Cause Feature Attribution (TreeSHAP Drivers)
The predictive models and anomaly detectors isolated the following primary risk drivers:
1. **`occupancy_type_enc`**: Standard credit attribute 'occupancy_type_enc'.
2. **`high_risk_combo`**: Standard credit attribute 'high_risk_combo'.
3. **`dpd_change_1m`**: Standard credit attribute 'dpd_change_1m'.

---

#### 4. Data Quality & Rule Reconciliation Findings
- **Rule Breach Triggered**: `VR-007_SERVICER_BALANCE_DIFF_11PCT (+0.162)`
- **Operational Analysis**:
  * Cross-feed reconciliation identified material discrepancies between master servicing portal and primary system feed (VR-007_SERVICER_BALANCE_DIFF_11PCT (+0.162)). Override secondary servicer records and enforce primary tape authority.

---
*Authored by Intain AI Reviewer Copilot Engine v1.0*


---

### Loan Audit Review Memo: `F19Q10191279` (Reporting: 202510)

> **GOVERNANCE DISCLAIMER**: *This is an AI-generated synthesis recommendation for decision support. Human auditor review and formal sign-off are required prior to executing account-level interventions.*

---

#### 1. Executive Summary & Recommended Action
- **Recommended Action**: **`OVERRIDE_SERVICER`** (Confidence: **0.8**)
- **Composite Anomaly Score**: `0.2750` | **Primary Exception**: `SERVICER_CONFLICT`
- **Evidence Breakdown**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.310` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.350` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Account Snapshot**: Balance **$161,443.37** ($184,000.00 Orig) | Status: **CURRENT** (0 DPD) | Servicer: **Newrez LLC**
- **Borrower Profile**: Credit **741-800 (Very Good)** | LTV **76-80%** | DTI **41-45%** | Docs: **VERIFIED**

---

#### 2. Multi-Horizon Credit & Yield Risk Forecast
- **12-Month Default Probability**: **`0.33%`** [NOMINAL RISK]
- **12-Month Prepayment Probability**: **`29.24%`** [STABLE DURATION]
- **3-Month Delinquency Migration**: **`1.30%`** | **6-Month Delinquency Migration**: **`1.79%`**
- **Projected Next Monthly State**: **`CURRENT`**

---

#### 3. Root Cause Feature Attribution (TreeSHAP Drivers)
The predictive models and anomaly detectors isolated the following primary risk drivers:
1. **`ever_delinquent`**: Standard credit attribute 'ever_delinquent'.
2. **`interest_rate`**: Standard credit attribute 'interest_rate'.
3. **`dti_x_ltv`**: Standard credit attribute 'dti_x_ltv'.

---

#### 4. Data Quality & Rule Reconciliation Findings
- **Rule Breach Triggered**: `VR-007_SERVICER_BALANCE_DIFF_11PCT (+0.162)`
- **Operational Analysis**:
  * Cross-feed reconciliation identified material discrepancies between master servicing portal and primary system feed (VR-007_SERVICER_BALANCE_DIFF_11PCT (+0.162)). Override secondary servicer records and enforce primary tape authority.

---
*Authored by Intain AI Reviewer Copilot Engine v1.0*


---

### Loan Audit Review Memo: `F19Q10197279` (Reporting: 202304)

> **GOVERNANCE DISCLAIMER**: *This is an AI-generated synthesis recommendation for decision support. Human auditor review and formal sign-off are required prior to executing account-level interventions.*

---

#### 1. Executive Summary & Recommended Action
- **Recommended Action**: **`REQUEST_CURE`** (Confidence: **0.98**)
- **Composite Anomaly Score**: `0.3797` | **Primary Exception**: `STATUS_CONFLICT`
- **Evidence Breakdown**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.598` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.350` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Account Snapshot**: Balance **$197,831.23** ($220,000.00 Orig) | Status: **CURRENT** (90 DPD) | Servicer: **Rocket Mortgage, LLC**
- **Borrower Profile**: Credit **741-800 (Very Good)** | LTV **<=60%** | DTI **21-30%** | Docs: **VERIFIED**

---

#### 2. Multi-Horizon Credit & Yield Risk Forecast
- **12-Month Default Probability**: **`0.23%`** [NOMINAL RISK]
- **12-Month Prepayment Probability**: **`15.60%`** [STABLE DURATION]
- **3-Month Delinquency Migration**: **`10.93%`** | **6-Month Delinquency Migration**: **`1.79%`**
- **Projected Next Monthly State**: **`CURRENT`**

---

#### 3. Root Cause Feature Attribution (TreeSHAP Drivers)
The predictive models and anomaly detectors isolated the following primary risk drivers:
1. **`maturity_pressure`**: Standard credit attribute 'maturity_pressure'.
2. **`age_x_rate`**: Standard credit attribute 'age_x_rate'.
3. **`distress_score`**: Standard credit attribute 'distress_score'.

---

#### 4. Data Quality & Rule Reconciliation Findings
- **Rule Breach Triggered**: `ISOLATION_FOREST_OUTLIER (+0.218)`
- **Operational Analysis**:
  * Non-critical data gap or term anomaly identified (STATUS_CONFLICT). Issue formal Request for Cure to Rocket Mortgage, LLC.

---
*Authored by Intain AI Reviewer Copilot Engine v1.0*


---

### Loan Audit Review Memo: `F19Q20011371` (Reporting: 202207)

> **GOVERNANCE DISCLAIMER**: *This is an AI-generated synthesis recommendation for decision support. Human auditor review and formal sign-off are required prior to executing account-level interventions.*

---

#### 1. Executive Summary & Recommended Action
- **Recommended Action**: **`REQUEST_CURE`** (Confidence: **0.98**)
- **Composite Anomaly Score**: `0.3869` | **Primary Exception**: `STATUS_CONFLICT`
- **Evidence Breakdown**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.618` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.350` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Account Snapshot**: Balance **$60,319.69** ($64,000.00 Orig) | Status: **CURRENT** (90 DPD) | Servicer: **Freedom Mortgage Corporation**
- **Borrower Profile**: Credit **801+ (Exceptional)** | LTV **76-80%** | DTI **46-50%** | Docs: **VERIFIED**

---

#### 2. Multi-Horizon Credit & Yield Risk Forecast
- **12-Month Default Probability**: **`0.23%`** [NOMINAL RISK]
- **12-Month Prepayment Probability**: **`14.27%`** [STABLE DURATION]
- **3-Month Delinquency Migration**: **`7.60%`** | **6-Month Delinquency Migration**: **`1.79%`**
- **Projected Next Monthly State**: **`CURRENT`**

---

#### 3. Root Cause Feature Attribution (TreeSHAP Drivers)
The predictive models and anomaly detectors isolated the following primary risk drivers:
1. **`maturity_pressure`**: Standard credit attribute 'maturity_pressure'.
2. **`age_x_rate`**: Standard credit attribute 'age_x_rate'.
3. **`credit_score_ord`**: Standard credit attribute 'credit_score_ord'.

---

#### 4. Data Quality & Rule Reconciliation Findings
- **Rule Breach Triggered**: `ISOLATION_FOREST_OUTLIER (+0.225)`
- **Operational Analysis**:
  * Non-critical data gap or term anomaly identified (STATUS_CONFLICT). Issue formal Request for Cure to Freedom Mortgage Corporation.

---
*Authored by Intain AI Reviewer Copilot Engine v1.0*


---

### Loan Audit Review Memo: `F19Q10270599` (Reporting: 202207)

> **GOVERNANCE DISCLAIMER**: *This is an AI-generated synthesis recommendation for decision support. Human auditor review and formal sign-off are required prior to executing account-level interventions.*

---

#### 1. Executive Summary & Recommended Action
- **Recommended Action**: **`REQUEST_CURE`** (Confidence: **0.98**)
- **Composite Anomaly Score**: `0.3851` | **Primary Exception**: `STATUS_CONFLICT`
- **Evidence Breakdown**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.592` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.350` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.200`
- **Account Snapshot**: Balance **$86,010.80** ($109,000.00 Orig) | Status: **CURRENT** (90 DPD) | Servicer: **Rocket Mortgage, LLC**
- **Borrower Profile**: Credit **801+ (Exceptional)** | LTV **61-75%** | DTI **31-40%** | Docs: **VERIFIED**

---

#### 2. Multi-Horizon Credit & Yield Risk Forecast
- **12-Month Default Probability**: **`0.23%`** [NOMINAL RISK]
- **12-Month Prepayment Probability**: **`73.35%`** [ACCELERATED PREPAYMENT]
- **3-Month Delinquency Migration**: **`46.88%`** | **6-Month Delinquency Migration**: **`65.38%`**
- **Projected Next Monthly State**: **`CURRENT`**

---

#### 3. Root Cause Feature Attribution (TreeSHAP Drivers)
The predictive models and anomaly detectors isolated the following primary risk drivers:
1. **`age_x_rate`**: Standard credit attribute 'age_x_rate'.
2. **`maturity_pressure`**: Standard credit attribute 'maturity_pressure'.
3. **`loan_age_months`**: Standard credit attribute 'loan_age_months'.

---

#### 4. Data Quality & Rule Reconciliation Findings
- **Rule Breach Triggered**: `ISOLATION_FOREST_OUTLIER (+0.215)`
- **Operational Analysis**:
  * Non-critical data gap or term anomaly identified (STATUS_CONFLICT). Issue formal Request for Cure to Rocket Mortgage, LLC.

---
*Authored by Intain AI Reviewer Copilot Engine v1.0*


---

### Loan Audit Review Memo: `F19Q20222909` (Reporting: 202209)

> **GOVERNANCE DISCLAIMER**: *This is an AI-generated synthesis recommendation for decision support. Human auditor review and formal sign-off are required prior to executing account-level interventions.*

---

#### 1. Executive Summary & Recommended Action
- **Recommended Action**: **`REQUEST_CURE`** (Confidence: **0.8**)
- **Composite Anomaly Score**: `0.3106` | **Primary Exception**: `INVALID_TERM`
- **Evidence Breakdown**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.408` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.350` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Account Snapshot**: Balance **$221,116.78** ($235,000.00 Orig) | Status: **CURRENT** (0 DPD) | Servicer: **Freedom Mortgage Corporation**
- **Borrower Profile**: Credit **801+ (Exceptional)** | LTV **61-75%** | DTI **41-45%** | Docs: **VERIFIED**

---

#### 2. Multi-Horizon Credit & Yield Risk Forecast
- **12-Month Default Probability**: **`0.33%`** [NOMINAL RISK]
- **12-Month Prepayment Probability**: **`23.87%`** [STABLE DURATION]
- **3-Month Delinquency Migration**: **`1.30%`** | **6-Month Delinquency Migration**: **`1.79%`**
- **Projected Next Monthly State**: **`CURRENT`**

---

#### 3. Root Cause Feature Attribution (TreeSHAP Drivers)
The predictive models and anomaly detectors isolated the following primary risk drivers:
1. **`age_x_rate`**: Standard credit attribute 'age_x_rate'.
2. **`loan_age_months`**: Standard credit attribute 'loan_age_months'.
3. **`credit_score_ord`**: Standard credit attribute 'credit_score_ord'.

---

#### 4. Data Quality & Rule Reconciliation Findings
- **Rule Breach Triggered**: `VR-004_INVALID_TERM_450M (+0.162)`
- **Operational Analysis**:
  * Non-critical data gap or term anomaly identified (INVALID_TERM). Issue formal Request for Cure to Freedom Mortgage Corporation.

---
*Authored by Intain AI Reviewer Copilot Engine v1.0*


---

### Loan Audit Review Memo: `F19Q10146837` (Reporting: 202212)

> **GOVERNANCE DISCLAIMER**: *This is an AI-generated synthesis recommendation for decision support. Human auditor review and formal sign-off are required prior to executing account-level interventions.*

---

#### 1. Executive Summary & Recommended Action
- **Recommended Action**: **`ACCEPT_PRIMARY`** (Confidence: **0.95**)
- **Composite Anomaly Score**: `0.3228` | **Primary Exception**: `STALE_RECORD`
- **Evidence Breakdown**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.632` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.200` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Account Snapshot**: Balance **$163,808.45** ($172,000.00 Orig) | Status: **30DPD** (30 DPD) | Servicer: **Rocket Mortgage, LLC**
- **Borrower Profile**: Credit **621-680 (Fair)** | LTV **81-90%** | DTI **41-45%** | Docs: **VERIFIED**

---

#### 2. Multi-Horizon Credit & Yield Risk Forecast
- **12-Month Default Probability**: **`0.23%`** [NOMINAL RISK]
- **12-Month Prepayment Probability**: **`10.77%`** [STABLE DURATION]
- **3-Month Delinquency Migration**: **`15.87%`** | **6-Month Delinquency Migration**: **`66.34%`**
- **Projected Next Monthly State**: **`30DPD`**

---

#### 3. Root Cause Feature Attribution (TreeSHAP Drivers)
The predictive models and anomaly detectors isolated the following primary risk drivers:
1. **`age_x_rate`**: Standard credit attribute 'age_x_rate'.
2. **`loan_age_months`**: Standard credit attribute 'loan_age_months'.
3. **`rate_spread_to_market`**: Standard credit attribute 'rate_spread_to_market'.

---

#### 4. Data Quality & Rule Reconciliation Findings
- **Rule Breach Triggered**: `ISOLATION_FOREST_OUTLIER (+0.230)`
- **Operational Analysis**:
  * Minor timing variance detected. Primary servicing record confirmed valid. Clear exception with standard acceptance code.

---
*Authored by Intain AI Reviewer Copilot Engine v1.0*


---

### Loan Audit Review Memo: `F19Q20159826` (Reporting: 202109)

> **GOVERNANCE DISCLAIMER**: *This is an AI-generated synthesis recommendation for decision support. Human auditor review and formal sign-off are required prior to executing account-level interventions.*

---

#### 1. Executive Summary & Recommended Action
- **Recommended Action**: **`ACCEPT_PRIMARY`** (Confidence: **0.95**)
- **Composite Anomaly Score**: `0.1871` | **Primary Exception**: `STALE_RECORD`
- **Evidence Breakdown**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.260` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.200` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Account Snapshot**: Balance **$114,537.16** ($122,000.00 Orig) | Status: **CURRENT** (0 DPD) | Servicer: **Nationstar Mortgage LLC (Mr. Cooper)**
- **Borrower Profile**: Credit **621-680 (Fair)** | LTV **91-95%** | DTI **31-40%** | Docs: **VERIFIED**

---

#### 2. Multi-Horizon Credit & Yield Risk Forecast
- **12-Month Default Probability**: **`0.33%`** [NOMINAL RISK]
- **12-Month Prepayment Probability**: **`12.09%`** [STABLE DURATION]
- **3-Month Delinquency Migration**: **`1.63%`** | **6-Month Delinquency Migration**: **`1.73%`**
- **Projected Next Monthly State**: **`CURRENT`**

---

#### 3. Root Cause Feature Attribution (TreeSHAP Drivers)
The predictive models and anomaly detectors isolated the following primary risk drivers:
1. **`credit_score_ord`**: Standard credit attribute 'credit_score_ord'.
2. **`creditworthiness_net`**: Standard credit attribute 'creditworthiness_net'.
3. **`property_type_enc`**: Standard credit attribute 'property_type_enc'.

---

#### 4. Data Quality & Rule Reconciliation Findings
- **Rule Breach Triggered**: `ISOLATION_FOREST_OUTLIER (+0.095)`
- **Operational Analysis**:
  * Minor timing variance detected. Primary servicing record confirmed valid. Clear exception with standard acceptance code.

---
*Authored by Intain AI Reviewer Copilot Engine v1.0*


---

### Loan Audit Review Memo: `F19Q20113064` (Reporting: 202110)

> **GOVERNANCE DISCLAIMER**: *This is an AI-generated synthesis recommendation for decision support. Human auditor review and formal sign-off are required prior to executing account-level interventions.*

---

#### 1. Executive Summary & Recommended Action
- **Recommended Action**: **`ACCEPT_PRIMARY`** (Confidence: **0.95**)
- **Composite Anomaly Score**: `0.1920` | **Primary Exception**: `STALE_RECORD`
- **Evidence Breakdown**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.273` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.200` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Account Snapshot**: Balance **$196,125.80** ($205,000.00 Orig) | Status: **CURRENT** (0 DPD) | Servicer: **Pennymac Loan Services, LLC**
- **Borrower Profile**: Credit **741-800 (Very Good)** | LTV **61-75%** | DTI **46-50%** | Docs: **VERIFIED**

---

#### 2. Multi-Horizon Credit & Yield Risk Forecast
- **12-Month Default Probability**: **`0.33%`** [NOMINAL RISK]
- **12-Month Prepayment Probability**: **`45.09%`** [ACCELERATED PREPAYMENT]
- **3-Month Delinquency Migration**: **`1.30%`** | **6-Month Delinquency Migration**: **`1.77%`**
- **Projected Next Monthly State**: **`CURRENT`**

---

#### 3. Root Cause Feature Attribution (TreeSHAP Drivers)
The predictive models and anomaly detectors isolated the following primary risk drivers:
1. **`creditworthiness_net`**: Standard credit attribute 'creditworthiness_net'.
2. **`dpd_change_1m`**: Standard credit attribute 'dpd_change_1m'.
3. **`high_risk_combo`**: Standard credit attribute 'high_risk_combo'.

---

#### 4. Data Quality & Rule Reconciliation Findings
- **Rule Breach Triggered**: `ISOLATION_FOREST_OUTLIER (+0.099)`
- **Operational Analysis**:
  * Minor timing variance detected. Primary servicing record confirmed valid. Clear exception with standard acceptance code.

---
*Authored by Intain AI Reviewer Copilot Engine v1.0*


---

### Loan Audit Review Memo: `F19Q10028250` (Reporting: 202208)

> **GOVERNANCE DISCLAIMER**: *This is an AI-generated synthesis recommendation for decision support. Human auditor review and formal sign-off are required prior to executing account-level interventions.*

---

#### 1. Executive Summary & Recommended Action
- **Recommended Action**: **`ACCEPT_PRIMARY`** (Confidence: **0.95**)
- **Composite Anomaly Score**: `0.2480` | **Primary Exception**: `STALE_RECORD`
- **Evidence Breakdown**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.427` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.200` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Account Snapshot**: Balance **$62,949.31** ($68,000.00 Orig) | Status: **CURRENT** (0 DPD) | Servicer: **Rocket Mortgage, LLC**
- **Borrower Profile**: Credit **681-740 (Good)** | LTV **81-90%** | DTI **<=20%** | Docs: **VERIFIED**

---

#### 2. Multi-Horizon Credit & Yield Risk Forecast
- **12-Month Default Probability**: **`0.00%`** [NOMINAL RISK]
- **12-Month Prepayment Probability**: **`8.38%`** [STABLE DURATION]
- **3-Month Delinquency Migration**: **`1.30%`** | **6-Month Delinquency Migration**: **`1.77%`**
- **Projected Next Monthly State**: **`CURRENT`**

---

#### 3. Root Cause Feature Attribution (TreeSHAP Drivers)
The predictive models and anomaly detectors isolated the following primary risk drivers:
1. **`ltv_ord`**: Standard credit attribute 'ltv_ord'.
2. **`credit_score_ord`**: Standard credit attribute 'credit_score_ord'.
3. **`dpd_change_1m`**: Standard credit attribute 'dpd_change_1m'.

---

#### 4. Data Quality & Rule Reconciliation Findings
- **Rule Breach Triggered**: `ISOLATION_FOREST_OUTLIER (+0.155)`
- **Operational Analysis**:
  * Minor timing variance detected. Primary servicing record confirmed valid. Clear exception with standard acceptance code.

---
*Authored by Intain AI Reviewer Copilot Engine v1.0*


---

### Loan Audit Review Memo: `F19Q10196724` (Reporting: 202107)

> **GOVERNANCE DISCLAIMER**: *This is an AI-generated synthesis recommendation for decision support. Human auditor review and formal sign-off are required prior to executing account-level interventions.*

---

#### 1. Executive Summary & Recommended Action
- **Recommended Action**: **`AUTO_APPROVE`** (Confidence: **0.91**)
- **Composite Anomaly Score**: `0.1409` | **Primary Exception**: `NONE`
- **Evidence Breakdown**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.387` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.000` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Account Snapshot**: Balance **$257,924.24** ($273,000.00 Orig) | Status: **CURRENT** (0 DPD) | Servicer: **Pennymac Loan Services, LLC**
- **Borrower Profile**: Credit **741-800 (Very Good)** | LTV **91-95%** | DTI **<=20%** | Docs: **VERIFIED**

---

#### 2. Multi-Horizon Credit & Yield Risk Forecast
- **12-Month Default Probability**: **`0.33%`** [NOMINAL RISK]
- **12-Month Prepayment Probability**: **`9.79%`** [STABLE DURATION]
- **3-Month Delinquency Migration**: **`0.97%`** | **6-Month Delinquency Migration**: **`0.68%`**
- **Projected Next Monthly State**: **`CURRENT`**

---

#### 3. Root Cause Feature Attribution (TreeSHAP Drivers)
The predictive models and anomaly detectors isolated the following primary risk drivers:
1. **`balance_change_1m`**: Standard credit attribute 'balance_change_1m'.
2. **`current_balance`**: Standard credit attribute 'current_balance'.
3. **`loan_purpose_enc`**: Standard credit attribute 'loan_purpose_enc'.

---

#### 4. Data Quality & Rule Reconciliation Findings
- **Rule Breach Triggered**: `NORMAL_CONFORMING`
- **Operational Analysis**:
  * Clean record. Performing within normal underwriting parameters with composite anomaly score 0.1409 and zero critical rule breaches.

---
*Authored by Intain AI Reviewer Copilot Engine v1.0*


---

### Loan Audit Review Memo: `F19Q10018861` (Reporting: 202107)

> **GOVERNANCE DISCLAIMER**: *This is an AI-generated synthesis recommendation for decision support. Human auditor review and formal sign-off are required prior to executing account-level interventions.*

---

#### 1. Executive Summary & Recommended Action
- **Recommended Action**: **`AUTO_APPROVE`** (Confidence: **0.91**)
- **Composite Anomaly Score**: `0.1475` | **Primary Exception**: `NONE`
- **Evidence Breakdown**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.405` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.000` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Account Snapshot**: Balance **$169,355.46** ($176,000.00 Orig) | Status: **30DPD** (30 DPD) | Servicer: **Wells Fargo Bank, N.A.**
- **Borrower Profile**: Credit **741-800 (Very Good)** | LTV **91-95%** | DTI **31-40%** | Docs: **VERIFIED**

---

#### 2. Multi-Horizon Credit & Yield Risk Forecast
- **12-Month Default Probability**: **`0.33%`** [NOMINAL RISK]
- **12-Month Prepayment Probability**: **`73.35%`** [ACCELERATED PREPAYMENT]
- **3-Month Delinquency Migration**: **`75.16%`** | **6-Month Delinquency Migration**: **`81.39%`**
- **Projected Next Monthly State**: **`CURRENT`**

---

#### 3. Root Cause Feature Attribution (TreeSHAP Drivers)
The predictive models and anomaly detectors isolated the following primary risk drivers:
1. **`maturity_pressure`**: Standard credit attribute 'maturity_pressure'.
2. **`distress_score`**: Standard credit attribute 'distress_score'.
3. **`balance_ratio_change`**: Standard credit attribute 'balance_ratio_change'.

---

#### 4. Data Quality & Rule Reconciliation Findings
- **Rule Breach Triggered**: `NORMAL_CONFORMING`
- **Operational Analysis**:
  * Clean record. Performing within normal underwriting parameters with composite anomaly score 0.1475 and zero critical rule breaches.

---
*Authored by Intain AI Reviewer Copilot Engine v1.0*


---

### Loan Audit Review Memo: `F19Q20148057` (Reporting: 202107)

> **GOVERNANCE DISCLAIMER**: *This is an AI-generated synthesis recommendation for decision support. Human auditor review and formal sign-off are required prior to executing account-level interventions.*

---

#### 1. Executive Summary & Recommended Action
- **Recommended Action**: **`AUTO_APPROVE`** (Confidence: **0.95**)
- **Composite Anomaly Score**: `0.0692` | **Primary Exception**: `NONE`
- **Evidence Breakdown**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.190` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.000` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Account Snapshot**: Balance **$346,904.06** ($360,000.00 Orig) | Status: **CURRENT** (0 DPD) | Servicer: **Freedom Mortgage Corporation**
- **Borrower Profile**: Credit **741-800 (Very Good)** | LTV **61-75%** | DTI **21-30%** | Docs: **VERIFIED**

---

#### 2. Multi-Horizon Credit & Yield Risk Forecast
- **12-Month Default Probability**: **`0.23%`** [NOMINAL RISK]
- **12-Month Prepayment Probability**: **`85.17%`** [ACCELERATED PREPAYMENT]
- **3-Month Delinquency Migration**: **`1.63%`** | **6-Month Delinquency Migration**: **`3.87%`**
- **Projected Next Monthly State**: **`CURRENT`**

---

#### 3. Root Cause Feature Attribution (TreeSHAP Drivers)
The predictive models and anomaly detectors isolated the following primary risk drivers:
1. **`balance_change_1m`**: Standard credit attribute 'balance_change_1m'.
2. **`loan_purpose_enc`**: Standard credit attribute 'loan_purpose_enc'.
3. **`ever_delinquent`**: Standard credit attribute 'ever_delinquent'.

---

#### 4. Data Quality & Rule Reconciliation Findings
- **Rule Breach Triggered**: `NORMAL_CONFORMING`
- **Operational Analysis**:
  * Clean record. Performing within normal underwriting parameters with composite anomaly score 0.0692 and zero critical rule breaches.

---
*Authored by Intain AI Reviewer Copilot Engine v1.0*


---

### Loan Audit Review Memo: `F19Q20021034` (Reporting: 202107)

> **GOVERNANCE DISCLAIMER**: *This is an AI-generated synthesis recommendation for decision support. Human auditor review and formal sign-off are required prior to executing account-level interventions.*

---

#### 1. Executive Summary & Recommended Action
- **Recommended Action**: **`AUTO_APPROVE`** (Confidence: **0.95**)
- **Composite Anomaly Score**: `0.0732` | **Primary Exception**: `NONE`
- **Evidence Breakdown**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.201` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.000` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Account Snapshot**: Balance **$144,175.95** ($152,000.00 Orig) | Status: **CURRENT** (0 DPD) | Servicer: **Newrez LLC**
- **Borrower Profile**: Credit **741-800 (Very Good)** | LTV **81-90%** | DTI **21-30%** | Docs: **VERIFIED**

---

#### 2. Multi-Horizon Credit & Yield Risk Forecast
- **12-Month Default Probability**: **`0.33%`** [NOMINAL RISK]
- **12-Month Prepayment Probability**: **`63.71%`** [ACCELERATED PREPAYMENT]
- **3-Month Delinquency Migration**: **`1.31%`** | **6-Month Delinquency Migration**: **`1.79%`**
- **Projected Next Monthly State**: **`CURRENT`**

---

#### 3. Root Cause Feature Attribution (TreeSHAP Drivers)
The predictive models and anomaly detectors isolated the following primary risk drivers:
1. **`original_balance`**: Standard credit attribute 'original_balance'.
2. **`ltv_ord`**: Standard credit attribute 'ltv_ord'.
3. **`occupancy_type_enc`**: Standard credit attribute 'occupancy_type_enc'.

---

#### 4. Data Quality & Rule Reconciliation Findings
- **Rule Breach Triggered**: `NORMAL_CONFORMING`
- **Operational Analysis**:
  * Clean record. Performing within normal underwriting parameters with composite anomaly score 0.0732 and zero critical rule breaches.

---
*Authored by Intain AI Reviewer Copilot Engine v1.0*


---

*Report generated by Intain AI Track — Phase 6: LLM Governance Engine*
