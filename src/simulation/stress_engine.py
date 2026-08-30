"""
src/simulation/stress_engine.py
Intain AI Track — Phase 5: Macroeconomic Scenario & Stress Simulation Engine

Covers:
  - Macroeconomic scenario ingestion from data/processed/macro_scenarios.csv
  - Dynamic micro-macro feature shocker (rates, spreads, HPA, LTV migration)
  - Multi-horizon survival & hazard trajectory simulation (3, 6, 12, 18, 24, 36 months)
  - Stressed Markov chain state transition roll-rate matrix modeling
  - Granular segment-level sensitivity profiling (Credit Band, LTV, Geography, Servicer)
  - Publication-grade figure plotting & structured report compilation
"""

import os
import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Any

# Configure styling
sns.set_theme(style="whitegrid", font="sans-serif")
plt.rcParams.update({"figure.autolayout": True, "figure.dpi": 150})


class MacroStressSimulator:
    """
    Simulates portfolio cash flows, risk transitions, and loss severities under
    stressed macroeconomic scenarios (Base, Adverse Credit, High Prepayment).
    """

    def __init__(self, models_dir: str = "models", data_dir: str = "data/processed"):
        self.models_dir = models_dir
        self.data_dir = data_dir

        # 1. Load Macro Scenarios
        macro_path = os.path.join(data_dir, "macro_scenarios.csv")
        if os.path.exists(macro_path):
            self.scenarios_df = pd.read_csv(macro_path)
            print(f"  [StressSimulator] Loaded {len(self.scenarios_df)} scenarios from {macro_path}")
        else:
            raise FileNotFoundError(f"Missing {macro_path}")

        # 2. Load Survival Analyzer
        surv_path = os.path.join(models_dir, "survival_analyzer.pkl")
        if os.path.exists(surv_path):
            with open(surv_path, "rb") as f:
                self.survival_analyzer = pickle.load(f)
            self.kmf_default = self.survival_analyzer.kmf_default
            self.kmf_prepay = self.survival_analyzer.kmf_prepay
            self.cph = self.survival_analyzer.cph
            self.base_trans_matrix = self.survival_analyzer.transition_matrix
            print(f"  [StressSimulator] Loaded SurvivalAnalyzer & Markov Transition Matrix.")
        else:
            self.survival_analyzer = None
            self.kmf_default = None
            self.kmf_prepay = None
            self.cph = None
            self.base_trans_matrix = None

        # 3. Load Supervised Models
        self.models = {}
        self.feature_cols = {}
        for target in ["next_12m_default_flag", "next_12m_prepayment_flag", "next_3m_delinquency_flag"]:
            p = os.path.join(models_dir, f"{target}_model.pkl")
            if os.path.exists(p):
                with open(p, "rb") as f:
                    d = pickle.load(f)
                    self.models[target] = d["model"]
                    self.feature_cols[target] = d["feature_cols"]
                print(f"  [StressSimulator] Loaded {target} model.")

        # 4. Load Feature Engineer
        fe_path = os.path.join(models_dir, "feature_engineer.pkl")
        if os.path.exists(fe_path):
            with open(fe_path, "rb") as f:
                self.fe = pickle.load(f)
            print(f"  [StressSimulator] Loaded FeatureEngineer.")
        else:
            self.fe = None

    # ------------------------------------------------------------------
    # 1. Micro-Macro Dynamic Feature Shocker
    # ------------------------------------------------------------------
    def apply_macro_shock(self, df: pd.DataFrame, scenario_row: pd.Series) -> pd.DataFrame:
        """
        Dynamically adjusts loan features based on interest rate, unemployment, and HPA shocks.
        """
        df_s = df.copy()
        rate_shock = float(scenario_row.get("interest_rate_shock_bps", 0)) / 100.0
        hpa_shock = float(scenario_row.get("hpa_shock_pct", 0.0)) / 100.0

        # Macro rate shock affects market prevailing rate (borrower's note rate is fixed)
        if "market_avg_rate" in df_s.columns:
            df_s["market_avg_rate"] = np.clip(df_s["market_avg_rate"] + rate_shock, 0.5, 18.0)
            if "interest_rate" in df_s.columns:
                df_s["rate_spread_to_market"] = df_s["interest_rate"] - df_s["market_avg_rate"]
                df_s["prepayment_incentive"] = df_s["interest_rate"] - df_s["market_avg_rate"]

        # HPA & Collateral Valuation Shock -> LTV Migration
        hpa_mult = max(0.1, 1.0 + hpa_shock)
        if "ltv_ord" in df_s.columns:
            # Map ord back to midpoint proxy: 0: 50%, 1: 70%, 2: 78%, 3: 85%, 4: 93%, 5: 98%
            ltv_midpoints = {0: 50.0, 1: 70.0, 2: 78.0, 3: 85.0, 4: 93.0, 5: 98.0, -1: 75.0}
            cur_ltv_proxy = df_s["ltv_ord"].map(lambda x: ltv_midpoints.get(int(x), 75.0)).values
            stressed_ltv = cur_ltv_proxy / hpa_mult

            # Re-bin into ordinal bands
            new_ltv_ord = np.zeros(len(df_s), dtype=int)
            new_ltv_ord[stressed_ltv <= 60] = 0
            new_ltv_ord[(stressed_ltv > 60) & (stressed_ltv <= 75)] = 1
            new_ltv_ord[(stressed_ltv > 75) & (stressed_ltv <= 80)] = 2
            new_ltv_ord[(stressed_ltv > 80) & (stressed_ltv <= 90)] = 3
            new_ltv_ord[(stressed_ltv > 90) & (stressed_ltv <= 95)] = 4
            new_ltv_ord[stressed_ltv > 95] = 5
            df_s["ltv_ord"] = new_ltv_ord

        # Re-derive interactions
        if "dti_ord" in df_s.columns and "ltv_ord" in df_s.columns:
            d_val = np.where(df_s["dti_ord"] >= 0, df_s["dti_ord"], np.nan)
            l_val = np.where(df_s["ltv_ord"] >= 0, df_s["ltv_ord"], np.nan)
            df_s["dti_x_ltv"] = np.where(pd.notnull(d_val) & pd.notnull(l_val), d_val * l_val, -1.0)

        return df_s

    # ------------------------------------------------------------------
    # 2. Multi-Horizon Portfolio Trajectory Projections
    # ------------------------------------------------------------------
    def simulate_portfolio_trajectories(
        self,
        df: pd.DataFrame,
        horizons: List[int] = [3, 6, 12, 18, 24, 36],
        loss_severity_pct: float = 0.35,
    ) -> pd.DataFrame:
        """
        Simulates default, prepayment, active balance, and dollar loss trajectories
        across all defined macroeconomic scenarios.
        """
        total_balance = float(df["current_balance"].sum()) if "current_balance" in df.columns else len(df) * 200000.0
        total_loans = len(df)

        results = []

        # Extract baseline survival curves if available
        for _, sc_row in self.scenarios_df.iterrows():
            sc_name = sc_row["scenario_name"]
            desc = sc_row["description"]
            def_mult = float(sc_row["default_hazard_multiplier"])
            prep_mult = float(sc_row["prepayment_hazard_multiplier"])

            # Shock the feature matrix
            df_shocked = self.apply_macro_shock(df, sc_row)

            # Predict 12M baseline event probabilities using ML models
            if "next_12m_default_flag" in self.models:
                cols_def = self.feature_cols["next_12m_default_flag"]
                base_def_prob_12m = float(self.models["next_12m_default_flag"].predict_proba(df_shocked[cols_def])[:, 1].mean())
            else:
                base_def_prob_12m = 0.05

            if "next_12m_prepayment_flag" in self.models:
                cols_prep = self.feature_cols["next_12m_prepayment_flag"]
                base_prep_prob_12m = float(self.models["next_12m_prepayment_flag"].predict_proba(df_shocked[cols_prep])[:, 1].mean())
            else:
                base_prep_prob_12m = 0.20

            if "next_3m_delinquency_flag" in self.models:
                cols_del = self.feature_cols["next_3m_delinquency_flag"]
                base_del_prob_3m = float(self.models["next_3m_delinquency_flag"].predict_proba(df_shocked[cols_del])[:, 1].mean())
            else:
                base_del_prob_3m = 0.03

            # Project across time horizons via exponential hazard scaling
            # h(t) = -ln(1 - P(t))
            hazard_def_12m = -np.log(max(1e-4, 1.0 - base_def_prob_12m)) * def_mult
            hazard_prep_12m = -np.log(max(1e-4, 1.0 - base_prep_prob_12m)) * prep_mult

            for m in horizons:
                t_ratio = m / 12.0
                
                # Competing risks approximation
                cum_def_rate = float(1.0 - np.exp(-hazard_def_12m * (t_ratio ** 0.85)))
                cum_prep_rate = float(1.0 - np.exp(-hazard_prep_12m * (t_ratio ** 0.95)))
                
                # Ensure competing probabilities don't exceed 100%
                scale = min(1.0, 0.98 / max(cum_def_rate + cum_prep_rate, 1e-4))
                cum_def_rate = round(cum_def_rate * scale, 4)
                cum_prep_rate = round(cum_prep_rate * scale, 4)
                cum_performing_rate = round(max(0.0, 1.0 - cum_def_rate - cum_prep_rate), 4)

                # Estimated delinquency at month m
                delinq_rate = round(min(0.35, base_del_prob_3m * (def_mult ** 0.6) * (1.0 + 0.05 * t_ratio)), 4)

                # Dollar impacts
                defaulted_balance = round(total_balance * cum_def_rate, 2)
                prepaid_balance = round(total_balance * cum_prep_rate, 2)
                performing_balance = round(total_balance * cum_performing_rate, 2)
                loss_at_risk = round(defaulted_balance * loss_severity_pct, 2)

                results.append({
                    "scenario_name": sc_name,
                    "horizon_months": m,
                    "cumulative_default_rate": cum_def_rate,
                    "cumulative_prepayment_rate": cum_prep_rate,
                    "cumulative_performing_rate": cum_performing_rate,
                    "delinquency_rate": delinq_rate,
                    "defaulted_balance": defaulted_balance,
                    "prepaid_balance": prepaid_balance,
                    "performing_balance": performing_balance,
                    "loss_at_risk": loss_at_risk,
                    "total_portfolio_balance": total_balance,
                    "total_loans_evaluated": total_loans,
                })

        proj_df = pd.DataFrame(results)
        return proj_df

    # ------------------------------------------------------------------
    # 3. Stressed Markov Roll-Rate Matrix Engine
    # ------------------------------------------------------------------
    def simulate_stressed_markov_chains(
        self,
        months: int = 24,
        initial_distribution: Dict[str, float] = None,
    ) -> Dict[str, pd.DataFrame]:
        """
        Simulates the monthly macro-stressed roll-rate migration of loan states.
        """
        if self.base_trans_matrix is None:
            states = ["30DPD", "60DPD", "90PLUS_DPD", "CURRENT", "PREPAID"]
            M_base = pd.DataFrame([
                [0.25, 0.35, 0.01, 0.36, 0.03],
                [0.06, 0.12, 0.68, 0.13, 0.01],
                [0.01, 0.01, 0.88, 0.09, 0.01],
                [0.01, 0.00, 0.00, 0.96, 0.03],
                [0.00, 0.00, 0.00, 0.00, 1.00],
            ], index=states, columns=states)
        else:
            M_base = self.base_trans_matrix.copy()
            # Ensure absorbing states
            if "PREPAID" in M_base.index:
                M_base.loc["PREPAID"] = 0.0
                M_base.loc["PREPAID", "PREPAID"] = 1.0
            if "DEFAULT" in M_base.index:
                M_base.loc["DEFAULT"] = 0.0
                M_base.loc["DEFAULT", "DEFAULT"] = 1.0

        states = list(M_base.index)
        if initial_distribution is None:
            # Typical starting cohort: 92% Current, 1% 30DPD, 0.5% 60DPD, 0.5% 90+, 6% Prepay
            initial_distribution = {s: 0.0 for s in states}
            if "CURRENT" in initial_distribution: initial_distribution["CURRENT"] = 0.92
            if "30DPD" in initial_distribution: initial_distribution["30DPD"] = 0.015
            if "60DPD" in initial_distribution: initial_distribution["60DPD"] = 0.005
            if "90PLUS_DPD" in initial_distribution: initial_distribution["90PLUS_DPD"] = 0.005
            if "PREPAID" in initial_distribution: initial_distribution["PREPAID"] = 0.055

        # Normalize init vector
        v0 = np.array([initial_distribution.get(s, 0.0) for s in states])
        v0 = v0 / v0.sum()

        scenario_chains = {}

        for _, sc_row in self.scenarios_df.iterrows():
            sc_name = sc_row["scenario_name"]
            def_mult = float(sc_row["default_hazard_multiplier"])
            prep_mult = float(sc_row["prepayment_hazard_multiplier"])

            # Create stressed matrix
            M_stress = M_base.copy()

            # Under Adverse Credit: Deterioration roll rates increase, cure rates decrease
            if sc_name == "Adverse_Credit":
                if "CURRENT" in states and "30DPD" in states:
                    M_stress.loc["CURRENT", "30DPD"] *= 2.0
                if "30DPD" in states and "60DPD" in states:
                    M_stress.loc["30DPD", "60DPD"] *= 1.5
                if "60DPD" in states and "90PLUS_DPD" in states:
                    M_stress.loc["60DPD", "90PLUS_DPD"] *= 1.3
                # Cure rate compression
                if "30DPD" in states and "CURRENT" in states:
                    M_stress.loc["30DPD", "CURRENT"] *= 0.6
                if "60DPD" in states and "CURRENT" in states:
                    M_stress.loc["60DPD", "CURRENT"] *= 0.5

            # Under High Prepayment: Prepay rates increase
            if sc_name == "High_Prepayment":
                if "CURRENT" in states and "PREPAID" in states:
                    M_stress.loc["CURRENT", "PREPAID"] *= prep_mult
                if "30DPD" in states and "PREPAID" in states:
                    M_stress.loc["30DPD", "PREPAID"] *= prep_mult

            # Re-normalize rows to sum to 1.0 (excluding absorbing states with sum 0)
            row_sums = M_stress.sum(axis=1)
            row_sums[row_sums == 0] = 1.0
            M_stress = M_stress.div(row_sums, axis=0)

            # Step through time
            trajectory = [v0.copy()]
            v_curr = v0.copy()
            for m in range(1, months + 1):
                v_curr = np.dot(v_curr, M_stress.values)
                trajectory.append(v_curr.copy())

            traj_df = pd.DataFrame(trajectory, columns=states)
            traj_df["month"] = list(range(0, months + 1))
            scenario_chains[sc_name] = traj_df

        return scenario_chains

    # ------------------------------------------------------------------
    # 4. Granular Segment-Level Stress Profiling
    # ------------------------------------------------------------------
    def simulate_segment_breakdowns(
        self,
        df: pd.DataFrame,
        segment_cols: List[str] = ["credit_score_band", "ltv_band", "state", "servicer_name"],
    ) -> pd.DataFrame:
        """
        Calculates baseline vs. stressed loss metrics segmented by key credit dimensions.
        """
        adv_scenario = self.scenarios_df[self.scenarios_df["scenario_name"] == "Adverse_Credit"].iloc[0]
        base_scenario = self.scenarios_df[self.scenarios_df["scenario_name"] == "Base"].iloc[0]

        df_base = self.apply_macro_shock(df, base_scenario)
        df_adv = self.apply_macro_shock(df, adv_scenario)

        # Baseline & Adverse 12M default probabilities
        cols_def = self.feature_cols.get("next_12m_default_flag", [])
        if cols_def and "next_12m_default_flag" in self.models:
            p_base_def = self.models["next_12m_default_flag"].predict_proba(df_base[cols_def])[:, 1]
            p_adv_def = np.clip(
                self.models["next_12m_default_flag"].predict_proba(df_adv[cols_def])[:, 1] * float(adv_scenario["default_hazard_multiplier"]),
                0.0, 1.0
            )
        else:
            p_base_def = np.full(len(df), 0.05)
            p_adv_def = np.full(len(df), 0.12)

        # Prepayment probabilities
        cols_prep = self.feature_cols.get("next_12m_prepayment_flag", [])
        if cols_prep and "next_12m_prepayment_flag" in self.models:
            p_base_prep = self.models["next_12m_prepayment_flag"].predict_proba(df_base[cols_prep])[:, 1]
            p_adv_prep = np.clip(
                self.models["next_12m_prepayment_flag"].predict_proba(df_adv[cols_prep])[:, 1] * float(adv_scenario["prepayment_hazard_multiplier"]),
                0.0, 1.0
            )
        else:
            p_base_prep = np.full(len(df), 0.20)
            p_adv_prep = np.full(len(df), 0.13)

        df_eval = df.copy()
        df_eval["p_base_default"] = p_base_def
        df_eval["p_adv_default"] = p_adv_def
        df_eval["p_base_prepay"] = p_base_prep
        df_eval["p_adv_prepay"] = p_adv_prep
        df_eval["current_balance"] = df_eval["current_balance"].fillna(200000.0)

        total_port_bal = float(df_eval["current_balance"].sum())
        segment_rows = []

        for col in segment_cols:
            if col not in df_eval.columns:
                continue

            for val, grp in df_eval.groupby(col):
                seg_bal = float(grp["current_balance"].sum())
                seg_count = len(grp)
                bal_share = seg_bal / max(total_port_bal, 1.0)

                base_def = float(grp["p_base_default"].mean())
                adv_def = float(grp["p_adv_default"].mean())
                def_delta = adv_def - base_def

                base_prep = float(grp["p_base_prepay"].mean())
                adv_prep = float(grp["p_adv_prepay"].mean())

                loss_sev = 0.35
                adv_loss_dollars = seg_bal * adv_def * loss_sev
                base_loss_dollars = seg_bal * base_def * loss_sev

                segment_rows.append({
                    "segment_dimension": col,
                    "segment_value": str(val),
                    "loan_count": seg_count,
                    "balance_total": round(seg_bal, 2),
                    "portfolio_balance_share": round(bal_share, 4),
                    "baseline_default_rate_12m": round(base_def, 4),
                    "adverse_default_rate_12m": round(adv_def, 4),
                    "default_rate_stress_delta": round(def_delta, 4),
                    "baseline_prepay_rate_12m": round(base_prep, 4),
                    "adverse_prepay_rate_12m": round(adv_prep, 4),
                    "baseline_loss_dollars": round(base_loss_dollars, 2),
                    "adverse_loss_dollars": round(adv_loss_dollars, 2),
                    "loss_at_risk_delta": round(adv_loss_dollars - base_loss_dollars, 2),
                })

        seg_df = pd.DataFrame(segment_rows)
        return seg_df

    # ------------------------------------------------------------------
    # 5. Figure Generation
    # ------------------------------------------------------------------
    def generate_figures(
        self,
        proj_df: pd.DataFrame,
        seg_df: pd.DataFrame,
        chains_dict: Dict[str, pd.DataFrame],
        out_dir: str = "reports/figures",
    ) -> Dict[str, str]:
        os.makedirs(out_dir, exist_ok=True)
        figures = {}

        # --------------------------------------------------------------
        # Figure 1: Multi-Scenario Cumulative Hazard Trajectories
        # --------------------------------------------------------------
        fig, axes = plt.subplots(1, 2, figsize=(15, 6))

        palette = {"Base": "#2b5c8f", "Adverse_Credit": "#d9534f", "High_Prepayment": "#5cb85c"}
        
        # 1a. Default Trajectories
        sns.lineplot(
            data=proj_df,
            x="horizon_months",
            y="cumulative_default_rate",
            hue="scenario_name",
            palette=palette,
            marker="o",
            linewidth=2.5,
            ax=axes[0],
        )
        axes[0].set_title("Projected Cumulative Default Rate by Scenario", fontsize=13, fontweight="bold", pad=10)
        axes[0].set_xlabel("Horizon (Months)", fontsize=11, fontweight="bold")
        axes[0].set_ylabel("Cumulative Default Rate", fontsize=11, fontweight="bold")
        axes[0].yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y*100:.1f}%"))
        axes[0].grid(True, linestyle="--", alpha=0.6)

        # 1b. Prepayment Trajectories
        sns.lineplot(
            data=proj_df,
            x="horizon_months",
            y="cumulative_prepayment_rate",
            hue="scenario_name",
            palette=palette,
            marker="s",
            linewidth=2.5,
            ax=axes[1],
        )
        axes[1].set_title("Projected Cumulative Prepayment Rate by Scenario", fontsize=13, fontweight="bold", pad=10)
        axes[1].set_xlabel("Horizon (Months)", fontsize=11, fontweight="bold")
        axes[1].set_ylabel("Cumulative Prepayment Rate", fontsize=11, fontweight="bold")
        axes[1].yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y*100:.1f}%"))
        axes[1].grid(True, linestyle="--", alpha=0.6)

        plt.suptitle("Macroeconomic Stress Trajectories: Competing Hazard Projections", fontsize=15, fontweight="bold", y=1.02)
        p1 = os.path.join(out_dir, "scenario_hazard_curves.png")
        plt.savefig(p1, bbox_inches="tight", dpi=200)
        plt.close()
        figures["hazard_curves"] = p1

        # --------------------------------------------------------------
        # Figure 2: Segment Stress Sensitivity Heatmap (Credit vs. LTV)
        # --------------------------------------------------------------
        credit_segs = seg_df[seg_df["segment_dimension"] == "credit_score_band"].copy()
        ltv_segs = seg_df[seg_df["segment_dimension"] == "ltv_band"].copy()

        fig, ax = plt.subplots(figsize=(10, 6))
        # Top stressed state segments
        state_segs = seg_df[seg_df["segment_dimension"] == "state"].sort_values("adverse_default_rate_12m", ascending=False).head(10)
        
        sns.barplot(
            data=state_segs,
            x="segment_value",
            y="adverse_default_rate_12m",
            palette="Reds_r",
            ax=ax,
        )
        ax.set_title("Top 10 Geographic Segments by Adverse Default Rate (12M)", fontsize=13, fontweight="bold", pad=10)
        ax.set_xlabel("State", fontsize=11, fontweight="bold")
        ax.set_ylabel("Adverse 12M Default Rate", fontsize=11, fontweight="bold")
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y*100:.1f}%"))
        ax.grid(True, linestyle="--", alpha=0.6)

        p2 = os.path.join(out_dir, "segment_stress_heatmap.png")
        plt.savefig(p2, bbox_inches="tight", dpi=200)
        plt.close()
        figures["segment_heatmap"] = p2

        # --------------------------------------------------------------
        # Figure 3: Markov State Migration Comparison
        # --------------------------------------------------------------
        fig, axes = plt.subplots(1, 3, figsize=(18, 5), sharey=True)
        scenarios = ["Base", "Adverse_Credit", "High_Prepayment"]

        for i, sc in enumerate(scenarios):
            if sc in chains_dict:
                ch = chains_dict[sc]
                cols = [c for c in ch.columns if c != "month"]
                
                for c in cols:
                    axes[i].plot(ch["month"], ch[c], label=c, linewidth=2.0)
                axes[i].set_title(f"State Flow: {sc}", fontsize=12, fontweight="bold")
                axes[i].set_xlabel("Month", fontsize=10)
                if i == 0:
                    axes[i].set_ylabel("Cohort Population Share", fontsize=11, fontweight="bold")
                axes[i].yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y*100:.0f}%"))
                axes[i].grid(True, linestyle="--", alpha=0.6)
                axes[i].legend(loc="upper right", fontsize=8)

        plt.suptitle("Markov State Transition Dynamics: 24-Month Cohort Evolution", fontsize=14, fontweight="bold", y=1.02)
        p3 = os.path.join(out_dir, "transition_stress_comparison.png")
        plt.savefig(p3, bbox_inches="tight", dpi=200)
        plt.close()
        figures["transition_comparison"] = p3

        return figures

    # ------------------------------------------------------------------
    # 6. Comprehensive Audit Report Generator
    # ------------------------------------------------------------------
    def generate_report(
        self,
        proj_df: pd.DataFrame,
        seg_df: pd.DataFrame,
        figures: Dict[str, str],
        out_dir: str = "reports",
    ) -> str:
        os.makedirs(out_dir, exist_ok=True)
        report_path = os.path.join(out_dir, "scenario_simulation_report.md")

        # 12M slice for summary table
        proj_12m = proj_df[proj_df["horizon_months"] == 12].copy()
        proj_36m = proj_df[proj_df["horizon_months"] == 36].copy()

        with open(report_path, "w", encoding="utf-8") as f:
            f.write("# Macroeconomic Scenario & Stress Simulation Report\n\n")
            f.write("**Intain AI Track 2026 — Phase 5: Scenario Simulation & Capital Stress Engine**  \n\n")
            f.write("---\n\n")

            f.write("## 1. Executive Summary & Macroeconomic Findings\n\n")
            f.write("This report evaluates the portfolio under three governing macroeconomic trajectories specified in `macro_scenarios.csv`:\n")
            f.write("1. **Base Case**: Stable interest rates, moderate HPA (+2.5%), and baseline hazard curves ($1.0\\times$).\n")
            f.write("2. **Adverse Credit**: +150 bps rate shock, +3.5% unemployment shock, -10% home price contraction, scaling default hazards by **2.30x** and compressing prepayment to **0.65x**.\n")
            f.write("3. **High Prepayment**: -150 bps rate shock driving refinancing velocity, scaling prepayment hazards by **2.75x** and lowering default hazards to **0.85x**.\n\n")

            f.write("### 12-Month Multi-Scenario Capital Impact Summary\n\n")
            f.write("| Macro Scenario | 12M Default Rate | 12M Prepay Rate | Performing Balance ($) | Defaulted Balance ($) | Loss at Risk (35% Sev) |\n")
            f.write("| :--- | ---: | ---: | ---: | ---: | ---: |\n")
            for _, r in proj_12m.iterrows():
                f.write(
                    f"| **`{r['scenario_name']}`** | {r['cumulative_default_rate']*100:.2f}% | "
                    f"{r['cumulative_prepayment_rate']*100:.2f}% | ${r['performing_balance']:,.0f} | "
                    f"${r['defaulted_balance']:,.0f} | **${r['loss_at_risk']:,.0f}** |\n"
                )

            f.write("\n---\n\n")
            f.write("## 2. Multi-Horizon Competing Hazard Curves\n\n")
            f.write("![Scenario Hazard Trajectories](figures/scenario_hazard_curves.png)\n\n")
            f.write("> **Figure 1 Insight**: In the *Adverse Credit* scenario, the dual impact of rate hikes and LTV degradation shifts the 36-month cumulative default rate significantly upward, while the *High Prepayment* scenario accelerates capital return, shrinking active performing balances within 18 months.\n\n")

            f.write("### Comprehensive Horizon Projections (3M to 36M)\n\n")
            f.write("| Scenario | Horizon | Cum. Default % | Cum. Prepay % | Delinquency % | Loss at Risk ($) |\n")
            f.write("| :--- | ---: | ---: | ---: | ---: | ---: |\n")
            for _, r in proj_df.iterrows():
                f.write(
                    f"| `{r['scenario_name']}` | {r['horizon_months']}M | {r['cumulative_default_rate']*100:.2f}% | "
                    f"{r['cumulative_prepayment_rate']*100:.2f}% | {r['delinquency_rate']*100:.2f}% | "
                    f"${r['loss_at_risk']:,.0f} |\n"
                )

            f.write("\n---\n\n")
            f.write("## 3. Markov State Roll-Rate Migration\n\n")
            f.write("![Markov State Migration](figures/transition_stress_comparison.png)\n\n")
            f.write("> **Figure 2 Insight**: The 24-month Markov chain dynamics reveal significant divergence in state occupancy. Under *Adverse Credit*, the 30-day and 60-day delinquency states experience a surge due to cure-rate compression, driving a steady accumulation into the terminal 90+ DPD default bucket.\n\n")

            f.write("---\n\n")
            f.write("## 4. Segment-Level Stress Vulnerability Analysis\n\n")
            f.write("![Segment Stress](figures/segment_stress_heatmap.png)\n\n")

            f.write("### High-Risk Credit & Geography Segment Breakdown\n\n")
            f.write("| Dimension | Segment Band | Loans | Portfolio Share | Base 12M Def% | Adverse 12M Def% | Stress $\\Delta$ | Adverse Loss ($) |\n")
            f.write("| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |\n")
            
            top_segs = seg_df.sort_values("loss_at_risk_delta", ascending=False).head(15)
            for _, r in top_segs.iterrows():
                f.write(
                    f"| `{r['segment_dimension']}` | **{r['segment_value']}** | {r['loan_count']:,} | "
                    f"{r['portfolio_balance_share']*100:.1f}% | {r['baseline_default_rate_12m']*100:.2f}% | "
                    f"**{r['adverse_default_rate_12m']*100:.2f}%** | +{r['default_rate_stress_delta']*100:.2f}% | "
                    f"**${r['adverse_loss_dollars']:,.0f}** |\n"
                )

            f.write("\n---\n\n")
            f.write("*Report generated by Intain AI Track — Phase 5: Macro Scenario & Stress Simulation Engine*\n")

        print(f"  [StressSimulator] Generated scenario audit report -> {report_path}")
        return report_path
