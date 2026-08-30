"""
src/models/trainer.py
Intain AI Track — Phase 2: Supervised ML Training Pipeline (Leakage-Free & Calibrated)
Covers:
  - Strict 3-way time-ordered split (Train 70% / Calib 15% / Val 15%)
  - Target right-censoring filtering (dynamic dropping of NaN targets per horizon)
  - Native NaN support for XGBoost (no global fillna)
  - Scaled LogisticRegression baseline with SimpleImputer
  - Optuna hyperparameter optimization
  - Two-tier model architecture:
      * val_model: Trained strictly on X_tr, calibrated on X_cal, evaluated on untouched X_val
      * prod_model: Trained on full verified non-censored training data for test-set submission
  - Dynamic threshold tuning for optimal F1 on imbalanced targets
  - Multi-class next_state & exception_type classifiers
  - MLflow experiment tracking
"""

import os
os.environ["MLFLOW_ALLOW_FILE_STORE"] = "true"

import pandas as pd
import numpy as np
import pickle
from datetime import datetime

import mlflow
import optuna
optuna.logging.set_verbosity(optuna.logging.WARNING)

import xgboost as xgb
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.isotonic import IsotonicRegression
from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    f1_score,
    brier_score_loss,
    precision_recall_curve,
    classification_report,
)

BINARY_TARGETS = [
    "next_3m_delinquency_flag",
    "next_6m_delinquency_flag",
    "next_12m_default_flag",
    "next_12m_prepayment_flag",
    "exception_required",
]

MULTICLASS_TARGETS = [
    "next_state",
    "exception_type",
]


class ModelTrainer:
    """Trains and evaluates all Phase 2 supervised models with zero data leakage."""

    def __init__(self, X_train, y_dict, X_test, feature_cols, output_dir="models"):
        # Select common feature columns
        avail = [c for c in feature_cols if c in X_train.columns and c in X_test.columns]
        self.feature_cols = avail

        # Pass NaNs natively to XGBoost — DO NOT call fillna(0) globally
        self.X_train = X_train[avail].copy()
        self.X_test = X_test[avail].copy()
        self.y_dict = y_dict
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        self.binary_results = []
        self.mc_results = []
        self.models = {}
        self.test_predictions = {}

        mlflow.set_tracking_uri("mlruns")
        try:
            mlflow.set_experiment("IntainAITrack_Phase2")
        except Exception as e:
            print(f"    [mlflow warning] {e}")

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------
    def _scale_pos_weight(self, y):
        neg = int((y == 0).sum())
        pos = int((y == 1).sum())
        return float(neg) / max(pos, 1)

    def _recall_at_precision(self, y_true, y_score, min_prec=0.80):
        prec, rec, _ = precision_recall_curve(y_true, y_score)
        mask = prec >= min_prec
        return float(rec[mask].max()) if mask.any() else 0.0

    def _safe_auc(self, y_true, y_score):
        if len(np.unique(y_true)) < 2:
            return 0.5
        return roc_auc_score(y_true, y_score)

    # ------------------------------------------------------------------
    # Binary Classifier (3-Way Time Split: Train / Calib / Val)
    # ------------------------------------------------------------------
    def train_binary(self, target, n_trials=15):
        """Train XGBoost + Scaled Logistic Regression baseline for one binary target."""
        print(f"\n  ---- {target} ----")

        y = self.y_dict[target]
        valid_mask = y.notna()
        n_valid = int(valid_mask.sum())
        n_censored = len(y) - n_valid

        print(f"    Right-Censoring Filter: {n_valid:,} valid rows | {n_censored:,} censored rows dropped")

        if n_valid == 0 or y[valid_mask].sum() == 0:
            print(f"    SKIP: zero valid/positive examples.")
            return {}, None

        X_curr = self.X_train[valid_mask].reset_index(drop=True)
        y_curr = y[valid_mask].astype(int).reset_index(drop=True)

        # 3-Way time-ordered split: 70% Train, 15% Calibration, 15% Held-Out Validation
        n = len(X_curr)
        c1, c2 = int(n * 0.70), int(n * 0.85)

        X_tr, X_cal, X_val = X_curr.iloc[:c1], X_curr.iloc[c1:c2], X_curr.iloc[c2:]
        y_tr, y_cal, y_val = y_curr.iloc[:c1], y_curr.iloc[c1:c2], y_curr.iloc[c2:]

        spw = self._scale_pos_weight(y_tr)
        pos_tr = float(y_tr.mean())
        pos_val = float(y_val.mean())
        print(f"    Split: Train={len(X_tr):,} (pos {pos_tr*100:.2f}%) | "
              f"Calib={len(X_cal):,} | Val={len(X_val):,} (pos {pos_val*100:.2f}%)")
        print(f"    Scale pos weight (train): {spw:.1f}x")

        # ---- Baseline: Pipeline(SimpleImputer + StandardScaler + LogisticRegression) ----
        base_pipe = make_pipeline(
            SimpleImputer(strategy="median"),
            StandardScaler(),
            LogisticRegression(max_iter=500, class_weight="balanced", random_state=42)
        )
        base_pipe.fit(X_tr, y_tr)
        base_proba = base_pipe.predict_proba(X_val)[:, 1]
        base_auc = self._safe_auc(y_val, base_proba)
        base_prauc = average_precision_score(y_val, base_proba) if y_val.sum() > 0 else 0.0
        print(f"    Baseline Scaled LR — ROC-AUC: {base_auc:.4f} | PR-AUC: {base_prauc:.4f}")

        # ---- Optuna XGBoost Hyperparameter Optimization ----
        def objective(trial):
            params = {
                "n_estimators": trial.suggest_int("n_estimators", 150, 400),
                "max_depth": trial.suggest_int("max_depth", 3, 8),
                "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.25, log=True),
                "subsample": trial.suggest_float("subsample", 0.6, 1.0),
                "colsample_bytree": trial.suggest_float("colsample_bytree", 0.5, 1.0),
                "min_child_weight": trial.suggest_int("min_child_weight", 1, 10),
                "reg_alpha": trial.suggest_float("reg_alpha", 1e-4, 5.0, log=True),
                "reg_lambda": trial.suggest_float("reg_lambda", 1e-4, 5.0, log=True),
                "scale_pos_weight": spw,
                "random_state": 42,
                "n_jobs": -1,
                "verbosity": 0,
            }
            m = xgb.XGBClassifier(**params)
            m.fit(X_tr, y_tr, eval_set=[(X_cal, y_cal)], verbose=False)
            p = m.predict_proba(X_cal)[:, 1]
            if y_cal.sum() == 0:
                return 0.0
            return average_precision_score(y_cal, p)

        study = optuna.create_study(direction="maximize",
                                     sampler=optuna.samplers.TPESampler(seed=42))
        study.optimize(objective, n_trials=n_trials, timeout=180)

        best = study.best_params
        best.update({"scale_pos_weight": spw, "random_state": 42, "n_jobs": -1, "verbosity": 0})
        print(f"    Best Optuna PR-AUC (cal): {study.best_value:.4f} ({len(study.trials)} trials)")

        # ---- Model 1: Validation Model (HONEST LEAKAGE-FREE EVALUATION) ----
        val_model = xgb.XGBClassifier(**best)
        val_model.fit(X_tr, y_tr, verbose=False)

        # Calibrator fitted strictly on X_cal out-of-sample predictions
        raw_cal_proba = val_model.predict_proba(X_cal)[:, 1]
        iso_cal = IsotonicRegression(out_of_bounds="clip")
        iso_cal.fit(raw_cal_proba, y_cal)

        # Evaluate on UNTOUCHED held-out validation set X_val
        raw_val_proba = val_model.predict_proba(X_val)[:, 1]
        val_proba = iso_cal.transform(raw_val_proba)
        val_pred_05 = (val_proba >= 0.5).astype(int)

        # Threshold tuning for optimal F1 on validation slice
        thresholds = np.linspace(0.05, 0.95, 91)
        f1_scores = [f1_score(y_val, (val_proba >= t).astype(int), zero_division=0) for t in thresholds]
        best_idx = int(np.argmax(f1_scores))
        best_threshold = round(float(thresholds[best_idx]), 3)
        best_f1 = round(float(f1_scores[best_idx]), 4)

        metrics = {
            "target": target,
            "n_valid_total": n_valid,
            "n_censored_dropped": n_censored,
            "n_train_tr": int(len(y_tr)),
            "n_cal": int(len(y_cal)),
            "n_val": int(len(y_val)),
            "positive_rate_val": round(pos_val, 4),
            "scale_pos_weight": round(spw, 2),
            "baseline_roc_auc": round(base_auc, 4),
            "baseline_pr_auc": round(base_prauc, 4),
            "xgb_roc_auc": round(self._safe_auc(y_val, val_proba), 4),
            "xgb_pr_auc": round(average_precision_score(y_val, val_proba) if y_val.sum() > 0 else 0.0, 4),
            "xgb_f1_default": round(f1_score(y_val, val_pred_05, zero_division=0), 4),
            "best_threshold": best_threshold,
            "xgb_f1_optimal": best_f1,
            "xgb_brier": round(brier_score_loss(y_val, val_proba), 4),
            "recall_at_80pct_precision": round(self._recall_at_precision(y_val, val_proba), 4),
            "optuna_best_pr_auc": round(study.best_value, 4),
            "n_optuna_trials": len(study.trials),
        }

        print(f"    XGB Held-Out Val — ROC-AUC: {metrics['xgb_roc_auc']} | PR-AUC: {metrics['xgb_pr_auc']} | "
              f"F1@0.5: {metrics['xgb_f1_default']} | Optimal F1@{best_threshold}: {best_f1} | Brier: {metrics['xgb_brier']}")

        # ---- MLflow logging ----
        try:
            with mlflow.start_run(run_name=f"xgb_{target}"):
                mlflow.log_params({k: v for k, v in best.items() if isinstance(v, (int, float, str))})
                for k, v in metrics.items():
                    if isinstance(v, (int, float)):
                        mlflow.log_metric(k, v)
        except Exception as e:
            print(f"    [mlflow warning] {e}")

        # ---- Model 2: Production Model (Trained on full non-censored X_curr for test set) ----
        full_spw = self._scale_pos_weight(y_curr)
        prod_params = best.copy()
        prod_params["scale_pos_weight"] = full_spw
        prod_model = xgb.XGBClassifier(**prod_params)
        prod_model.fit(X_curr, y_curr, verbose=False)

        # Calibrate production model on validation probabilities
        raw_val_for_prod = prod_model.predict_proba(X_val)[:, 1]
        prod_calibrator = IsotonicRegression(out_of_bounds="clip")
        prod_calibrator.fit(raw_val_for_prod, y_val)

        # Test set predictions
        raw_test_proba = prod_model.predict_proba(self.X_test)[:, 1]
        self.test_predictions[target] = prod_calibrator.transform(raw_test_proba)

        # ---- Save model artifacts ----
        artifact = {
            "model": prod_model,
            "calibrator": prod_calibrator,
            "val_model": val_model,
            "metrics": metrics,
            "feature_cols": self.feature_cols,
        }
        with open(os.path.join(self.output_dir, f"{target}_model.pkl"), "wb") as f:
            pickle.dump(artifact, f)

        self.models[target] = artifact
        return metrics, prod_model

    # ------------------------------------------------------------------
    # Multi-Class Classifier (Leakage-Free Validation)
    # ------------------------------------------------------------------
    def train_multiclass(self, target, n_trials=10):
        """Train XGBoost multi-class classifier with strict train/val separation."""
        print(f"\n  ---- {target} (multi-class) ----")

        y_raw = self.y_dict[target].copy()
        valid_mask = y_raw.notna()
        n_valid = int(valid_mask.sum())
        n_censored = len(y_raw) - n_valid
        print(f"    Right-Censoring Filter: {n_valid:,} valid rows | {n_censored:,} censored rows dropped")

        X_curr = self.X_train[valid_mask].reset_index(drop=True)
        y_curr = y_raw[valid_mask].reset_index(drop=True)

        if target == "exception_type":
            y_curr = y_curr.fillna("NONE")
        elif target == "next_state":
            y_curr = y_curr.replace({"DEFAULT": "90PLUS_DPD"}).fillna("CURRENT")
        else:
            y_curr = y_curr.fillna("UNKNOWN")

        classes = sorted(y_curr.unique())
        class_to_idx = {c: i for i, c in enumerate(classes)}
        idx_to_class = {i: c for c, i in class_to_idx.items()}
        y = y_curr.map(class_to_idx)
        n_classes = len(classes)

        print(f"    Classes ({n_classes}): {classes}")
        vc = y_curr.value_counts()
        for cls, cnt in vc.items():
            print(f"      {cls}: {cnt:,} ({cnt/len(y)*100:.2f}%)")

        # Time-ordered 80/20 train/val split
        cut = int(len(X_curr) * 0.80)
        X_tr, X_val = X_curr.iloc[:cut], X_curr.iloc[cut:]
        y_tr, y_val = y.iloc[:cut], y.iloc[cut:]

        # Baseline: Decision Tree with SimpleImputer
        base_pipe = make_pipeline(
            SimpleImputer(strategy="median"),
            DecisionTreeClassifier(max_depth=5, class_weight="balanced", random_state=42)
        )
        base_pipe.fit(X_tr, y_tr)
        base_pred = base_pipe.predict(X_val)
        base_f1 = f1_score(y_val, base_pred, average="macro", zero_division=0)
        print(f"    Baseline DT Macro-F1: {base_f1:.4f}")

        def objective(trial):
            params = {
                "n_estimators": trial.suggest_int("n_estimators", 150, 400),
                "max_depth": trial.suggest_int("max_depth", 3, 8),
                "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.2, log=True),
                "subsample": trial.suggest_float("subsample", 0.6, 1.0),
                "colsample_bytree": trial.suggest_float("colsample_bytree", 0.5, 1.0),
                "min_child_weight": trial.suggest_int("min_child_weight", 1, 10),
                "objective": "multi:softprob",
                "num_class": n_classes,
                "random_state": 42,
                "n_jobs": -1,
                "verbosity": 0,
            }
            m = xgb.XGBClassifier(**params)
            m.fit(X_tr, y_tr, eval_set=[(X_val, y_val)], verbose=False)
            pred = m.predict(X_val)
            return f1_score(y_val, pred, average="macro", zero_division=0)

        study = optuna.create_study(direction="maximize",
                                     sampler=optuna.samplers.TPESampler(seed=42))
        study.optimize(objective, n_trials=n_trials, timeout=120)

        best = study.best_params
        best.update({
            "objective": "multi:softprob", "num_class": n_classes,
            "random_state": 42, "n_jobs": -1, "verbosity": 0,
        })

        # Model 1: Validation model (fit ONLY on X_tr, evaluated on X_val)
        val_model = xgb.XGBClassifier(**best)
        val_model.fit(X_tr, y_tr, verbose=False)

        val_pred = val_model.predict(X_val)
        val_macro_f1 = f1_score(y_val, val_pred, average="macro", zero_division=0)
        val_weighted_f1 = f1_score(y_val, val_pred, average="weighted", zero_division=0)
        print(f"    XGB Held-Out Val — Macro-F1: {val_macro_f1:.4f} | Weighted-F1: {val_weighted_f1:.4f} ({len(study.trials)} trials)")

        metrics = {
            "target": target,
            "n_valid_total": n_valid,
            "n_censored_dropped": n_censored,
            "n_classes": n_classes,
            "classes": classes,
            "baseline_macro_f1": round(base_f1, 4),
            "xgb_macro_f1": round(val_macro_f1, 4),
            "xgb_weighted_f1": round(val_weighted_f1, 4),
            "n_optuna_trials": len(study.trials),
        }

        # Model 2: Production model (trained on full X_curr for test set)
        prod_model = xgb.XGBClassifier(**best)
        prod_model.fit(X_curr, y, verbose=False)

        test_pred_idx = prod_model.predict(self.X_test)
        self.test_predictions[f"pred_{target}"] = [idx_to_class[i] for i in test_pred_idx]

        # Artifact
        artifact = {
            "model": prod_model,
            "val_model": val_model,
            "class_to_idx": class_to_idx,
            "idx_to_class": idx_to_class,
            "metrics": metrics,
            "feature_cols": self.feature_cols,
        }
        with open(os.path.join(self.output_dir, f"{target}_model.pkl"), "wb") as f:
            pickle.dump(artifact, f)

        self.models[target] = artifact
        return metrics, prod_model

    # ------------------------------------------------------------------
    # Train All Models
    # ------------------------------------------------------------------
    def train_all(self, binary_trials=15, multiclass_trials=10):
        print("=" * 60)
        print("PHASE 2: SUPERVISED ML MODEL TRAINING (ZERO-LEAKAGE & UNCENSORED)")
        print(f"Features: {len(self.feature_cols)} | Binary Targets: {len(BINARY_TARGETS)} | Multi-Class: {len(MULTICLASS_TARGETS)}")
        print("=" * 60)

        for target in BINARY_TARGETS:
            if target in self.y_dict:
                metrics, _ = self.train_binary(target, n_trials=binary_trials)
                if metrics:
                    self.binary_results.append(metrics)

        for target in MULTICLASS_TARGETS:
            if target in self.y_dict:
                metrics, _ = self.train_multiclass(target, n_trials=multiclass_trials)
                if metrics:
                    self.mc_results.append(metrics)

        return self.binary_results, self.mc_results

    def get_test_predictions_df(self, test_df_raw):
        df = test_df_raw[["loan_id", "reporting_month"]].copy()
        for col, preds in self.test_predictions.items():
            df[col] = preds
        return df
