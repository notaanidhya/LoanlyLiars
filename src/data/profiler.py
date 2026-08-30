"""
src/data/profiler.py
Intain AI Track Phase 1: Data Intelligence & Profiling Engine
Covers: column profiling, missingness, outliers, validation rules,
        servicer conflicts, PSI drift, DQ scoring, report generation.
"""

import pandas as pd
import numpy as np
import json
import os
from datetime import datetime

RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)


class LoanDataProfiler:

    def __init__(self, train_path, test_path, servicer_path, rules_path, output_dir="reports"):
        print("=" * 70)
        print("LOAN DATA PROFILER  PHASE 1: DATA INTELLIGENCE AND PROFILING")
        print("=" * 70)

        print("\nLoading training data...")
        self.df_train = pd.read_csv(train_path, low_memory=False)
        print(f"  Train shape: {self.df_train.shape}")

        print("Loading test data...")
        self.df_test = pd.read_csv(test_path, low_memory=False)
        print(f"  Test shape: {self.df_test.shape}")

        print("Loading servicer updates...")
        self.df_servicer = pd.read_csv(servicer_path, low_memory=False)
        print(f"  Servicer updates shape: {self.df_servicer.shape}")

        print("Loading validation rules...")
        with open(rules_path, "r") as fh:
            self.rules = json.load(fh)["rules"]
        print(f"  Loaded {len(self.rules)} validation rules")

        os.makedirs(output_dir, exist_ok=True)
        self.output_dir = output_dir

        # Results containers
        self.col_profile = pd.DataFrame()
        self.missing_analysis = pd.DataFrame()
        self.outlier_results = pd.DataFrame()
        self.rule_violations = pd.DataFrame()
        self.servicer_conflicts = {}
        self.psi_results = pd.DataFrame()
        self.dq_scores = None
        self.batch_dq = {}

    # ------------------------------------------------------------------
    # STEP 1.1 - Column Distribution Profiling
    # ------------------------------------------------------------------
    def profile_columns(self):
        print("\n" + "=" * 70)
        print("STEP 1.1: Column Distribution Profiling...")
        print("=" * 70)

        df = self.df_train
        results = []

        for col in df.columns:
            cd = df[col]
            null_count = int(cd.isnull().sum())
            null_pct = round(null_count / len(df) * 100, 2)
            n_unique = int(cd.nunique())
            dtype = str(cd.dtype)

            row = dict(column=col, dtype=dtype, n_unique=n_unique,
                       null_count=null_count, null_pct=null_pct)

            if cd.dtype.kind in ("i", "f", "u"):
                nn = cd.dropna()
                if len(nn) > 0:
                    row.update(
                        min=round(float(nn.min()), 4),
                        max=round(float(nn.max()), 4),
                        mean=round(float(nn.mean()), 4),
                        std=round(float(nn.std()), 4),
                        q25=round(float(nn.quantile(0.25)), 4),
                        median=round(float(nn.median()), 4),
                        q75=round(float(nn.quantile(0.75)), 4),
                        skew=round(float(nn.skew()), 4),
                        top_values="N/A (numeric)",
                    )
                else:
                    row.update(min=None, max=None, mean=None, std=None,
                               q25=None, median=None, q75=None, skew=None,
                               top_values="N/A (all null)")
            else:
                vc = cd.value_counts().head(3)
                top = ", ".join([f"{v}: {c}" for v, c in vc.items()])
                row.update(min=None, max=None, mean=None, std=None,
                           q25=None, median=None, q75=None, skew=None,
                           top_values=top)

            results.append(row)

        self.col_profile = pd.DataFrame(results)
        print(f"  Profiled {len(results)} columns.")
        return self.col_profile

    # ------------------------------------------------------------------
    # STEP 1.2 - Missingness Analysis
    # ------------------------------------------------------------------
    def analyze_missingness(self):
        print("\n" + "=" * 70)
        print("STEP 1.2: Missingness Pattern Analysis...")
        print("=" * 70)

        df = self.df_train
        null_cols = [c for c in df.columns if df[c].isnull().any()]
        print(f"  Columns with missing values: {len(null_cols)}")

        rows = []
        for col in null_cols:
            mask = df[col].isnull()
            null_count = int(mask.sum())
            null_pct = round(null_count / len(df) * 100, 2)

            # Heuristic MAR test: does missingness rate vary by status?
            miss_type = "MCAR"
            if "current_status" in df.columns:
                by_status = df.groupby("current_status")[col].apply(
                    lambda x: x.isnull().mean()
                )
                if by_status.std() > 0.05:
                    miss_type = "MAR"

            impact = "HIGH" if null_pct > 20 else ("MEDIUM" if null_pct > 5 else "LOW")
            rows.append(dict(column=col, null_count=null_count,
                             null_pct=null_pct, pattern=miss_type, impact=impact))

        self.missing_analysis = pd.DataFrame(rows) if rows else pd.DataFrame()
        mar_count = sum(1 for r in rows if r["pattern"] == "MAR")
        print(f"  Missing analysis complete. MAR-pattern columns: {mar_count}")
        return self.missing_analysis

    # ------------------------------------------------------------------
    # STEP 1.3 - Outlier Detection (3x IQR fence)
    # ------------------------------------------------------------------
    def detect_outliers(self):
        print("\n" + "=" * 70)
        print("STEP 1.3: Outlier Detection (3x IQR Fence)...")
        print("=" * 70)

        df = self.df_train
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        summary = []

        for col in numeric_cols:
            nn = df[col].dropna()
            if len(nn) < 10:
                continue
            q1, q3 = nn.quantile(0.25), nn.quantile(0.75)
            iqr = q3 - q1
            if iqr == 0:
                continue
            lower = q1 - 3.0 * iqr
            upper = q3 + 3.0 * iqr
            out_mask = (df[col] < lower) | (df[col] > upper)
            cnt = int(out_mask.sum())
            if cnt > 0:
                summary.append(dict(
                    column=col,
                    iqr_lower=round(float(lower), 2),
                    iqr_upper=round(float(upper), 2),
                    outlier_count=cnt,
                    outlier_pct=round(cnt / len(df) * 100, 2),
                    col_min=round(float(df[col].min()), 2),
                    col_max=round(float(df[col].max()), 2),
                ))

        self.outlier_results = pd.DataFrame(summary) if summary else pd.DataFrame()
        print(f"  Outliers found in {len(summary)} numeric columns.")
        return self.outlier_results

    # ------------------------------------------------------------------
    # STEP 1.4 - Validation Rule Application
    # ------------------------------------------------------------------
    def apply_validation_rules(self):
        print("\n" + "=" * 70)
        print("STEP 1.4: Applying Validation Rules (VR-001 to VR-006)...")
        print("=" * 70)

        df = self.df_train.copy()
        vr = []

        # VR-001: Balance ratio upper bound
        if {"current_balance", "original_balance", "modification_flag"}.issubset(df.columns):
            mask = (df["current_balance"] > df["original_balance"] * 1.15) & (df["modification_flag"] != "Y")
            vr.append(dict(rule_id="VR-001", rule_name="Balance Ratio Upper Bound",
                           severity="CRITICAL", violation_count=int(mask.sum()),
                           violation_pct=round(mask.mean() * 100, 2),
                           exception_type="BALANCE_INCONSISTENCY"))
            df["vr001"] = mask.astype(int)

        # VR-002: Status-DPD consistency
        if {"days_past_due", "current_status"}.issubset(df.columns):
            mask = (df["days_past_due"] > 0) & (df["current_status"] == "CURRENT")
            vr.append(dict(rule_id="VR-002", rule_name="Status DPD Consistency",
                           severity="HIGH", violation_count=int(mask.sum()),
                           violation_pct=round(mask.mean() * 100, 2),
                           exception_type="STATUS_CONFLICT"))
            df["vr002"] = mask.astype(int)

        # VR-003: Date validity
        if {"reporting_month", "origination_month"}.issubset(df.columns):
            mask = df["reporting_month"].astype(str) < df["origination_month"].astype(str)
            vr.append(dict(rule_id="VR-003", rule_name="Origination Date Validity",
                           severity="CRITICAL", violation_count=int(mask.sum()),
                           violation_pct=round(mask.mean() * 100, 2),
                           exception_type="INVALID_DATE"))
            df["vr003"] = mask.astype(int)

        # VR-004: Remaining term sanity
        if "remaining_term_months" in df.columns:
            mask = (df["remaining_term_months"] < 0) | (df["remaining_term_months"] > 360)
            vr.append(dict(rule_id="VR-004", rule_name="Remaining Term Sanity",
                           severity="HIGH", violation_count=int(mask.sum()),
                           violation_pct=round(mask.mean() * 100, 2),
                           exception_type="INVALID_TERM"))
            df["vr004"] = mask.astype(int)

        # VR-005: Prepayment balance check
        if {"current_status", "current_balance"}.issubset(df.columns):
            mask = (df["current_status"] == "PREPAID") & (df["current_balance"] > 0)
            vr.append(dict(rule_id="VR-005", rule_name="Prepayment Balance Check",
                           severity="CRITICAL", violation_count=int(mask.sum()),
                           violation_pct=round(mask.mean() * 100, 2),
                           exception_type="BALANCE_INCONSISTENCY"))
            df["vr005"] = mask.astype(int)

        # VR-006: Document gap
        if "document_status" in df.columns:
            mask = df["document_status"] != "VERIFIED"
            vr.append(dict(rule_id="VR-006", rule_name="Document Verification Status",
                           severity="MEDIUM", violation_count=int(mask.sum()),
                           violation_pct=round(mask.mean() * 100, 2),
                           exception_type="DOCUMENT_GAP"))
            df["vr006"] = mask.astype(int)

        self.rule_violations = pd.DataFrame(vr)
        self.df_with_violations = df
        total = sum(r["violation_count"] for r in vr)
        print(f"  Applied {len(vr)} rules. Total violations: {total:,}")
        return self.rule_violations

    # ------------------------------------------------------------------
    # STEP 1.5 - Servicer Conflict Detection
    # ------------------------------------------------------------------
    def detect_servicer_conflicts(self):
        print("\n" + "=" * 70)
        print("STEP 1.5: Servicer Conflict and Staleness Detection...")
        print("=" * 70)

        df = self.df_train
        sv = self.df_servicer

        keep_cols = ["loan_id", "reporting_month", "servicer_reported_balance",
                     "servicer_reported_status", "servicer_days_past_due",
                     "servicer_update_timestamp"]
        keep_cols = [c for c in keep_cols if c in sv.columns]

        merged = df.merge(sv[keep_cols], on=["loan_id", "reporting_month"], how="inner")
        print(f"  Records matched with servicer feed: {len(merged):,}")

        if {"current_balance", "servicer_reported_balance", "original_balance"}.issubset(merged.columns):
            diff_pct = (
                (merged["current_balance"] - merged["servicer_reported_balance"]).abs()
                / (merged["original_balance"] + 1e-5)
            )
            merged["balance_conflict"] = (diff_pct > 0.05).astype(int)
            merged["balance_diff_pct"] = (diff_pct * 100).round(2)
        else:
            merged["balance_conflict"] = 0
            merged["balance_diff_pct"] = 0.0

        if {"current_status", "servicer_reported_status"}.issubset(merged.columns):
            merged["status_conflict"] = (
                merged["current_status"] != merged["servicer_reported_status"]
            ).astype(int)
        else:
            merged["status_conflict"] = 0

        if "servicer_update_timestamp" in merged.columns:
            merged["rep_year"] = merged["reporting_month"].astype(str).str[:4].astype(int)
            merged["upd_year"] = merged["servicer_update_timestamp"].astype(str).str[:4].astype(int)
            merged["stale_flag"] = (merged["upd_year"] < merged["rep_year"] - 1).astype(int)
        else:
            merged["stale_flag"] = 0

        any_conflict = (merged[["balance_conflict", "status_conflict", "stale_flag"]].sum(axis=1) > 0)

        self.servicer_conflicts = dict(
            total_matched=len(merged),
            balance_conflicts=int(merged["balance_conflict"].sum()),
            balance_conflict_pct=round(merged["balance_conflict"].mean() * 100, 2),
            status_conflicts=int(merged["status_conflict"].sum()),
            status_conflict_pct=round(merged["status_conflict"].mean() * 100, 2),
            stale_records=int(merged["stale_flag"].sum()),
            stale_pct=round(merged["stale_flag"].mean() * 100, 2),
            any_conflict=int(any_conflict.sum()),
        )

        show_cols = [c for c in ["loan_id", "reporting_month", "current_balance",
                                  "servicer_reported_balance", "balance_diff_pct",
                                  "current_status", "servicer_reported_status",
                                  "balance_conflict", "status_conflict", "stale_flag"]
                     if c in merged.columns]
        self.conflict_examples = merged[any_conflict][show_cols].head(25)
        self.merged_servicer = merged

        sc = self.servicer_conflicts
        print(f"  Balance conflicts: {sc['balance_conflicts']:,} ({sc['balance_conflict_pct']}%)")
        print(f"  Status conflicts:  {sc['status_conflicts']:,} ({sc['status_conflict_pct']}%)")
        print(f"  Stale records:     {sc['stale_records']:,} ({sc['stale_pct']}%)")
        return sc

    # ------------------------------------------------------------------
    # STEP 1.6 - Population Stability Index (PSI)
    # ------------------------------------------------------------------
    def compute_psi(self):
        print("\n" + "=" * 70)
        print("STEP 1.6: Train vs. Test Drift Analysis (PSI)...")
        print("=" * 70)

        exclude = {
            "loan_id", "next_3m_delinquency_flag", "next_6m_delinquency_flag",
            "next_12m_default_flag", "next_12m_prepayment_flag", "next_state",
            "exception_required", "exception_type",
            "reporting_month", "origination_month", "last_updated_at",
        }
        common = [c for c in self.df_train.columns
                  if c in self.df_test.columns and c not in exclude]

        rows = []
        for col in common:
            tr = self.df_train[col].dropna()
            te = self.df_test[col].dropna()
            if len(tr) == 0 or len(te) == 0:
                continue
            try:
                if self.df_train[col].dtype.kind in ("i", "f", "u"):
                    # Numeric: 10-bin equal-frequency on train
                    quantiles = np.percentile(tr, np.linspace(0, 100, 11))
                    bins = np.unique(quantiles)
                    if len(bins) < 2:
                        continue
                    tr_cnt = np.histogram(tr, bins=bins)[0]
                    te_cnt = np.histogram(te, bins=bins)[0]
                    n = min(len(tr_cnt), len(te_cnt))
                    tr_pct = np.clip(tr_cnt[:n] / len(tr), 1e-4, None)
                    te_pct = np.clip(te_cnt[:n] / len(te), 1e-4, None)
                    psi = float(np.sum((te_pct - tr_pct) * np.log(te_pct / tr_pct)))
                else:
                    # Categorical
                    tr_vc = tr.value_counts(normalize=True)
                    te_vc = te.value_counts(normalize=True)
                    cats = set(tr_vc.index) | set(te_vc.index)
                    psi = sum(
                        (max(te_vc.get(c, 0), 1e-4) - max(tr_vc.get(c, 0), 1e-4))
                        * np.log(max(te_vc.get(c, 0), 1e-4) / max(tr_vc.get(c, 0), 1e-4))
                        for c in cats
                    )
                psi = abs(psi)
                drift = "HIGH" if psi > 0.2 else ("MEDIUM" if psi > 0.1 else "LOW")
                rows.append(dict(column=col, psi=round(psi, 4), drift_level=drift,
                                 dtype=str(self.df_train[col].dtype)))
            except Exception:
                continue

        self.psi_results = (pd.DataFrame(rows).sort_values("psi", ascending=False)
                            if rows else pd.DataFrame())
        high = (self.psi_results["drift_level"] == "HIGH").sum() if not self.psi_results.empty else 0
        print(f"  PSI computed for {len(rows)} features. High-drift columns: {high}")
        return self.psi_results

    # ------------------------------------------------------------------
    # STEP 1.7 - Record-Level DQ Scoring
    # ------------------------------------------------------------------
    def compute_dq_scores(self):
        print("\n" + "=" * 70)
        print("STEP 1.7: Computing Record-Level Data Quality Scores (0-100)...")
        print("=" * 70)

        df = self.df_train.copy()
        score = pd.Series(100.0, index=df.index)

        # Missing required fields: -5 per field, cap at -30
        req = ["loan_id", "current_balance", "interest_rate",
               "credit_score_band", "ltv_band", "dti_band",
               "current_status", "days_past_due"]
        req = [c for c in req if c in df.columns]
        score -= (df[req].isnull().sum(axis=1) * 5).clip(upper=30)

        # Balance inconsistency: -20
        if {"current_balance", "original_balance", "modification_flag"}.issubset(df.columns):
            score -= ((df["current_balance"] > df["original_balance"] * 1.15) &
                      (df["modification_flag"] != "Y")).astype(float) * 20

        # Status-DPD conflict: -15
        if {"days_past_due", "current_status"}.issubset(df.columns):
            score -= ((df["days_past_due"] > 0) &
                      (df["current_status"] == "CURRENT")).astype(float) * 15

        # Term out of range: -10
        if "remaining_term_months" in df.columns:
            score -= ((df["remaining_term_months"] < 0) |
                      (df["remaining_term_months"] > 360)).astype(float) * 10

        # Document gap: -10
        if "document_status" in df.columns:
            score -= (df["document_status"] != "VERIFIED").astype(float) * 10

        # Prepayment balance mismatch: -20
        if {"current_status", "current_balance"}.issubset(df.columns):
            score -= ((df["current_status"] == "PREPAID") &
                      (df["current_balance"] > 0)).astype(float) * 20

        score = score.clip(lower=0, upper=100).round(1)
        df["dq_score"] = score

        keep = [c for c in ["loan_id", "reporting_month", "dq_score"] if c in df.columns]
        self.dq_scores = df[keep].copy()

        self.batch_dq = dict(
            mean_dq_score=round(float(score.mean()), 2),
            median_dq_score=round(float(score.median()), 2),
            pct_lt_60=round(float((score < 60).mean() * 100), 2),
            pct_lt_80=round(float((score < 80).mean() * 100), 2),
            pct_perfect=round(float((score == 100).mean() * 100), 2),
            min_score=round(float(score.min()), 2),
            max_score=round(float(score.max()), 2),
        )

        out_path = os.path.join("data", "processed", "record_dq_scores.csv")
        self.dq_scores.to_csv(out_path, index=False)
        print(f"  Mean DQ Score   : {self.batch_dq['mean_dq_score']} / 100")
        print(f"  Score < 80      : {self.batch_dq['pct_lt_80']}% of records")
        print(f"  Perfect (100)   : {self.batch_dq['pct_perfect']}% of records")
        print(f"  DQ scores saved : {out_path}")
        return self.dq_scores

    # ------------------------------------------------------------------
    # STEP 1.8 - Report Generation
    # ------------------------------------------------------------------
    def generate_report(self):
        print("\n" + "=" * 70)
        print("STEP 1.8: Generating Data Intelligence Report...")
        print("=" * 70)

        report_path = os.path.join(self.output_dir, "data_intelligence_report.md")
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Build top-5 issues list
        top_issues = []
        if not self.rule_violations.empty:
            for _, r in self.rule_violations[self.rule_violations["severity"] == "CRITICAL"].iterrows():
                if r["violation_count"] > 0:
                    top_issues.append(
                        f"**{r['rule_name']}** (CRITICAL): {r['violation_count']:,} violations "
                        f"({r['violation_pct']}%) - Exception: `{r['exception_type']}`"
                    )
        if not self.missing_analysis.empty:
            for _, r in self.missing_analysis[self.missing_analysis["impact"] == "HIGH"].iterrows():
                top_issues.append(f"**High Missingness** in `{r['column']}`: {r['null_pct']}% null ({r['pattern']})")
        if self.servicer_conflicts.get("balance_conflicts", 0) > 0:
            sc = self.servicer_conflicts
            top_issues.append(
                f"**Servicer Balance Conflicts**: {sc['balance_conflicts']:,} records "
                f"({sc['balance_conflict_pct']}%) exceed 5% discrepancy threshold"
            )
        if not self.psi_results.empty:
            hd = self.psi_results[self.psi_results["drift_level"] == "HIGH"]
            if len(hd) > 0:
                top_issues.append(
                    f"**High Train/Test Drift** (PSI > 0.2) in {len(hd)} features: "
                    + ", ".join(hd["column"].head(3).tolist())
                )

        with open(report_path, "w", encoding="utf-8") as f:

            # Header
            f.write("# Data Intelligence Report\n\n")
            f.write(f"**Intain AI Track 2026 — Loan Performance Intelligence Engine**  \n")
            f.write(f"**Generated**: {now}  \n\n---\n\n")

            # Executive Summary
            f.write("## Executive Summary\n\n")
            f.write("| Metric | Value |\n| :--- | ---: |\n")
            f.write(f"| Training Unique Loans | {self.df_train['loan_id'].nunique():,} |\n")
            f.write(f"| Training Monthly Records | {len(self.df_train):,} |\n")
            f.write(f"| Test Monthly Records | {len(self.df_test):,} |\n")
            f.write(f"| Train Reporting Period | {self.df_train['reporting_month'].min()} "
                    f"to {self.df_train['reporting_month'].max()} |\n")
            f.write(f"| Test Reporting Period | {self.df_test['reporting_month'].min()} "
                    f"to {self.df_test['reporting_month'].max()} |\n")
            f.write(f"| Servicer Update Records | {len(self.df_servicer):,} |\n")
            bq = self.batch_dq
            f.write(f"| Mean DQ Score | {bq.get('mean_dq_score', 'N/A')} / 100 |\n")
            f.write(f"| Records with DQ Score below 80 | {bq.get('pct_lt_80', 'N/A')}% |\n\n")

            f.write("### Top Data Quality Issues\n\n")
            if top_issues:
                for i, iss in enumerate(top_issues[:5], 1):
                    f.write(f"{i}. {iss}\n")
            else:
                f.write("No critical data quality issues detected.\n")
            f.write("\n---\n\n")

            # 1. Column Profile
            f.write("## 1. Column Distribution Profile\n\n")
            cp = self.col_profile
            if not cp.empty:
                num_cp = cp[cp["dtype"].str.contains("float|int", case=False, na=False)]
                cat_cp = cp[~cp["dtype"].str.contains("float|int", case=False, na=False)]
                f.write(f"- **Total Columns**: {len(cp)}\n")
                f.write(f"- **Numeric Columns**: {len(num_cp)}\n")
                f.write(f"- **Categorical Columns**: {len(cat_cp)}\n\n")

                f.write("### 1a. Numeric Column Statistics\n\n")
                f.write("| Column | Null% | Min | Max | Mean | Std | Median | Skew |\n")
                f.write("| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |\n")
                for _, r in num_cp.iterrows():
                    f.write(f"| `{r['column']}` | {r['null_pct']}% | {r['min']} | {r['max']} | "
                            f"{r['mean']} | {r['std']} | {r['median']} | {r['skew']} |\n")
                f.write("\n")

                f.write("### 1b. Categorical Column Summary\n\n")
                f.write("| Column | Null% | Unique | Top 3 Values |\n")
                f.write("| :--- | ---: | ---: | :--- |\n")
                for _, r in cat_cp.iterrows():
                    f.write(f"| `{r['column']}` | {r['null_pct']}% | {r['n_unique']} | {r['top_values']} |\n")
                f.write("\n")
            f.write("---\n\n")

            # 2. Missingness
            f.write("## 2. Missing Value Analysis\n\n")
            ma = self.missing_analysis
            if not ma.empty:
                f.write("| Column | Null Count | Null% | Pattern | Impact |\n")
                f.write("| :--- | ---: | ---: | :--- | :--- |\n")
                for _, r in ma.iterrows():
                    badge = "🔴" if r["impact"] == "HIGH" else ("🟠" if r["impact"] == "MEDIUM" else "🟡")
                    f.write(f"| `{r['column']}` | {r['null_count']:,} | {r['null_pct']}% | "
                            f"{r['pattern']} | {badge} {r['impact']} |\n")
            else:
                f.write("No missing values detected in the training dataset.\n")
            f.write("\n---\n\n")

            # 3. Outliers
            f.write("## 3. Outlier Detection (3x IQR Fence)\n\n")
            od = self.outlier_results
            if not od.empty:
                f.write("| Column | Lower Fence | Upper Fence | Outlier Count | Outlier% |\n")
                f.write("| :--- | ---: | ---: | ---: | ---: |\n")
                for _, r in od.iterrows():
                    f.write(f"| `{r['column']}` | {r['iqr_lower']:,} | {r['iqr_upper']:,} | "
                            f"{r['outlier_count']:,} | {r['outlier_pct']}% |\n")
            else:
                f.write("No significant outliers detected.\n")
            f.write("\n---\n\n")

            # 4. Validation Rules
            f.write("## 4. Validation Rule Results\n\n")
            rv = self.rule_violations
            if not rv.empty:
                f.write("| Rule ID | Rule Name | Severity | Violations | Violation% | Exception Type |\n")
                f.write("| :--- | :--- | :--- | ---: | ---: | :--- |\n")
                for _, r in rv.iterrows():
                    badge = "🔴" if r["severity"] == "CRITICAL" else ("🟠" if r["severity"] == "HIGH" else "🟡")
                    f.write(f"| {r['rule_id']} | {r['rule_name']} | {badge} {r['severity']} | "
                            f"{r['violation_count']:,} | {r['violation_pct']}% | `{r['exception_type']}` |\n")
            f.write("\n---\n\n")

            # 5. Servicer Conflicts
            f.write("## 5. Servicer Feed Reconciliation\n\n")
            sc = self.servicer_conflicts
            if sc:
                total = sc.get("total_matched", 1)
                f.write("| Conflict Type | Count | Percentage |\n| :--- | ---: | ---: |\n")
                f.write(f"| Matched Records | {sc.get('total_matched', 0):,} | 100.00% |\n")
                f.write(f"| Balance Conflicts (>5% diff) | {sc.get('balance_conflicts', 0):,} | {sc.get('balance_conflict_pct', 0)}% |\n")
                f.write(f"| Status Conflicts (mismatch) | {sc.get('status_conflicts', 0):,} | {sc.get('status_conflict_pct', 0)}% |\n")
                f.write(f"| Stale Records (lag > 1 year) | {sc.get('stale_records', 0):,} | {sc.get('stale_pct', 0)}% |\n")
                f.write(f"| Any Conflict (union) | {sc.get('any_conflict', 0):,} | "
                        f"{round(sc.get('any_conflict', 0) / max(total, 1) * 100, 2)}% |\n\n")

                if hasattr(self, "conflict_examples") and len(self.conflict_examples) > 0:
                    f.write("### Sample Conflict Records (Top 10)\n\n")
                    f.write("| Loan ID | Month | Primary Bal | Servicer Bal | Diff% | Primary Status | Servicer Status | Flags |\n")
                    f.write("| :--- | :--- | ---: | ---: | ---: | :--- | :--- | :--- |\n")
                    for _, r in self.conflict_examples.head(10).iterrows():
                        flags = []
                        if r.get("balance_conflict", 0): flags.append("BAL")
                        if r.get("status_conflict", 0): flags.append("STATUS")
                        if r.get("stale_flag", 0): flags.append("STALE")
                        pb = f"${r.get('current_balance', 0):,.2f}"
                        sb = f"${r.get('servicer_reported_balance', 0):,.2f}"
                        dp = r.get("balance_diff_pct", 0)
                        ps = r.get("current_status", "")
                        ss = r.get("servicer_reported_status", "")
                        f.write(f"| {r['loan_id']} | {r['reporting_month']} | {pb} | {sb} | "
                                f"{dp}% | {ps} | {ss} | {'+'.join(flags)} |\n")
            f.write("\n---\n\n")

            # 6. PSI Drift
            f.write("## 6. Train vs. Test Population Stability Index (PSI)\n\n")
            f.write("> PSI below 0.10 = Low (stable) | 0.10 to 0.20 = Medium (monitor) | above 0.20 = High (investigate)\n\n")
            psi = self.psi_results
            if not psi.empty:
                f.write("| Feature | PSI | Drift Level | Type |\n")
                f.write("| :--- | ---: | :--- | :--- |\n")
                for _, r in psi.iterrows():
                    badge = "🔴" if r["drift_level"] == "HIGH" else ("🟠" if r["drift_level"] == "MEDIUM" else "🟢")
                    f.write(f"| `{r['column']}` | {r['psi']} | {badge} {r['drift_level']} | {r['dtype']} |\n")
            f.write("\n---\n\n")

            # 7. DQ Score Distribution
            f.write("## 7. Data Quality Score Distribution\n\n")
            f.write("Record-level DQ Score (0-100): starts at 100, deducted for rule violations, missing fields, and balance anomalies.\n\n")
            bq = self.batch_dq
            f.write("| DQ Metric | Value |\n| :--- | ---: |\n")
            f.write(f"| Mean DQ Score | {bq.get('mean_dq_score', 'N/A')} |\n")
            f.write(f"| Median DQ Score | {bq.get('median_dq_score', 'N/A')} |\n")
            f.write(f"| Min DQ Score | {bq.get('min_score', 'N/A')} |\n")
            f.write(f"| Max DQ Score | {bq.get('max_score', 'N/A')} |\n")
            f.write(f"| Records below 60 (Critical) | {bq.get('pct_lt_60', 'N/A')}% |\n")
            f.write(f"| Records below 80 (Warning) | {bq.get('pct_lt_80', 'N/A')}% |\n")
            f.write(f"| Records at 100 (Perfect) | {bq.get('pct_perfect', 'N/A')}% |\n\n")

            f.write("---\n\n")
            f.write("*Generated by the Intain AI Track Loan Performance Intelligence Engine — Phase 1: Data Intelligence and Profiling*\n")

        print(f"  Report saved to: {report_path}")
        return report_path

    # ------------------------------------------------------------------
    # Run full Phase 1 pipeline
    # ------------------------------------------------------------------
    def run(self):
        print("\nStarting Phase 1: Data Intelligence and Profiling Pipeline...\n")
        self.profile_columns()
        self.analyze_missingness()
        self.detect_outliers()
        self.apply_validation_rules()
        self.detect_servicer_conflicts()
        self.compute_psi()
        self.compute_dq_scores()
        report_path = self.generate_report()
        print("\n" + "=" * 70)
        print("PHASE 1 COMPLETE!")
        print(f"Report: {report_path}")
        print("=" * 70)
        return report_path


if __name__ == "__main__":
    profiler = LoanDataProfiler(
        train_path="data/processed/loan_monthly_performance_train.csv",
        test_path="data/processed/loan_monthly_performance_test.csv",
        servicer_path="data/processed/servicer_updates.csv",
        rules_path="data/processed/validation_rules.json",
        output_dir="reports",
    )
    profiler.run()
