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
