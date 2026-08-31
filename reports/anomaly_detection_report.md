# Anomaly & Exception Intelligence Report

**Intain AI Track 2026 — Phase 3: Anomaly & Exception Detection Engine**  
**Generated**: 2026-08-31 18:44:33  

---

## 1. Executive Summary & Mathematical Weight Calibration

The Anomaly & Exception Engine fuses 4 orthogonal evidence layers to detect contractual, behavioral, and cross-source reporting anomalies.

### 1a. Evidence Weight Calibration (Differential Evolution on Training Slice)

- **Optimization Status**: `SUCCESSFULLY_CALIBRATED`
- **Baseline Equal Weights PR-AUC**: `0.3164`
- **Optimized Weights PR-AUC**: `0.3239` ($\Delta = +0.0075$)

| Evidence Layer | Focus & Input Scope | Equal Baseline Weight | **Calibrated Optimal Weight** |
| :--- | :--- | ---: | ---: |
| **$S_{\text{ML}}$ (Unsupervised)** | Non-rule behavioral & interaction space (`IsolationForest`, contamination=3.15%) | 25.0% | **36.4%** |
| **$S_{\text{rule}}$ (Validation Rules)** | All 8 contractual & feed rules from `validation_rules.json` (VR-001..VR-008) | 35.0% | **46.3%** |
| **$S_{\text{servicer}}$ (Reconciliation)** | Cross-source status discrepancies & payment timing drift | 25.0% | **13.5%** |
| **$S_{\text{DQ}}$ (Completeness)** | Non-rule missingness and schema format integrity | 15.0% | **3.8%** |

### 1b. Dataset-Level Anomaly Statistics

| Metric | Training Set (Historical) | Test Set (Evaluation) |
| :--- | ---: | ---: |
| Total Records Evaluated | 407,733 | 304,374 |
| Mean Anomaly Score | 0.0793 | 0.1661 |
| Flagged Exceptions (`exception_required == 1`) | 37,575 (9.22%) | 19,615 (6.44%) |
| High Risk Anomaly Score (>= 0.50) | 415 (0.10%) | 443 (0.15%) |

## 2. Prescriptive Reviewer Action Distribution (Test Set — Dynamic Confidence)

| Reviewer Action | Record Count | Percentage | Mean Confidence | Min Conf | Max Conf |
| :--- | ---: | ---: | ---: | ---: | ---: |
| `AUTO_APPROVE` | 284,641 | 93.52% | **0.90** | 0.85 | 0.99 |
| `REQUEST_CURE` | 9,772 | 3.21% | **0.86** | 0.80 | 0.98 |
| `OVERRIDE_SERVICER` | 3,164 | 1.04% | **0.81** | 0.80 | 0.98 |
| `MANUAL_AUDIT` | 2,871 | 0.94% | **0.90** | 0.88 | 0.95 |
| `ESCALATE_DOC_REVIEW` | 2,264 | 0.74% | **0.93** | 0.88 | 0.95 |
| `ACCEPT_PRIMARY` | 1,662 | 0.55% | **0.95** | 0.95 | 0.95 |

---

## 3. Stratified Reviewer Case Cards (24 Diverse Audit Cases)

> Each audit card presents full loan attributes, 4-layer score decomposition ($w_i \cdot S_i$), mathematically exact driver contributions summing to $S_{\text{anomaly}}$, and prescriptive reviewer guidance notes.

### Action Class: `MANUAL_AUDIT` (4 Example Audit Cards)

#### Case #01: Loan `F19Q10000290` (Period: `201902`)

- **Composite Anomaly Score**: `0.4305 / 1.0000` | **Action**: `MANUAL_AUDIT` (Confidence: 91%) | **Exception**: `INVALID_DATE`
- **Loan Attributes**: Orig Bal: $160,000.00 | Current Bal: $160,000.00 | Status: `CURRENT` | DPD: `0` | Doc Status: `VERIFIED` | Rem Term: `360m`
- **Evidence Decomposition**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.037` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.393` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Top Root Cause Drivers (Mathematical Sum = 0.430)**:
  1. `VR-003_INVALID_DATE_SEQUENCE (+0.393)`
  2. `ISOLATION_FOREST_OUTLIER (+0.037)`
  3. `NO_TERTIARY_ISSUE`
- **Reviewer Audit Note**: *Critical balance surge, term violation, or multi-rule contradiction detected. Escalate to senior audit team for balance tape recalculation and servicer feed verification.*

#### Case #02: Loan `F19Q10001353` (Period: `201902`)

- **Composite Anomaly Score**: `0.3606 / 1.0000` | **Action**: `MANUAL_AUDIT` (Confidence: 90%) | **Exception**: `INVALID_DATE`
- **Loan Attributes**: Orig Bal: $359,000.00 | Current Bal: $359,000.00 | Status: `CURRENT` | DPD: `0` | Doc Status: `MISSING_NOTE` | Rem Term: `360m`
- **Evidence Decomposition**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.037` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.324` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Top Root Cause Drivers (Mathematical Sum = 0.361)**:
  1. `VR-003_INVALID_DATE_SEQUENCE (+0.324)`
  2. `ISOLATION_FOREST_OUTLIER (+0.037)`
  3. `NO_TERTIARY_ISSUE`
- **Reviewer Audit Note**: *Critical balance surge, term violation, or multi-rule contradiction detected. Escalate to senior audit team for balance tape recalculation and servicer feed verification.*

#### Case #03: Loan `F19Q10003577` (Period: `201902`)

- **Composite Anomaly Score**: `0.5680 / 1.0000` | **Action**: `MANUAL_AUDIT` (Confidence: 92%) | **Exception**: `STATUS_CONFLICT`
- **Loan Attributes**: Orig Bal: $380,000.00 | Current Bal: $380,000.00 | Status: `CURRENT` | DPD: `90` | Doc Status: `VERIFIED` | Rem Term: `360m`
- **Evidence Decomposition**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.175` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.393` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Top Root Cause Drivers (Mathematical Sum = 0.568)**:
  1. `VR-002_STATUS_CONFLICT_90DPD (+0.393)`
  2. `ISOLATION_FOREST_OUTLIER (+0.175)`
  3. `NO_TERTIARY_ISSUE`
- **Reviewer Audit Note**: *Critical balance surge, term violation, or multi-rule contradiction detected. Escalate to senior audit team for balance tape recalculation and servicer feed verification.*

#### Case #04: Loan `F19Q10003861` (Period: `201902`)

- **Composite Anomaly Score**: `0.5315 / 1.0000` | **Action**: `MANUAL_AUDIT` (Confidence: 92%) | **Exception**: `BALANCE_INCONSISTENCY`
- **Loan Attributes**: Orig Bal: $335,000.00 | Current Bal: $474,071.99 | Status: `CURRENT` | DPD: `0` | Doc Status: `VERIFIED` | Rem Term: `360m`
- **Evidence Decomposition**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.069` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.463` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Top Root Cause Drivers (Mathematical Sum = 0.531)**:
  1. `VR-001_BALANCE_SURGE_142PCT (+0.463)`
  2. `ISOLATION_FOREST_OUTLIER (+0.069)`
  3. `NO_TERTIARY_ISSUE`
- **Reviewer Audit Note**: *Critical balance surge, term violation, or multi-rule contradiction detected. Escalate to senior audit team for balance tape recalculation and servicer feed verification.*

---

### Action Class: `ESCALATE_DOC_REVIEW` (4 Example Audit Cards)

#### Case #05: Loan `F19Q10000843` (Period: `201903`)

- **Composite Anomaly Score**: `0.1444 / 1.0000` | **Action**: `ESCALATE_DOC_REVIEW` (Confidence: 88%) | **Exception**: `DOCUMENT_GAP`
- **Loan Attributes**: Orig Bal: $85,000.00 | Current Bal: $85,000.00 | Status: `CURRENT` | DPD: `0` | Doc Status: `INCOMPLETE_INCOME` | Rem Term: `359m`
- **Evidence Decomposition**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.052` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.093` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Top Root Cause Drivers (Mathematical Sum = 0.144)**:
  1. `NORMAL_CONFORMING`
  2. `NO_SECONDARY_ISSUE`
  3. `NO_TERTIARY_ISSUE`
- **Reviewer Audit Note**: *Document verification incomplete (missing note / unverified appraisal). Request trailing document package from originator prior to credit decision.*

#### Case #06: Loan `F19Q10009387` (Period: `201903`)

- **Composite Anomaly Score**: `0.1615 / 1.0000` | **Action**: `ESCALATE_DOC_REVIEW` (Confidence: 88%) | **Exception**: `DOCUMENT_GAP`
- **Loan Attributes**: Orig Bal: $195,000.00 | Current Bal: $195,000.00 | Status: `CURRENT` | DPD: `0` | Doc Status: `INCOMPLETE_INCOME` | Rem Term: `359m`
- **Evidence Decomposition**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.069` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.093` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Top Root Cause Drivers (Mathematical Sum = 0.162)**:
  1. `VR-006_DOCUMENT_GAP_INCOMPLETE_INCOME (+0.093)`
  2. `ISOLATION_FOREST_OUTLIER (+0.069)`
  3. `NO_TERTIARY_ISSUE`
- **Reviewer Audit Note**: *Document verification incomplete (missing note / unverified appraisal). Request trailing document package from originator prior to credit decision.*

#### Case #07: Loan `F19Q10030187` (Period: `201903`)

- **Composite Anomaly Score**: `0.1770 / 1.0000` | **Action**: `ESCALATE_DOC_REVIEW` (Confidence: 95%) | **Exception**: `DOCUMENT_GAP`
- **Loan Attributes**: Orig Bal: $74,000.00 | Current Bal: $74,000.00 | Status: `CURRENT` | DPD: `0` | Doc Status: `MISSING_NOTE` | Rem Term: `359m`
- **Evidence Decomposition**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.084` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.093` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Top Root Cause Drivers (Mathematical Sum = 0.177)**:
  1. `VR-006_DOCUMENT_GAP_MISSING_NOTE (+0.093)`
  2. `ISOLATION_FOREST_OUTLIER (+0.085)`
  3. `NO_TERTIARY_ISSUE`
- **Reviewer Audit Note**: *Document verification incomplete (missing note / unverified appraisal). Request trailing document package from originator prior to credit decision.*

#### Case #08: Loan `F19Q10031211` (Period: `201903`)

- **Composite Anomaly Score**: `0.2214 / 1.0000` | **Action**: `ESCALATE_DOC_REVIEW` (Confidence: 88%) | **Exception**: `DOCUMENT_GAP`
- **Loan Attributes**: Orig Bal: $350,000.00 | Current Bal: $350,000.00 | Status: `CURRENT` | DPD: `0` | Doc Status: `INCOMPLETE_INCOME` | Rem Term: `359m`
- **Evidence Decomposition**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.129` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.093` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Top Root Cause Drivers (Mathematical Sum = 0.221)**:
  1. `ISOLATION_FOREST_OUTLIER (+0.129)`
  2. `VR-006_DOCUMENT_GAP_INCOMPLETE_INCOME (+0.093)`
  3. `NO_TERTIARY_ISSUE`
- **Reviewer Audit Note**: *Document verification incomplete (missing note / unverified appraisal). Request trailing document package from originator prior to credit decision.*

---

### Action Class: `OVERRIDE_SERVICER` (4 Example Audit Cards)

#### Case #09: Loan `F19Q10006346` (Period: `201902`)

- **Composite Anomaly Score**: `0.2076 / 1.0000` | **Action**: `OVERRIDE_SERVICER` (Confidence: 80%) | **Exception**: `SERVICER_CONFLICT`
- **Loan Attributes**: Orig Bal: $300,000.00 | Current Bal: $299,000.00 | Status: `CURRENT` | DPD: `0` | Doc Status: `VERIFIED` | Rem Term: `239m`
- **Evidence Decomposition**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.046` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.162` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Top Root Cause Drivers (Mathematical Sum = 0.208)**:
  1. `VR-007_SERVICER_BALANCE_DIFF_6PCT (+0.162)`
  2. `ISOLATION_FOREST_OUTLIER (+0.046)`
  3. `NO_TERTIARY_ISSUE`
- **Reviewer Audit Note**: *Cross-source servicer status conflict detected against verified primary transaction ledger. Retain primary ledger balance and override servicer record.*

#### Case #10: Loan `F19Q10000960` (Period: `201903`)

- **Composite Anomaly Score**: `0.2012 / 1.0000` | **Action**: `OVERRIDE_SERVICER` (Confidence: 80%) | **Exception**: `SERVICER_CONFLICT`
- **Loan Attributes**: Orig Bal: $256,000.00 | Current Bal: $256,000.00 | Status: `CURRENT` | DPD: `0` | Doc Status: `VERIFIED` | Rem Term: `359m`
- **Evidence Decomposition**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.039` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.162` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Top Root Cause Drivers (Mathematical Sum = 0.201)**:
  1. `VR-007_SERVICER_BALANCE_DIFF_10PCT (+0.162)`
  2. `ISOLATION_FOREST_OUTLIER (+0.039)`
  3. `NO_TERTIARY_ISSUE`
- **Reviewer Audit Note**: *Cross-source servicer status conflict detected against verified primary transaction ledger. Retain primary ledger balance and override servicer record.*

#### Case #11: Loan `F19Q10002998` (Period: `201903`)

- **Composite Anomaly Score**: `0.2058 / 1.0000` | **Action**: `OVERRIDE_SERVICER` (Confidence: 80%) | **Exception**: `SERVICER_CONFLICT`
- **Loan Attributes**: Orig Bal: $219,000.00 | Current Bal: $218,000.00 | Status: `CURRENT` | DPD: `0` | Doc Status: `VERIFIED` | Rem Term: `359m`
- **Evidence Decomposition**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.044` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.162` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Top Root Cause Drivers (Mathematical Sum = 0.206)**:
  1. `VR-007_SERVICER_BALANCE_DIFF_14PCT (+0.162)`
  2. `ISOLATION_FOREST_OUTLIER (+0.044)`
  3. `NO_TERTIARY_ISSUE`
- **Reviewer Audit Note**: *Cross-source servicer status conflict detected against verified primary transaction ledger. Retain primary ledger balance and override servicer record.*

#### Case #12: Loan `F19Q10007829` (Period: `201903`)

- **Composite Anomaly Score**: `0.1842 / 1.0000` | **Action**: `OVERRIDE_SERVICER` (Confidence: 80%) | **Exception**: `SERVICER_CONFLICT`
- **Loan Attributes**: Orig Bal: $312,000.00 | Current Bal: $312,000.00 | Status: `CURRENT` | DPD: `0` | Doc Status: `VERIFIED` | Rem Term: `359m`
- **Evidence Decomposition**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.022` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.162` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Top Root Cause Drivers (Mathematical Sum = 0.184)**:
  1. `VR-007_SERVICER_BALANCE_DIFF_13PCT (+0.162)`
  2. `ISOLATION_FOREST_OUTLIER (+0.022)`
  3. `NO_TERTIARY_ISSUE`
- **Reviewer Audit Note**: *Cross-source servicer status conflict detected against verified primary transaction ledger. Retain primary ledger balance and override servicer record.*

---

### Action Class: `REQUEST_CURE` (4 Example Audit Cards)

#### Case #13: Loan `F19Q10000418` (Period: `201901`)

- **Composite Anomaly Score**: `0.2968 / 1.0000` | **Action**: `REQUEST_CURE` (Confidence: 80%) | **Exception**: `INVALID_DATE`
- **Loan Attributes**: Orig Bal: $247,000.00 | Current Bal: $247,000.00 | Status: `CURRENT` | DPD: `0` | Doc Status: `VERIFIED` | Rem Term: `360m`
- **Evidence Decomposition**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.065` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.231` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Top Root Cause Drivers (Mathematical Sum = 0.297)**:
  1. `VR-003_INVALID_DATE_SEQUENCE (+0.231)`
  2. `ISOLATION_FOREST_OUTLIER (+0.065)`
  3. `NO_TERTIARY_ISSUE`
- **Reviewer Audit Note**: *Borrower is in active delinquency roll or status conflict. Request workout agreement, forbearance schedule, or servicer cure timeline.*

#### Case #14: Loan `F19Q10002275` (Period: `201903`)

- **Composite Anomaly Score**: `0.2144 / 1.0000` | **Action**: `REQUEST_CURE` (Confidence: 80%) | **Exception**: `INVALID_TERM`
- **Loan Attributes**: Orig Bal: $412,000.00 | Current Bal: $411,000.00 | Status: `CURRENT` | DPD: `0` | Doc Status: `VERIFIED` | Rem Term: `450m`
- **Evidence Decomposition**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.052` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.162` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Top Root Cause Drivers (Mathematical Sum = 0.214)**:
  1. `VR-004_INVALID_TERM_450M (+0.162)`
  2. `ISOLATION_FOREST_OUTLIER (+0.052)`
  3. `NO_TERTIARY_ISSUE`
- **Reviewer Audit Note**: *Borrower is in active delinquency roll or status conflict. Request workout agreement, forbearance schedule, or servicer cure timeline.*

#### Case #15: Loan `F19Q10003868` (Period: `201903`)

- **Composite Anomaly Score**: `0.3124 / 1.0000` | **Action**: `REQUEST_CURE` (Confidence: 98%) | **Exception**: `STATUS_CONFLICT`
- **Loan Attributes**: Orig Bal: $70,000.00 | Current Bal: $70,000.00 | Status: `CURRENT` | DPD: `90` | Doc Status: `VERIFIED` | Rem Term: `359m`
- **Evidence Decomposition**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.150` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.162` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Top Root Cause Drivers (Mathematical Sum = 0.312)**:
  1. `VR-002_STATUS_CONFLICT_90DPD (+0.162)`
  2. `ISOLATION_FOREST_OUTLIER (+0.150)`
  3. `NO_TERTIARY_ISSUE`
- **Reviewer Audit Note**: *Borrower is in active delinquency roll or status conflict. Request workout agreement, forbearance schedule, or servicer cure timeline.*

#### Case #16: Loan `F19Q10009654` (Period: `201903`)

- **Composite Anomaly Score**: `0.3749 / 1.0000` | **Action**: `REQUEST_CURE` (Confidence: 98%) | **Exception**: `STATUS_CONFLICT`
- **Loan Attributes**: Orig Bal: $229,000.00 | Current Bal: $229,000.00 | Status: `CURRENT` | DPD: `90` | Doc Status: `VERIFIED` | Rem Term: `359m`
- **Evidence Decomposition**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.213` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.162` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Top Root Cause Drivers (Mathematical Sum = 0.375)**:
  1. `ISOLATION_FOREST_OUTLIER (+0.213)`
  2. `VR-002_STATUS_CONFLICT_90DPD (+0.162)`
  3. `NO_TERTIARY_ISSUE`
- **Reviewer Audit Note**: *Borrower is in active delinquency roll or status conflict. Request workout agreement, forbearance schedule, or servicer cure timeline.*

---

### Action Class: `ACCEPT_PRIMARY` (4 Example Audit Cards)

#### Case #17: Loan `F19Q10003084` (Period: `201903`)

- **Composite Anomaly Score**: `0.1957 / 1.0000` | **Action**: `ACCEPT_PRIMARY` (Confidence: 95%) | **Exception**: `STALE_RECORD`
- **Loan Attributes**: Orig Bal: $366,000.00 | Current Bal: $363,000.00 | Status: `CURRENT` | DPD: `0` | Doc Status: `VERIFIED` | Rem Term: `179m`
- **Evidence Decomposition**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.103` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.093` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Top Root Cause Drivers (Mathematical Sum = 0.196)**:
  1. `ISOLATION_FOREST_OUTLIER (+0.103)`
  2. `VR-008_FEED_STALENESS_EXCEEDS_60D (+0.093)`
  3. `NO_TERTIARY_ISSUE`
- **Reviewer Audit Note**: *Minor timing/escrow rounding discrepancy between servicer and primary (< 3%). Accept primary servicing ledger.*

#### Case #18: Loan `F19Q10004199` (Period: `201903`)

- **Composite Anomaly Score**: `0.1850 / 1.0000` | **Action**: `ACCEPT_PRIMARY` (Confidence: 95%) | **Exception**: `STALE_RECORD`
- **Loan Attributes**: Orig Bal: $70,000.00 | Current Bal: $69,000.00 | Status: `CURRENT` | DPD: `0` | Doc Status: `VERIFIED` | Rem Term: `359m`
- **Evidence Decomposition**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.092` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.093` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Top Root Cause Drivers (Mathematical Sum = 0.185)**:
  1. `VR-008_FEED_STALENESS_EXCEEDS_60D (+0.093)`
  2. `ISOLATION_FOREST_OUTLIER (+0.092)`
  3. `NO_TERTIARY_ISSUE`
- **Reviewer Audit Note**: *Minor timing/escrow rounding discrepancy between servicer and primary (< 3%). Accept primary servicing ledger.*

#### Case #19: Loan `F19Q10005434` (Period: `201903`)

- **Composite Anomaly Score**: `0.2295 / 1.0000` | **Action**: `ACCEPT_PRIMARY` (Confidence: 95%) | **Exception**: `STALE_RECORD`
- **Loan Attributes**: Orig Bal: $188,000.00 | Current Bal: $188,000.00 | Status: `CURRENT` | DPD: `0` | Doc Status: `VERIFIED` | Rem Term: `359m`
- **Evidence Decomposition**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.137` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.093` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Top Root Cause Drivers (Mathematical Sum = 0.230)**:
  1. `ISOLATION_FOREST_OUTLIER (+0.137)`
  2. `VR-008_FEED_STALENESS_EXCEEDS_60D (+0.093)`
  3. `NO_TERTIARY_ISSUE`
- **Reviewer Audit Note**: *Minor timing/escrow rounding discrepancy between servicer and primary (< 3%). Accept primary servicing ledger.*

#### Case #20: Loan `F19Q10011501` (Period: `201903`)

- **Composite Anomaly Score**: `0.2207 / 1.0000` | **Action**: `ACCEPT_PRIMARY` (Confidence: 95%) | **Exception**: `STALE_RECORD`
- **Loan Attributes**: Orig Bal: $75,000.00 | Current Bal: $75,000.00 | Status: `CURRENT` | DPD: `0` | Doc Status: `VERIFIED` | Rem Term: `359m`
- **Evidence Decomposition**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.128` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.093` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Top Root Cause Drivers (Mathematical Sum = 0.221)**:
  1. `ISOLATION_FOREST_OUTLIER (+0.128)`
  2. `VR-008_FEED_STALENESS_EXCEEDS_60D (+0.093)`
  3. `NO_TERTIARY_ISSUE`
- **Reviewer Audit Note**: *Minor timing/escrow rounding discrepancy between servicer and primary (< 3%). Accept primary servicing ledger.*

---

### Action Class: `AUTO_APPROVE` (4 Example Audit Cards)

#### Case #21: Loan `F19Q10000418` (Period: `201902`)

- **Composite Anomaly Score**: `0.0545 / 1.0000` | **Action**: `AUTO_APPROVE` (Confidence: 96%) | **Exception**: `NONE`
- **Loan Attributes**: Orig Bal: $247,000.00 | Current Bal: $246,000.00 | Status: `CURRENT` | DPD: `0` | Doc Status: `VERIFIED` | Rem Term: `359m`
- **Evidence Decomposition**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.054` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.000` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Top Root Cause Drivers (Mathematical Sum = 0.054)**:
  1. `NORMAL_CONFORMING`
  2. `NO_SECONDARY_ISSUE`
  3. `NO_TERTIARY_ISSUE`
- **Reviewer Audit Note**: *Standard conforming prime loan record. Full data integrity verified across all 4 evidence layers. Automatically approve.*

#### Case #22: Loan `F19Q10001397` (Period: `201903`)

- **Composite Anomaly Score**: `0.1632 / 1.0000` | **Action**: `AUTO_APPROVE` (Confidence: 90%) | **Exception**: `NONE`
- **Loan Attributes**: Orig Bal: $257,000.00 | Current Bal: $257,000.00 | Status: `CURRENT` | DPD: `0` | Doc Status: `VERIFIED` | Rem Term: `359m`
- **Evidence Decomposition**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.163` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.000` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Top Root Cause Drivers (Mathematical Sum = 0.163)**:
  1. `ISOLATION_FOREST_OUTLIER (+0.163)`
  2. `NO_SECONDARY_ISSUE`
  3. `NO_TERTIARY_ISSUE`
- **Reviewer Audit Note**: *Standard conforming prime loan record. Full data integrity verified across all 4 evidence layers. Automatically approve.*

#### Case #23: Loan `F19Q10005590` (Period: `201903`)

- **Composite Anomaly Score**: `0.1590 / 1.0000` | **Action**: `AUTO_APPROVE` (Confidence: 90%) | **Exception**: `NONE`
- **Loan Attributes**: Orig Bal: $57,000.00 | Current Bal: $57,000.00 | Status: `CURRENT` | DPD: `0` | Doc Status: `VERIFIED` | Rem Term: `359m`
- **Evidence Decomposition**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.159` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.000` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Top Root Cause Drivers (Mathematical Sum = 0.159)**:
  1. `ISOLATION_FOREST_OUTLIER (+0.159)`
  2. `NO_SECONDARY_ISSUE`
  3. `NO_TERTIARY_ISSUE`
- **Reviewer Audit Note**: *Standard conforming prime loan record. Full data integrity verified across all 4 evidence layers. Automatically approve.*

#### Case #24: Loan `F19Q10010213` (Period: `201903`)

- **Composite Anomaly Score**: `0.1668 / 1.0000` | **Action**: `AUTO_APPROVE` (Confidence: 90%) | **Exception**: `NONE`
- **Loan Attributes**: Orig Bal: $325,000.00 | Current Bal: $324,000.00 | Status: `CURRENT` | DPD: `0` | Doc Status: `VERIFIED` | Rem Term: `359m`
- **Evidence Decomposition**: ML Layer ($w_1 \cdot S_{\text{ML}}$): `0.167` | Rule Layer ($w_2 \cdot S_{\text{rule}}$): `0.000` | Servicer Layer ($w_3 \cdot S_{\text{servicer}}$): `0.000` | DQ Layer ($w_4 \cdot S_{\text{DQ}}$): `0.000`
- **Top Root Cause Drivers (Mathematical Sum = 0.167)**:
  1. `ISOLATION_FOREST_OUTLIER (+0.167)`
  2. `NO_SECONDARY_ISSUE`
  3. `NO_TERTIARY_ISSUE`
- **Reviewer Audit Note**: *Standard conforming prime loan record. Full data integrity verified across all 4 evidence layers. Automatically approve.*

---

*Report generated by Intain AI Track — Phase 3: Anomaly & Exception Detection Engine*
