"""
Generates a synthetic PaySim-like dataset and trains the XGBoost model.
Saves ml/artifacts/model.joblib and ml/artifacts/meta.json.

Run from the project root:
    python ml/generate_and_train.py
"""

import json
import random
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
RANDOM_SEED = 42


# ---------------------------------------------------------------------------
# Synthetic data generation
# ---------------------------------------------------------------------------

def generate_dataset(n_normal: int = 50_000, n_fraud: int = 2_500) -> pd.DataFrame:
    """
    Create a PaySim-like DataFrame with realistic fraud patterns.

    Normal transactions:
      - amount is a small fraction of the sender balance
      - balances add up correctly (errorBalance ≈ 0)

    Fraud transactions (TRANSFER only):
      - sender drains their entire balance
      - destination balance doesn't change (mule account already emptied)
      - deliberate balance discrepancies
    """
    rng = np.random.default_rng(RANDOM_SEED)
    rows = []

    # -- Normal transactions ------------------------------------------------
    for _ in range(n_normal):
        txn_type = rng.choice(["TRANSFER", "CASH_OUT"])
        type_code = 1 if txn_type == "TRANSFER" else 0

        old_org  = float(rng.choice([5_000, 10_000, 20_000, 50_000, 100_000, 300_000]))
        amount   = round(float(old_org * rng.uniform(0.01, 0.35)), 2)
        new_org  = round(old_org - amount, 2)

        old_dest = float(rng.choice([0, 5_000, 20_000, 80_000, 250_000]))
        new_dest = round(old_dest + amount, 2)

        rows.append({
            "type_code":    type_code,
            "amount":       amount,
            "oldbalanceOrg":  old_org,
            "newbalanceOrig": new_org,
            "oldbalanceDest": old_dest,
            "newbalanceDest": new_dest,
            "isFraud": 0,
        })

    # -- Fraud transactions -------------------------------------------------
    for _ in range(n_fraud):
        # Fraud is always TRANSFER in PaySim
        type_code = 1

        old_org  = float(rng.choice([5_000, 20_000, 80_000, 300_000]))
        amount   = old_org                   # drain the whole balance
        new_org  = 0.0                       # sender is emptied

        old_dest = 0.0                       # mule starts empty
        new_dest = 0.0                       # and stays empty (already withdrawn)

        rows.append({
            "type_code":    type_code,
            "amount":       amount,
            "oldbalanceOrg":  old_org,
            "newbalanceOrig": new_org,
            "oldbalanceDest": old_dest,
            "newbalanceDest": new_dest,
            "isFraud": 1,
        })

    df = pd.DataFrame(rows)

    # Derived error features (same formula as predictor.py / notebook)
    df["errorBalanceOrig"] = df["newbalanceOrig"] + df["amount"] - df["oldbalanceOrg"]
    df["errorBalanceDest"] = df["oldbalanceDest"] + df["amount"] - df["newbalanceDest"]

    # Shuffle
    return df.sample(frac=1, random_state=RANDOM_SEED).reset_index(drop=True)


# ---------------------------------------------------------------------------
# Training helpers  (identical to train_local.py)
# ---------------------------------------------------------------------------

def train_model(X_train, y_train) -> XGBClassifier:
    weight = (y_train == 0).sum() / (y_train == 1).sum()
    print(f"  Class weight  : {weight:.2f}")
    model = XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        scale_pos_weight=weight,
        random_state=RANDOM_SEED,
        eval_metric="logloss",
    )
    model.fit(X_train, y_train)
    return model


def evaluate(model, X_test, y_test) -> dict:
    scores  = model.predict_proba(X_test)[:, 1]
    guesses = (scores >= 0.5).astype(int)
    m = {
        "precision": round(float(precision_score(y_test, guesses, zero_division=0)), 6),
        "recall":    round(float(recall_score(y_test, guesses, zero_division=0)), 6),
        "f1":        round(float(f1_score(y_test, guesses, zero_division=0)), 6),
        "pr_auc":    round(float(average_precision_score(y_test, scores)), 6),
    }
    print(f"  Metrics       : {m}")
    return m


def find_threshold(model, X_test, y_test) -> int:
    scores = model.predict_proba(X_test)[:, 1] * 100
    best_f1, best_t = 0.0, 50
    for t in range(1, 100):
        g = (scores >= t).astype(int)
        f = f1_score(y_test, g, zero_division=0)
        if f > best_f1:
            best_f1, best_t = f, t
    print(f"  Best threshold: {best_t}  (F1={best_f1:.4f})")
    return best_t


def save_artifacts(model, metrics: dict, threshold: int) -> None:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)

    model_path = ARTIFACTS / "model.joblib"
    joblib.dump(model, model_path)
    print(f"  Saved → {model_path}")

    meta = {
        "version":               VERSION,
        "features":              FEATURES,
        "recommended_threshold": threshold,
        "metrics":               metrics,
    }
    meta_path = ARTIFACTS / "meta.json"
    meta_path.write_text(json.dumps(meta, indent=2))
    print(f"  Saved → {meta_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=== Step 1: Generating synthetic PaySim-like dataset ===")
    df = generate_dataset(n_normal=50_000, n_fraud=2_500)
    print(f"  Total rows    : {len(df)}")
    print(f"  Fraud rows    : {df['isFraud'].sum()}")

    X = df[FEATURES]
    y = df["isFraud"]

    print("\n=== Step 2: Train / test split (80 / 20) ===")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=RANDOM_SEED
    )

    print("\n=== Step 3: Training XGBoost ===")
    model = train_model(X_train, y_train)

    print("\n=== Step 4: Evaluation ===")
    metrics = evaluate(model, X_test, y_test)

    print("\n=== Step 5: Finding best threshold ===")
    threshold = find_threshold(model, X_test, y_test)

    print("\n=== Step 6: Saving artifacts ===")
    save_artifacts(model, metrics, threshold)

    print("\nDone! Artifacts are in ml/artifacts/")
