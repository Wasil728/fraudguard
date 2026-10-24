"""
Local training script — replicates notebooks/train.ipynb.
Run from the project root:
    python ml/train_local.py --data path/to/paysim.csv

Outputs:
    ml/artifacts/model.joblib
    ml/artifacts/meta.json
"""

import argparse
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import (
    average_precision_score,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

ARTIFACTS = Path(__file__).resolve().parent / "artifacts"
FEATURES = [
    "type_code",
    "amount",
    "oldbalanceOrg",
    "newbalanceOrig",
    "oldbalanceDest",
    "newbalanceDest",
    "errorBalanceOrig",
    "errorBalanceDest",
]
VERSION = "v1.0.0"


def load_data(csv_path: str) -> tuple:
    """Load and preprocess the PaySim CSV."""
    print(f"Loading data from {csv_path} ...")
    cols = ["type", "amount", "oldbalanceOrg", "newbalanceOrig",
            "oldbalanceDest", "newbalanceDest", "isFraud"]
    df = pd.read_csv(csv_path, usecols=cols)

    print(f"  Dataset shape : {df.shape}")
    print(f"  Fraud counts  :\n{df['isFraud'].value_counts()}")

    # Keep only the two transaction types where fraud occurs
    df = df[df["type"].isin(["TRANSFER", "CASH_OUT"])].copy()

    # Encode type as a number
    df["type_code"] = df["type"].map({"TRANSFER": 1, "CASH_OUT": 0})

    # Two balance-error features
    df["errorBalanceOrig"] = df["newbalanceOrig"] + df["amount"] - df["oldbalanceOrg"]
    df["errorBalanceDest"] = df["oldbalanceDest"] + df["amount"] - df["newbalanceDest"]

    X = df[FEATURES]
    y = df["isFraud"]
    return X, y


def train(X_train, y_train) -> XGBClassifier:
    """Train an XGBoost classifier (mirrors the notebook)."""
    weight = (y_train == 0).sum() / (y_train == 1).sum()
    print(f"  Class weight  : {weight:.1f}  (normal / fraud)")

    model = XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        scale_pos_weight=weight,
        random_state=42,
        eval_metric="logloss",
    )
    print("Training XGBoost ...")
    model.fit(X_train, y_train)
    return model


def evaluate(model, X_test, y_test) -> dict:
    """Return precision / recall / f1 / pr_auc."""
    scores  = model.predict_proba(X_test)[:, 1]
    guesses = (scores >= 0.5).astype(int)
    metrics = {
        "precision": round(float(precision_score(y_test, guesses)), 6),
        "recall":    round(float(recall_score(y_test, guesses)), 6),
        "f1":        round(float(f1_score(y_test, guesses)), 6),
        "pr_auc":    round(float(average_precision_score(y_test, scores)), 6),
    }
    print(f"  Metrics : {metrics}")
    return metrics


def find_threshold(model, X_test, y_test) -> int:
    """
    Pick the score threshold (as an integer 0-100) that maximises F1.
    This mirrors the 'recommended_threshold' used by seed_demo.
    """
    scores = model.predict_proba(X_test)[:, 1] * 100
    best_f1, best_t = 0.0, 50
    for t in range(1, 100):
        guesses = (scores >= t).astype(int)
        f = f1_score(y_test, guesses, zero_division=0)
        if f > best_f1:
            best_f1, best_t = f, t
    print(f"  Best threshold: {best_t}  (F1={best_f1:.4f})")
    return best_t


def save_artifacts(model, metrics: dict, threshold: int) -> None:
    """Save model.joblib and meta.json to ml/artifacts/."""
    ARTIFACTS.mkdir(parents=True, exist_ok=True)

    # model
    model_path = ARTIFACTS / "model.joblib"
    joblib.dump(model, model_path)
    print(f"  Saved model  → {model_path}")

    # meta
    meta = {
        "version":                VERSION,
        "features":               FEATURES,
        "recommended_threshold":  threshold,
        "metrics":                metrics,
    }
    meta_path = ARTIFACTS / "meta.json"
    meta_path.write_text(json.dumps(meta, indent=2))
    print(f"  Saved meta   → {meta_path}")


def main():
    parser = argparse.ArgumentParser(description="Train the FraudGuard XGBoost model.")
    parser.add_argument("--data", required=True, help="Path to paysim.csv")
    args = parser.parse_args()

    X, y = load_data(args.data)

    print("Splitting data (80 / 20) ...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )

    model   = train(X_train, y_train)
    metrics = evaluate(model, X_test, y_test)
    thresh  = find_threshold(model, X_test, y_test)

    print("Saving artifacts ...")
    save_artifacts(model, metrics, thresh)
    print("Done!")


if __name__ == "__main__":
    main()
