# Model Card — Loan Performance Intelligence Engine

**Intain Campus FinTech Challenge 2026 | AI Track**  
**Version**: 1.0.0  
**Date**: August 2026  
**Authors**: Antigravity AI Assistant & Engineering Team  
**License**: MIT / Competition Evaluation License  

---

## 1. Model Details

### Overview
The **Loan Performance Intelligence Engine** is a multi-tier, hybrid predictive and anomaly detection system engineered for residential mortgage portfolios. It unifies non-LLM supervised machine learning, survival analysis, unsupervised anomaly detection, macroeconomic stress simulation, TreeSHAP explainability, and governed LLM reviewer copilots.

### Model Architecture Breakdown
| Component Layer | Algorithm / Methodology | Primary Purpose | Key Hyperparameters / Config |
| :--- | :--- | :--- | :--- |
| **Credit Risk Classifiers** | XGBoost + Isotonic Calibration | 12M Default, 3M/6M Delinquency | `max_depth=4-6`, `learning_rate=0.03-0.08`, `scale_pos_weight=16-33x` |
| **Duration Risk Classifier** | XGBoost + Isotonic Calibration | 12M Prepayment Velocity | `max_depth=5`, `learning_rate=0.05`, `scale_pos_weight=1.9x` |
| **State Transition Model** | Multi-Class XGBoost | 1-Month Ahead Roll-State (`CURRENT`, `30DPD`, `60DPD`, `90PLUS_DPD`, `PREPAID`) | `objective=multi:softprob`, `num_class=5` |
| **Survival & Hazard Engine** | Kaplan-Meier & Cox PH | Time-to-Default & Prepayment Curves | `penalizer=0.1` (Ridge regularization), C-stat: `0.6866` |
| **Anomaly Detection Layer** | Hybrid Arbitrator (Isolation Forest + Deterministic Rules + Servicer Reconciler) | Record-level Anomaly Score & Action Precedence | Weights: $w_{\text{Rule}}=46.5\%$, $w_{\text{ML}}=34.4\%$, $w_{\text{Serv}}=15.2\%$, $w_{\text{DQ}}=3.8\%$ |
| **Explainability Layer** | TreeSHAP (`shap.TreeExplainer`) | Global feature beeswarms & local waterfall attribution | Directional attribution (positive log-odds vs. negative path length) |
| **Reviewer Copilot** | Grounded LLM + Knowledge Retrieval | Structured reviewer memos & hallucination auditing | Grounded on `data_dictionary.md` and `validation_rules.json` |

---

## 2. Intended Use & Scope

### Primary Intended Uses
- **Secondary Mortgage Market Due Diligence**: Automated tape auditing and data-quality scoring for loan pools prior to securitization.
- **Servicer Feed Reconciliation**: Cross-system conflict detection (VR-007 balance divergence, status mismatches, feed staleness).
- **Portfolio Loss & Capital Stress Testing**: Cash flow, default, and prepayment trajectory forecasting under macroeconomic rate and HPA shocks.
- **Human Reviewer Decision Support**: Synthesizing natural language memos to accelerate manual underwriting and compliance exceptions.

### Out-of-Scope & Non-Intended Uses
- **Fully Autonomous Consumer Credit Denials**: The engine is strictly a secondary-market decision-support tool. It must NOT be used as a standalone autonomous credit decisioning system under ECOA / FCRA without human auditor oversight and adverse action notices.
- **Commercial Real Estate (CRE) / Unsecured Lending**: The models are trained strictly on residential 1-to-4 family single-family mortgage performance data.

---

## 3. Factors & Demographic Cohorts

### Evaluated Risk Dimensions
The model's performance and stability are audited across five primary structural dimensions:
1. **Credit Score Bands**: Subprime ($\le 620$), Fair ($621-680$), Good ($681-740$), Very Good ($741-800$), Exceptional ($801+$).
2. **Collateral Leverage (LTV Bands)**: Low ($\le 60\%$), Moderate ($61-75\%$), High ($76-80\%$, $81-90\%$), Elevated ($91-95\%$), Super-High ($>95\%$).
3. **Debt-to-Income (DTI Bands)**: $\le 20\%$, $21-30\%$, $31-40\%$, $41-45\%$, $46-50\%$, $>50\%$.
4. **Geography (Top States)**: CA, TX, FL, NY, IL, NC, GA, VA, NJ, OH.
5. **Servicer Entities**: Rocket, Wells Fargo, JPMorgan Chase, Pennymac, Nationstar (Mr. Cooper), Newrez, Freedom, U.S. Bank.

---

## 4. Quantitative Performance Summary

### Held-Out Chronological Validation (Untouched 15% Cohort)
| Target Horizon | Baseline Model | Baseline PR-AUC | **XGBoost PR-AUC** | **XGBoost ROC-AUC** | **Optimal F1 (Thresh)** | Brier Score |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: |
| **`next_12m_default_flag`** | Scaled Logistic Regression | 0.1622 | **0.3380** | **0.8595** | **0.3850** (`@0.22`) | 0.0273 |
| **`next_12m_prepayment_flag`** | Scaled Logistic Regression | 0.3791 | **0.5048** | **0.6542** | **0.5368** (`@0.26`) | 0.1943 |
| **`next_3m_delinquency_flag`** | Scaled Logistic Regression | 0.3134 | **0.6368** | **0.8916** | **0.6480** (`@0.16`) | 0.0253 |
| **`next_6m_delinquency_flag`** | Scaled Logistic Regression | 0.3019 | **0.5812** | **0.8827** | **0.5940** (`@0.17`) | 0.0442 |
| **`exception_required`\*** | Scaled Logistic Regression | 0.6079 | **0.9964** | **0.9997** | **0.9926** (`@0.26`) | 0.0008 |
| **`next_state` (Multi-class)** | Decision Tree Baseline | Macro-F1: 0.5765 | **Macro-F1: 0.6479** | **Weighted-F1: 0.9316** | — | — |
| **`exception_type` (Multi-class)**| Decision Tree Baseline | Macro-F1: 1.0000 | **Macro-F1: 0.9855** | **Weighted-F1: 0.9988** | — | — |

> **\* Operational vs. Behavioral Target Transparency Note**:  
> Unlike forward-looking credit risk projections (`next_12m_default_flag`, `next_12m_prepayment_flag`), `exception_required` and `exception_type` are instantaneous data-quality targets defined by contractual validation rule breaches (VR-001..VR-008). TreeSHAP feature attribution demonstrates that **78.74%** of feature importance derives from structural snapshot indicators (`maturity_pressure`: 28.96%, `document_status_enc`: 26.00%, `balance_pct_original`: 23.78%). The models function as empirical soft-rule reconstructors, explaining why decision trees and XGBoost partition deterministic data-quality breaches with near-perfect F1/AUC while behavioral credit forecasts maintain realistic market difficulty.

---

## 5. Training, Validation & Leakage Controls

### Dataset Profile
- **Training Cohort**: 407,733 monthly records ($\le 2021-06$) across 20,000 unique loans.
- **Holdout Test Set**: 304,374 monthly records ($> 2021-06$).

### Leakage Eradication Protocols
1. **Strict Chronological 3-Way Split**: Data is ordered globally by `reporting_month`. Split into Train (70%), Calibration (15%), and untouched Validation (15%). Per-loan history and lag features are computed prior to the calendar-time split boundary.
2. **Transition-Only Universe Masking**: Supervised credit models exclude terminal records (`default_flag == 1` or `prepayment_flag == 1`) from training matrices, preventing artificial memorization of pre-existing default states.
3. **Inference Lag Persistence**: `FeatureEngineer.history_tail_df` stores the boundary state per loan, eliminating inference lag collapse on forward test batches.
4. **Missingness Sentinel Masking**: Missing/unknown ordinals (`-1`) are masked before computing interaction products (`dti_x_ltv`, `distress_score`), eliminating false prime risk distortions.

---

## 6. Ethical Considerations & Fair Lending Compliance

- **Fair Lending Safeguards**: The model excludes protected class attributes (race, gender, marital status, national origin).
- **Proxy Variable Mitigation**: Geographic features (`state`) are evaluated solely as macroeconomic and legal foreclosure timeline proxies.
- **Explainability & Contestability**: Every loan record produces 3 distinct TreeSHAP drivers (`top_driver_1`, `top_driver_2`, `top_driver_3`), providing borrowers and secondary market auditors with complete visibility into adverse risk attributions.

---

## 7. Caveats, Known Limitations & Operational Guidelines

1. **Macroeconomic Sensitivity**: In severe stagflation scenarios ($>+200\text{ bps}$ interest rate shock and $>-15\%$ HPA), non-linear default accelerations should be calibrated against stress scenarios generated in Phase 5.
2. **Human-in-the-Loop Requirement**: All LLM Reviewer Copilot memos are advisory recommendations. Secondary credit committees must maintain final override and approval authority.
3. **Periodic Recalibration**: Anomaly weights and Isotonic calibration curves should be recalibrated quarterly to adapt to changing servicer reporting practices and interest rate environments.
