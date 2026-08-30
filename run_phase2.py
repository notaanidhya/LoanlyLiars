"""
run_phase2.py  —  Intain AI Track Phase 2 Orchestrator
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

        # Binary models
        f.write("## 1. Binary Classification Results\n\n")
        f.write("> Evaluation on 20% held-out validation split (time-ordered, no shuffle)\n\n")
        f.write("| Target | Pos Rate | Baseline ROC-AUC | XGB ROC-AUC | XGB PR-AUC | XGB F1 | Brier | Recall@80%P |\n")
        f.write("| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |\n")
        for r in binary_results:
            delta_auc = round(r["xgb_roc_auc"] - r["baseline_roc_auc"], 4)
            f.write(
                f"| `{r['target']}` | {r['positive_rate']*100:.1f}% | "
                f"{r['baseline_roc_auc']} | **{r['xgb_roc_auc']}** (+{delta_auc}) | "
                f"{r['xgb_pr_auc']} | {r['xgb_f1']} | {r['xgb_brier']} | "
                f"{r['recall_at_80pct_precision']} |\n"
            )
        f.write("\n> **Brier Score**: Lower is better (0 = perfect). PR-AUC is the primary metric for imbalanced targets.\n\n")

        # Multi-class models
        f.write("## 2. Multi-Class Transition Models\n\n")
        f.write("| Target | Classes | Baseline Macro-F1 | XGB Macro-F1 | XGB Weighted-F1 |\n")
        f.write("| :--- | ---: | ---: | ---: | ---: |\n")
        for r in mc_results:
            delta_f1 = round(r["xgb_macro_f1"] - r["baseline_macro_f1"], 4)
            f.write(
                f"| `{r['target']}` | {r['n_classes']} | "
                f"{r['baseline_macro_f1']} | **{r['xgb_macro_f1']}** (+{delta_f1}) | "
                f"{r['xgb_weighted_f1']} |\n"
            )
        f.write("\n")

        # Survival
        f.write("## 3. Survival & Time-to-Event Modeling\n\n")
        if survival_results:
            cph = survival_results.get("cph")
            ci = survival_results.get("concordance_index")
            if ci is not None:
                f.write(f"**Cox PH Concordance Index (C-stat)**: {ci:.4f}  \n")
                f.write("> C-stat > 0.7 indicates good discriminative ability for default timing.\n\n")

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

            if cph is not None:
                f.write("### 3b. Cox PH Hazard Ratios (Default)\n\n")
                f.write("| Feature | Coeff | Hazard Ratio (exp coef) | Std Err | p-value |\n")
                f.write("| :--- | ---: | ---: | ---: | ---: |\n")
                summary = cph.summary[["coef", "exp(coef)", "se(coef)", "p"]].copy()
                summary["abs_coef"] = summary["coef"].abs()
                summary = summary.sort_values("abs_coef", ascending=False).drop(columns=["abs_coef"])
                for feat, row in summary.iterrows():
                    direction = "Risk UP" if row["coef"] > 0 else "Risk DOWN"
                    f.write(
                        f"| `{feat}` | {row['coef']:.4f} | {row['exp(coef)']:.4f} | "
                        f"{row['se(coef)']:.4f} | {row['p']:.4f} | \n"
                    )
                f.write("\n")

            tm = survival_results.get("transition_matrix")
            if tm is not None:
                f.write("### 3c. Markov State Transition Matrix (Monthly Probabilities)\n\n")
                f.write("| From State | " + " | ".join(tm.columns.tolist()) + " |\n")
                f.write("| :--- | " + " | ".join(["---:"] * len(tm.columns)) + " |\n")
                for state, row in tm.iterrows():
                    f.write(f"| **{state}** | " + " | ".join([f"{v:.3f}" for v in row.values]) + " |\n")
                f.write("\n")

        f.write("---\n\n")
        f.write("*Report generated by Intain AI Track — Phase 2: Loan Performance Prediction Engine*\n")

    print(f"\nPhase 2 report: {path}")
    return path


# ── Main Orchestrator ─────────────────────────────────────────────────────────

def run_phase2():
    print("=" * 70)
    print("PHASE 2: LOAN PERFORMANCE INTELLIGENCE ENGINE")
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
            y_dict[t] = train_fe[t].fillna(0).astype(int)
            print(f"  {t}: +{int(y_dict[t].sum()):,} / {len(y_dict[t]):,} ({y_dict[t].mean()*100:.2f}% positive)")

    for t in mc_targets:
        if t in train_fe.columns:
            y_dict[t] = train_fe[t].fillna("UNKNOWN")
            print(f"  {t}: {dict(y_dict[t].value_counts().head(4))}")

    # 4. ML Training
    print("\n[4/5] ML Model Training...")
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
    # Add ordinal features to train_fe if missing
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
    print("PHASE 2 COMPLETE!")
    print("=" * 70)
    print(f"  Models        -> models/")
    print(f"  Predictions   -> {pred_path}")
    print(f"  Report        -> {report_path}")
    print("=" * 70)


if __name__ == "__main__":
    run_phase2()
