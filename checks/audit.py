"""
FraudGuard Model Audit Script
checks/audit.py
Run with: .\\venv\\Scripts\\python.exe checks\\audit.py
"""

import sys, os, warnings, json, glob, traceback
from io import StringIO
from pathlib import Path

# ── project root so "import ml" works ──────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

REPORT_PATH = ROOT / "checks" / "model_check_report.txt"
ARTIFACTS   = ROOT / "ml" / "artifacts"
MODEL_PATH  = ARTIFACTS / "model.joblib"
META_PATH   = ARTIFACTS / "meta.json"

# ── expected feature order ──────────────────────────────────────────────────
EXPECTED_FEATURES = [
    "type_code", "amount", "oldbalanceOrg", "newbalanceOrig",
    "oldbalanceDest", "newbalanceDest", "errorBalanceOrig", "errorBalanceDest",
]

lines = []   # accumulated report lines

def L(text=""):
    lines.append(str(text))
    sys.stdout.buffer.write((str(text) + "\n").encode("utf-8", errors="replace"))
    sys.stdout.buffer.flush()

def section(title):
    L()
    L("=" * 70)
    L(f"  {title}")
    L("=" * 70)

# ═══════════════════════════════════════════════════════════════════════════
# CHECK 1 – Environment versions
# ═══════════════════════════════════════════════════════════════════════════
section("CHECK 1 · Environment versions")
try:
    import xgboost, sklearn, shap, pandas, numpy, joblib
    L(f"Python      : {sys.version}")
    L(f"xgboost     : {xgboost.__version__}")
    L(f"scikit-learn: {sklearn.__version__}")
    L(f"shap        : {shap.__version__}")
    L(f"pandas      : {pandas.__version__}")
    L(f"numpy       : {numpy.__version__}")
    L(f"joblib      : {joblib.__version__}")
except Exception as e:
    L(f"ERROR in check 1: {e}")

# ═══════════════════════════════════════════════════════════════════════════
# CHECK 2 – Artifacts
# ═══════════════════════════════════════════════════════════════════════════
section("CHECK 2 · Artifacts")
model = None
meta  = None
try:
    import joblib as _joblib
    with warnings.catch_warnings(record=True) as caught_warnings:
        warnings.simplefilter("always")
        model = _joblib.load(MODEL_PATH)
        for w in caught_warnings:
            L(f"  WARNING during load: {w.category.__name__}: {w.message}")

    with open(META_PATH) as f:
        meta = json.load(f)

    L("meta.json full content:")
    L(json.dumps(meta, indent=2))

    meta_features = meta.get("features", meta.get("feature_names", []))
    L(f"\nFeatures in meta.json  : {meta_features}")
    L(f"Expected feature order : {EXPECTED_FEATURES}")
    if meta_features == EXPECTED_FEATURES:
        L("Feature list & order   : MATCH")
    else:
        L("Feature list & order   : MISMATCH — see above")
    L(f"Model type             : {type(model)}")
    L(f"n_features_in_         : {getattr(model, 'n_features_in_', 'N/A')}")
except Exception as e:
    L(f"ERROR in check 2: {e}")
    L(traceback.format_exc())

# ═══════════════════════════════════════════════════════════════════════════
# CHECK 3 – Predictor
# ═══════════════════════════════════════════════════════════════════════════
section("CHECK 3 · ml/predictor.py smoke test")
try:
    with warnings.catch_warnings(record=True) as caught_warnings:
        warnings.simplefilter("always")
        from ml.predictor import predict
        for w in caught_warnings:
            L(f"  WARNING during import: {w.category.__name__}: {w.message}")

    sample = {
        "type_code": 1, "amount": 250000.0,
        "oldbalanceOrg": 250000.0, "newbalanceOrig": 0.0,
        "oldbalanceDest": 0.0,     "newbalanceDest": 0.0,
        "errorBalanceOrig": 0.0,   "errorBalanceDest": 250000.0,
    }
    with warnings.catch_warnings(record=True) as caught_warnings:
        warnings.simplefilter("always")
        result = predict(sample)
        for w in caught_warnings:
            L(f"  WARNING during predict(): {w.category.__name__}: {w.message}")

    L(f"predict() output: {result}")
    L("Predictor: LOADED AND RUNS")
except Exception as e:
    L(f"ERROR in check 3: {e}")
    L(traceback.format_exc())

# ═══════════════════════════════════════════════════════════════════════════
# CHECK 4 – Find the PaySim CSV
# ═══════════════════════════════════════════════════════════════════════════
section("CHECK 4 · Dataset search")

SEARCH_DIRS = [
    ROOT / "data",
    Path.home() / "Downloads",
    Path.home() / "Desktop",
    Path.home() / "Documents",
    Path("C:/Users"),
]

csv_path = None
L("Locations searched:")
for d in SEARCH_DIRS:
    L(f"  {d}")
    if not d.exists():
        L("    (directory does not exist)")
        continue
    for csv in d.rglob("*.csv"):
        try:
            with open(csv, "r", errors="ignore") as f:
                header = f.readline().lower()
            if "oldbalanceorg" in header and "isfraud" in header:
                L(f"    FOUND PaySim CSV: {csv}  ({csv.stat().st_size:,} bytes)")
                csv_path = csv
                break
        except Exception:
            pass

if csv_path is None:
    L("\nPaySim CSV not found in any searched location.")
    L("SKIPPING checks 5 through 9 (dataset required).")
else:
    L(f"\nUsing CSV: {csv_path}")

# ═══════════════════════════════════════════════════════════════════════════
# CHECKS 5-9 (only if CSV found)
# ═══════════════════════════════════════════════════════════════════════════
if csv_path is not None:
    import pandas as pd
    import numpy as np
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import (precision_score, recall_score, f1_score,
                                  confusion_matrix, average_precision_score)

    # ── build exact test set ─────────────────────────────────────────────
    section("CHECK 5 · Rebuild test set")
    try:
        COLS = ["type","amount","oldbalanceOrg","newbalanceOrig",
                "oldbalanceDest","newbalanceDest","isFraud"]
        df = pd.read_csv(csv_path, usecols=COLS)
        df = df[df["type"].isin(["TRANSFER","CASH_OUT"])].copy()
        df["type_code"] = (df["type"] == "TRANSFER").astype(int)
        df["errorBalanceOrig"] = df["newbalanceOrig"] + df["amount"] - df["oldbalanceOrg"]
        df["errorBalanceDest"] = df["oldbalanceDest"] + df["amount"] - df["newbalanceDest"]
        X = df[EXPECTED_FEATURES]
        y = df["isFraud"]
        _, X_test, _, y_test = train_test_split(
            X, y, test_size=0.2, stratify=y, random_state=42
        )
        L(f"Test set size          : {len(X_test):,} rows")
        L(f"Fraud rows in test set : {y_test.sum():,}")
        L(f"Fraud rate in test set : {y_test.mean()*100:.4f}%")
    except Exception as e:
        L(f"ERROR in check 5: {e}")
        L(traceback.format_exc())
        csv_path = None   # abort remaining checks

if csv_path is not None:
    # ── get probabilities ────────────────────────────────────────────────
    try:
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            y_prob = model.predict_proba(X_test)[:,1]
    except Exception as e:
        L(f"ERROR getting probabilities: {e}")
        csv_path = None

if csv_path is not None:
    meta_precision = meta["metrics"]["precision"]
    meta_recall    = meta["metrics"]["recall"]
    meta_f1        = meta["metrics"]["f1"]
    meta_prauc     = meta["metrics"]["pr_auc"]
    rec_thresh     = meta.get("recommended_threshold", 90) / 100.0

    # ── CHECK 6 – Metrics at two thresholds ─────────────────────────────
    section("CHECK 6 · Metrics at threshold=0.50 and recommended threshold")
    for label, thresh in [("0.50", 0.50), (f"{rec_thresh:.2f} (recommended)", rec_thresh)]:
        try:
            y_pred = (y_prob >= thresh).astype(int)
            prec  = precision_score(y_test, y_pred, zero_division=0)
            rec   = recall_score(y_test, y_pred, zero_division=0)
            f1    = f1_score(y_test, y_pred, zero_division=0)
            prauc = average_precision_score(y_test, y_prob)
            tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()
            L(f"\n--- Threshold: {label} ---")
            L(f"  Precision : {prec:.6f}  (meta: {meta_precision:.6f})  diff: {abs(prec-meta_precision):.6f}{'  *** > 0.01' if abs(prec-meta_precision)>0.01 else ''}")
            L(f"  Recall    : {rec:.6f}  (meta: {meta_recall:.6f})  diff: {abs(rec-meta_recall):.6f}{'  *** > 0.01' if abs(rec-meta_recall)>0.01 else ''}")
            L(f"  F1        : {f1:.6f}  (meta: {meta_f1:.6f})  diff: {abs(f1-meta_f1):.6f}{'  *** > 0.01' if abs(f1-meta_f1)>0.01 else ''}")
            L(f"  PR-AUC    : {prauc:.6f}  (meta: {meta_prauc:.6f})  diff: {abs(prauc-meta_prauc):.6f}{'  *** > 0.01' if abs(prauc-meta_prauc)>0.01 else ''}")
            L(f"  Confusion : TN={tn:,}  FP={fp:,}  FN={fn:,}  TP={tp:,}")
        except Exception as e:
            L(f"ERROR at threshold {label}: {e}")

    # ── CHECK 7 – Threshold sweep ────────────────────────────────────────
    section("CHECK 7 : Threshold sweep 0.1 -> 0.9")
    total_test = len(y_test)
    header = f"{'Thresh':>7}  {'Precision':>10}  {'Recall':>8}  {'F1':>8}  {'Flagged':>9}  {'FlagRate%':>10}"
    L(header)
    L("-" * len(header))
    for t in [round(x * 0.1, 1) for x in range(1, 10)]:
        y_pred = (y_prob >= t).astype(int)
        prec  = precision_score(y_test, y_pred, zero_division=0)
        rec   = recall_score(y_test, y_pred, zero_division=0)
        f1    = f1_score(y_test, y_pred, zero_division=0)
        flagged = int(y_pred.sum())
        rate  = flagged / total_test * 100
        L(f"{t:>7.1f}  {prec:>10.6f}  {rec:>8.6f}  {f1:>8.6f}  {flagged:>9,}  {rate:>9.4f}%")

    # ── CHECK 8 – Score distribution ────────────────────────────────────
    section("CHECK 8 · Fraud score distribution")
    fraud_scores  = y_prob[y_test == 1]
    normal_scores = y_prob[y_test == 0]
    for label, scores in [("Fraud rows", fraud_scores), ("Normal rows", normal_scores)]:
        L(f"\n  {label} (n={len(scores):,}):")
        L(f"    Mean   : {scores.mean():.6f}")
        L(f"    Median : {float(np.median(scores)):.6f}")
        L(f"    95th % : {float(np.percentile(scores, 95)):.6f}")

    # ── CHECK 9 – Context checks ─────────────────────────────────────────
    section("CHECK 9 · Context checks")

    # 9a baseline
    L("\n9a) 'Always predict normal' baseline:")
    baseline_acc = (y_test == 0).mean()
    L(f"    Accuracy: {baseline_acc:.6f}")

    # 9b simple rule
    L("\n9b) Simple rule: newbalanceOrig==0 AND amount==oldbalanceOrg:")
    rule_pred = ((X_test["newbalanceOrig"] == 0) & (X_test["amount"] == X_test["oldbalanceOrg"])).astype(int)
    r_prec = precision_score(y_test, rule_pred, zero_division=0)
    r_rec  = recall_score(y_test, rule_pred, zero_division=0)
    r_f1   = f1_score(y_test, rule_pred, zero_division=0)
    L(f"    Precision: {r_prec:.6f}")
    L(f"    Recall   : {r_rec:.6f}")
    L(f"    F1       : {r_f1:.6f}")

    # 9c feature importance + SHAP
    L("\n9c) Feature importance (model gain):")
    try:
        importances = model.get_booster().get_score(importance_type="gain")
        for feat in EXPECTED_FEATURES:
            L(f"    {feat:<22}: {importances.get(feat, 0.0):.4f}")
    except Exception as e:
        L(f"    ERROR reading feature importance: {e}")

    L("\n9c) Mean absolute SHAP values on 2000 random test rows:")
    try:
        import shap as _shap
        rng = np.random.default_rng(42)
        idx = rng.choice(len(X_test), size=min(2000, len(X_test)), replace=False)
        X_sample = X_test.iloc[idx]
        with warnings.catch_warnings(record=True) as shap_warns:
            warnings.simplefilter("always")
            explainer   = _shap.TreeExplainer(model)
            shap_values = explainer.shap_values(X_sample)
            for w in shap_warns:
                L(f"    SHAP WARNING: {w.category.__name__}: {w.message}")
        mean_abs_shap = np.abs(shap_values).mean(axis=0)
        shap_pairs = sorted(zip(EXPECTED_FEATURES, mean_abs_shap), key=lambda x: -x[1])
        for feat, val in shap_pairs:
            L(f"    {feat:<22}: {val:.6f}")
        top_feat, top_val = shap_pairs[0]
        second_val = shap_pairs[1][1] if len(shap_pairs) > 1 else 0
        ratio = top_val / second_val if second_val > 0 else float("inf")
        L(f"\n    Top feature '{top_feat}' is {ratio:.2f}x the second feature.")
        if ratio > 3.0:
            L("    SUSPICIOUS: one feature dominates (ratio > 3x).")
        else:
            L("    No single feature dominates strongly.")
    except Exception as e:
        L(f"    ERROR in SHAP: {e}")
        L(traceback.format_exc())

# ═══════════════════════════════════════════════════════════════════════════
# CHECK 10 – Scenario tests (always run)
# ═══════════════════════════════════════════════════════════════════════════
section("CHECK 10 · Scenario tests")

SCENARIOS = [
    ("TRANSFER",  250000, 250000,  0,      0,      0),
    ("CASH_OUT",   90000,  90000,  0,  21182,      0),
    ("TRANSFER",    5000,  80000, 75000, 20000,  25000),
    ("CASH_OUT",    2000,  30000, 28000, 100000, 102000),
]

try:
    import shap as _shap
    import numpy as np
    import pandas as pd

    with warnings.catch_warnings(record=True):
        warnings.simplefilter("always")
        explainer_10 = _shap.TreeExplainer(model)

    for i, (txn_type, amount, oldOrig, newOrig, oldDest, newDest) in enumerate(SCENARIOS, 1):
        type_code = 1 if txn_type == "TRANSFER" else 0
        eOrig = newOrig + amount - oldOrig
        eDest = oldDest + amount - newDest
        row_dict = {
            "type_code": type_code, "amount": amount,
            "oldbalanceOrg": oldOrig, "newbalanceOrig": newOrig,
            "oldbalanceDest": oldDest, "newbalanceDest": newDest,
            "errorBalanceOrig": eOrig, "errorBalanceDest": eDest,
        }
        row_df = pd.DataFrame([row_dict])[EXPECTED_FEATURES]

        with warnings.catch_warnings(record=True) as sc_warns:
            warnings.simplefilter("always")
            prob = float(model.predict_proba(row_df)[0][1])
            sv   = explainer_10.shap_values(row_df)[0]
            for w in sc_warns:
                pass  # suppress repetitive xgboost serialization warning

        risk_score = round(prob * 100, 2)
        shap_pairs_sc = sorted(zip(EXPECTED_FEATURES, sv), key=lambda x: -abs(x[1]))
        top3 = shap_pairs_sc[:3]

        L(f"\n  Scenario {i}: {txn_type}, amount={amount:,}, "
          f"{oldOrig:,}→{newOrig:,} (orig), {oldDest:,}→{newDest:,} (dest)")
        L(f"    Risk score (0-100)  : {risk_score}")
        L(f"    Raw probability     : {prob:.6f}")
        L(f"    Engineered features :")
        L(f"      errorBalanceOrig  = {eOrig:.2f}")
        L(f"      errorBalanceDest  = {eDest:.2f}")
        L(f"    Top 3 SHAP reasons  :")
        for feat, sv_val in top3:
            direction = "^ fraud" if sv_val > 0 else "v fraud"
            L(f"      {feat:<22}: {sv_val:+.6f}  ({direction})")

except Exception as e:
    L(f"ERROR in check 10: {e}")
    L(traceback.format_exc())

# ═══════════════════════════════════════════════════════════════════════════
# Save report
# ═══════════════════════════════════════════════════════════════════════════
section("REPORT SAVED")
with open(REPORT_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
L(f"Full report saved to: {REPORT_PATH}")
