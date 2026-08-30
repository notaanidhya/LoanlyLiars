"""
src/explainability/explainer.py
Intain AI Track — Phase 4: Model Explainability Engine (TreeSHAP & Error Diagnostics)

Features:
  - Global Feature Importance & Beeswarm Summary Visualizations (Default, Delinquency, Prepayment, Anomaly)
  - Directional SHAP Attribution:
      * Supervised Classifiers: Highest positive log-odds pushes (np.argsort(-shap))
      * Isolation Forest: Lowest algebraic path length compression (np.argsort(shap))
  - 20+ Reviewer-Ready Local Waterfall Case Card Generation
  - Vectorized Full Test-Set Driver Extraction (top_driver_1, 2, 3) for submission staging
  - Diagnostic False Positive / False Negative Holdout Segment Profiling
"""

import os
import pickle
import numpy as np
import pandas as pd
import shap
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Any

from src.models.anomaly_engine import ORTHOGONAL_ML_FEATURES, HybridAnomalyArbitrator


class ModelExplainer:
    """Unified explainability and attribution engine using TreeSHAP."""

    def __init__(self, models_dir: str = "models", background_samples: int = 5000, random_state: int = 42):
        self.models_dir = models_dir
        self.background_samples = background_samples
        self.random_state = random_state

        # Load models
        self.models = {}
        self.val_models = {}
        self.calibrators = {}
        self.feature_cols = {}
        self.explainers = {}

        # 1. Supervised Models
        supervised_targets = [
            "next_12m_default_flag",
            "next_3m_delinquency_flag",
            "next_12m_prepayment_flag",
            "next_6m_delinquency_flag",
        ]
        for target in supervised_targets:
            path = os.path.join(models_dir, f"{target}_model.pkl")
            if os.path.exists(path):
                with open(path, "rb") as f:
                    data = pickle.load(f)
                    self.models[target] = data["model"]
                    self.val_models[target] = data.get("val_model", data["model"])
                    self.calibrators[target] = data.get("calibrator", None)
                    self.feature_cols[target] = data["feature_cols"]
                    self.explainers[target] = shap.TreeExplainer(self.models[target])
                    print(f"  [ModelExplainer] Loaded {target} model & initialized TreeExplainer.")

        # 2. Unsupervised Anomaly Isolation Forest
        anomaly_path = os.path.join(models_dir, "anomaly_engine.pkl")
        if os.path.exists(anomaly_path):
            with open(anomaly_path, "rb") as f:
                self.anomaly_engine = pickle.load(f)
                self.iforest = self.anomaly_engine.detector.model
                self.models["isolation_forest"] = self.iforest
                self.feature_cols["isolation_forest"] = ORTHOGONAL_ML_FEATURES
                self.explainers["isolation_forest"] = shap.TreeExplainer(self.iforest)
                print("  [ModelExplainer] Loaded Isolation Forest & initialized TreeExplainer.")
        else:
            self.anomaly_engine = None
            self.iforest = None

    def generate_global_summary_plots(
        self,
        X_df: pd.DataFrame,
        out_dir: str = "reports/figures",
        sample_size: int = 5000,
    ) -> Dict[str, str]:
        os.makedirs(out_dir, exist_ok=True)
        generated_plots = {}

        if len(X_df) > sample_size:
            sample_df = X_df.sample(n=sample_size, random_state=self.random_state)
        else:
            sample_df = X_df

        plot_configs = [
            ("next_12m_default_flag", "shap_global_default_12m.png", "12-Month Mortgage Default Risk Drivers (TreeSHAP)"),
            ("next_3m_delinquency_flag", "shap_global_delinquency_3m.png", "3-Month Delinquency Risk Drivers (TreeSHAP)"),
            ("next_12m_prepayment_flag", "shap_global_prepayment_12m.png", "12-Month Voluntary Prepayment / Yield Risk Drivers (TreeSHAP)"),
            ("isolation_forest", "shap_global_anomaly_iforest.png", "Unsupervised Isolation Forest Outlier Drivers (TreeSHAP)"),
        ]

        for model_key, filename, title in plot_configs:
            if model_key not in self.explainers:
                continue

            cols = self.feature_cols[model_key]
            avail_cols = [c for c in cols if c in sample_df.columns]
            X_sub = sample_df[avail_cols]

            print(f"  Computing global SHAP values for {model_key} ({len(X_sub)} rows)...")
            shap_values = self.explainers[model_key].shap_values(X_sub)

            plt.figure(figsize=(11, 7), dpi=300)
            shap.summary_plot(
                shap_values,
                X_sub,
                plot_type="dot",
                max_display=15,
                show=False,
                feature_names=avail_cols,
            )
            plt.title(title, fontsize=14, pad=15, fontweight="bold")
            plt.xlabel("SHAP Value (Impact on Model Output Log-Odds / Path Length)", fontsize=11)
            plt.tight_layout()

            out_path = os.path.join(out_dir, filename)
            plt.savefig(out_path, bbox_inches="tight")
            plt.close()

            generated_plots[model_key] = out_path
            print(f"  -> Saved global plot: {out_path}")

        return generated_plots

    def generate_local_waterfall_cases(
        self,
        test_fe: pd.DataFrame,
        anomaly_scores_df: pd.DataFrame,
        out_dir: str = "reports/figures",
        target_quota: int = 20,
    ) -> List[Dict[str, Any]]:
        os.makedirs(out_dir, exist_ok=True)
        cases_metadata = []

        merged = anomaly_scores_df.copy()
        merged["orig_idx"] = np.arange(len(merged))
        
        actions = ["MANUAL_AUDIT", "ESCALATE_DOC_REVIEW", "OVERRIDE_SERVICER", "REQUEST_CURE", "ACCEPT_PRIMARY"]
        selected_indices = []

        for act in actions:
            sub = merged[merged["reviewer_action"] == act].sort_values("anomaly_score", ascending=False)
            take_n = min(5, len(sub))
            selected_indices.extend(sub["orig_idx"].iloc[:take_n].tolist())

        if len(selected_indices) < target_quota:
            remaining = merged.loc[~merged["orig_idx"].isin(selected_indices)].sort_values("anomaly_score", ascending=False)
            needed = target_quota - len(selected_indices)
            selected_indices.extend(remaining["orig_idx"].iloc[:needed].tolist())

        selected_indices = selected_indices[:max(target_quota, len(selected_indices))]
        print(f"  Generating {len(selected_indices)} reviewer-ready local waterfall case charts...")

        for i, idx in enumerate(selected_indices, start=1):
            row_meta = merged.iloc[idx]
            loan_id = str(row_meta.get("loan_id", f"LOAN_{idx}"))
            rm = str(row_meta.get("reporting_month", "N/A"))
            act = str(row_meta.get("reviewer_action", "AUDIT"))
            s_comp = float(row_meta.get("anomaly_score", 0.0))
            exc_type = str(row_meta.get("exception_type", "NONE"))

            if act in ["OVERRIDE_SERVICER", "ACCEPT_PRIMARY"] or "ISOLATION" in str(row_meta.get("top_driver_1", "")):
                model_key = "isolation_forest"
                target_label = "Isolation Forest Outlier Score"
            elif act == "REQUEST_CURE" or float(test_fe.iloc[idx].get("days_past_due", 0)) > 30:
                model_key = "next_3m_delinquency_flag"
                target_label = "3-Month Delinquency Probability"
            elif float(test_fe.iloc[idx].get("prepayment_incentive", 0)) > 50:
                model_key = "next_12m_prepayment_flag"
                target_label = "12-Month Prepayment Probability"
            else:
                model_key = "next_12m_default_flag"
                target_label = "12-Month Default Probability"

            if model_key not in self.explainers:
                model_key = "next_12m_default_flag" if "next_12m_default_flag" in self.explainers else list(self.explainers.keys())[0]

            cols = self.feature_cols[model_key]
            X_single = test_fe.iloc[[idx]][cols]
            explainer = self.explainers[model_key]

            shap_vals = explainer(X_single)
            exp_obj = shap_vals[0]

            plt.figure(figsize=(10, 6), dpi=250)
            shap.plots.waterfall(exp_obj, max_display=10, show=False)
            plt.title(
                f"Case #{i:02d}: Loan {loan_id} ({rm})\nAction: {act} | Anomaly Score: {s_comp:.3f} | Model: {target_label}",
                fontsize=11,
                fontweight="bold",
                pad=12,
            )
            plt.tight_layout()

            out_filename = f"waterfall_case_{i:02d}.png"
            out_path = os.path.join(out_dir, out_filename)
            plt.savefig(out_path, bbox_inches="tight")
            plt.close()

            vals = exp_obj.values
            if model_key == "isolation_forest":
                top_d_idx = np.argsort(vals)[:3]
            else:
                top_d_idx = np.argsort(-vals)[:3]

            top_drivers = [f"{cols[d_idx]} ({vals[d_idx]:+.3f})" for d_idx in top_d_idx]

            case_info = {
                "case_num": i,
                "loan_id": loan_id,
                "reporting_month": rm,
                "reviewer_action": act,
                "anomaly_score": s_comp,
                "exception_type": exc_type,
                "model_key": model_key,
                "target_label": target_label,
                "figure_path": out_path,
                "figure_name": out_filename,
                "top_drivers": top_drivers,
            }
            cases_metadata.append(case_info)

        print(f"  Successfully generated {len(cases_metadata)} waterfall plots in {out_dir}/")
        return cases_metadata

    def extract_full_test_drivers_vectorized(
        self,
        test_fe: pd.DataFrame,
        anomaly_scores_df: pd.DataFrame = None,
        batch_size: int = 50000,
    ) -> pd.DataFrame:
        n_rows = len(test_fe)
        print(f"  Vectorizing TreeSHAP driver extraction across all {n_rows:,} test rows...")

        # 1. Isolation Forest SHAP Drivers
        if "isolation_forest" in self.explainers:
            cols_if = self.feature_cols["isolation_forest"]
            X_if = test_fe[cols_if].values
            expl_if = self.explainers["isolation_forest"]

            if_top1 = np.empty(n_rows, dtype=object)
            if_top2 = np.empty(n_rows, dtype=object)
            if_top3 = np.empty(n_rows, dtype=object)

            for start_idx in range(0, n_rows, batch_size):
                end_idx = min(start_idx + batch_size, n_rows)
                batch_X = X_if[start_idx:end_idx]
                shap_b = expl_if.shap_values(batch_X)
                sort_idx = np.argsort(shap_b, axis=1)
                for k in range(end_idx - start_idx):
                    if_top1[start_idx + k] = cols_if[sort_idx[k, 0]]
                    if_top2[start_idx + k] = cols_if[sort_idx[k, 1]]
                    if_top3[start_idx + k] = cols_if[sort_idx[k, 2]]
            print("  -> Extracted Isolation Forest anomaly drivers.")
        else:
            if_top1 = if_top2 = if_top3 = np.array(["unknown"] * n_rows)

        # 2. Supervised Default Risk SHAP Drivers
        if "next_12m_default_flag" in self.explainers:
            cols_def = self.feature_cols["next_12m_default_flag"]
            X_def = test_fe[cols_def].values
            expl_def = self.explainers["next_12m_default_flag"]

            def_top1 = np.empty(n_rows, dtype=object)
            def_top2 = np.empty(n_rows, dtype=object)
            def_top3 = np.empty(n_rows, dtype=object)

            for start_idx in range(0, n_rows, batch_size):
                end_idx = min(start_idx + batch_size, n_rows)
                batch_X = X_def[start_idx:end_idx]
                shap_b = expl_def.shap_values(batch_X)
                sort_idx = np.argsort(-shap_b, axis=1)
                for k in range(end_idx - start_idx):
                    def_top1[start_idx + k] = cols_def[sort_idx[k, 0]]
                    def_top2[start_idx + k] = cols_def[sort_idx[k, 1]]
                    def_top3[start_idx + k] = cols_def[sort_idx[k, 2]]
            print("  -> Extracted Supervised Default credit risk drivers.")
        else:
            def_top1 = def_top2 = def_top3 = np.array(["unknown"] * n_rows)

        # 3. Supervised Prepayment Risk SHAP Drivers
        if "next_12m_prepayment_flag" in self.explainers:
            cols_prep = self.feature_cols["next_12m_prepayment_flag"]
            X_prep = test_fe[cols_prep].values
            expl_prep = self.explainers["next_12m_prepayment_flag"]

            prep_top1 = np.empty(n_rows, dtype=object)
            prep_top2 = np.empty(n_rows, dtype=object)
            prep_top3 = np.empty(n_rows, dtype=object)

            for start_idx in range(0, n_rows, batch_size):
                end_idx = min(start_idx + batch_size, n_rows)
                batch_X = X_prep[start_idx:end_idx]
                shap_b = expl_prep.shap_values(batch_X)
                sort_idx = np.argsort(-shap_b, axis=1)
                for k in range(end_idx - start_idx):
                    prep_top1[start_idx + k] = cols_prep[sort_idx[k, 0]]
                    prep_top2[start_idx + k] = cols_prep[sort_idx[k, 1]]
                    prep_top3[start_idx + k] = cols_prep[sort_idx[k, 2]]
            print("  -> Extracted Supervised Prepayment yield risk drivers.")
        else:
            prep_top1 = prep_top2 = prep_top3 = np.array(["unknown"] * n_rows)

        primary_top1 = np.copy(def_top1)
        primary_top2 = np.copy(def_top2)
        primary_top3 = np.copy(def_top3)

        if anomaly_scores_df is not None and "anomaly_score" in anomaly_scores_df.columns:
            s_anom = anomaly_scores_df["anomaly_score"].values
            anom_mask = s_anom >= 0.30
            primary_top1[anom_mask] = if_top1[anom_mask]
            primary_top2[anom_mask] = if_top2[anom_mask]
            primary_top3[anom_mask] = if_top3[anom_mask]

        if "prepayment_incentive" in test_fe.columns:
            prep_mask = (test_fe["prepayment_incentive"].values > 50) & (~(anomaly_scores_df["anomaly_score"].values >= 0.30) if anomaly_scores_df is not None else True)
            primary_top1[prep_mask] = prep_top1[prep_mask]
            primary_top2[prep_mask] = prep_top2[prep_mask]
            primary_top3[prep_mask] = prep_top3[prep_mask]

        staging_df = pd.DataFrame({
            "loan_id": test_fe["loan_id"].values if "loan_id" in test_fe.columns else np.arange(n_rows),
            "reporting_month": test_fe["reporting_month"].values if "reporting_month" in test_fe.columns else np.zeros(n_rows),
            "iforest_top_driver_1": if_top1,
            "iforest_top_driver_2": if_top2,
            "iforest_top_driver_3": if_top3,
            "default_top_driver_1": def_top1,
            "default_top_driver_2": def_top2,
            "default_top_driver_3": def_top3,
            "prepay_top_driver_1": prep_top1,
            "prepay_top_driver_2": prep_top2,
            "prepay_top_driver_3": prep_top3,
            "top_driver_1": primary_top1,
            "top_driver_2": primary_top2,
            "top_driver_3": primary_top3,
        })

        return staging_df

    def perform_error_analysis(
        self,
        X_val: pd.DataFrame,
        y_val: pd.Series,
        y_prob: np.ndarray,
        threshold: float = 0.5,
        target_name: str = "next_12m_default_flag",
        feature_cols: List[str] = None,
    ) -> Dict[str, Any]:
        valid_mask = y_val.notna()
        y_v = y_val[valid_mask].values.astype(int)
        y_p = y_prob[valid_mask]
        y_pred = (y_p >= threshold).astype(int)
        X_v = X_val[valid_mask].copy()

        tp_mask = (y_v == 1) & (y_pred == 1)
        fp_mask = (y_v == 0) & (y_pred == 1)
        fn_mask = (y_v == 1) & (y_pred == 0)
        tn_mask = (y_v == 0) & (y_pred == 0)

        n_tp, n_fp, n_fn, n_tn = tp_mask.sum(), fp_mask.sum(), fn_mask.sum(), tn_mask.sum()
        total = len(y_v)

        if feature_cols is None:
            feature_cols = [c for c in X_v.columns if np.issubdtype(X_v[c].dtype, np.number)]
        else:
            feature_cols = [c for c in feature_cols if c in X_v.columns and np.issubdtype(X_v[c].dtype, np.number)]

        fp_div = {}
        fn_div = {}

        if n_fp > 0 and n_tn > 0:
            for c in feature_cols[:20]:
                std_all = X_v[c].std()
                if std_all > 1e-6:
                    delta_fp = (X_v.loc[fp_mask, c].mean() - X_v.loc[tn_mask, c].mean()) / std_all
                    fp_div[c] = round(float(delta_fp), 3)

        if n_fn > 0 and n_tp > 0:
            for c in feature_cols[:20]:
                std_all = X_v[c].std()
                if std_all > 1e-6:
                    delta_fn = (X_v.loc[fn_mask, c].mean() - X_v.loc[tp_mask, c].mean()) / std_all
                    fn_div[c] = round(float(delta_fn), 3)

        top_fp_drivers = sorted(fp_div.items(), key=lambda x: abs(x[1]), reverse=True)[:5]
        top_fn_drivers = sorted(fn_div.items(), key=lambda x: abs(x[1]), reverse=True)[:5]

        return {
            "target": target_name,
            "threshold": threshold,
            "counts": {"TP": int(n_tp), "FP": int(n_fp), "FN": int(n_fn), "TN": int(n_tn), "Total": int(total)},
            "precision": float(n_tp / max(n_tp + n_fp, 1)),
            "recall": float(n_tp / max(n_tp + n_fn, 1)),
            "false_positive_rate": float(n_fp / max(n_fp + n_tn, 1)),
            "false_negative_rate": float(n_fn / max(n_fn + n_tp, 1)),
            "top_fp_divergence": top_fp_drivers,
            "top_fn_divergence": top_fn_drivers,
        }
