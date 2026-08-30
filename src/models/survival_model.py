"""
src/models/survival_model.py
Intain AI Track — Phase 2: Survival & Transition Modeling
Covers: Kaplan-Meier event curves, Cox Proportional Hazards,
        Markov state transition probability matrix.
"""

import pandas as pd
import numpy as np
from lifelines import KaplanMeierFitter, CoxPHFitter
import os
import pickle


class SurvivalAnalyzer:
    """
    Computes time-to-event (default / prepayment) models from a monthly
    performance panel dataset and derives a Markov state transition matrix.
    """

    def __init__(self, df_train):
        self.df_train = df_train
        self.kmf_default = None
        self.kmf_prepay = None
        self.cph = None
        self.transition_matrix = None
        self.loan_level_df = None
        self.km_table = None

    def prepare_loan_level_data(self):
        df = self.df_train.copy()
        df = df.sort_values(["loan_id", "reporting_month"])
        results = []

        for loan_id, grp in df.groupby("loan_id", sort=False):
            grp = grp.reset_index(drop=True)
            max_obs = int(grp["month_index"].max())

            # Default event
            default_mask = grp["default_flag"] == 1
            if "current_status" in grp.columns:
                default_mask = default_mask | (grp["current_status"] == "90PLUS_DPD")
            def_rows = grp[default_mask]
            if len(def_rows) > 0:
                t_def = max(1, int(def_rows["month_index"].min()))
                e_def = 1
            else:
                t_def = max(1, max_obs)
                e_def = 0

            # Prepayment event
            prepay_mask = grp["prepayment_flag"] == 1
            if "current_status" in grp.columns:
                prepay_mask = prepay_mask | (grp["current_status"] == "PREPAID")
            pre_rows = grp[prepay_mask]
            if len(pre_rows) > 0:
                t_pre = max(1, int(pre_rows["month_index"].min()))
                e_pre = 1
            else:
                t_pre = max(1, max_obs)
                e_pre = 0

            first = grp.iloc[0]
            row = {
                "loan_id": loan_id,
                "time_to_default": t_def,
                "default_event": e_def,
                "time_to_prepay": t_pre,
                "prepay_event": e_pre,
                "interest_rate": float(first.get("interest_rate", 4.5)),
                "original_balance": float(first.get("original_balance", 200000)),
                "loan_age_at_origin": float(first.get("loan_age_months", 0)),
            }
            for feat in ["credit_score_ord", "ltv_ord", "dti_ord"]:
                row[feat] = float(first[feat]) if feat in first.index else 2.0

            results.append(row)

        self.loan_level_df = pd.DataFrame(results)
        n_def = int(self.loan_level_df["default_event"].sum())
        n_pre = int(self.loan_level_df["prepay_event"].sum())
        print(f"    Loan-level: {len(results):,} loans | Default events: {n_def:,} | Prepay events: {n_pre:,}")
        return self.loan_level_df

    def fit_kaplan_meier(self, loan_df):
        print("\n    Fitting Kaplan-Meier (Default)...")
        self.kmf_default = KaplanMeierFitter(label="Default Survival")
        self.kmf_default.fit(durations=loan_df["time_to_default"], event_observed=loan_df["default_event"])

        print("    Fitting Kaplan-Meier (Prepayment)...")
        self.kmf_prepay = KaplanMeierFitter(label="Prepayment Survival")
        self.kmf_prepay.fit(durations=loan_df["time_to_prepay"], event_observed=loan_df["prepay_event"])

        # Key time checkpoints
        checkpoints = [3, 6, 12, 18, 24]
        def_sf = self.kmf_default.survival_function_
        pre_sf = self.kmf_prepay.survival_function_

        km_rows = []
        for t in checkpoints:
            def_s = float(def_sf[def_sf.index <= t].iloc[-1].values[0]) if (def_sf.index <= t).any() else 1.0
            pre_s = float(pre_sf[pre_sf.index <= t].iloc[-1].values[0]) if (pre_sf.index <= t).any() else 1.0
            km_rows.append({
                "month": t,
                "default_survival_prob": round(def_s, 4),
                "cumulative_default_prob": round(1 - def_s, 4),
                "prepay_survival_prob": round(pre_s, 4),
                "cumulative_prepay_prob": round(1 - pre_s, 4),
            })

        self.km_table = pd.DataFrame(km_rows)
        print(f"    KM Median time-to-default:    {self.kmf_default.median_survival_time_} months")
        print(f"    KM Median time-to-prepayment: {self.kmf_prepay.median_survival_time_} months")
        print(f"\n{self.km_table.to_string(index=False)}")
        return self.kmf_default, self.kmf_prepay

    def fit_cox_ph(self, loan_df, cox_features):
        print("\n    Fitting Cox Proportional Hazards (Default)...")
        required = ["time_to_default", "default_event"] + cox_features
        cox_df = loan_df[required].dropna().copy()
        cox_df = cox_df[cox_df["time_to_default"] > 0]

        self.cph = CoxPHFitter(penalizer=0.1)
        try:
            self.cph.fit(cox_df, duration_col="time_to_default", event_col="default_event")
            print(f"    Concordance Index (C-stat): {self.cph.concordance_index_:.4f}")
            summary = self.cph.summary[["coef", "exp(coef)", "se(coef)", "p"]].copy()
            summary["abs_coef"] = summary["coef"].abs()
            summary = summary.sort_values("abs_coef", ascending=False).drop(columns=["abs_coef"])
            print("\n    Cox PH Feature Hazard Ratios:")
            print(summary.round(4).to_string())
        except Exception as ex:
            print(f"    WARNING: Cox PH failed — {ex}")
            self.cph = None
        return self.cph

    def compute_transition_matrix(self):
        print("\n    Computing Markov State Transition Matrix...")
        df = self.df_train.copy()
        df = df.sort_values(["loan_id", "reporting_month"])
        df["next_status"] = df.groupby("loan_id")["current_status"].shift(-1)
        df_t = df.dropna(subset=["next_status"]).copy()

        all_states = sorted(
            set(df_t["current_status"].unique()) | set(df_t["next_status"].unique())
        )
        counts = pd.crosstab(df_t["current_status"], df_t["next_status"])
        counts = counts.reindex(index=all_states, columns=all_states, fill_value=0)
        prob_matrix = counts.div(counts.sum(axis=1), axis=0).fillna(0)

        self.transition_matrix = prob_matrix
        self.transition_counts = counts
        print("\n    Monthly State Transition Probabilities:")
        print(prob_matrix.round(3).to_string())
        return prob_matrix

    def run(self):
        print("  Preparing loan-level time-to-event data...")
        loan_df = self.prepare_loan_level_data()

        print("\n  Kaplan-Meier Analysis:")
        self.fit_kaplan_meier(loan_df)

        print("\n  Cox Proportional Hazards:")
        cox_features = [c for c in ["interest_rate", "credit_score_ord", "ltv_ord", "dti_ord",
                                     "original_balance", "loan_age_at_origin"] if c in loan_df.columns]
        self.fit_cox_ph(loan_df, cox_features)

        print("\n  State Transition Matrix:")
        self.compute_transition_matrix()

        return {
            "kmf_default": self.kmf_default,
            "kmf_prepay": self.kmf_prepay,
            "cph": self.cph,
            "transition_matrix": self.transition_matrix,
            "km_table": self.km_table,
            "concordance_index": self.cph.concordance_index_ if self.cph else None,
        }

    def save(self, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(self, f)
        print(f"  SurvivalAnalyzer saved: {path}")
