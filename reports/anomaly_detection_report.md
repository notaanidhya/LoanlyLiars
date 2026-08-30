# Anomaly & Exception Intelligence Report

**Intain AI Track 2026 — Phase 3: Anomaly & Exception Detection Engine**  
**Generated**: 2026-08-30 14:49:50  

---

## 1. Executive Summary & Mathematical Weight Calibration

The Anomaly & Exception Engine fuses 4 orthogonal evidence layers to detect contractual, behavioral, and cross-source reporting anomalies.

### 1a. Evidence Weight Calibration (Differential Evolution on Training Slice)

- **Optimization Status**: `SUCCESSFULLY_CALIBRATED`
- **Baseline Equal Weights PR-AUC**: `0.3088`
- **Optimized Weights PR-AUC**: `0.3137` ($\Delta = +0.0049$)

| Evidence Layer | Focus & Input Scope | Equal Baseline Weight | **Calibrated Optimal Weight** |
| :--- | :--- | ---: | ---: |
| **$S_{\text{ML}}$ (Unsupervised)** | Non-rule behavioral & interaction space (`IsolationForest`, contamination=3.15%) | 25.0% | **34.4%** |
| **$S_{\text{rule}}$ (Validation Rules)** | All 8 contractual & feed rules from `validation_rules.json` (VR-001..VR-008) | 35.0% | **46.5%** |
| **$S_{\text{servicer}}$ (Reconciliation)** | Cross-source status discrepancies & payment timing drift | 25.0% | **15.2%** |
| **$S_{\text{DQ}}$ (Completeness)** | Non-rule missingness and schema format integrity | 15.0% | **3.8%** |

### 1b. Dataset-Level Anomaly Statistics

| Metric | Training Set (Historical) | Test Set (Evaluation) |
| :--- | ---: | ---: |
| Total Records Evaluated | 407,733 | 304,374 |
| Mean Anomaly Score | 0.0757 | 0.1517 |
| Flagged Exceptions (`exception_required == 1`) | 37,575 (9.22%) | 19,615 (6.44%) |
| High Risk Anomaly Score (>= 0.50) | 403 (0.10%) | 343 (0.11%) |

## 2. Prescriptive Reviewer Action Distribution (Test Set — Dynamic Confidence)

| Reviewer Action | Record Count | Percentage | Mean Confidence | Min Conf | Max Conf |
| :--- | ---: | ---: | ---: | ---: | ---: |
| `AUTO_APPROVE` | 284,641 | 93.52% | **0.91** | 0.85 | 0.99 |
| `REQUEST_CURE` | 14,480 | 4.76% | **0.84** | 0.80 | 0.98 |
| `MANUAL_AUDIT` | 2,871 | 0.94% | **0.90** | 0.88 | 0.95 |
| `ESCALATE_DOC_REVIEW` | 2,264 | 0.74% | **0.93** | 0.88 | 0.95 |
| `OVERRIDE_SERVICER` | 118 | 0.04% | **0.96** | 0.92 | 0.98 |

---

## 3. Stratified Reviewer Case Cards (24 Diverse Audit Cases)

> Each audit card presents full loan attributes, 4-layer score decomposition ($w_i \cdot S_i$), mathematically exact driver contributions summing to $S_{\text{anomaly}}$, and prescriptive reviewer guidance notes.

### Action Class: `MANUAL_AUDIT` (4 Example Audit Cards)

#### Case #01: Loan `F19Q10000290` (Period: `201902`)

- **Composite Anomaly Score**: `0.4277 / 1.0000` | **Action**: `MANUAL_AUDIT` (Confidence: 91%) | **Exception**: `INVALID_DATE`
- **Loan Attributes**: Orig Bal: $160,000.00 | Current Bal: $160,000.00 | Status: `CURRENT` | DPD: `0` | Doc Status: `VERIFIED` | Rem Term: `360m`
- **Evidence Decomposition**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.032` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.395` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Top Root Cause Drivers (Mathematical Sum = 0.428)**:
  1. `VR-003_INVALID_DATE_SEQUENCE (+0.395)`
  2. `ISOLATION_FOREST_OUTLIER (+0.032)`
  3. `NO_TERTIARY_ISSUE`
- **Reviewer Audit Note**: *Critical balance surge, term violation, or multi-rule contradiction detected. Escalate to senior audit team for balance tape recalculation and servicer feed verification.*

#### Case #02: Loan `F19Q10001353` (Period: `201902`)

- **Composite Anomaly Score**: `0.3672 / 1.0000` | **Action**: `MANUAL_AUDIT` (Confidence: 90%) | **Exception**: `INVALID_DATE`
- **Loan Attributes**: Orig Bal: $359,000.00 | Current Bal: $359,000.00 | Status: `CURRENT` | DPD: `0` | Doc Status: `MISSING_NOTE` | Rem Term: `360m`
- **Evidence Decomposition**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.042` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.326` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Top Root Cause Drivers (Mathematical Sum = 0.367)**:
  1. `VR-003_INVALID_DATE_SEQUENCE (+0.326)`
  2. `ISOLATION_FOREST_OUTLIER (+0.042)`
  3. `NO_TERTIARY_ISSUE`
- **Reviewer Audit Note**: *Critical balance surge, term violation, or multi-rule contradiction detected. Escalate to senior audit team for balance tape recalculation and servicer feed verification.*

#### Case #03: Loan `F19Q10003577` (Period: `201902`)

- **Composite Anomaly Score**: `0.5579 / 1.0000` | **Action**: `MANUAL_AUDIT` (Confidence: 92%) | **Exception**: `STATUS_CONFLICT`
- **Loan Attributes**: Orig Bal: $380,000.00 | Current Bal: $380,000.00 | Status: `CURRENT` | DPD: `90` | Doc Status: `VERIFIED` | Rem Term: `360m`
- **Evidence Decomposition**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.163` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.395` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Top Root Cause Drivers (Mathematical Sum = 0.558)**:
  1. `VR-002_STATUS_CONFLICT_90DPD (+0.395)`
  2. `ISOLATION_FOREST_OUTLIER (+0.163)`
  3. `NO_TERTIARY_ISSUE`
- **Reviewer Audit Note**: *Critical balance surge, term violation, or multi-rule contradiction detected. Escalate to senior audit team for balance tape recalculation and servicer feed verification.*

#### Case #04: Loan `F19Q10003861` (Period: `201902`)

- **Composite Anomaly Score**: `0.5364 / 1.0000` | **Action**: `MANUAL_AUDIT` (Confidence: 92%) | **Exception**: `BALANCE_INCONSISTENCY`
- **Loan Attributes**: Orig Bal: $335,000.00 | Current Bal: $474,071.99 | Status: `CURRENT` | DPD: `0` | Doc Status: `VERIFIED` | Rem Term: `360m`
- **Evidence Decomposition**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.071` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.465` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Top Root Cause Drivers (Mathematical Sum = 0.536)**:
  1. `VR-001_BALANCE_SURGE_142PCT (+0.465)`
  2. `ISOLATION_FOREST_OUTLIER (+0.071)`
  3. `NO_TERTIARY_ISSUE`
- **Reviewer Audit Note**: *Critical balance surge, term violation, or multi-rule contradiction detected. Escalate to senior audit team for balance tape recalculation and servicer feed verification.*

---

### Action Class: `ESCALATE_DOC_REVIEW` (4 Example Audit Cards)

#### Case #05: Loan `F19Q10000843` (Period: `201903`)

- **Composite Anomaly Score**: `0.1481 / 1.0000` | **Action**: `ESCALATE_DOC_REVIEW` (Confidence: 88%) | **Exception**: `DOCUMENT_GAP`
- **Loan Attributes**: Orig Bal: $85,000.00 | Current Bal: $85,000.00 | Status: `CURRENT` | DPD: `0` | Doc Status: `INCOMPLETE_INCOME` | Rem Term: `359m`
- **Evidence Decomposition**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.055` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.093` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Top Root Cause Drivers (Mathematical Sum = 0.148)**:
  1. `NORMAL_CONFORMING`
  2. `NO_SECONDARY_ISSUE`
  3. `NO_TERTIARY_ISSUE`
- **Reviewer Audit Note**: *Document verification incomplete (missing note / unverified appraisal). Request trailing document package from originator prior to credit decision.*

#### Case #06: Loan `F19Q10009387` (Period: `201903`)

- **Composite Anomaly Score**: `0.1680 / 1.0000` | **Action**: `ESCALATE_DOC_REVIEW` (Confidence: 88%) | **Exception**: `DOCUMENT_GAP`
- **Loan Attributes**: Orig Bal: $195,000.00 | Current Bal: $195,000.00 | Status: `CURRENT` | DPD: `0` | Doc Status: `INCOMPLETE_INCOME` | Rem Term: `359m`
- **Evidence Decomposition**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.075` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.093` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Top Root Cause Drivers (Mathematical Sum = 0.168)**:
  1. `VR-006_DOCUMENT_GAP_INCOMPLETE_INCOME (+0.093)`
  2. `ISOLATION_FOREST_OUTLIER (+0.075)`
  3. `NO_TERTIARY_ISSUE`
- **Reviewer Audit Note**: *Document verification incomplete (missing note / unverified appraisal). Request trailing document package from originator prior to credit decision.*

#### Case #07: Loan `F19Q10030187` (Period: `201903`)

- **Composite Anomaly Score**: `0.1679 / 1.0000` | **Action**: `ESCALATE_DOC_REVIEW` (Confidence: 95%) | **Exception**: `DOCUMENT_GAP`
- **Loan Attributes**: Orig Bal: $74,000.00 | Current Bal: $74,000.00 | Status: `CURRENT` | DPD: `0` | Doc Status: `MISSING_NOTE` | Rem Term: `359m`
- **Evidence Decomposition**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.075` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.093` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Top Root Cause Drivers (Mathematical Sum = 0.168)**:
  1. `VR-006_DOCUMENT_GAP_MISSING_NOTE (+0.093)`
  2. `ISOLATION_FOREST_OUTLIER (+0.075)`
  3. `NO_TERTIARY_ISSUE`
- **Reviewer Audit Note**: *Document verification incomplete (missing note / unverified appraisal). Request trailing document package from originator prior to credit decision.*

#### Case #08: Loan `F19Q10031211` (Period: `201903`)

- **Composite Anomaly Score**: `0.1869 / 1.0000` | **Action**: `ESCALATE_DOC_REVIEW` (Confidence: 88%) | **Exception**: `DOCUMENT_GAP`
- **Loan Attributes**: Orig Bal: $350,000.00 | Current Bal: $350,000.00 | Status: `CURRENT` | DPD: `0` | Doc Status: `INCOMPLETE_INCOME` | Rem Term: `359m`
- **Evidence Decomposition**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.094` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.093` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Top Root Cause Drivers (Mathematical Sum = 0.187)**:
  1. `ISOLATION_FOREST_OUTLIER (+0.094)`
  2. `VR-006_DOCUMENT_GAP_INCOMPLETE_INCOME (+0.093)`
  3. `NO_TERTIARY_ISSUE`
- **Reviewer Audit Note**: *Document verification incomplete (missing note / unverified appraisal). Request trailing document package from originator prior to credit decision.*

---

### Action Class: `OVERRIDE_SERVICER` (4 Example Audit Cards)

#### Case #09: Loan `F19Q10014366` (Period: `201905`)

- **Composite Anomaly Score**: `0.2384 / 1.0000` | **Action**: `OVERRIDE_SERVICER` (Confidence: 98%) | **Exception**: `NONE`
- **Loan Attributes**: Orig Bal: $690,000.00 | Current Bal: $0.00 | Status: `PREPAID` | DPD: `0` | Doc Status: `VERIFIED` | Rem Term: `357m`
- **Evidence Decomposition**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.147` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.000` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.091` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Top Root Cause Drivers (Mathematical Sum = 0.238)**:
  1. `ISOLATION_FOREST_OUTLIER (+0.147)`
  2. `SERVICER_STATUS_CONFLICT (+0.091)`
  3. `NO_TERTIARY_ISSUE`
- **Reviewer Audit Note**: *Cross-source servicer status conflict detected against verified primary transaction ledger. Retain primary ledger balance and override servicer record.*

#### Case #10: Loan `F19Q10013120` (Period: `201906`)

- **Composite Anomaly Score**: `0.2492 / 1.0000` | **Action**: `OVERRIDE_SERVICER` (Confidence: 98%) | **Exception**: `NONE`
- **Loan Attributes**: Orig Bal: $516,000.00 | Current Bal: $0.00 | Status: `PREPAID` | DPD: `0` | Doc Status: `VERIFIED` | Rem Term: `356m`
- **Evidence Decomposition**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.158` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.000` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.091` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Top Root Cause Drivers (Mathematical Sum = 0.249)**:
  1. `ISOLATION_FOREST_OUTLIER (+0.158)`
  2. `SERVICER_STATUS_CONFLICT (+0.091)`
  3. `NO_TERTIARY_ISSUE`
- **Reviewer Audit Note**: *Cross-source servicer status conflict detected against verified primary transaction ledger. Retain primary ledger balance and override servicer record.*

#### Case #11: Loan `F19Q10197507` (Period: `201906`)

- **Composite Anomaly Score**: `0.2782 / 1.0000` | **Action**: `OVERRIDE_SERVICER` (Confidence: 98%) | **Exception**: `NONE`
- **Loan Attributes**: Orig Bal: $256,000.00 | Current Bal: $0.00 | Status: `PREPAID` | DPD: `0` | Doc Status: `VERIFIED` | Rem Term: `358m`
- **Evidence Decomposition**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.187` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.000` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.091` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Top Root Cause Drivers (Mathematical Sum = 0.278)**:
  1. `ISOLATION_FOREST_OUTLIER (+0.187)`
  2. `SERVICER_STATUS_CONFLICT (+0.091)`
  3. `NO_TERTIARY_ISSUE`
- **Reviewer Audit Note**: *Cross-source servicer status conflict detected against verified primary transaction ledger. Retain primary ledger balance and override servicer record.*

#### Case #12: Loan `F19Q10015531` (Period: `201907`)

- **Composite Anomaly Score**: `0.2565 / 1.0000` | **Action**: `OVERRIDE_SERVICER` (Confidence: 98%) | **Exception**: `NONE`
- **Loan Attributes**: Orig Bal: $363,000.00 | Current Bal: $0.00 | Status: `PREPAID` | DPD: `0` | Doc Status: `VERIFIED` | Rem Term: `355m`
- **Evidence Decomposition**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.165` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.000` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.091` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Top Root Cause Drivers (Mathematical Sum = 0.257)**:
  1. `ISOLATION_FOREST_OUTLIER (+0.165)`
  2. `SERVICER_STATUS_CONFLICT (+0.091)`
  3. `NO_TERTIARY_ISSUE`
- **Reviewer Audit Note**: *Cross-source servicer status conflict detected against verified primary transaction ledger. Retain primary ledger balance and override servicer record.*

---

### Action Class: `REQUEST_CURE` (4 Example Audit Cards)

#### Case #13: Loan `F19Q10000418` (Period: `201901`)

- **Composite Anomaly Score**: `0.2846 / 1.0000` | **Action**: `REQUEST_CURE` (Confidence: 80%) | **Exception**: `INVALID_DATE`
- **Loan Attributes**: Orig Bal: $247,000.00 | Current Bal: $247,000.00 | Status: `CURRENT` | DPD: `0` | Doc Status: `VERIFIED` | Rem Term: `360m`
- **Evidence Decomposition**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.052` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.233` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Top Root Cause Drivers (Mathematical Sum = 0.285)**:
  1. `VR-003_INVALID_DATE_SEQUENCE (+0.233)`
  2. `ISOLATION_FOREST_OUTLIER (+0.052)`
  3. `NO_TERTIARY_ISSUE`
- **Reviewer Audit Note**: *Borrower is in active delinquency roll or status conflict. Request workout agreement, forbearance schedule, or servicer cure timeline.*

#### Case #14: Loan `F19Q10006346` (Period: `201902`)

- **Composite Anomaly Score**: `0.2120 / 1.0000` | **Action**: `REQUEST_CURE` (Confidence: 80%) | **Exception**: `SERVICER_CONFLICT`
- **Loan Attributes**: Orig Bal: $300,000.00 | Current Bal: $299,000.00 | Status: `CURRENT` | DPD: `0` | Doc Status: `VERIFIED` | Rem Term: `239m`
- **Evidence Decomposition**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.049` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.163` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Top Root Cause Drivers (Mathematical Sum = 0.212)**:
  1. `VR-007_SERVICER_BALANCE_DIFF_6PCT (+0.163)`
  2. `ISOLATION_FOREST_OUTLIER (+0.049)`
  3. `NO_TERTIARY_ISSUE`
- **Reviewer Audit Note**: *Borrower is in active delinquency roll or status conflict. Request workout agreement, forbearance schedule, or servicer cure timeline.*

#### Case #15: Loan `F19Q10000960` (Period: `201903`)

- **Composite Anomaly Score**: `0.2039 / 1.0000` | **Action**: `REQUEST_CURE` (Confidence: 80%) | **Exception**: `SERVICER_CONFLICT`
- **Loan Attributes**: Orig Bal: $256,000.00 | Current Bal: $256,000.00 | Status: `CURRENT` | DPD: `0` | Doc Status: `VERIFIED` | Rem Term: `359m`
- **Evidence Decomposition**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.041` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.163` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Top Root Cause Drivers (Mathematical Sum = 0.204)**:
  1. `VR-007_SERVICER_BALANCE_DIFF_10PCT (+0.163)`
  2. `ISOLATION_FOREST_OUTLIER (+0.041)`
  3. `NO_TERTIARY_ISSUE`
- **Reviewer Audit Note**: *Borrower is in active delinquency roll or status conflict. Request workout agreement, forbearance schedule, or servicer cure timeline.*

#### Case #16: Loan `F19Q10002275` (Period: `201903`)

- **Composite Anomaly Score**: `0.2164 / 1.0000` | **Action**: `REQUEST_CURE` (Confidence: 80%) | **Exception**: `INVALID_TERM`
- **Loan Attributes**: Orig Bal: $412,000.00 | Current Bal: $411,000.00 | Status: `CURRENT` | DPD: `0` | Doc Status: `VERIFIED` | Rem Term: `450m`
- **Evidence Decomposition**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.054` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.163` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Top Root Cause Drivers (Mathematical Sum = 0.216)**:
  1. `VR-004_INVALID_TERM_450M (+0.163)`
  2. `ISOLATION_FOREST_OUTLIER (+0.054)`
  3. `NO_TERTIARY_ISSUE`
- **Reviewer Audit Note**: *Borrower is in active delinquency roll or status conflict. Request workout agreement, forbearance schedule, or servicer cure timeline.*

---

### Action Class: `ACCEPT_PRIMARY` (0 Example Audit Cards)

---

### Action Class: `AUTO_APPROVE` (4 Example Audit Cards)

#### Case #17: Loan `F19Q10000418` (Period: `201902`)

- **Composite Anomaly Score**: `0.0454 / 1.0000` | **Action**: `AUTO_APPROVE` (Confidence: 96%) | **Exception**: `NONE`
- **Loan Attributes**: Orig Bal: $247,000.00 | Current Bal: $246,000.00 | Status: `CURRENT` | DPD: `0` | Doc Status: `VERIFIED` | Rem Term: `359m`
- **Evidence Decomposition**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.045` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.000` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Top Root Cause Drivers (Mathematical Sum = 0.045)**:
  1. `NORMAL_CONFORMING`
  2. `NO_SECONDARY_ISSUE`
  3. `NO_TERTIARY_ISSUE`
- **Reviewer Audit Note**: *Standard conforming prime loan record. Full data integrity verified across all 4 evidence layers. Automatically approve.*

#### Case #18: Loan `F19Q10001397` (Period: `201903`)

- **Composite Anomaly Score**: `0.1842 / 1.0000` | **Action**: `AUTO_APPROVE` (Confidence: 89%) | **Exception**: `NONE`
- **Loan Attributes**: Orig Bal: $257,000.00 | Current Bal: $257,000.00 | Status: `CURRENT` | DPD: `0` | Doc Status: `VERIFIED` | Rem Term: `359m`
- **Evidence Decomposition**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.184` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.000` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Top Root Cause Drivers (Mathematical Sum = 0.184)**:
  1. `ISOLATION_FOREST_OUTLIER (+0.184)`
  2. `NO_SECONDARY_ISSUE`
  3. `NO_TERTIARY_ISSUE`
- **Reviewer Audit Note**: *Standard conforming prime loan record. Full data integrity verified across all 4 evidence layers. Automatically approve.*

#### Case #19: Loan `F19Q10001708` (Period: `201903`)

- **Composite Anomaly Score**: `0.1642 / 1.0000` | **Action**: `AUTO_APPROVE` (Confidence: 90%) | **Exception**: `NONE`
- **Loan Attributes**: Orig Bal: $73,000.00 | Current Bal: $73,000.00 | Status: `CURRENT` | DPD: `0` | Doc Status: `VERIFIED` | Rem Term: `359m`
- **Evidence Decomposition**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.164` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.000` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Top Root Cause Drivers (Mathematical Sum = 0.164)**:
  1. `ISOLATION_FOREST_OUTLIER (+0.164)`
  2. `NO_SECONDARY_ISSUE`
  3. `NO_TERTIARY_ISSUE`
- **Reviewer Audit Note**: *Standard conforming prime loan record. Full data integrity verified across all 4 evidence layers. Automatically approve.*

#### Case #20: Loan `F19Q10001904` (Period: `201903`)

- **Composite Anomaly Score**: `0.1780 / 1.0000` | **Action**: `AUTO_APPROVE` (Confidence: 89%) | **Exception**: `NONE`
- **Loan Attributes**: Orig Bal: $248,000.00 | Current Bal: $248,000.00 | Status: `CURRENT` | DPD: `0` | Doc Status: `VERIFIED` | Rem Term: `359m`
- **Evidence Decomposition**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.178` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.000` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Top Root Cause Drivers (Mathematical Sum = 0.178)**:
  1. `ISOLATION_FOREST_OUTLIER (+0.178)`
  2. `NO_SECONDARY_ISSUE`
  3. `NO_TERTIARY_ISSUE`
- **Reviewer Audit Note**: *Standard conforming prime loan record. Full data integrity verified across all 4 evidence layers. Automatically approve.*

---

*Report generated by Intain AI Track — Phase 3: Anomaly & Exception Detection Engine*
