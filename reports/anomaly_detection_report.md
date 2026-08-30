# Anomaly & Exception Intelligence Report

**Intain AI Track 2026 — Phase 3: Anomaly & Exception Detection Engine**  
**Generated**: 2026-08-30 19:24:13  

---

## 1. Executive Summary & Mathematical Weight Calibration

The Anomaly & Exception Engine fuses 4 orthogonal evidence layers to detect contractual, behavioral, and cross-source reporting anomalies.

### 1a. Evidence Weight Calibration (Differential Evolution on Training Slice)

- **Optimization Status**: `SUCCESSFULLY_CALIBRATED`
- **Baseline Equal Weights PR-AUC**: `0.3171`
- **Optimized Weights PR-AUC**: `0.3271` ($\Delta = +0.0100$)

| Evidence Layer | Focus & Input Scope | Equal Baseline Weight | **Calibrated Optimal Weight** |
| :--- | :--- | ---: | ---: |
| **$S_{\text{ML}}$ (Unsupervised)** | Non-rule behavioral & interaction space (`IsolationForest`, contamination=3.15%) | 25.0% | **38.2%** |
| **$S_{\text{rule}}$ (Validation Rules)** | All 8 contractual & feed rules from `validation_rules.json` (VR-001..VR-008) | 35.0% | **49.6%** |
| **$S_{\text{servicer}}$ (Reconciliation)** | Cross-source status discrepancies & payment timing drift | 25.0% | **8.2%** |
| **$S_{\text{DQ}}$ (Completeness)** | Non-rule missingness and schema format integrity | 15.0% | **4.0%** |

### 1b. Dataset-Level Anomaly Statistics

| Metric | Training Set (Historical) | Test Set (Evaluation) |
| :--- | ---: | ---: |
| Total Records Evaluated | 51,462 | 92,586 |
| Mean Anomaly Score | 0.0849 | 0.1689 |
| Flagged Exceptions (`exception_required == 1`) | 4,685 (9.10%) | 6,077 (6.56%) |
| High Risk Anomaly Score (>= 0.50) | 67 (0.13%) | 166 (0.18%) |

## 2. Prescriptive Reviewer Action Distribution (Test Set — Dynamic Confidence)

| Reviewer Action | Record Count | Percentage | Mean Confidence | Min Conf | Max Conf |
| :--- | ---: | ---: | ---: | ---: | ---: |
| `AUTO_APPROVE` | 86,469 | 93.39% | **0.90** | 0.85 | 0.98 |
| `REQUEST_CURE` | 4,503 | 4.86% | **0.84** | 0.80 | 0.98 |
| `MANUAL_AUDIT` | 895 | 0.97% | **0.91** | 0.89 | 0.96 |
| `ESCALATE_DOC_REVIEW` | 679 | 0.73% | **0.93** | 0.88 | 0.95 |
| `OVERRIDE_SERVICER` | 40 | 0.04% | **0.96** | 0.92 | 0.98 |

---

## 3. Stratified Reviewer Case Cards (24 Diverse Audit Cases)

> Each audit card presents full loan attributes, 4-layer score decomposition ($w_i \cdot S_i$), mathematically exact driver contributions summing to $S_{\text{anomaly}}$, and prescriptive reviewer guidance notes.

### Action Class: `MANUAL_AUDIT` (4 Example Audit Cards)

#### Case #01: Loan `F19Q10003196` (Period: `201902`)

- **Composite Anomaly Score**: `0.5157 / 1.0000` | **Action**: `MANUAL_AUDIT` (Confidence: 92%) | **Exception**: `INVALID_DATE`
- **Loan Attributes**: Orig Bal: $69,000.00 | Current Bal: $69,000.00 | Status: `CURRENT` | DPD: `0` | Doc Status: `VERIFIED` | Rem Term: `450m`
- **Evidence Decomposition**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.094` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.422` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Top Root Cause Drivers (Mathematical Sum = 0.516)**:
  1. `VR-003_INVALID_DATE_SEQUENCE (+0.422)`
  2. `ISOLATION_FOREST_OUTLIER (+0.094)`
  3. `NO_TERTIARY_ISSUE`
- **Reviewer Audit Note**: *Critical balance surge, term violation, or multi-rule contradiction detected. Escalate to senior audit team for balance tape recalculation and servicer feed verification.*

#### Case #02: Loan `F19Q10008688` (Period: `201902`)

- **Composite Anomaly Score**: `0.6440 / 1.0000` | **Action**: `MANUAL_AUDIT` (Confidence: 93%) | **Exception**: `STATUS_CONFLICT`
- **Loan Attributes**: Orig Bal: $160,000.00 | Current Bal: $160,000.00 | Status: `CURRENT` | DPD: `90` | Doc Status: `VERIFIED` | Rem Term: `360m`
- **Evidence Decomposition**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.222` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.422` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Top Root Cause Drivers (Mathematical Sum = 0.644)**:
  1. `VR-002_STATUS_CONFLICT_90DPD (+0.422)`
  2. `ISOLATION_FOREST_OUTLIER (+0.222)`
  3. `NO_TERTIARY_ISSUE`
- **Reviewer Audit Note**: *Critical balance surge, term violation, or multi-rule contradiction detected. Escalate to senior audit team for balance tape recalculation and servicer feed verification.*

#### Case #03: Loan `F19Q10020081` (Period: `201902`)

- **Composite Anomaly Score**: `0.5322 / 1.0000` | **Action**: `MANUAL_AUDIT` (Confidence: 92%) | **Exception**: `BALANCE_INCONSISTENCY`
- **Loan Attributes**: Orig Bal: $632,000.00 | Current Bal: $821,296.02 | Status: `CURRENT` | DPD: `0` | Doc Status: `VERIFIED` | Rem Term: `360m`
- **Evidence Decomposition**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.036` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.496` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Top Root Cause Drivers (Mathematical Sum = 0.532)**:
  1. `VR-001_BALANCE_SURGE_130PCT (+0.496)`
  2. `ISOLATION_FOREST_OUTLIER (+0.036)`
  3. `NO_TERTIARY_ISSUE`
- **Reviewer Audit Note**: *Critical balance surge, term violation, or multi-rule contradiction detected. Escalate to senior audit team for balance tape recalculation and servicer feed verification.*

#### Case #04: Loan `F19Q10095553` (Period: `201902`)

- **Composite Anomaly Score**: `0.5327 / 1.0000` | **Action**: `MANUAL_AUDIT` (Confidence: 92%) | **Exception**: `BALANCE_INCONSISTENCY`
- **Loan Attributes**: Orig Bal: $189,000.00 | Current Bal: $322,442.97 | Status: `CURRENT` | DPD: `0` | Doc Status: `VERIFIED` | Rem Term: `360m`
- **Evidence Decomposition**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.036` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.496` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Top Root Cause Drivers (Mathematical Sum = 0.533)**:
  1. `VR-001_BALANCE_SURGE_171PCT (+0.496)`
  2. `ISOLATION_FOREST_OUTLIER (+0.036)`
  3. `NO_TERTIARY_ISSUE`
- **Reviewer Audit Note**: *Critical balance surge, term violation, or multi-rule contradiction detected. Escalate to senior audit team for balance tape recalculation and servicer feed verification.*

---

### Action Class: `ESCALATE_DOC_REVIEW` (4 Example Audit Cards)

#### Case #05: Loan `F19Q10046413` (Period: `201903`)

- **Composite Anomaly Score**: `0.1468 / 1.0000` | **Action**: `ESCALATE_DOC_REVIEW` (Confidence: 95%) | **Exception**: `DOCUMENT_GAP`
- **Loan Attributes**: Orig Bal: $327,000.00 | Current Bal: $325,000.00 | Status: `CURRENT` | DPD: `0` | Doc Status: `MISSING_NOTE` | Rem Term: `179m`
- **Evidence Decomposition**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.048` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.099` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Top Root Cause Drivers (Mathematical Sum = 0.147)**:
  1. `NORMAL_CONFORMING`
  2. `NO_SECONDARY_ISSUE`
  3. `NO_TERTIARY_ISSUE`
- **Reviewer Audit Note**: *Document verification incomplete (missing note / unverified appraisal). Request trailing document package from originator prior to credit decision.*

#### Case #06: Loan `F19Q10063592` (Period: `201903`)

- **Composite Anomaly Score**: `0.1891 / 1.0000` | **Action**: `ESCALATE_DOC_REVIEW` (Confidence: 95%) | **Exception**: `DOCUMENT_GAP`
- **Loan Attributes**: Orig Bal: $146,000.00 | Current Bal: $146,000.00 | Status: `CURRENT` | DPD: `0` | Doc Status: `UNVERIFIED_APPRAISAL` | Rem Term: `359m`
- **Evidence Decomposition**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.090` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.099` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Top Root Cause Drivers (Mathematical Sum = 0.189)**:
  1. `VR-006_DOCUMENT_GAP_UNVERIFIED_APPRAISAL (+0.099)`
  2. `ISOLATION_FOREST_OUTLIER (+0.090)`
  3. `NO_TERTIARY_ISSUE`
- **Reviewer Audit Note**: *Document verification incomplete (missing note / unverified appraisal). Request trailing document package from originator prior to credit decision.*

#### Case #07: Loan `F19Q10034677` (Period: `201904`)

- **Composite Anomaly Score**: `0.1629 / 1.0000` | **Action**: `ESCALATE_DOC_REVIEW` (Confidence: 95%) | **Exception**: `DOCUMENT_GAP`
- **Loan Attributes**: Orig Bal: $182,000.00 | Current Bal: $181,000.00 | Status: `CURRENT` | DPD: `0` | Doc Status: `MISSING_NOTE` | Rem Term: `358m`
- **Evidence Decomposition**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.064` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.099` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Top Root Cause Drivers (Mathematical Sum = 0.163)**:
  1. `VR-006_DOCUMENT_GAP_MISSING_NOTE (+0.099)`
  2. `ISOLATION_FOREST_OUTLIER (+0.064)`
  3. `NO_TERTIARY_ISSUE`
- **Reviewer Audit Note**: *Document verification incomplete (missing note / unverified appraisal). Request trailing document package from originator prior to credit decision.*

#### Case #08: Loan `F19Q10085948` (Period: `201904`)

- **Composite Anomaly Score**: `0.2027 / 1.0000` | **Action**: `ESCALATE_DOC_REVIEW` (Confidence: 88%) | **Exception**: `DOCUMENT_GAP`
- **Loan Attributes**: Orig Bal: $176,000.00 | Current Bal: $176,000.00 | Status: `30DPD` | DPD: `30` | Doc Status: `INCOMPLETE_INCOME` | Rem Term: `359m`
- **Evidence Decomposition**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.103` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.099` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Top Root Cause Drivers (Mathematical Sum = 0.203)**:
  1. `ISOLATION_FOREST_OUTLIER (+0.103)`
  2. `VR-006_DOCUMENT_GAP_INCOMPLETE_INCOME (+0.099)`
  3. `NO_TERTIARY_ISSUE`
- **Reviewer Audit Note**: *Document verification incomplete (missing note / unverified appraisal). Request trailing document package from originator prior to credit decision.*

---

### Action Class: `OVERRIDE_SERVICER` (4 Example Audit Cards)

#### Case #09: Loan `F19Q10230630` (Period: `201907`)

- **Composite Anomaly Score**: `0.2295 / 1.0000` | **Action**: `OVERRIDE_SERVICER` (Confidence: 98%) | **Exception**: `NONE`
- **Loan Attributes**: Orig Bal: $670,000.00 | Current Bal: $0.00 | Status: `PREPAID` | DPD: `0` | Doc Status: `VERIFIED` | Rem Term: `357m`
- **Evidence Decomposition**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.181` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.000` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.049` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Top Root Cause Drivers (Mathematical Sum = 0.230)**:
  1. `ISOLATION_FOREST_OUTLIER (+0.181)`
  2. `SERVICER_STATUS_CONFLICT (+0.049)`
  3. `NO_TERTIARY_ISSUE`
- **Reviewer Audit Note**: *Cross-source servicer status conflict detected against verified primary transaction ledger. Retain primary ledger balance and override servicer record.*

#### Case #10: Loan `F19Q10092285` (Period: `201911`)

- **Composite Anomaly Score**: `0.2605 / 1.0000` | **Action**: `OVERRIDE_SERVICER` (Confidence: 98%) | **Exception**: `NONE`
- **Loan Attributes**: Orig Bal: $495,000.00 | Current Bal: $0.00 | Status: `PREPAID` | DPD: `0` | Doc Status: `VERIFIED` | Rem Term: `351m`
- **Evidence Decomposition**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.212` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.000` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.049` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Top Root Cause Drivers (Mathematical Sum = 0.261)**:
  1. `ISOLATION_FOREST_OUTLIER (+0.212)`
  2. `SERVICER_STATUS_CONFLICT (+0.049)`
  3. `NO_TERTIARY_ISSUE`
- **Reviewer Audit Note**: *Cross-source servicer status conflict detected against verified primary transaction ledger. Retain primary ledger balance and override servicer record.*

#### Case #11: Loan `F19Q10078167` (Period: `201912`)

- **Composite Anomaly Score**: `0.2738 / 1.0000` | **Action**: `OVERRIDE_SERVICER` (Confidence: 98%) | **Exception**: `NONE`
- **Loan Attributes**: Orig Bal: $102,000.00 | Current Bal: $0.00 | Status: `PREPAID` | DPD: `0` | Doc Status: `VERIFIED` | Rem Term: `351m`
- **Evidence Decomposition**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.225` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.000` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.049` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Top Root Cause Drivers (Mathematical Sum = 0.274)**:
  1. `ISOLATION_FOREST_OUTLIER (+0.225)`
  2. `SERVICER_STATUS_CONFLICT (+0.049)`
  3. `NO_TERTIARY_ISSUE`
- **Reviewer Audit Note**: *Cross-source servicer status conflict detected against verified primary transaction ledger. Retain primary ledger balance and override servicer record.*

#### Case #12: Loan `F19Q10175524` (Period: `202004`)

- **Composite Anomaly Score**: `0.2187 / 1.0000` | **Action**: `OVERRIDE_SERVICER` (Confidence: 98%) | **Exception**: `NONE`
- **Loan Attributes**: Orig Bal: $247,000.00 | Current Bal: $0.00 | Status: `PREPAID` | DPD: `0` | Doc Status: `VERIFIED` | Rem Term: `348m`
- **Evidence Decomposition**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.170` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.000` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.049` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Top Root Cause Drivers (Mathematical Sum = 0.219)**:
  1. `ISOLATION_FOREST_OUTLIER (+0.170)`
  2. `SERVICER_STATUS_CONFLICT (+0.049)`
  3. `NO_TERTIARY_ISSUE`
- **Reviewer Audit Note**: *Cross-source servicer status conflict detected against verified primary transaction ledger. Retain primary ledger balance and override servicer record.*

---

### Action Class: `REQUEST_CURE` (4 Example Audit Cards)

#### Case #13: Loan `F19Q10006318` (Period: `201901`)

- **Composite Anomaly Score**: `0.3257 / 1.0000` | **Action**: `REQUEST_CURE` (Confidence: 80%) | **Exception**: `INVALID_DATE`
- **Loan Attributes**: Orig Bal: $105,000.00 | Current Bal: $104,000.00 | Status: `CURRENT` | DPD: `0` | Doc Status: `VERIFIED` | Rem Term: `360m`
- **Evidence Decomposition**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.078` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.248` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Top Root Cause Drivers (Mathematical Sum = 0.326)**:
  1. `VR-003_INVALID_DATE_SEQUENCE (+0.248)`
  2. `ISOLATION_FOREST_OUTLIER (+0.078)`
  3. `NO_TERTIARY_ISSUE`
- **Reviewer Audit Note**: *Borrower is in active delinquency roll or status conflict. Request workout agreement, forbearance schedule, or servicer cure timeline.*

#### Case #14: Loan `F19Q10014939` (Period: `201903`)

- **Composite Anomaly Score**: `0.2800 / 1.0000` | **Action**: `REQUEST_CURE` (Confidence: 80%) | **Exception**: `SERVICER_CONFLICT`
- **Loan Attributes**: Orig Bal: $116,000.00 | Current Bal: $116,000.00 | Status: `CURRENT` | DPD: `0` | Doc Status: `VERIFIED` | Rem Term: `359m`
- **Evidence Decomposition**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.106` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.174` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Top Root Cause Drivers (Mathematical Sum = 0.280)**:
  1. `VR-007_SERVICER_BALANCE_DIFF_9PCT (+0.174)`
  2. `ISOLATION_FOREST_OUTLIER (+0.106)`
  3. `NO_TERTIARY_ISSUE`
- **Reviewer Audit Note**: *Borrower is in active delinquency roll or status conflict. Request workout agreement, forbearance schedule, or servicer cure timeline.*

#### Case #15: Loan `F19Q10017485` (Period: `201903`)

- **Composite Anomaly Score**: `0.3593 / 1.0000` | **Action**: `REQUEST_CURE` (Confidence: 98%) | **Exception**: `STATUS_CONFLICT`
- **Loan Attributes**: Orig Bal: $252,000.00 | Current Bal: $251,000.00 | Status: `CURRENT` | DPD: `90` | Doc Status: `VERIFIED` | Rem Term: `359m`
- **Evidence Decomposition**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.186` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.174` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Top Root Cause Drivers (Mathematical Sum = 0.359)**:
  1. `ISOLATION_FOREST_OUTLIER (+0.186)`
  2. `VR-002_STATUS_CONFLICT_90DPD (+0.174)`
  3. `NO_TERTIARY_ISSUE`
- **Reviewer Audit Note**: *Borrower is in active delinquency roll or status conflict. Request workout agreement, forbearance schedule, or servicer cure timeline.*

#### Case #16: Loan `F19Q10018216` (Period: `201903`)

- **Composite Anomaly Score**: `0.1795 / 1.0000` | **Action**: `REQUEST_CURE` (Confidence: 80%) | **Exception**: `STALE_RECORD`
- **Loan Attributes**: Orig Bal: $337,000.00 | Current Bal: $336,000.00 | Status: `CURRENT` | DPD: `0` | Doc Status: `VERIFIED` | Rem Term: `358m`
- **Evidence Decomposition**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.080` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.099` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Top Root Cause Drivers (Mathematical Sum = 0.179)**:
  1. `VR-008_FEED_STALENESS_EXCEEDS_60D (+0.099)`
  2. `ISOLATION_FOREST_OUTLIER (+0.080)`
  3. `NO_TERTIARY_ISSUE`
- **Reviewer Audit Note**: *Borrower is in active delinquency roll or status conflict. Request workout agreement, forbearance schedule, or servicer cure timeline.*

---

### Action Class: `ACCEPT_PRIMARY` (0 Example Audit Cards)

---

### Action Class: `AUTO_APPROVE` (4 Example Audit Cards)

#### Case #17: Loan `F19Q10006318` (Period: `201902`)

- **Composite Anomaly Score**: `0.0650 / 1.0000` | **Action**: `AUTO_APPROVE` (Confidence: 95%) | **Exception**: `NONE`
- **Loan Attributes**: Orig Bal: $105,000.00 | Current Bal: $104,000.00 | Status: `CURRENT` | DPD: `0` | Doc Status: `VERIFIED` | Rem Term: `359m`
- **Evidence Decomposition**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.065` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.000` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Top Root Cause Drivers (Mathematical Sum = 0.065)**:
  1. `NORMAL_CONFORMING`
  2. `NO_SECONDARY_ISSUE`
  3. `NO_TERTIARY_ISSUE`
- **Reviewer Audit Note**: *Standard conforming prime loan record. Full data integrity verified across all 4 evidence layers. Automatically approve.*

#### Case #18: Loan `F19Q10008589` (Period: `201903`)

- **Composite Anomaly Score**: `0.1812 / 1.0000` | **Action**: `AUTO_APPROVE` (Confidence: 89%) | **Exception**: `NONE`
- **Loan Attributes**: Orig Bal: $139,000.00 | Current Bal: $138,000.00 | Status: `CURRENT` | DPD: `0` | Doc Status: `VERIFIED` | Rem Term: `119m`
- **Evidence Decomposition**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.181` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.000` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Top Root Cause Drivers (Mathematical Sum = 0.181)**:
  1. `ISOLATION_FOREST_OUTLIER (+0.181)`
  2. `NO_SECONDARY_ISSUE`
  3. `NO_TERTIARY_ISSUE`
- **Reviewer Audit Note**: *Standard conforming prime loan record. Full data integrity verified across all 4 evidence layers. Automatically approve.*

#### Case #19: Loan `F19Q10014179` (Period: `201903`)

- **Composite Anomaly Score**: `0.1509 / 1.0000` | **Action**: `AUTO_APPROVE` (Confidence: 91%) | **Exception**: `NONE`
- **Loan Attributes**: Orig Bal: $128,000.00 | Current Bal: $128,000.00 | Status: `CURRENT` | DPD: `0` | Doc Status: `VERIFIED` | Rem Term: `359m`
- **Evidence Decomposition**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.151` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.000` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Top Root Cause Drivers (Mathematical Sum = 0.151)**:
  1. `ISOLATION_FOREST_OUTLIER (+0.151)`
  2. `NO_SECONDARY_ISSUE`
  3. `NO_TERTIARY_ISSUE`
- **Reviewer Audit Note**: *Standard conforming prime loan record. Full data integrity verified across all 4 evidence layers. Automatically approve.*

#### Case #20: Loan `F19Q10024270` (Period: `201903`)

- **Composite Anomaly Score**: `0.1590 / 1.0000` | **Action**: `AUTO_APPROVE` (Confidence: 90%) | **Exception**: `NONE`
- **Loan Attributes**: Orig Bal: $76,000.00 | Current Bal: $76,000.00 | Status: `30DPD` | DPD: `30` | Doc Status: `VERIFIED` | Rem Term: `359m`
- **Evidence Decomposition**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.159` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.000` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Top Root Cause Drivers (Mathematical Sum = 0.159)**:
  1. `ISOLATION_FOREST_OUTLIER (+0.159)`
  2. `NO_SECONDARY_ISSUE`
  3. `NO_TERTIARY_ISSUE`
- **Reviewer Audit Note**: *Standard conforming prime loan record. Full data integrity verified across all 4 evidence layers. Automatically approve.*

---

*Report generated by Intain AI Track — Phase 3: Anomaly & Exception Detection Engine*
