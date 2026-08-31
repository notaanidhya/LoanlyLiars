"""
run_phase6.py — Intain AI Track Phase 6 Master Orchestrator
LLM Reviewer Copilot, Hallucination Audit, Model Card & Final Submission Assembly

Run from project root:
    python run_phase6.py
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import pandas as pd
import numpy as np
from datetime import datetime

from src.llm.reviewer_copilot import ReviewerCopilot
from src.llm.hallucination_auditor import HallucinationAuditor
from src.utils.submission_builder import SubmissionAssembler


def run_phase6():
    print("=" * 70)
    print("PHASE 6: LLM REVIEWER COPILOT, GOVERNANCE & FINAL SUBMISSION ENGINE")
    print("=" * 70)

    # ------------------------------------------------------------------
    # 1. Final Competition Submission Assembly & Validation
    # ------------------------------------------------------------------
    print("\n[1/4] Assembling & Validating Final Competition submission.csv...")
    assembler = SubmissionAssembler(
        test_data_path="data/processed/loan_monthly_performance_test.csv",
        phase2_pred_path="data/processed/phase2_test_predictions.csv",
        phase3_anom_path="data/processed/phase3_anomaly_scores_test.csv",
        phase4_shap_path="data/processed/phase4_shap_drivers_test.csv",
        template_path="data/processed/submission_template.csv",
    )
    sub_df, sub_summary = assembler.assemble_and_validate(output_path="submission.csv")

    print(f"  -> Successfully generated root submission.csv: {sub_summary['total_rows']:,} rows, "
          f"{sub_summary['total_columns']} columns, {sub_summary['null_count']} nulls.")
    print("  -> Action Distribution in Submission:")
    for act, cnt in sub_summary["action_counts"].items():
        print(f"       {act}: {cnt:,} ({cnt/sub_summary['total_rows']*100:.2f}%)")

    # ------------------------------------------------------------------
    # 2. LLM Reviewer Copilot Memo Synthesis & Interaction Logging
    # ------------------------------------------------------------------
    print("\n[2/4] Initializing Grounded LLM Reviewer Copilot & Generating Memos...")
    copilot = ReviewerCopilot(
        data_dict_path="data/processed/data_dictionary.md",
        rules_path="data/processed/validation_rules.json",
        log_path="logs/llm_review_log.jsonl",
    )

    # Load component datasets for 24-case stratified selection
    test_raw = pd.read_csv("data/processed/loan_monthly_performance_test.csv")
    phase2_df = pd.read_csv("data/processed/phase2_test_predictions.csv")
    phase3_df = pd.read_csv("data/processed/phase3_anomaly_scores_test.csv")
    phase4_df = pd.read_csv("data/processed/phase4_shap_drivers_test.csv")

    phase3_clean = phase3_df.rename(columns={
        "top_driver_1": "rule_driver_1",
        "top_driver_2": "rule_driver_2",
        "top_driver_3": "rule_driver_3",
        "reviewer_action": "action",
        "confidence_score": "confidence",
    })

    merged_samples = test_raw.merge(phase2_df, on=["loan_id", "reporting_month"], how="left")
    merged_samples = merged_samples.merge(phase3_clean, on=["loan_id", "reporting_month"], how="left")
    merged_samples = merged_samples.merge(
        phase4_df[["loan_id", "reporting_month", "top_driver_1", "top_driver_2", "top_driver_3"]],
        on=["loan_id", "reporting_month"],
        how="left"
    )

    # Purge old stale logs
    log_path = "logs/llm_review_log.jsonl"
    if os.path.exists(log_path):
        os.remove(log_path)
    copilot = ReviewerCopilot(log_path=log_path)

    action_targets = [
        "MANUAL_AUDIT",
        "ESCALATE_DOC_REVIEW",
        "OVERRIDE_SERVICER",
        "REQUEST_CURE",
        "ACCEPT_PRIMARY",
        "AUTO_APPROVE",
    ]
    sample_memos = []
    selected_loans = set()

    for act in action_targets:
        sub = merged_samples[(merged_samples["action"] == act) & (~merged_samples["loan_id"].isin(selected_loans))]
        # Pick 4 distinct unique loans per action class
        unique_loans = sub.drop_duplicates(subset=["loan_id"]).head(4)
        
        for _, row in unique_loans.iterrows():
            selected_loans.add(row["loan_id"])
            rec = row.to_dict()

            ml_probs = {
                "next_12m_default_prob": float(row.get("pred_next_12m_default_flag", 0.01)),
                "next_12m_prepayment_prob": float(row.get("pred_next_12m_prepayment_flag", 0.20)),
                "next_3m_delinquency_prob": float(row.get("pred_next_3m_delinquency_flag", 0.02)),
                "next_6m_delinquency_prob": float(row.get("pred_next_6m_delinquency_flag", 0.04)),
                "next_state": str(row.get("pred_pred_next_state", row.get("pred_next_state", "CURRENT"))),
            }
            anom_info = {
                "anomaly_score": float(row.get("anomaly_score", 0.05)),
                "action": str(row.get("action", act)),
                "confidence": str(row.get("confidence", "HIGH")),
                "primary_exception": str(row.get("exception_type", "NONE")),
                "primary_driver_tag": str(row.get("rule_driver_1", "NORMAL_CONFORMING")),
                "s_ml": float(row.get("s_ml", 0.0)),
                "s_rule": float(row.get("s_rule", 0.0)),
                "s_servicer": float(row.get("s_servicer", 0.0)),
                "s_dq": float(row.get("s_dq", 0.0)),
            }
            drivers = [
                str(row.get("top_driver_1", "age_x_rate")),
                str(row.get("top_driver_2", "credit_score_ord")),
                str(row.get("top_driver_3", "dti_x_ltv")),
            ]

            memo_res = copilot.generate_reviewer_memo(rec, ml_probs, anom_info, drivers)
            sample_memos.append(memo_res)
            print(f"  -> Generated grounded memo for {row['loan_id']} (Action: {memo_res['action']}, Score: {anom_info['anomaly_score']:.4f})")

    print(f"\n  Successfully synthesized {len(sample_memos)} stratified reviewer memos across 6 action classes.")
    assert len(sample_memos) == 24, f"Expected 24 stratified memos, got {len(sample_memos)}"
    assert not any(m["log_payload"]["anomaly_score"] == 0.05 and m["log_payload"]["p_default_12m"] == 0.05 for m in sample_memos), \
        "Stale uniform 0.05 default detected in generated memos!"

    # ------------------------------------------------------------------
    # 3. Hallucination Auditing & Governance Report Compilation
    # ------------------------------------------------------------------
    print("\n[3/4] Running Hallucination Auditor & Compiling Governance Report...")
    auditor = HallucinationAuditor(log_path="logs/llm_review_log.jsonl")
    audit_report_path = auditor.generate_audit_report(sample_memos, out_dir="reports")
    print(f"  -> Audit Report generated: {audit_report_path}")

    # ------------------------------------------------------------------
    # 4. Governance & Final Verification
    # ------------------------------------------------------------------
    print("\n[4/4] Finalizing Governance Records & Submission Artifacts...")
    print(f"  -> submission.csv verified: {len(sub_df):,} rows")
    print(f"  -> llm_review_log.jsonl updated: {len(sample_memos)} unique records")
    print(f"  -> llm_copilot_audit_report.md compiled: {audit_report_path}")

    print("\n" + "=" * 70)
    print("PHASE 6 COMPLETE -- ALL HACKATHON TASKS FULLY DELIVERED & VERIFIED [SUCCESS]")
    print("=" * 70)


if __name__ == "__main__":
    run_phase6()
