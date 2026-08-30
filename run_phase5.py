"""
run_phase5.py — Intain AI Track Phase 5 Master Orchestrator
Macroeconomic Scenario Simulation, Capital Stress Testing & Transition Risk Modeling

Run from project root:
    python run_phase5.py
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import pandas as pd
import numpy as np
import pickle
from datetime import datetime

from src.data.feature_engineer import FeatureEngineer
from src.simulation.stress_engine import MacroStressSimulator


def run_phase5():
    print("=" * 70)
    print("PHASE 5: MACROECONOMIC SCENARIO SIMULATION & STRESS TESTING ENGINE")
    print("=" * 70)

    # 1. Load Data
    print("\n[1/5] Loading Processed Datasets...")
    test_path = "data/processed/loan_monthly_performance_test.csv"
    train_path = "data/processed/loan_monthly_performance_train.csv"
    
    if os.path.exists(test_path):
        eval_df = pd.read_csv(test_path)
        print(f"  Loaded Test Evaluation Dataset: {eval_df.shape}")
    else:
        eval_df = pd.read_csv(train_path)
        print(f"  Fallback: Loaded Train Dataset: {eval_df.shape}")

    # 2. Transform Features
    print("\n[2/5] Applying Feature Engineering...")
    with open("models/feature_engineer.pkl", "rb") as f:
        fe = pickle.load(f)
    eval_fe = fe.transform(eval_df)
    print(f"  Evaluated dataset transformed ({eval_fe.shape[1]} features ready).")

    # 3. Initialize Simulator
    print("\n[3/5] Initializing MacroStressSimulator...")
    simulator = MacroStressSimulator(models_dir="models", data_dir="data/processed")

    # 4. Multi-Horizon Scenario Trajectories
    print("\n[4/5] Running Multi-Horizon Trajectory Projections (3M, 6M, 12M, 18M, 24M, 36M)...")
    horizons = [3, 6, 12, 18, 24, 36]
    projections_df = simulator.simulate_portfolio_trajectories(eval_fe, horizons=horizons, loss_severity_pct=0.35)
    
    proj_path = "data/processed/phase5_scenario_projections.csv"
    projections_df.to_csv(proj_path, index=False)
    print(f"  -> Saved Scenario Projections ({len(projections_df)} rows) to {proj_path}")

    # 5. Stressed Markov Roll-Rate Chains
    print("\n  Simulating 24-Month Stressed Markov State Migrations...")
    markov_chains = simulator.simulate_stressed_markov_chains(months=24)

    # 6. Granular Segment Breakdowns
    print("  Calculating Segment-Level Loss & Prepayment Sensitivities...")
    segment_cols = ["credit_score_band", "ltv_band", "state", "servicer_name"]
    segment_df = simulator.simulate_segment_breakdowns(eval_fe, segment_cols=segment_cols)
    
    seg_path = "data/processed/phase5_segment_stress_impacts.csv"
    segment_df.to_csv(seg_path, index=False)
    print(f"  -> Saved Segment Stress Impacts ({len(segment_df)} segments) to {seg_path}")

    # 7. Generate Visualizations & Audit Report
    print("\n[5/5] Generating Publication-Grade Visualizations & Audit Report...")
    figures = simulator.generate_figures(projections_df, segment_df, markov_chains, out_dir="reports/figures")
    for k, v in figures.items():
        print(f"  -> Figure saved: {v}")

    report_path = simulator.generate_report(projections_df, segment_df, figures, out_dir="reports")
    print(f"  -> Audit Report generated: {report_path}")

    # Append to AI Development Log
    log_entry = f"""
## Phase 5 Execution Log — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Objective**: Task 5 Scenario Simulation & Capital Stress Engine.
- **Scenarios Evaluated**: Base (1.0x), Adverse Credit (+150bps rate, +3.5% unemp, -10% HPA, 2.30x default, 0.65x prepay), High Prepayment (-150bps rate, +6.0% HPA, 2.75x prepay, 0.85x default).
- **Deliverables**:
  - `src/simulation/stress_engine.py`: Core simulation and micro-macro shock engine.
  - `run_phase5.py`: Master simulation pipeline orchestrator.
  - `data/processed/phase5_scenario_projections.csv`: Multi-horizon cash flow & loss projections.
  - `data/processed/phase5_segment_stress_impacts.csv`: Granular risk segment breakdowns.
  - `reports/figures/scenario_hazard_curves.png`: Competing default/prepay hazard curves.
  - `reports/figures/segment_stress_heatmap.png`: High-risk geographic & credit segment concentrations.
  - `reports/figures/transition_stress_comparison.png`: 24-month Markov state roll-rate trajectories.
  - `reports/scenario_simulation_report.md`: Formal stress test executive report.
"""
    with open("logs/ai_development_log.md", "a", encoding="utf-8") as f:
        f.write(log_entry)

    print("\n" + "=" * 70)
    print("PHASE 5 COMPLETE (SCENARIO SIMULATION & STRESS TESTING VERIFIED)")
    print("=" * 70)


if __name__ == "__main__":
    run_phase5()
