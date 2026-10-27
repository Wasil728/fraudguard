# checks/stats_check.py
# Read-only check reusing data loading and preprocessing from checks/audit.py

from pathlib import Path
import pandas as pd

CSV_PATH = Path(r"C:\Users\aliwa\Downloads\paysim.csv\paysim.csv.csv")

COLS = ["type", "amount", "oldbalanceOrg", "newbalanceOrig",
        "oldbalanceDest", "newbalanceDest", "isFraud"]

df = pd.read_csv(CSV_PATH, usecols=COLS)
df = df[df["type"].isin(["TRANSFER", "CASH_OUT"])].copy()

# Engineered features matching checks/audit.py
df["errorBalanceOrig"] = df["newbalanceOrig"] + df["amount"] - df["oldbalanceOrg"]
df["errorBalanceDest"] = df["oldbalanceDest"] + df["amount"] - df["newbalanceDest"]

fraud = df[df["isFraud"] == 1]
normal = df[df["isFraud"] == 0]

metrics = [
    ("Row count",
     f"{len(fraud):,}",
     f"{len(normal):,}"),
    ("errorBalanceOrig == 0 (%)",
     f"{(fraud['errorBalanceOrig'] == 0).mean() * 100:.4f}%",
     f"{(normal['errorBalanceOrig'] == 0).mean() * 100:.4f}%"),
    ("errorBalanceDest == 0 (%)",
     f"{(fraud['errorBalanceDest'] == 0).mean() * 100:.4f}%",
     f"{(normal['errorBalanceDest'] == 0).mean() * 100:.4f}%"),
    ("newbalanceOrig == 0 (%)",
     f"{(fraud['newbalanceOrig'] == 0).mean() * 100:.4f}%",
     f"{(normal['newbalanceOrig'] == 0).mean() * 100:.4f}%"),
    ("newbalanceOrig == oldbalanceOrg (%)",
     f"{(fraud['newbalanceOrig'] == fraud['oldbalanceOrg']).mean() * 100:.4f}%",
     f"{(normal['newbalanceOrig'] == normal['oldbalanceOrg']).mean() * 100:.4f}%"),
    ("Median amount",
     f"{fraud['amount'].median():,.2f}",
     f"{normal['amount'].median():,.2f}")
]

header = f"{'Metric':<38} | {'Fraud (isFraud=1)':>20} | {'Normal (isFraud=0)':>20}"
sep = "-" * len(header)
print(sep)
print(header)
print(sep)
for name, f_val, n_val in metrics:
    print(f"{name:<38} | {f_val:>20} | {n_val:>20}")
print(sep)
