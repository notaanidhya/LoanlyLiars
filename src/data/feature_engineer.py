"""
src/data/feature_engineer.py
Intain AI Track — Phase 2: Feature Engineering Pipeline
Covers: ordinal encoding, categorical encoding, temporal lag features,
        DPD trends, balance trajectory, interaction terms.
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
import pickle
import os

# Ordinal mappings
CREDIT_SCORE_MAP = {
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

NOMINAL_COLS = [
    "state",
    "loan_purpose",
    "occupancy_type",
    "property_type",
    "servicer_name",
    "source_system",
]


class FeatureEngineer:
    """Full feature engineering pipeline for loan monthly performance data."""

    def __init__(self):
        self.label_encoders = {}
        self.feature_cols = []
        self.fitted = False

    def encode_ordinals(self, df):
        df = df.copy()
        if "credit_score_band" in df.columns:
            df["credit_score_ord"] = df["credit_score_band"].map(CREDIT_SCORE_MAP).fillna(2).astype(int)
        if "ltv_band" in df.columns:
            df["ltv_ord"] = df["ltv_band"].map(LTV_MAP).fillna(2).astype(int)
        if "dti_band" in df.columns:
            df["dti_ord"] = df["dti_band"].map(DTI_MAP).fillna(2).astype(int)
        if "current_status" in df.columns:
            df["status_severity"] = df["current_status"].map(STATUS_SEVERITY).fillna(0).astype(int)
        return df

    def encode_categoricals(self, df, fit=True):
        df = df.copy()
        for col in NOMINAL_COLS:
            if col not in df.columns:
                continue
            vals = df[col].astype(str).fillna("UNKNOWN")
            if fit:
                le = LabelEncoder()
                df[col + "_enc"] = le.fit_transform(vals)
                self.label_encoders[col] = le
            else:
                if col not in self.label_encoders:
                    continue
                le = self.label_encoders[col]
                known = set(le.classes_)
                vals = vals.apply(lambda x: x if x in known else le.classes_[0])
                df[col + "_enc"] = le.transform(vals)
        return df

    def create_temporal_features(self, df):
        df = df.copy()
        df = df.sort_values(["loan_id", "reporting_month"]).reset_index(drop=True)
        grp = df.groupby("loan_id", sort=False)

        # Balance trajectory
        df["prev_balance"] = grp["current_balance"].shift(1)
        df["balance_change_1m"] = df["current_balance"] - df["prev_balance"]
        df["balance_pct_original"] = df["current_balance"] / (df["original_balance"] + 1e-5)
        df["balance_ratio_change"] = df["balance_change_1m"] / (df["original_balance"] + 1e-5)
        df["amortization_pct"] = (1.0 - df["balance_pct_original"]).clip(lower=0, upper=1)

        # DPD trends
        df["prev_dpd"] = grp["days_past_due"].shift(1)
        df["dpd_change_1m"] = df["days_past_due"] - df["prev_dpd"]
        df["dpd_3m_max"] = grp["days_past_due"].transform(lambda x: x.rolling(3, min_periods=1).max())
        df["dpd_3m_mean"] = grp["days_past_due"].transform(lambda x: x.rolling(3, min_periods=1).mean())
        df["dpd_6m_max"] = grp["days_past_due"].transform(lambda x: x.rolling(6, min_periods=1).max())
        df["ever_delinquent"] = grp["days_past_due"].transform(lambda x: (x > 0).cumsum().clip(upper=1))
        df["cumulative_prepay_flags"] = grp["prepayment_flag"].transform("cumsum")
        df["cumulative_default_flags"] = grp["default_flag"].transform("cumsum")

        # Status severity lag
        if "status_severity" in df.columns:
            df["prev_status_severity"] = grp["status_severity"].shift(1)
            df["status_delta"] = df["status_severity"] - df["prev_status_severity"]
            df["prev_status_severity"] = df["prev_status_severity"].fillna(0)
            df["status_delta"] = df["status_delta"].fillna(0)

        # Rate spread vs market
        month_avg_rate = df.groupby("reporting_month")["interest_rate"].transform("mean")
        df["rate_spread_to_market"] = df["interest_rate"] - month_avg_rate
        df["prepayment_incentive"] = -df["rate_spread_to_market"]

        # Fill NaN lag cols
        for col in ["prev_balance", "balance_change_1m", "balance_ratio_change", "prev_dpd", "dpd_change_1m"]:
            if col in df.columns:
                df[col] = df[col].fillna(0)

        return df

    def create_interaction_features(self, df):
        df = df.copy()
        if "dti_ord" in df.columns and "ltv_ord" in df.columns:
            df["dti_x_ltv"] = df["dti_ord"] * df["ltv_ord"]
        if "loan_age_months" in df.columns and "interest_rate" in df.columns:
            df["age_x_rate"] = df["loan_age_months"] * df["interest_rate"]
        if "credit_score_ord" in df.columns and "dti_ord" in df.columns:
            df["creditworthiness_net"] = df["credit_score_ord"] - df["dti_ord"]
        if all(c in df.columns for c in ["credit_score_ord", "ltv_ord", "dti_ord"]):
            df["high_risk_combo"] = (
                (df["credit_score_ord"] <= 1) & (df["ltv_ord"] >= 3) & (df["dti_ord"] >= 3)
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
            "rate_spread_to_market", "prepayment_incentive",
        ]
        interactions = [
            "dti_x_ltv", "age_x_rate", "creditworthiness_net",
            "high_risk_combo", "distress_score", "maturity_pressure",
        ]
        all_c = static + ordinal + cat_enc + temporal + interactions
        return [c for c in all_c if c in df.columns]

    def fit_transform(self, df):
        df = self.encode_ordinals(df)
        df = self.encode_categoricals(df, fit=True)
        df["modification_flag_bin"] = (df["modification_flag"].astype(str).str.strip() == "Y").astype(int)
        df = self.create_temporal_features(df)
        df = self.create_interaction_features(df)
        self.feature_cols = self._get_feature_columns(df)
        self.fitted = True
        print(f"  FeatureEngineer: {len(self.feature_cols)} features derived.")
        return df

    def transform(self, df):
        df = self.encode_ordinals(df)
        df = self.encode_categoricals(df, fit=False)
        if "modification_flag" in df.columns:
            df["modification_flag_bin"] = (df["modification_flag"].astype(str).str.strip() == "Y").astype(int)
        else:
            df["modification_flag_bin"] = 0
        df = self.create_temporal_features(df)
        df = self.create_interaction_features(df)
        return df

    def save(self, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(self, f)
        print(f"  FeatureEngineer saved: {path}")

    @staticmethod
    def load(path):
        with open(path, "rb") as f:
            return pickle.load(f)
