# AI Development Log — Intain AI Track 2026
**Project**: Loan Performance Intelligence Engine  
**Tracking Start**: 2026-08-29  

---

## 1. AI Tools & Models Used
- **Antigravity AI Assistant** (Powered by Claude / Gemini) — Architecture design, pipeline generation, optimization, and code execution.
- **Python Ecosystem**: pandas, lightgbm, xgboost, lifelines, shap, optuna, scikit-learn, imbalanced-learn, mlflow.

---

## 2. Representative Prompts & Development Iterations

### Phase 0: Environment Setup & Data Pack Assembly
- **Prompt**: Ingest Freddie Mac 2019 Single-Family sample files (`sample_orig_2019.txt` and `sample_perf_2019.txt`) and construct the official 8-file hackathon dataset pack matching Section 6 and 7 of the problem statement.
- **Outcome**: Extracted 20,000 loans with 712,107 monthly performance panel records. Applied strict time-aware splitting (407,733 train rows through 2021-06; 304,374 forward holdout test rows). Generated secondary servicer conflict feeds, validation rules, macroeconomic stress parameters, and data dictionaries.

---

## 3. Accepted vs. Rejected AI Outputs

| Timestamp | Component | AI Proposal | Human / Technical Decision | Rationale |
| :--- | :--- | :--- | :--- | :--- |
| 2026-08-29 | Data Ingestion | Use 2025 single-quarter raw dump | **REJECTED** | 2025Q2 lacked multi-year default and prepayment outcomes (only 12 months old). Swapped to 2019 multi-year Freddie Mac benchmark. |
| 2026-08-29 | Data Splitting | Random row-level train/val split | **REJECTED** | Problem statement explicitly penalizes random splits across panel data. Enforced strict calendar-time cut with per-loan history lag computation prior to the split boundary. |
| 2026-08-29 | Data Packaging | Custom 8-file pipeline in `src/data/builder.py` | **ACCEPTED** | Generates all 8 required files with clean forward target labels and ~5% servicer conflict rate for downstream reconciliation tasks. |

---

## 4. Code Ownership & Share by Module

| Module | Purpose | Estimated AI Share | Human Review & Verification |
| :--- | :--- | :--- | :--- |
| `src/data/builder.py` | Dataset extraction & transformation | 90% | Verified schema alignment with Section 6 and 7, validated no look-ahead target leakage. |
| `src/data/feature_engineer.py` | Lag persistence & macro features | 85% | Audited boundary lag states and zero-leakage ordinal mappings. |
| `src/models/trainer.py` | Supervised model training & calibration | 80% | Verified 3-way time-split and Isotonic calibration isolation. |
| `src/models/anomaly_engine.py` | 4-Layer hybrid anomaly arbitrator | 85% | Solved Differential Evolution weights; verified 6-tier precedence. |
| `src/llm/reviewer_copilot.py` | Grounded reviewer memo generation | 85% | Audited data dictionary lookup and governance banners. |
| `src/llm/hallucination_auditor.py` | Guardrail audit & rejection catalog | 90% | Verified 4 failure modes against deterministic rule overrides. |
| `src/utils/submission_builder.py` | Final competition submission assembler | 90% | Enforced 304,374-row schema validation and zero-null assertions. |
| `logs/ai_development_log.md` | Development trajectory tracking | 85% | Audited for authentic progression and rejected outputs. |

---

## 5. Development Trajectory & Phase Milestones

### Entry: Git Configuration & Repository Hygiene
- **Action**: Created comprehensive `.gitignore`.
- **Ignored**: ~8 GB raw Freddie Mac quarterlies, processed CSVs (>250MB), serialized `.pkl` models, MLflow tracking runs (`mlruns/`), Python caches, virtual environments, and system files.
- **Tracked**: Source code, documentation (`data_dictionary.md`, `validation_rules.json`), reports, and AI development log.

### Entry: Phase 2 ML Pipeline Refactoring — Leakage Elimination & Calibration Fix
- **Identified Defect**: In-sample evaluation where production model refitted on all data was evaluated on `val_split`; isotonic calibrator was fit on same validation set.
- **Architectural Fix Implemented**:
  1. Global chronological ordering by `(reporting_month, loan_id)`.
  2. 3-Way time split: Train 70% (`X_tr`), Calibration 15% (`X_cal`), and Held-Out Validation 15% (`X_val`).
  3. Two-tier model pattern: `val_model` trained only on `X_tr`, calibrated on `X_cal`, and evaluated strictly out-of-sample on untouched `X_val`.
  4. Scaled Logistic Regression baseline using `SimpleImputer` + `StandardScaler` pipeline.
  5. XGBoost native `NaN` routing preserved (no blind `fillna(0)`).
  6. F1 threshold optimization dynamically computed on held-out slice.
  7. Multi-class state transition model consolidated 5 clean states with 0.6479 Macro-F1 / 0.9316 Weighted-F1.
- **Outcome**: Honest, publication-grade benchmark with 0.8595 ROC-AUC on 12m Default, 0.8916 ROC-AUC on 3m Delinquency, and C-statistic of 0.6866 on Cox PH survival.

### Entry: Phase 3 Anomaly & Exception Detection Engine Built & Verified
- **Architecture**:
  1. Orthogonal Unsupervised ML: Isolation Forest (`n_estimators=200`, `contamination=0.0315`, train-only) fitted on non-rule behavioral space.
  2. Deterministic Rule Breach Evaluator: VR-001 to VR-008 severity penalties.
  3. Servicer Cross-Reconciliation Engine: Discrepancy and staleness flags.
  4. Structural Data Quality Evaluator: Non-rule missingness and format integrity.
  5. Mathematical Weight Calibration: Solved optimal weights ($w_{\text{ML}}=34.4\%$, $w_{\text{Rule}}=46.5\%$, $w_{\text{Servicer}}=15.2\%$, $w_{\text{DQ}}=3.8\%$) on training slice via Differential Evolution.
  6. Reviewer Action Precedence Matrix: 6-tier deterministic hierarchy (`MANUAL_AUDIT` -> `ESCALATE_DOC_REVIEW` -> `OVERRIDE_SERVICER` -> `REQUEST_CURE` -> `ACCEPT_PRIMARY` -> `AUTO_APPROVE`).
- **Deliverables Produced**:
  * `models/anomaly_engine.pkl`
  * `data/processed/phase3_anomaly_scores_test.csv` (304,374 test records scored)
  * `reports/anomaly_detection_report.md` (24 stratified audit case cards across all 6 action classes)
- **Case Selection Stratification (24 Case Cards)**:
  * Stratified strictly across all 6 prescriptive reviewer action classes (4 cases per action class: `MANUAL_AUDIT`, `ESCALATE_DOC_REVIEW`, `OVERRIDE_SERVICER`, `REQUEST_CURE`, `ACCEPT_PRIMARY`, `AUTO_APPROVE`).

### Entry: Full Pipeline Remediation (Right-Censoring, Zero-Leakage Static Encodings, Macro Features)
- **Modifications Executed**:
  1. **Right-Censoring Applied**: Rebuilt forward-looking target generation in `src/data/builder.py`. Records with truncated terminal observation windows now output `NaN` instead of false `0`s. `src/models/trainer.py` dynamically filters uncensored rows per target horizon.
  2. **Zero-Leakage Static Mappings**: Replaced dataset-wide `LabelEncoder` with deterministic dictionary mappings in `src/data/feature_engineer.py`.
  3. **Macroeconomic Linkage**: Added `market_avg_rate`, `rate_spread_to_market`, and `prepayment_incentive` as continuous features (total 44 features derived) enabling direct interest rate shocks in Phase 5.
  4. **Inference Lag State Persistence**: Implemented `history_tail_df` persistence in `src/data/feature_engineer.py`. Eliminates test boundary lag collapse for all 20,000 loans.
- **Metrics Refreshed**:
  * `next_3m_delinquency_flag`: ROC-AUC = 0.8916, PR-AUC = 0.6368, Optimal F1 = 0.6480
  * `next_6m_delinquency_flag`: ROC-AUC = 0.8827, PR-AUC = 0.5812, Optimal F1 = 0.5940
  * `next_12m_default_flag`: ROC-AUC = 0.8595, PR-AUC = 0.3380, Optimal F1 = 0.3850
  * `next_12m_prepayment_flag`: ROC-AUC = 0.6542, PR-AUC = 0.5048, Optimal F1 = 0.5368
  * Cox PH Concordance Index: 0.6866
- **Operational vs. Behavioral Target Analysis (`exception_required`)**:
  * `exception_required` is an instantaneous data-quality flag (1 if a record breaches VR-001..VR-008). 
  * Feature attribution analysis reveals that 78.74% of feature importance for this model derives from structural snapshot indicators (`maturity_pressure`: 28.96%, `document_status_enc`: 26.00%, `balance_pct_original`: 23.78%). 
  * It operates as an empirical soft-rule reconstructor rather than a forward-looking credit risk forecast, explaining why instantaneous rule reconstruction achieves near-perfect metrics while forward behavioral outcomes (`next_12m_default_flag`, `next_12m_prepayment_flag`) exhibit realistic market difficulty.

### Entry: Phase 4 Model Explainability (TreeSHAP), Dual-Risk Attribution & Error Diagnostics
- **TreeSHAP Global Summary Visualizations**:
  * Generated beeswarm and feature impact plots across 4 key models:
    - `next_12m_default_flag`: Credit risk escalation driven by `dpd_3m_mean`, `dti_x_ltv`, `status_severity`.
    - `next_12m_prepayment_flag`: Prepayment yield risk driven by `prepayment_incentive`, `market_avg_rate`, `credit_score_ord`.
    - `next_3m_delinquency_flag`: Short-term default risk driven by `days_past_due`, `status_severity`, `maturity_pressure`.
    - `IsolationForest`: Multivariate anomaly isolation driven by `distress_score`, `age_x_rate`, `rate_spread_to_market`.
- **Directional Attribution Framework**:
  * Supervised Classifiers: Filtered by highest positive log-odds (`np.argsort(-shap, axis=1)`).
  * Isolation Forest ($S_{\text{ML}}$): Filtered by lowest algebraic path length compression (`np.argsort(shap, axis=1)`), preventing normality-inducing features from being misattributed as anomaly drivers.
- **Deliverables Produced**:
  * `data/processed/phase4_shap_drivers_test.csv` (304,374 rows, 0 nulls)
  * `reports/model_explainability_report.md` (20 local waterfall case cards, False Positive / False Negative diagnostics)
- **Case Selection Stratification (20 Waterfall Cards)**:
  * Stratified specifically across distinct local TreeSHAP directional attribution profiles and prediction-error quadrants (False Positives, False Negatives, and Boundary Outliers) to evaluate model uncertainty.

### Entry: Phase 5 Macroeconomic Scenario & Stress Simulation
- **Objective**: Task 5 Scenario Simulation & Capital Stress Engine.
- **Scenarios Evaluated**: 
  - Base ($1.0\times$ baseline hazard)
  - Adverse Credit ($+150\text{ bps}$ interest rate, $+3.5\%$ unemployment, $-10\%\text{ HPA}$, $2.30\times\text{ default}$, $0.65\times\text{ prepay}$)
  - High Prepayment ($-150\text{ bps}$ interest rate, $+6.0\%\text{ HPA}$, $2.75\times\text{ prepay}$, $0.85\times\text{ default}$)
- **Deliverables Produced**:
  - `src/simulation/stress_engine.py`: Core simulation and micro-macro shock engine.
  - `run_phase5.py`: Master simulation pipeline orchestrator.
  - `data/processed/phase5_scenario_projections.csv`: Multi-horizon cash flow & loss projections.
  - `data/processed/phase5_segment_stress_impacts.csv`: Granular risk segment breakdowns.
  - `reports/scenario_simulation_report.md`: Formal stress test executive report.

### Entry: Phase 6 LLM Reviewer Copilot, Governance & Final Submission Packaging
- **Objective**: Task 7 LLM Reviewer Copilot, Task 8 Model Governance, and Final `submission.csv` Packaging.
- **Deliverables Produced**:
  - `src/llm/reviewer_copilot.py`: Grounded Reviewer Copilot with prompt logger and idempotent JSONL writer.
  - `src/llm/hallucination_auditor.py`: 4-case hallucination failure mode and guardrail audit.
  - `src/utils/submission_builder.py`: Final `submission.csv` assembler with full-scale merge validation.
  - `submission.csv`: 100% clean, 0-null competition submission (304,374 rows).
  - `reports/llm_copilot_audit_report.md`: Formal LLM copilot memos, logs, and hallucination rejection catalog.
  - `reports/model_card.md`: Industry-standard Model Card (Mitchell et al., 2019).
  - `logs/llm_review_log.jsonl`: ISO-timestamped prompt and response audit trail.
