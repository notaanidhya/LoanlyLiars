"""
src/models/trainer.py
Intain AI Track — Phase 2: Supervised ML Training Pipeline
Covers: binary XGBoost classifiers with Optuna tuning, probability
        calibration (Isotonic), baseline comparison (Logistic Regression),
        multi-class next-state and exception-type classifiers,
        MLflow experiment tracking.
"""

import pandas as pd
import numpy as np
import os
import pickle
from datetime import datetime

import mlflow
import optuna
optuna.logging.set_verbosity(optuna.logging.WARNING)

import xgboost as xgb
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
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
    """Trains and evaluates all Phase 2 supervised models."""

    def __init__(self, X_train, y_dict, X_test, feature_cols, output_dir="models"):
        self.feature_cols = feature_cols

        # Ensure only feature columns that exist in both datasets
        avail = [c for c in feature_cols if c in X_train.columns and c in X_test.columns]
        self.X_train = X_train[avail].copy().fillna(0)
        self.X_test = X_test[avail].copy().fillna(0)
        self.feature_cols = avail

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
        except Exception:
            pass

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
    # Binary Classifier
    # ------------------------------------------------------------------
    def train_binary(self, target, n_trials=15):
        """Train XGBoost + Logistic Regression baseline for one binary target."""
        print(f"\n  ---- {target} ----")

        y = self.y_dict[target]
        if y.sum() == 0:
            print(f"    SKIP: zero positive examples.")
            return {}, None

        spw = self._scale_pos_weight(y)
        pos_rate = float(y.mean())
        print(f"    Positive rate: {pos_rate*100:.2f}%  | Scale pos weight: {spw:.1f}x")

        # Time-respecting 80/20 split (no shuffle)
        n = len(self.X_train)
        cut = int(n * 0.80)
        X_tr, X_val = self.X_train.iloc[:cut], self.X_train.iloc[cut:]
        y_tr, y_val = y.iloc[:cut], y.iloc[cut:]

        # ---- Baseline: Logistic Regression ----
        base = LogisticRegression(max_iter=500, class_weight="balanced", C=1.0, random_state=42)
        base.fit(X_tr, y_tr)
        base_proba = base.predict_proba(X_val)[:, 1]
        base_auc = self._safe_auc(y_val, base_proba)
        base_prauc = average_precision_score(y_val, base_proba) if y_val.sum() > 0 else 0.0
        print(f"    Baseline LR  — ROC-AUC: {base_auc:.4f} | PR-AUC: {base_prauc:.4f}")

        # ---- Optuna XGBoost ----
        def objective(trial):
            params = {
                "n_estimators": trial.suggest_int("n_estimators", 150, 500),
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
            m.fit(X_tr, y_tr, eval_set=[(X_val, y_val)], verbose=False)
            p = m.predict_proba(X_val)[:, 1]
            if y_val.sum() == 0:
                return 0.0
            return average_precision_score(y_val, p)

        study = optuna.create_study(direction="maximize",
                                     sampler=optuna.samplers.TPESampler(seed=42))
        study.optimize(objective, n_trials=n_trials, timeout=180)

        best = study.best_params
        best.update({"scale_pos_weight": spw, "random_state": 42, "n_jobs": -1, "verbosity": 0})
        print(f"    Best Optuna PR-AUC (val): {study.best_value:.4f}")

        # ---- Train final model on full train set ----
        final = xgb.XGBClassifier(**best)
        final.fit(self.X_train, y, verbose=False)

        # ---- Manual isotonic calibration on validation split ----
        # cv='prefit' was removed from sklearn >= 1.4 — use IsotonicRegression directly
        raw_val_proba = final.predict_proba(X_val)[:, 1]
        iso = IsotonicRegression(out_of_bounds="clip")
        iso.fit(raw_val_proba, y_val)

        # ---- Evaluate (calibrated) on validation set ----
        val_proba = iso.transform(raw_val_proba)
        val_pred = (val_proba >= 0.5).astype(int)

        metrics = {
            "target": target,
            "n_train": int(len(y_tr)),
            "n_val": int(len(y_val)),
            "positive_rate": round(pos_rate, 4),
            "scale_pos_weight": round(spw, 2),
            "baseline_roc_auc": round(base_auc, 4),
            "baseline_pr_auc": round(base_prauc, 4),
            "xgb_roc_auc": round(self._safe_auc(y_val, val_proba), 4),
            "xgb_pr_auc": round(average_precision_score(y_val, val_proba) if y_val.sum() > 0 else 0.0, 4),
            "xgb_f1": round(f1_score(y_val, val_pred, zero_division=0), 4),
            "xgb_brier": round(brier_score_loss(y_val, val_proba), 4),
            "recall_at_80pct_precision": round(self._recall_at_precision(y_val, val_proba), 4),
            "optuna_best_pr_auc": round(study.best_value, 4),
        }
        print(f"    XGB val — ROC-AUC: {metrics['xgb_roc_auc']} | PR-AUC: {metrics['xgb_pr_auc']} | "
              f"F1: {metrics['xgb_f1']} | Brier: {metrics['xgb_brier']}")

        # ---- MLflow logging ----
        try:
            with mlflow.start_run(run_name=f"xgb_{target}"):
                mlflow.log_params({k: v for k, v in best.items() if isinstance(v, (int, float, str))})
                for k, v in metrics.items():
                    if isinstance(v, (int, float)):
                        mlflow.log_metric(k, v)
        except Exception:
            pass

        # ---- Generate test predictions (apply calibration) ----
        raw_test_proba = final.predict_proba(self.X_test)[:, 1]
        self.test_predictions[target] = iso.transform(raw_test_proba)

        # ---- Save model ----
        artifact = {"model": final, "calibrator": iso, "metrics": metrics, "feature_cols": self.feature_cols}
        with open(os.path.join(self.output_dir, f"{target}_model.pkl"), "wb") as f:
            pickle.dump(artifact, f)

        self.models[target] = artifact
        return metrics, iso

    # ------------------------------------------------------------------
    # Multi-Class Classifier
    # ------------------------------------------------------------------
    def train_multiclass(self, target, n_trials=10):
        """Train XGBoost multi-class classifier."""
        print(f"\n  ---- {target} (multi-class) ----")

        y_raw = self.y_dict[target]
        classes = sorted(y_raw.unique())
        class_to_idx = {c: i for i, c in enumerate(classes)}
        idx_to_class = {i: c for c, i in class_to_idx.items()}
        y = y_raw.map(class_to_idx)
        n_classes = len(classes)

        print(f"    Classes ({n_classes}): {classes}")
        vc = y_raw.value_counts()
        for cls, cnt in vc.items():
            print(f"      {cls}: {cnt:,} ({cnt/len(y)*100:.2f}%)")

        cut = int(len(self.X_train) * 0.80)
        X_tr, X_val = self.X_train.iloc[:cut], self.X_train.iloc[cut:]
        y_tr, y_val = y.iloc[:cut], y.iloc[cut:]

        # Baseline: Decision Tree
        base = DecisionTreeClassifier(max_depth=5, class_weight="balanced", random_state=42)
        base.fit(X_tr, y_tr)
        base_pred = base.predict(X_val)
        base_f1 = f1_score(y_val, base_pred, average="macro", zero_division=0)
        print(f"    Baseline DT Macro-F1: {base_f1:.4f}")

        def objective(trial):
            params = {
                "n_estimators": trial.suggest_int("n_estimators", 150, 500),
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

        final = xgb.XGBClassifier(**best)
        final.fit(self.X_train, y, verbose=False)

        val_pred = final.predict(X_val)
        val_macro_f1 = f1_score(y_val, val_pred, average="macro", zero_division=0)
        val_weighted_f1 = f1_score(y_val, val_pred, average="weighted", zero_division=0)

        print(f"    XGB val — Macro-F1: {val_macro_f1:.4f} | Weighted-F1: {val_weighted_f1:.4f}")

        metrics = {
            "target": target,
            "n_classes": n_classes,
            "classes": classes,
            "class_to_idx": class_to_idx,
            "baseline_macro_f1": round(base_f1, 4),
            "xgb_macro_f1": round(val_macro_f1, 4),
            "xgb_weighted_f1": round(val_weighted_f1, 4),
            "optuna_best_macro_f1": round(study.best_value, 4),
        }

        # Test predictions → class labels
        test_pred_enc = final.predict(self.X_test)
        self.test_predictions[target] = np.array([idx_to_class[i] for i in test_pred_enc])
        self.test_predictions[f"{target}_proba"] = final.predict_proba(self.X_test)

        try:
            with mlflow.start_run(run_name=f"xgb_{target}"):
                mlflow.log_params({k: v for k, v in best.items() if isinstance(v, (int, float, str))})
                for k, v in metrics.items():
                    if isinstance(v, (int, float)):
                        mlflow.log_metric(k, v)
        except Exception:
            pass

        artifact = {
            "model": final, "metrics": metrics, "class_to_idx": class_to_idx,
            "idx_to_class": idx_to_class, "feature_cols": self.feature_cols,
        }
        with open(os.path.join(self.output_dir, f"{target}_model.pkl"), "wb") as f:
            pickle.dump(artifact, f)

        self.models[target] = artifact
        return metrics, final

    # ------------------------------------------------------------------
    # Train All
    # ------------------------------------------------------------------
    def train_all(self):
        print("\n" + "=" * 70)
        print("PHASE 2: SUPERVISED ML TRAINING — ALL MODELS")
        print("=" * 70)

        # Binary models
        for target in BINARY_TARGETS:
            if target in self.y_dict:
                metrics, _ = self.train_binary(target)
                if metrics:
                    self.binary_results.append(metrics)

        # Multi-class models
        for target in MULTICLASS_TARGETS:
            if target in self.y_dict:
                metrics, _ = self.train_multiclass(target)
                if metrics:
                    self.mc_results.append(metrics)

        print("\n" + "=" * 70)
        print("TRAINING SUMMARY")
        print("=" * 70)
        for r in self.binary_results:
            print(f"  {r['target']:42s}  ROC-AUC={r['xgb_roc_auc']:.4f}  "
                  f"PR-AUC={r['xgb_pr_auc']:.4f}  Brier={r['xgb_brier']:.4f}")
        for r in self.mc_results:
            print(f"  {r['target']:42s}  Macro-F1={r['xgb_macro_f1']:.4f}")

        return self.binary_results, self.mc_results
