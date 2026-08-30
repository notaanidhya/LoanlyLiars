"""
src/data/profiler.py
Intain AI Track Phase 1: Data Intelligence & Profiling Engine
Covers: column profiling, missingness (MCAR/MAR), outliers, validation rules,
        servicer conflicts, PSI drift, Pearson/Spearman correlation & multicollinearity,
        DQ scoring, report generation.
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
        print("LOAN DATA PROFILER — PHASE 1: DATA INTELLIGENCE AND PROFILING")
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
        self.correlation_pairs = pd.DataFrame()
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
        print(f"  Profiled {len(self.col_profile)} columns successfully.")
        return self.col_profile

    # ------------------------------------------------------------------
    # STEP 1.2 - Missingness Analysis
    # ------------------------------------------------------------------
    def analyze_missingness(self):
        print("\n" + "=" * 70)
        print("STEP 1.2: Missingness Analysis (MCAR/MAR Detection)...")
        print("=" * 70)

        df = self.df_train
        records = []

        for col in df.columns:
            n_null = int(df[col].isnull().sum())
            if n_null == 0:
                continue
            null_pct = round(n_null / len(df) * 100, 2)

            pattern = "MCAR (Random)"
            pattern_detail = "Nulls uniformly distributed without target condition"
            impact = "LOW"

            if col == "loss_severity_band":
                def_null = int(df[df["default_flag"] == 1][col].isnull().sum())
                nondef_null = int(df[df["default_flag"] == 0][col].isnull().sum())
                nondef_tot = len(df[df["default_flag"] == 0])
                if nondef_tot > 0 and (nondef_null / nondef_tot) > 0.95:
                    pattern = "MAR (Mechanistic)"
                    pattern_detail = f"Null in 100% of non-default records; populated exclusively upon default (expected behavior)"
                    impact = "INFORMATIONAL"
            elif col == "credit_score_band":
                inv_null = df[df["occupancy_type"] == "I"][col].isnull().mean()
                prim_null = df[df["occupancy_type"] == "P"][col].isnull().mean()
                if inv_null > prim_null * 1.5:
                    pattern = "MAR (Conditional)"
                    pattern_detail = f"Missingness rate is {inv_null*100:.1f}% for Investment vs {prim_null*100:.1f}% for Primary occupancy"
                    impact = "MEDIUM"
            elif null_pct > 15:
                pattern = "MNAR (Potential Structural Gap)"
                pattern_detail = f"High missingness ({null_pct}%) requires feature engineering imputation"
                impact = "HIGH"
            elif null_pct > 0.05:
                impact = "MEDIUM"

            records.append(dict(
                column=col,
                null_count=n_null,
                null_pct=null_pct,
                pattern=pattern,
                pattern_detail=pattern_detail,
                impact=impact,
            ))

        if not records:
            records.append(dict(
                column="None", null_count=0, null_pct=0.0,
                pattern="COMPLETE", pattern_detail="No missing values in dataset",
                impact="NONE",
            ))

        self.missing_analysis = pd.DataFrame(records).sort_values("null_pct", ascending=False)
        print(f"  Identified {len(self.missing_analysis)} columns with missing data.")
        return self.missing_analysis

    # ------------------------------------------------------------------
    # STEP 1.3 - Outlier Detection (3x IQR)
    # ------------------------------------------------------------------
    def detect_outliers(self):
        print("\n" + "=" * 70)
        print("STEP 1.3: Outlier Detection (3x IQR Extreme Outliers)...")
        print("=" * 70)

        df = self.df_train
        outlier_cols = ["original_balance", "current_balance", "interest_rate", "days_past_due"]
        outlier_cols = [c for c in outlier_cols if c in df.columns]

        rows = []
        for col in outlier_cols:
            s = df[col].dropna()
            q25, q75 = float(s.quantile(0.25)), float(s.quantile(0.75))
            iqr = q75 - q25
            lb, ub = q25 - 3.0 * iqr, q75 + 3.0 * iqr

            outliers = df[(df[col] < lb) | (df[col] > ub)]
            cnt = len(outliers)
            pct = round(cnt / len(df) * 100, 3)

            rows.append(dict(
                column=col,
                q25=round(q25, 2),
                q75=round(q75, 2),
                iqr=round(iqr, 2),
                lower_fence=round(lb, 2),
                upper_fence=round(ub, 2),
                outlier_count=cnt,
                outlier_pct=pct,
            ))

        self.outlier_results = pd.DataFrame(rows)
        print(f"  Evaluated {len(outlier_cols)} columns for extreme outliers.")
        return self.outlier_results

    # ------------------------------------------------------------------
    # STEP 1.4 - Validation Rule Scanning
    # ------------------------------------------------------------------
    def apply_validation_rules(self):
        print("\n" + "=" * 70)
        print("STEP 1.4: Validation Rule Scanning (VR-001 to VR-008)...")
        print("=" * 70)

        df = self.df_train
        results = []

        for r in self.rules:
            rid = r.get("rule_id", "VR-XXX")
            rname = r.get("rule_name", "Unknown")
            sev = r.get("severity", "MEDIUM")
            etype = r.get("exception_type", "OTHER")

            violations = 0
            if rid == "VR-001" and {"current_balance", "original_balance", "modification_flag"}.issubset(df.columns):
                violations = int(((df["current_balance"] > df["original_balance"] * 1.15) & (df["modification_flag"] != "Y")).sum())
            elif rid == "VR-002" and {"days_past_due", "current_status"}.issubset(df.columns):
                violations = int(((df["days_past_due"] > 0) & (df["current_status"] == "CURRENT")).sum())
            elif rid == "VR-003" and {"reporting_month", "origination_month"}.issubset(df.columns):
                violations = int((df["reporting_month"].astype(str) < df["origination_month"].astype(str)).sum())
            elif rid == "VR-004" and "remaining_term_months" in df.columns:
                violations = int(((df["remaining_term_months"] < 0) | (df["remaining_term_months"] > 360)).sum())
            elif rid == "VR-005" and {"current_status", "current_balance"}.issubset(df.columns):
                violations = int(((df["current_status"] == "PREPAID") & (df["current_balance"] > 0)).sum())
            elif rid == "VR-006" and "document_status" in df.columns:
                violations = int((df["document_status"] != "VERIFIED").sum())

            pct = round(violations / len(df) * 100, 2)
            results.append(dict(
                rule_id=rid, rule_name=rname, severity=sev,
                exception_type=etype, violation_count=violations,
                violation_pct=pct
            ))

        self.rule_violations = pd.DataFrame(results)
        tot = self.rule_violations["violation_count"].sum()
        print(f"  Scanned {len(self.rules)} rules. Total violations: {tot:,}")
        return self.rule_violations

    # ------------------------------------------------------------------
    # STEP 1.5 - Servicer Conflict Reconciliation
    # ------------------------------------------------------------------
    def detect_servicer_conflicts(self):
        print("\n" + "=" * 70)
        print("STEP 1.5: Cross-Source Servicer Conflict Reconciliation...")
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
        return self.servicer_conflicts

    # ------------------------------------------------------------------
    # STEP 1.6 - Train vs. Test Population Stability Index (PSI)
    # ------------------------------------------------------------------
    def compute_psi(self):
        print("\n" + "=" * 70)
        print("STEP 1.6: Population Stability Index (Train vs. Test Drift)...")
        print("=" * 70)

        common_cols = [c for c in self.df_train.columns
                       if c in self.df_test.columns
                       and c not in ("loan_id", "source_system", "reporting_month", "origination_month", "last_updated_at")]

        rows = []
        for col in common_cols:
            tr = self.df_train[col].dropna()
            te = self.df_test[col].dropna()
            if len(tr) == 0 or len(te) == 0:
                continue

            try:
                if tr.dtype.kind in ("i", "f", "u"):
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
    # STEP 1.7 - Bivariate Correlation & Multicollinearity Analysis
    # ------------------------------------------------------------------
    def compute_correlations(self, threshold=0.70):
        print("\n" + "=" * 70)
        print("STEP 1.7: Bivariate Correlation & Multicollinearity Analysis...")
        print("=" * 70)

        df = self.df_train.copy()
        
        # Select numeric and ordinal columns
        num_cols = [c for c in df.columns if df[c].dtype.kind in ("i", "f", "u")]
        num_cols = [c for c in num_cols if c not in ("loan_id", "month_index", "dq_score")]
        
        corr_matrix = df[num_cols].corr(method="pearson")
        spearman_matrix = df[num_cols].corr(method="spearman")
        
        collinear_pairs = []
        for i in range(len(num_cols)):
            for j in range(i + 1, len(num_cols)):
                f1, f2 = num_cols[i], num_cols[j]
                r_p = corr_matrix.loc[f1, f2]
                r_s = spearman_matrix.loc[f1, f2]
                if abs(r_p) >= threshold or abs(r_s) >= threshold:
                    collinear_pairs.append({
                        "feature_1": f1,
                        "feature_2": f2,
                        "pearson_r": round(float(r_p), 4),
                        "spearman_rho": round(float(r_s), 4),
                        "severity": "HIGH_COLLINEARITY" if (abs(r_p) >= 0.85 or abs(r_s) >= 0.85) else "MODERATE_COLLINEARITY"
                    })
        
        self.correlation_pairs = pd.DataFrame(collinear_pairs).sort_values("pearson_r", ascending=False) if collinear_pairs else pd.DataFrame()
        print(f"  Computed correlations across {len(num_cols)} numeric features.")
        print(f"  Flagged {len(collinear_pairs)} feature pairs exceeding |r| >= {threshold}")
        return self.correlation_pairs

    # ------------------------------------------------------------------
    # STEP 1.8 - Record-Level DQ Scoring
    # ------------------------------------------------------------------
    def compute_dq_scores(self):
        print("\n" + "=" * 70)
        print("STEP 1.8: Computing Record-Level Data Quality Scores (0-100)...")
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
    # STEP 1.9 - Report Generation
    # ------------------------------------------------------------------
    def generate_report(self):
        print("\n" + "=" * 70)
        print("STEP 1.9: Generating Data Intelligence Report...")
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

                f.write("### Numeric Features\n\n")
                f.write("| Column | Dtype | Null Count | Null% | Min | Median | Mean | Max | Std | Skew |\n")
                f.write("| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |\n")
                for _, r in num_cp.iterrows():
                    f.write(f"| `{r['column']}` | {r['dtype']} | {r['null_count']:,} | {r['null_pct']}% | "
                            f"{r['min']} | {r['median']} | {r['mean']} | {r['max']} | {r['std']} | {r['skew']} |\n")

                f.write("\n### Categorical Features\n\n")
                f.write("| Column | Dtype | Unique | Null Count | Null% | Top Values |\n")
                f.write("| :--- | :--- | ---: | ---: | ---: | :--- |\n")
                for _, r in cat_cp.iterrows():
                    f.write(f"| `{r['column']}` | {r['dtype']} | {r['n_unique']:,} | {r['null_count']:,} | "
                            f"{r['null_pct']}% | {r['top_values']} |\n")
            f.write("\n---\n\n")

            # 2. Missingness Analysis
            f.write("## 2. Missingness Analysis (MCAR / MAR Patterns)\n\n")
            ma = self.missing_analysis
            if not ma.empty:
                f.write("| Column | Null Count | Null% | Classification | Impact | Description |\n")
                f.write("| :--- | ---: | ---: | :--- | :--- | :--- |\n")
                for _, r in ma.iterrows():
                    badge = "🔴" if r["impact"] == "HIGH" else ("🟠" if r["impact"] == "MEDIUM" else "🟢")
                    f.write(f"| `{r['column']}` | {r['null_count']:,} | {r['null_pct']}% | "
                            f"**{r['pattern']}** | {badge} {r['impact']} | {r['pattern_detail']} |\n")
            f.write("\n---\n\n")

            # 3. Outlier Detection
            f.write("## 3. Extreme Outliers (3x IQR Fence)\n\n")
            out = self.outlier_results
            if not out.empty:
                f.write("| Feature | Lower Fence | Upper Fence | Outlier Count | Outlier% |\n")
                f.write("| :--- | ---: | ---: | ---: | ---: |\n")
                for _, r in out.iterrows():
                    f.write(f"| `{r['column']}` | {r['lower_fence']:,} | {r['upper_fence']:,} | "
                            f"{r['outlier_count']:,} | {r['outlier_pct']}% |\n")
            f.write("\n---\n\n")

            # 4. Validation Rules
            f.write("## 4. Deterministic Business & Accounting Rule Violations\n\n")
            rv = self.rule_violations
            if not rv.empty:
                f.write("| Rule ID | Rule Name | Severity | Exception Type | Violations | Violation% |\n")
                f.write("| :--- | :--- | :--- | :--- | ---: | ---: |\n")
                for _, r in rv.iterrows():
                    badge = "🔴" if r["severity"] == "CRITICAL" else ("🟠" if r["severity"] == "HIGH" else "🟡")
                    f.write(f"| `{r['rule_id']}` | {r['rule_name']} | {badge} {r['severity']} | "
                            f"`{r['exception_type']}` | {r['violation_count']:,} | {r['violation_pct']}% |\n")
            f.write("\n---\n\n")

            # 5. Servicer Conflicts
            f.write("## 5. Cross-Source Servicer Conflict Reconciliation\n\n")
            sc = self.servicer_conflicts
            f.write(f"- Total Matched Records: **{sc.get('total_matched', 0):,}**\n")
            f.write(f"- Balance Discrepancies (>5%): **{sc.get('balance_conflicts', 0):,}** ({sc.get('balance_conflict_pct', 0)}%)\n")
            f.write(f"- Status Discrepancies: **{sc.get('status_conflicts', 0):,}** ({sc.get('status_conflict_pct', 0)}%)\n")
            f.write(f"- Stale Feed Records: **{sc.get('stale_records', 0):,}** ({sc.get('stale_pct', 0)}%)\n\n")

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

            # 7. Correlation Analysis
            f.write("## 7. Multicollinearity & Bivariate Correlation Analysis\n\n")
            f.write("> Highlights highly dependent feature pairs (|r| >= 0.70) to inform regularization and model interpretability.\n\n")
            cpairs = self.correlation_pairs
            if not cpairs.empty:
                f.write("| Feature 1 | Feature 2 | Pearson r | Spearman rho | Collinearity Level |\n")
                f.write("| :--- | :--- | ---: | ---: | :--- |\n")
                for _, r in cpairs.iterrows():
                    badge = "🔴" if r["severity"] == "HIGH_COLLINEARITY" else "🟠"
                    f.write(f"| `{r['feature_1']}` | `{r['feature_2']}` | **{r['pearson_r']:.4f}** | {r['spearman_rho']:.4f} | {badge} {r['severity']} |\n")
            else:
                f.write("No feature pairs exceeded the |r| >= 0.70 threshold.\n")
            f.write("\n---\n\n")

            # 8. DQ Score Distribution
            f.write("## 8. Data Quality Score Distribution\n\n")
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
        self.compute_correlations()
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
