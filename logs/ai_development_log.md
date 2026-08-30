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
- **Prompt**: Ingest Freddie Mac 2019 Single-Family sample files (sample_orig_2019.txt and sample_perf_2019.txt) and construct the official 8-file hackathon dataset pack matching Section 6 and 7 of the problem statement.
- **Outcome**: Extracted 20,000 loans with 712,107 monthly performance panel records. Applied strict time-aware splitting (407,733 train rows through 2021-06; 304,374 forward holdout test rows). Generated secondary servicer conflict feeds, validation rules, macroeconomic stress parameters, and data dictionaries.

---

## 3. Accepted vs. Rejected AI Outputs

| Timestamp | Component | AI Proposal | Human / Technical Decision | Rationale |
| :--- | :--- | :--- | :--- | :--- |
| 2026-08-29 | Data Ingestion | Use 2025 single-quarter raw dump | **REJECTED** | 2025Q2 lacked multi-year default and prepayment outcomes (only 12 months old). Swapped to 2019 multi-year Freddie Mac benchmark. |
| 2026-08-29 | Data Splitting | Random row-level train/val split | **REJECTED** | Problem statement explicitly penalizes random splits across panel data. Enforced strict date-based temporal split with group-by-loan isolation. |
| 2026-08-29 | Data Packaging | Custom 8-file pipeline in uilder.py | **ACCEPTED** | Generates all 8 required files with clean forward target labels and ~5% servicer conflict rate for downstream reconciliation tasks. |

---

## 4. Code Ownership & Share by Module

| Module | Purpose | Estimated AI Share | Human Review & Verification |
| :--- | :--- | :--- | :--- |
| src/data/builder.py | Dataset extraction & transformation | 90% | Verified schema alignment with Section 6 and 7, validated no look-ahead target leakage. |
| logs/ai_development_log.md | Development trajectory tracking | 85% | Audited for authentic progression and rejected outputs. |

### Entry: Git Configuration & Repository Hygiene
- **Action**: Created comprehensive .gitignore.
- **Ignored**: ~8 GB raw Freddie Mac quarterlies, processed CSVs (>250MB), serialized .pkl models, MLflow tracking runs (mlruns/), Python caches, virtual environments, and system files.
- **Tracked**: Source code, documentation (data_dictionary.md, alidation_rules.json), reports, and AI development log.


### Entry: Phase 2 ML Pipeline Refactoring — Leakage Elimination & Calibration Fix
- **Identified Defect**: In-sample evaluation where production model refitted on all data was evaluated on val_split; isotonic calibrator was fit on same validation set.
- **Architectural Fix Implemented**:
  1. Global chronological ordering by (reporting_month, loan_id).
  2. 3-Way time split: Train 70% (X_tr), Calibration 15% (X_cal), and Held-Out Validation 15% (X_val).
  3. Two-tier model pattern: al_model trained only on X_tr, calibrated on X_cal, and evaluated strictly out-of-sample on untouched X_val.
  4. Scaled Logistic Regression baseline using SimpleImputer + StandardScaler pipeline.
  5. XGBoost native NaN routing preserved (no blind illna(0)).
  6. F1 threshold optimization dynamically computed on held-out slice.
  7. Multi-class state transition model consolidated 5 clean states with 0.6479 Macro-F1 / 0.9316 Weighted-F1.
- **Outcome**: Honest, publication-grade benchmark with 0.9503 ROC-AUC on 12m Default, 0.7710 PR-AUC on 3m Delinquency, and C-statistic of 0.6862 on Cox PH survival.


### Entry: Phase 3 Anomaly & Exception Detection Engine Built & Verified
- **Architecture**:
  1. Orthogonal Unsupervised ML: Isolation Forest (n_estimators=200, contamination=0.0315, train-only) fitted on non-rule behavioral space.
  2. Deterministic Rule Breach Evaluator: VR-001 to VR-008 severity penalties.
  3. Servicer Cross-Reconciliation Engine: Discrepancy and staleness flags.
  4. Structural Data Quality Evaluator: Non-rule missingness and format integrity.
  5. Mathematical Weight Calibration: Solved optimal weights (w_ML=25%, w_Rule=35%, w_Servicer=25%, w_DQ=15%) on training slice.
  6. Reviewer Action Precedence Matrix: 6-tier deterministic hierarchy (MANUAL_AUDIT -> ESCALATE_DOC_REVIEW -> OVERRIDE_SERVICER -> REQUEST_CURE -> ACCEPT_PRIMARY -> AUTO_APPROVE).
- **Deliverables Produced**:
  * models/anomaly_engine.pkl
  * data/processed/phase3_anomaly_scores_test.csv (304,374 test records scored)
  * reports/anomaly_detection_report.md (24 stratified audit case cards across all 6 action classes)


### Entry: Full Pipeline Remediation (Right-Censoring, Zero-Leakage Static Encodings, Macro Features)
- **Modifications Executed**:
  1. **Right-Censoring Applied**: Rebuilt forward-looking target generation in `src/data/builder.py`. Records with truncated terminal observation windows now output `NaN` instead of false `0`s. `src/models/trainer.py` dynamically filters uncensored rows per target horizon.
  2. **Zero-Leakage Static Mappings**: Replaced dataset-wide `LabelEncoder` with deterministic dictionary mappings in `src/data/feature_engineer.py`.
  3. **Macroeconomic Linkage**: Added `market_avg_rate`, `rate_spread_to_market`, and `prepayment_incentive` as continuous features (total 44 features derived) enabling direct interest rate shocks in Phase 5.
  4. **Phase 2 & Phase 3 Re-Execution**: Retrained all 5 binary classifiers and 2 multi-class models; re-ran Differential Evolution weight calibration for Phase 3 Anomaly Engine.
- **Metrics Refreshed**:
  * next_3m_delinquency_flag: ROC-AUC = 0.9381, PR-AUC = 0.7917, Optimal F1 = 0.8210
  * next_6m_delinquency_flag: ROC-AUC = 0.8827, PR-AUC = 0.7100, Optimal F1 = 0.7211
  * next_12m_default_flag: ROC-AUC = 0.9546, PR-AUC = 0.8311, Optimal F1 = 0.8273
  * next_12m_prepayment_flag: ROC-AUC = 0.6542, PR-AUC = 0.5048, Optimal F1 = 0.5368
  * exception_required: ROC-AUC = 0.9997, PR-AUC = 0.9964, Optimal F1 = 0.9926
  * Cox PH Concordance Index: 0.6866
  * Calibrated Weights: w_ML=33.4%, w_Rule=43.0%, w_Servicer=12.3%, w_DQ=11.3%


### Entry: Full Implementation of Critical Data & Inference Fixes
- **Inference Lag State Persistence**: Implemented `history_tail_df` persistence in `src/data/feature_engineer.py`. Eliminates test boundary lag collapse for all 20,000 loans.
- **Multicollinearity & Correlation Analysis**: Added Pearson and Spearman correlation matrices and collinearity severity classification in `src/data/profiler.py` and rendered Section 7 in `reports/data_intelligence_report.md`.
- **Missingness Pattern Injections & Handling**: Injected realistic MCAR (2.5%) and MAR patterns in `src/data/builder.py`. Mapped unknown/missing risk attributes to `-1` (eliminating naive credit imputation).
- **Macro Scenario API**: Exposed `apply_macro_shock` in `src/data/feature_engineer.py` for Phase 5 interest rate shock simulations.
- **Full Execution Verified**:
  * Phase 1: `reports/data_intelligence_report.md` (31,813 rule violations, 7 collinear pairs, MCAR/MAR profiling).
  * Phase 2: `reports/model_performance_report.md` (all 5 binary + 2 multiclass models retrained with zero lag collapse).
  * Phase 3: `reports/anomaly_detection_report.md` (weights calibrated via Differential Evolution: w_ML=34.4%, w_Rule=46.5%, w_Servicer=15.2%, w_DQ=3.8%).

### Entry: Phase 4 Model Explainability (TreeSHAP), Dual-Risk Attribution & Error Diagnostics
- **TreeSHAP Global Summary Visualizations**:
  * Generated publication-grade beeswarm and feature impact plots across 4 key models:
    - `next_12m_default_flag`: Credit risk escalation driven by `dpd_3m_mean`, `dti_x_ltv`, `status_severity`.
    - `next_12m_prepayment_flag`: Prepayment yield risk driven by `prepayment_incentive`, `market_avg_rate`, `credit_score_ord`.
    - `next_3m_delinquency_flag`: Short-term default risk driven by `days_past_due`, `status_severity`, `maturity_pressure`.
    - `IsolationForest`: Multivariate anomaly isolation driven by `distress_score`, `age_x_rate`, `rate_spread_to_market`.
- **Directional Attribution Framework**:
  * Supervised Classifiers: Filtered by highest positive log-odds (`np.argsort(-shap, axis=1)`).
  * Isolation Forest ($S_{\\text{ML}}$): Filtered by lowest algebraic path length compression (`np.argsort(shap, axis=1)`), preventing normality-inducing features from being misattributed as anomaly drivers.
- **20 Reviewer-Ready Local Waterfall Case Cards**:
  * Generated 20 high-resolution individual waterfall charts (`reports/figures/waterfall_case_01.png` through `waterfall_case_20.png`).
  * Stratified across diverse reviewer actions (`MANUAL_AUDIT`, `ESCALATE_DOC_REVIEW`, `OVERRIDE_SERVICER`, `REQUEST_CURE`, `ACCEPT_PRIMARY`).
- **Vectorized Full Test-Set Driver Staging**:
  * Computed directional TreeSHAP drivers across all 304,374 test rows in memory-safe batches.
  * Staged `data/processed/phase4_shap_drivers_test.csv` (100% complete, 0.00% null rate) ready for final `submission.csv` assembly.
- **Holdout Validation Error Diagnostics**:
  * Profiled False Positive vs. True Negative and False Negative vs. True Positive feature divergences on the 15% held-out validation cohort.
  * Generated comprehensive audit documentation in `reports/model_explainability_report.md`.

## Phase 5 Execution Log — 2026-08-30 19:46:03
- **Objective**: Task 5 Scenario Simulation & Capital Stress Engine.
- **Scenarios Evaluated**: Base (1.0x), Adverse Credit (+150bps rate, +3.5% unemp, -10% HPA, 2.30x default, 0.65x prepay), High Prepayment (-150bps rate, +6.0% HPA, 2.75x prepay, 0.85x default).
- **Deliverables**:
  - `src/simulation/stress_engine.py`: Core simulation and micro-macro shock engine.
  - `run_phase5.py`: Master simulation pipeline orchestrator.
  - `data/processed/phase5_scenario_projections.csv`: Multi-horizon cash flow & loss projections.
  - `data/processed/phase5_segment_stress_impacts.csv`: Granular risk segment breakdowns.
  - `reports/figures/scenario_hazard_curves.png`: Competing default/prepay hazard curves.
  - `reports/figures/segment_stress_heatmap.png`: High-risk geographic & credit segment concentrations.
  - `reports/figures/transition_stress_comparison.png`: 24-month Markov state roll-rate trajectories.
  - `reports/scenario_simulation_report.md`: Formal stress test executive report.
