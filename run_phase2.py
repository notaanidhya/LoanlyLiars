"""
run_phase2.py — Intain AI Track Phase 2 Orchestrator (Leakage-Free & Calibrated)
Run from project root:
    python run_phase2.py
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import pandas as pd
import numpy as np
import pickle
from datetime import datetime

from src.data.feature_engineer import FeatureEngineer
from src.models.trainer import ModelTrainer, BINARY_TARGETS, MULTICLASS_TARGETS
from src.models.survival_model import SurvivalAnalyzer


# ── Report Generator ─────────────────────────────────────────────────────────

def generate_phase2_report(binary_results, mc_results, survival_results, out_dir="reports"):
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "model_performance_report.md")
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(path, "w", encoding="utf-8") as f:
        f.write("# Model Performance Report\n\n")
        f.write("**Intain AI Track 2026 — Phase 2: Loan Performance Prediction Engine**  \n")
        f.write(f"**Generated**: {now}  \n\n---\n\n")

        f.write("## 0. Validation & Leakage Controls Methodology\n\n")
        f.write("> **Strict Leakage Prevention Framework:**\n")
        f.write("> 1. **Chronological Panel Split**: Data is ordered globally by `reporting_month` before any splitting.\n")
        f.write("> 2. **3-Way Split**: **Train (70%)** for model learning + Optuna tuning, **Calibration (15%)** for Isotonic probability calibration, and **Validation (15%)** held completely untouched for final honest metric reporting.\n")
        f.write("> 3. **Two-Tier Architecture**: `val_model` evaluates out-of-sample performance on `X_val` with zero in-sample contamination. `prod_model` is trained on full historical data solely for `test.csv` submission predictions.\n")
        f.write("> 4. **Fair Baseline**: Logistic Regression baseline utilizes `SimpleImputer` + `StandardScaler` pipeline; XGBoost receives uncorrupted native NaNs.\n\n---\n\n")

        # Binary models
        f.write("## 1. Binary Classification Results (Untouched Held-Out Validation Slice)\n\n")
        f.write("| Target | Val Pos% | Scaled LR AUC | **XGB ROC-AUC** | **XGB PR-AUC** | F1 @ 0.5 | **Optimal F1 (Thresh)** | Brier Score | Recall @ 80% Prec | Optuna Trials |\n")
        f.write("| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |\n")
        for r in binary_results:
            delta_auc = round(r["xgb_roc_auc"] - r["baseline_roc_auc"], 4)
            delta_str = f"+{delta_auc}" if delta_auc >= 0 else f"{delta_auc}"
            f.write(
                f"| `{r['target']}` | {r['positive_rate_val']*100:.2f}% | "
                f"{r['baseline_roc_auc']:.4f} | **{r['xgb_roc_auc']:.4f}** ({delta_str}) | "
                f"**{r['xgb_pr_auc']:.4f}** | {r['xgb_f1_default']:.4f} | "
                f"**{r['xgb_f1_optimal']:.4f}** (`@{r['best_threshold']}`) | {r['xgb_brier']:.4f} | "
                f"{r['recall_at_80pct_precision']:.4f} | {r.get('n_optuna_trials', 15)} |\n"
            )
        f.write("\n> **Metrics Note**: PR-AUC is the primary benchmark for rare event credit risk. Brier Score evaluates post-isotonic calibration quality (0 = perfect calibration).\n\n---\n\n")

        # Multi-class models
        f.write("## 2. Multi-Class Transition Models\n\n")
        f.write("| Target | Classes | Baseline DT Macro-F1 | **XGB Macro-F1** | **XGB Weighted-F1** | Optuna Trials |\n")
        f.write("| :--- | ---: | ---: | ---: | ---: | ---: |\n")
        for r in mc_results:
            delta_f1 = round(r["xgb_macro_f1"] - r["baseline_macro_f1"], 4)
            delta_str = f"+{delta_f1}" if delta_f1 >= 0 else f"{delta_f1}"
            f.write(
                f"| `{r['target']}` | {r['n_classes']} | "
                f"{r['baseline_macro_f1']:.4f} | **{r['xgb_macro_f1']:.4f}** ({delta_str}) | "
                f"**{r['xgb_weighted_f1']:.4f}** | {r.get('n_optuna_trials', 10)} |\n"
            )
        f.write("\n---\n\n")

        # Survival
        f.write("## 3. Survival & Time-to-Event Modeling\n\n")
        if survival_results:
            ci = survival_results.get("concordance_index")
            if ci is not None:
                f.write(f"**Cox Proportional Hazards Concordance Index (C-stat)**: **{ci:.4f}**  \n")
                f.write("> C-stat > 0.65 indicates strong discriminative power for default timing over multi-year horizons.\n\n")

            km_table = survival_results.get("km_table")
            if km_table is not None:
                f.write("### 3a. Kaplan-Meier Event Probabilities\n\n")
                f.write("| Month | Default Survival | Cumulative Default | Prepay Survival | Cumulative Prepay |\n")
                f.write("| ---: | ---: | ---: | ---: | ---: |\n")
                for _, row in km_table.iterrows():
                    f.write(
                        f"| {int(row['month'])} | {row['default_survival_prob']} | "
                        f"{row['cumulative_default_prob']} | {row['prepay_survival_prob']} | "
                        f"{row['cumulative_prepay_prob']} |\n"
                    )
                f.write("\n")

            cph = survival_results.get("cph")
            if cph is not None:
                f.write("### 3b. Cox PH Hazard Ratios (Default Risk Drivers)\n\n")
                f.write("| Feature | Coeff | Hazard Ratio (exp coef) | Std Err | p-value |\n")
                f.write("| :--- | ---: | ---: | ---: | ---: |\n")
                summary = cph.summary[["coef", "exp(coef)", "se(coef)", "p"]].copy()
                summary["abs_coef"] = summary["coef"].abs()
                summary = summary.sort_values("abs_coef", ascending=False).drop(columns=["abs_coef"])
                for feat, row in summary.iterrows():
                    f.write(
                        f"| `{feat}` | {row['coef']:.4f} | {row['exp(coef)']:.4f} | "
                        f"{row['se(coef)']:.4f} | {row['p']:.4f} |\n"
                    )
                f.write("\n")

            tm = survival_results.get("transition_matrix")
            if tm is not None:
                f.write("### 3c. Markov State Transition Matrix (Monthly Empirical Probabilities)\n\n")
                f.write("| From State | " + " | ".join(tm.columns.tolist()) + " |\n")
                f.write("| :--- | " + " | ".join(["---:"] * len(tm.columns)) + " |\n")
                for state, row in tm.iterrows():
                    f.write(f"| **{state}** | " + " | ".join([f"{v:.3f}" for v in row.values]) + " |\n")
                f.write("\n")

        f.write("---\n\n")
        f.write("*Report generated by Intain AI Track — Phase 2: Loan Performance Prediction Engine*\n")

    print(f"\nPhase 2 report generated: {path}")
    return path


# ── Main Orchestrator ─────────────────────────────────────────────────────────

def run_phase2():
    print("=" * 70)
    print("PHASE 2: LOAN PERFORMANCE INTELLIGENCE ENGINE (LEAKAGE-FREE & CALIBRATED)")
    print("=" * 70)

    # 1. Load data
    print("\n[1/5] Loading datasets...")
    train = pd.read_csv("data/processed/loan_monthly_performance_train.csv", low_memory=False)
    test = pd.read_csv("data/processed/loan_monthly_performance_test.csv", low_memory=False)
    print(f"  Train: {train.shape}  |  Test: {test.shape}")

    # 2. Feature Engineering
    print("\n[2/5] Feature Engineering...")
    os.makedirs("models", exist_ok=True)
    fe = FeatureEngineer()
    train_fe = fe.fit_transform(train)
    test_fe = fe.transform(test)
    feature_cols = fe.feature_cols
    print(f"  Total features: {len(feature_cols)}")
    fe.save("models/feature_engineer.pkl")

    # 3. Prepare targets
    print("\n[3/5] Preparing targets...")
    binary_targets = [
        "next_3m_delinquency_flag",
        "next_6m_delinquency_flag",
        "next_12m_default_flag",
        "next_12m_prepayment_flag",
        "exception_required",
    ]
    mc_targets = ["next_state", "exception_type"]

    y_dict = {}
    for t in binary_targets:
        if t in train_fe.columns:
            y_dict[t] = train_fe[t]  # Preserve NaNs for right-censoring filter in trainer
            valid_cnt = train_fe[t].notna().sum()
            pos_cnt = (train_fe[t] == 1).sum()
            print(f"  {t}: +{pos_cnt:,} / {valid_cnt:,} valid ({pos_cnt/max(valid_cnt, 1)*100:.2f}% positive)")

    for t in mc_targets:
        if t in train_fe.columns:
            y_dict[t] = train_fe[t]
            valid_cnt = train_fe[t].notna().sum()
            print(f"  {t}: {valid_cnt:,} valid records")

    # 4. ML Training
    print("\n[4/5] ML Model Training (3-Way Split: Train 70% / Calib 15% / Val 15%)...")
    trainer = ModelTrainer(
        X_train=train_fe,
        y_dict=y_dict,
        X_test=test_fe,
        feature_cols=feature_cols,
        output_dir="models",
    )
    binary_results, mc_results = trainer.train_all()

    # 5. Survival Analysis
    print("\n[5/5] Survival & Transition Modeling...")
    if "credit_score_ord" not in train_fe.columns:
        fe2 = FeatureEngineer()
        train_fe = fe2.encode_ordinals(train_fe)
    analyzer = SurvivalAnalyzer(train_fe)
    survival_results = analyzer.run()
    analyzer.save("models/survival_analyzer.pkl")

    # Save test predictions
    print("\nSaving test predictions...")
    pred_df = test[["loan_id", "reporting_month"]].copy()
    for target, preds in trainer.test_predictions.items():
        if not target.endswith("_proba"):
            pred_df[f"pred_{target}"] = preds
    pred_path = "data/processed/phase2_test_predictions.csv"
    pred_df.to_csv(pred_path, index=False)
    print(f"  Saved {len(pred_df):,} predictions -> {pred_path}")

    # Generate report
    report_path = generate_phase2_report(binary_results, mc_results, survival_results)

    print("\n" + "=" * 70)
    print("PHASE 2 COMPLETE (LEAKAGE-FREE & HONEST BENCHMARK)")
    print("=" * 70)
    print(f"  Models        -> models/")
    print(f"  Predictions   -> {pred_path}")
    print(f"  Report        -> {report_path}")
    print("=" * 70)


if __name__ == "__main__":
    run_phase2()
