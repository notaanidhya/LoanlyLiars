"""
src/data/feature_engineer.py
Intain AI Track — Phase 2: Feature Engineering Pipeline (Refactored & Production-Grade)
Covers:
  - Inference Lag State Persistence across Train/Test boundaries (Zero Lag Collapse)
  - Deterministic Macro Rate Mapping & Scenario Shock API (Phase 5 Linkage)
  - Missingness-aware Ordinal Encodings (-1 for missing risk data, no naive imputation)
  - Deterministic static nominal encodings (zero chronological leak)
  - Temporal lag features, balance trajectory, DPD velocity & roll stats
  - Multi-feature risk interactions
  - Strict panel-wide chronological sorting
"""

import pandas as pd
import numpy as np
import pickle
import os

# Deterministic Ordinal Mappings (Missing maps to -1 for native XGBoost handling)
CREDIT_SCORE_MAP = {
    "<=620 (Poor)": 0,
    "<=620 (Sub-Prime)": 0,
    "621-680 (Fair)": 1,
    "681-740 (Good)": 2,
    "741-800 (Very Good)": 3,
    "801-850 (Excellent)": 4,
    ">850": 5,
}

LTV_MAP = {
    "<=60%": 0,
    "61-75%": 1,
    "76-80%": 2,
    "81-90%": 3,
    "91-95%": 4,
    ">95%": 5,
}

DTI_MAP = {
    "<=20%": 0,
    "21-30%": 1,
    "31-40%": 2,
    "41-45%": 3,
    "46-50%": 4,
    ">50%": 5,
}

STATUS_SEVERITY = {
    "CURRENT": 0,
    "30_DPD": 1,
    "60_DPD": 2,
    "90PLUS_DPD": 3,
    "DEFAULT": 4,
    "PREPAID": -1,
    "MODIFIED": 1,
}

US_STATES = [
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
    "DC", "PR", "VI", "GU"
]
STATE_MAP = {s: i for i, s in enumerate(US_STATES)}

SERVICER_NAMES = [
    "Freedom Mortgage Corporation",
    "JPMorgan Chase Bank, N.A.",
    "Nationstar Mortgage LLC (Mr. Cooper)",
    "Newrez LLC",
    "Pennymac Loan Services, LLC",
    "Rocket Mortgage, LLC",
    "U.S. Bank National Association",
    "Wells Fargo Bank, N.A."
]
SERVICER_MAP = {s: i for i, s in enumerate(SERVICER_NAMES)}

STATIC_NOMINAL_MAPS = {
    "loan_purpose": {"P": 0, "C": 1, "N": 2, "R": 3, "PURCHASE": 0, "REFINANCE": 1, "CASH_OUT": 2},
    "occupancy_type": {"P": 0, "I": 1, "S": 2, "PRIMARY": 0, "INVESTMENT": 1, "SECOND_HOME": 2},
    "property_type": {"SF": 0, "CO": 1, "PU": 2, "MH": 3, "CP": 4, "SINGLE_FAMILY": 0, "CONDO": 1, "PUD": 2, "MANUFACTURED": 3},
    "source_system": {"CORE_SERVICING_SYSTEM": 0, "ORIGINATION_SYSTEM": 1, "SERVICER_PORTAL": 2},
    "document_status": {"VERIFIED": 0, "MISSING_NOTE": 1, "INCOMPLETE_INCOME": 2, "UNVERIFIED_APPRAISAL": 3, "PENDING": 4},
}


class FeatureEngineer:
    """Production-grade feature engineering pipeline for loan monthly performance data."""

    def __init__(self):
        self.feature_cols = []
        self.fitted = False
        self.history_tail_df = None
        self.macro_rate_map = {}
        self.baseline_macro_rate = 4.25

    def encode_ordinals(self, df):
        df = df.copy()
        # Map missing risk attributes to -1 (never impute missing credit as 'Good')
        if "credit_score_band" in df.columns:
            df["credit_score_ord"] = df["credit_score_band"].map(CREDIT_SCORE_MAP).fillna(-1).astype(int)
        if "ltv_band" in df.columns:
            df["ltv_ord"] = df["ltv_band"].map(LTV_MAP).fillna(-1).astype(int)
        if "dti_band" in df.columns:
            df["dti_ord"] = df["dti_band"].map(DTI_MAP).fillna(-1).astype(int)
        if "current_status" in df.columns:
            df["status_severity"] = df["current_status"].map(STATUS_SEVERITY).fillna(0).astype(int)
        return df

    def encode_categoricals(self, df):
        df = df.copy()
        if "state" in df.columns:
            df["state_enc"] = df["state"].map(STATE_MAP).fillna(-1).astype(int)
        if "servicer_name" in df.columns:
            df["servicer_name_enc"] = df["servicer_name"].map(SERVICER_MAP).fillna(-1).astype(int)

        for col, m in STATIC_NOMINAL_MAPS.items():
            if col in df.columns:
                df[col + "_enc"] = df[col].astype(str).str.strip().map(m).fillna(-1).astype(int)
        return df

    def apply_macro_shock(self, shock_bps: float):
        """Simulates Phase 5 macroeconomic interest rate shocks by shifting the macro curve."""
        shock_pct = shock_bps / 100.0
        for k in self.macro_rate_map:
            self.macro_rate_map[k] += shock_pct
        self.baseline_macro_rate += shock_pct
        print(f"  Applied macro interest rate shock: {shock_bps:+d} bps (New baseline: {self.baseline_macro_rate:.2f}%)")

    def create_temporal_features(self, df, is_test=False):
        df = df.copy()

        # If evaluating test batch, prepend historical boundary state from training
        if is_test and self.history_tail_df is not None:
            hist_rows = self.history_tail_df.copy()
            hist_rows["_is_history"] = True
            df["_is_history"] = False
            combined = pd.concat([hist_rows, df], ignore_index=True)
        else:
            combined = df
            combined["_is_history"] = False

        combined = combined.sort_values(["loan_id", "reporting_month"]).reset_index(drop=True)
        grp = combined.groupby("loan_id", sort=False)

        # Balance trajectory
        combined["prev_balance"] = grp["current_balance"].shift(1)
        combined["balance_change_1m"] = combined["current_balance"] - combined["prev_balance"]
        safe_orig = np.maximum(combined["original_balance"].fillna(1.0), 1.0)
        combined["balance_pct_original"] = combined["current_balance"] / safe_orig
        combined["balance_ratio_change"] = combined["balance_change_1m"] / (combined["original_balance"] + 1e-5)
        combined["amortization_pct"] = (1.0 - combined["balance_pct_original"]).clip(lower=0, upper=1)

        # DPD trends & roll rates
        combined["prev_dpd"] = grp["days_past_due"].shift(1)
        combined["dpd_change_1m"] = combined["days_past_due"] - combined["prev_dpd"]
        combined["dpd_3m_max"] = grp["days_past_due"].transform(lambda x: x.rolling(3, min_periods=1).max())
        combined["dpd_3m_mean"] = grp["days_past_due"].transform(lambda x: x.rolling(3, min_periods=1).mean())
        combined["dpd_6m_max"] = grp["days_past_due"].transform(lambda x: x.rolling(6, min_periods=1).max())
        combined["ever_delinquent"] = grp["days_past_due"].transform(lambda x: (x > 0).cumsum().clip(upper=1))
        combined["cumulative_prepay_flags"] = grp["prepayment_flag"].transform("cumsum")
        combined["cumulative_default_flags"] = grp["default_flag"].transform("cumsum")

        # Status severity lag
        if "status_severity" in combined.columns:
            combined["prev_status_severity"] = grp["status_severity"].shift(1)
            combined["status_delta"] = combined["status_severity"] - combined["prev_status_severity"]
            combined["prev_status_severity"] = combined["prev_status_severity"].fillna(0)
            combined["status_delta"] = combined["status_delta"].fillna(0)

        # Deterministic Macroeconomic Interest Rate Level and Spread to Market
        if not self.fitted:
            month_avg_rate = combined.groupby("reporting_month")["interest_rate"].mean().to_dict()
            self.macro_rate_map = month_avg_rate
            self.baseline_macro_rate = float(combined["interest_rate"].mean())

        rep_months = combined["reporting_month"].astype(str).values
        macro_rates = np.array([self.macro_rate_map.get(m, self.baseline_macro_rate) for m in rep_months])
        combined["market_avg_rate"] = macro_rates
        combined["rate_spread_to_market"] = combined["interest_rate"] - macro_rates
        combined["prepayment_incentive"] = combined["interest_rate"] - macro_rates

        # Fill difference lags for genuine first-ever observations
        for col in ["prev_balance", "balance_change_1m", "balance_ratio_change", "prev_dpd", "dpd_change_1m"]:
            if col in combined.columns:
                combined[col] = combined[col].fillna(0)

        # If test, slice out only the test records
        if is_test and self.history_tail_df is not None:
            out_df = combined[combined["_is_history"] == False].drop(columns=["_is_history"]).reset_index(drop=True)
        else:
            out_df = combined.drop(columns=["_is_history"]).reset_index(drop=True)

        # Re-sort globally by reporting_month and loan_id for strict chronological time splits
        out_df = out_df.sort_values(["reporting_month", "loan_id"]).reset_index(drop=True)
        return out_df

    def create_interaction_features(self, df):
        df = df.copy()
        if "dti_ord" in df.columns and "ltv_ord" in df.columns:
            d_val = np.where(df["dti_ord"] >= 0, df["dti_ord"], np.nan)
            l_val = np.where(df["ltv_ord"] >= 0, df["ltv_ord"], np.nan)
            df["dti_x_ltv"] = np.where(pd.notnull(d_val) & pd.notnull(l_val), d_val * l_val, -1.0)
        if "loan_age_months" in df.columns and "interest_rate" in df.columns:
            df["age_x_rate"] = df["loan_age_months"] * df["interest_rate"]
        if "credit_score_ord" in df.columns and "dti_ord" in df.columns:
            c_val = np.where(df["credit_score_ord"] >= 0, df["credit_score_ord"], np.nan)
            d_val = np.where(df["dti_ord"] >= 0, df["dti_ord"], np.nan)
            df["creditworthiness_net"] = np.where(pd.notnull(c_val) & pd.notnull(d_val), c_val - d_val, -1.0)
        if all(c in df.columns for c in ["credit_score_ord", "ltv_ord", "dti_ord"]):
            df["high_risk_combo"] = (
                (df["credit_score_ord"] >= 0) & (df["credit_score_ord"] <= 1) & 
                (df["ltv_ord"] >= 3) & (df["dti_ord"] >= 3)
            ).astype(int)
        if "dpd_3m_mean" in df.columns and "balance_pct_original" in df.columns:
            df["distress_score"] = df["dpd_3m_mean"] * df["balance_pct_original"]
        if "remaining_term_months" in df.columns and "days_past_due" in df.columns:
            df["maturity_pressure"] = df["remaining_term_months"] / 12.0 * (df["days_past_due"] + 1)
        return df

    def _get_feature_columns(self, df):
        static = [
            "loan_age_months", "remaining_term_months", "original_balance",
            "current_balance", "interest_rate", "days_past_due",
            "prepayment_flag", "default_flag", "modification_flag_bin",
        ]
        ordinal = ["credit_score_ord", "ltv_ord", "dti_ord", "status_severity"]
        cat_enc = sorted([c for c in df.columns if c.endswith("_enc")])
        temporal = [
            "prev_balance", "balance_change_1m", "balance_pct_original",
            "balance_ratio_change", "amortization_pct",
            "prev_dpd", "dpd_change_1m", "dpd_3m_max", "dpd_3m_mean",
            "dpd_6m_max", "ever_delinquent",
            "cumulative_prepay_flags", "cumulative_default_flags",
            "prev_status_severity", "status_delta",
        ]
        macro = ["market_avg_rate", "rate_spread_to_market", "prepayment_incentive"]
        interactions = [
            "dti_x_ltv", "age_x_rate", "creditworthiness_net",
            "high_risk_combo", "distress_score", "maturity_pressure",
        ]
        all_c = static + ordinal + cat_enc + temporal + macro + interactions
        return [c for c in all_c if c in df.columns]

    def fit_transform(self, df):
        df = self.encode_ordinals(df)
        df = self.encode_categoricals(df)
        df["modification_flag_bin"] = (df["modification_flag"].astype(str).str.strip() == "Y").astype(int)
        df = self.create_temporal_features(df, is_test=False)
        df = self.create_interaction_features(df)
        self.feature_cols = self._get_feature_columns(df)
        self.fitted = True

        # Store historical boundary tail per loan for seamless inference lag calculations
        df_sorted = df.sort_values(["loan_id", "reporting_month"]).reset_index(drop=True)
        self.history_tail_df = df_sorted.groupby("loan_id", sort=False).tail(1).copy()
        print(f"  FeatureEngineer: {len(self.feature_cols)} features derived. Persisted {len(self.history_tail_df):,} loan historical tail states.")
        return df

    def transform(self, df):
        df = self.encode_ordinals(df)
        df = self.encode_categoricals(df)
        if "modification_flag" in df.columns:
            df["modification_flag_bin"] = (df["modification_flag"].astype(str).str.strip() == "Y").astype(int)
        else:
            df["modification_flag_bin"] = 0
        df = self.create_temporal_features(df, is_test=True)
        df = self.create_interaction_features(df)
        return df

    def save(self, path="models/feature_engineer.pkl"):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(self, f)
        print(f"  FeatureEngineer saved: {path}")

    @staticmethod
    def load(path="models/feature_engineer.pkl"):
        with open(path, "rb") as f:
            return pickle.load(f)
