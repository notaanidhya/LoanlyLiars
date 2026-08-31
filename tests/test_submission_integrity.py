"""
tests/test_submission_integrity.py
Deep verification suite auditing submission.csv completeness and value-level integrity.
"""

import os
import pytest
import numpy as np
import pandas as pd


def test_submission_integrity():
    sub_path = "submission.csv"
    test_path = "data/processed/loan_monthly_performance_test.csv"
    p2_path = "data/processed/phase2_test_predictions.csv"
    p3_path = "data/processed/phase3_anomaly_scores_test.csv"
    p4_path = "data/processed/phase4_shap_drivers_test.csv"
    tpl_path = "data/processed/submission_template.csv"

    assert os.path.exists(sub_path), f"{sub_path} does not exist!"
    assert os.path.exists(test_path), f"{test_path} does not exist!"

    df_sub = pd.read_csv(sub_path)
    df_test = pd.read_csv(test_path)
    df_p2 = pd.read_csv(p2_path)
    df_p3 = pd.read_csv(p3_path)
    df_p4 = pd.read_csv(p4_path)

    # 1. Structural Checks
    assert len(df_sub) == len(df_test), f"Row count mismatch: expected {len(df_test)}, got {len(df_sub)}"
    assert len(df_sub) == 304374, f"Expected 304,374 rows, got {len(df_sub)}"
    assert df_sub.isnull().sum().sum() == 0, "Null values found in submission.csv"

    # 2. Template Schema Validation
    if os.path.exists(tpl_path):
        tpl = pd.read_csv(tpl_path)
        assert list(df_sub.columns) == list(tpl.columns), "Columns mismatch template!"

    # 3. String Key Normalization
    for df in [df_sub, df_test, df_p2, df_p3, df_p4]:
        df["loan_id"] = df["loan_id"].astype(str).str.strip()
        if "reporting_month" in df.columns:
            df["reporting_month"] = df["reporting_month"].astype(str).str.strip()

    # 4. Full-Scale Merge Completeness Checks across all 304,374 rows
    m_p2 = df_test.merge(df_p2, on=["loan_id", "reporting_month"], how="left", indicator=True)
    assert (m_p2["_merge"] == "both").all(), "Some test rows failed to match Phase 2 predictions!"
    assert len(m_p2) == len(df_test), "Phase 2 merge duplicate keys detected!"

    m_p3 = df_test.merge(df_p3, on=["loan_id", "reporting_month"], how="left", indicator=True)
    assert (m_p3["_merge"] == "both").all(), "Some test rows failed to match Phase 3 anomaly scores!"
    assert len(m_p3) == len(df_test), "Phase 3 merge duplicate keys detected!"

    m_p4 = df_test.merge(df_p4, on=["loan_id", "reporting_month"], how="left", indicator=True)
    assert (m_p4["_merge"] == "both").all(), "Some test rows failed to match Phase 4 SHAP drivers!"
    assert len(m_p4) == len(df_test), "Phase 4 merge duplicate keys detected!"

    # 5. Full-Scale Tolerance Value Checks across all 304,374 rows
    merged_all = df_test[["loan_id", "reporting_month"]].merge(df_p2, on=["loan_id", "reporting_month"], how="left")
    merged_all = merged_all.merge(df_p3, on=["loan_id", "reporting_month"], how="left")
    merged_all = merged_all.merge(df_p4, on=["loan_id", "reporting_month"], how="left")

    # Check 12M Default Prob
    p2_def = merged_all["pred_next_12m_default_flag"].fillna(0.01).values
    sub_def = df_sub["next_12m_default_prob"].values
    assert np.isclose(sub_def, p2_def, atol=1e-4).all(), "12M default prob mismatch against Phase 2 source!"

    # Check 12M Prepayment Prob
    p2_prep = merged_all["pred_next_12m_prepayment_flag"].fillna(0.20).values
    sub_prep = df_sub["next_12m_prepayment_prob"].values
    assert np.isclose(sub_prep, p2_prep, atol=1e-4).all(), "12M prepayment prob mismatch against Phase 2 source!"

    # Check Anomaly Score
    p3_anom = merged_all["anomaly_score"].fillna(0.05).values
    sub_anom = df_sub["anomaly_score"].values
    assert np.isclose(sub_anom, p3_anom, atol=1e-4).all(), "Anomaly score mismatch against Phase 3 source!"

    # Check Reviewer Actions
    p3_action = merged_all["reviewer_action"].fillna("AUTO_APPROVE").values
    sub_action = df_sub["action"].values
    assert (sub_action == p3_action).all(), "Action mismatch against Phase 3 source!"

    # Check Top Driver 1
    p4_d1 = merged_all["top_driver_1_y"].fillna("age_x_rate").values if "top_driver_1_y" in merged_all.columns else merged_all["top_driver_1"].values
    sub_d1 = df_sub["top_driver_1"].values
    assert (sub_d1 == p4_d1).all(), "Top driver 1 mismatch against Phase 4 source!"

    print("ALL SUBMISSION INTEGRITY ASSERTIONS PASSED (100% COMPLETE, 0 NULLS, EXACT TOLERANCE MATCH)")


if __name__ == "__main__":
    test_submission_integrity()
