import json
from pathlib import Path

import joblib
import pandas as pd
import shap

# The folder where model.joblib and meta.json are saved
ARTIFACTS = Path(__file__).resolve().parent / "artifacts"

# Load everything ONE time when Django starts
model = joblib.load(ARTIFACTS / "model.joblib")
meta = json.loads((ARTIFACTS / "meta.json").read_text())
explainer = shap.TreeExplainer(model)

# Friendly names to show on the website instead of column names
FRIENDLY = {
    "type_code":        "Transaction type",
    "amount":           "Transaction amount",
    "oldbalanceOrg":    "Sender balance before",
    "newbalanceOrig":   "Sender balance after",
    "oldbalanceDest":   "Receiver balance before",
    "newbalanceDest":   "Receiver balance after",
    "errorBalanceOrig": "Sender balance check",
    "errorBalanceDest": "Receiver balance check",
}


def build_features(txn_type, amount, old_org, new_org, old_dest, new_dest):
    """Turn the form values into the 8 clues the model expects."""
    if txn_type == "TRANSFER":
        type_code = 1
    else:
        type_code = 0
    return {
        "type_code":        type_code,
        "amount":           amount,
        "oldbalanceOrg":    old_org,
        "newbalanceOrig":   new_org,
        "oldbalanceDest":   old_dest,
        "newbalanceDest":   new_dest,
        "errorBalanceOrig": new_org + amount - old_org,
        "errorBalanceDest": old_dest + amount - new_dest,
    }


def get_impact(reason):
    """Helper for sorting: how strong is this reason?"""
    return abs(reason["impact"])


def predict(features):
    """Return the risk score (0 to 100) and the top 5 reasons."""
    # One-row table, with the columns in the same order as during training
    row = pd.DataFrame([features])[meta["features"]]

    score = model.predict_proba(row)[0][1] * 100   # fraud chance x 100
    shap_values = explainer.shap_values(row)[0]    # one SHAP number per clue

    reasons = []
    for name, value in zip(meta["features"], shap_values):
        reasons.append({"feature": FRIENDLY[name], "impact": round(float(value), 4)})

    reasons.sort(key=get_impact, reverse=True)
    return round(float(score), 2), reasons[:5]
