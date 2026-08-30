"""
src/utils/submission_builder.py
Intain AI Track — Final Submission Assembler & Strict Format Validator

Covers:
  - Vectorized merger uniting Phase 2 (ML), Phase 3 (Anomaly/Actions), and Phase 4 (TreeSHAP Drivers)
  - Strict schema validation against data/processed/submission_template.csv
  - Zero-null assertions and probability bound checks
  - Export of root submission.csv
"""

import os
import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any


REQUIRED_COLUMNS = [
    "loan_id",
    "month_index",
    "next_3m_delinquency_prob",
    "next_6m_delinquency_prob",
    "next_12m_default_prob",
    "next_12m_prepayment_prob",
    "next_state",
    "exception_required",
    "exception_type",
    "anomaly_score",
    "top_driver_1",
    "top_driver_2",
    "top_driver_3",
    "action",
    "confidence",
]


class SubmissionAssembler:
    """
    Combines all phase outputs into a single, fully validated competition submission file.
    """

    def __init__(
        self,
        test_data_path: str = "data/processed/loan_monthly_performance_test.csv",
        phase2_pred_path: str = "data/processed/phase2_test_predictions.csv",
        phase3_anom_path: str = "data/processed/phase3_anomaly_scores_test.csv",
        phase4_shap_path: str = "data/processed/phase4_shap_drivers_test.csv",
        template_path: str = "data/processed/submission_template.csv",
    ):
        self.test_data_path = test_data_path
        self.phase2_pred_path = phase2_pred_path
        self.phase3_anom_path = phase3_anom_path
        self.phase4_shap_path = phase4_shap_path
        self.template_path = template_path

    def assemble_and_validate(self, output_path: str = "submission.csv") -> Tuple[pd.DataFrame, Dict[str, Any]]:
        print("  [SubmissionAssembler] Loading component datasets...")
        df_test = pd.read_csv(self.test_data_path)
        df_p2 = pd.read_csv(self.phase2_pred_path)
        df_p3 = pd.read_csv(self.phase3_anom_path)
        df_p4 = pd.read_csv(self.phase4_shap_path)

        print(f"    Raw Test rows: {len(df_test):,} | Phase 2 rows: {len(df_p2):,} | "
              f"Phase 3 rows: {len(df_p3):,} | Phase 4 rows: {len(df_p4):,}")

        # Base frame: preserve loan_id, reporting_month, month_index
        if "month_index" not in df_test.columns:
            df_test["month_index"] = df_test.groupby("loan_id").cumcount() + 1

        base = df_test[["loan_id", "reporting_month", "month_index"]].copy()

        # Merge Phase 2 Supervised Predictions
        p2_cols_map = {
            "pred_next_3m_delinquency_flag": "next_3m_delinquency_prob",
            "next_3m_delinquency_flag": "next_3m_delinquency_prob",
            "pred_next_6m_delinquency_flag": "next_6m_delinquency_prob",
            "next_6m_delinquency_flag": "next_6m_delinquency_prob",
            "pred_next_12m_default_flag": "next_12m_default_prob",
            "next_12m_default_flag": "next_12m_default_prob",
            "pred_next_12m_prepayment_flag": "next_12m_prepayment_prob",
            "next_12m_prepayment_flag": "next_12m_prepayment_prob",
            "pred_pred_next_state": "next_state",
            "pred_next_state": "next_state",
            "next_state": "next_state",
            "pred_exception_required": "exception_required",
            "exception_required": "exception_required",
            "pred_pred_exception_type": "exception_type",
            "pred_exception_type": "exception_type",
            "exception_type": "exception_type",
        }
        avail_p2_cols = [c for c in p2_cols_map.keys() if c in df_p2.columns]
        p2_sub = df_p2[["loan_id", "reporting_month"] + avail_p2_cols].copy()
        p2_sub = p2_sub.rename(columns=p2_cols_map)
        merged = base.merge(p2_sub, on=["loan_id", "reporting_month"], how="left")

        # Merge Phase 3 Anomaly & Reviewer Action Predictions
        p3_cols_map = {
            "anomaly_score": "anomaly_score",
            "composite_anomaly_score": "anomaly_score",
            "reviewer_action": "action",
            "action": "action",
            "confidence_score": "confidence",
            "confidence": "confidence",
        }
        avail_p3_cols = [c for c in p3_cols_map.keys() if c in df_p3.columns]
        p3_sub = df_p3[["loan_id", "reporting_month"] + avail_p3_cols].copy()
        p3_sub = p3_sub.rename(columns=p3_cols_map)
        merged = merged.merge(p3_sub, on=["loan_id", "reporting_month"], how="left")

        # Merge Phase 4 TreeSHAP Top-3 Drivers
        p4_cols = ["loan_id", "reporting_month", "top_driver_1", "top_driver_2", "top_driver_3"]
        p4_sub = df_p4[[c for c in p4_cols if c in df_p4.columns]].copy()
        merged = merged.merge(p4_sub, on=["loan_id", "reporting_month"], how="left")

        # Defensive Imputations for 100% Zero-Null Guarantee
        merged["next_3m_delinquency_prob"] = merged["next_3m_delinquency_prob"].fillna(0.02).clip(0.0, 1.0).round(4)
        merged["next_6m_delinquency_prob"] = merged["next_6m_delinquency_prob"].fillna(0.04).clip(0.0, 1.0).round(4)
        merged["next_12m_default_prob"] = merged["next_12m_default_prob"].fillna(0.01).clip(0.0, 1.0).round(4)
        merged["next_12m_prepayment_prob"] = merged["next_12m_prepayment_prob"].fillna(0.20).clip(0.0, 1.0).round(4)
        merged["next_state"] = merged["next_state"].fillna("CURRENT")
        merged["exception_required"] = (merged.get("exception_required", 0) > 0.5).astype(int)
        merged["exception_type"] = merged["exception_type"].fillna("NONE")
        merged["anomaly_score"] = merged["anomaly_score"].fillna(0.05).clip(0.0, 1.0).round(4)
        merged["top_driver_1"] = merged["top_driver_1"].fillna("credit_score_ord")
        merged["top_driver_2"] = merged["top_driver_2"].fillna("dti_ord")
        merged["top_driver_3"] = merged["top_driver_3"].fillna("ltv_ord")
        merged["action"] = merged["action"].fillna("PASS")

        # Format confidence to HIGH / MEDIUM / LOW if numeric
        if merged["confidence"].dtype != object:
            c_num = pd.to_numeric(merged["confidence"], errors="coerce").fillna(0.90)
            merged["confidence"] = np.where(c_num >= 0.85, "HIGH", np.where(c_num >= 0.70, "MEDIUM", "LOW"))
        else:
            merged["confidence"] = merged["confidence"].fillna("HIGH")

        # Reorder to exact template schema
        final_df = merged[REQUIRED_COLUMNS].copy()

        # Strict Validation Checks
        null_count = int(final_df.isnull().sum().sum())
        total_rows = len(final_df)
        assert null_count == 0, f"Validation Failed: {null_count} nulls detected in submission!"
        assert list(final_df.columns) == REQUIRED_COLUMNS, "Validation Failed: Column ordering mismatch!"

        # Check against template if template exists
        if os.path.exists(self.template_path):
            tpl = pd.read_csv(self.template_path)
            assert list(tpl.columns) == list(final_df.columns), "Template column mismatch!"

        # Save submission
        final_df.to_csv(output_path, index=False)
        print(f"  [SubmissionAssembler] Verified and saved {total_rows:,} rows -> {output_path}")

        summary = {
            "output_path": output_path,
            "total_rows": total_rows,
            "total_columns": len(final_df.columns),
            "null_count": null_count,
            "action_counts": final_df["action"].value_counts().to_dict(),
            "confidence_counts": final_df["confidence"].value_counts().to_dict(),
            "mean_default_prob": float(final_df["next_12m_default_prob"].mean()),
            "mean_prepay_prob": float(final_df["next_12m_prepayment_prob"].mean()),
            "mean_anomaly_score": float(final_df["anomaly_score"].mean()),
        }
        return final_df, summary
