import json
import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from alerts.models import FraudAlert, ModelMetric
from core.models import RiskSetting
from ml.predictor import ARTIFACTS, build_features, predict
from transactions.models import Transaction


class Command(BaseCommand):
    help = "Create demo data so the charts are not empty"

    def handle(self, *args, **options):
        # 1. Save the model's test results (precision, recall ...) in the database
        meta = json.loads((ARTIFACTS / "meta.json").read_text())
        m = meta["metrics"]
        ModelMetric.objects.create(
            model_version=meta["version"],
            precision=m["precision"],
            recall=m["recall"],
            f1_score=m["f1"],
            pr_auc=m["pr_auc"],
        )

        # 2. Use the threshold we found in Step 13
        setting = RiskSetting.get_setting()
        setting.threshold = meta["recommended_threshold"]
        setting.save()

        # 3. Create 200 demo transactions
        random.seed(7)
        for i in range(200):
            when    = timezone.now() - timedelta(days=random.randint(0, 13))
            balance = random.choice([5000, 20000, 80000, 300000])

            if random.random() < 0.12:
                # fraud-like: the whole balance is sent away
                txn_type = "TRANSFER"
                amount   = balance
                new_org  = 0
                old_dest = 0
                new_dest = 0
            else:
                # normal: a small part of the balance goes to an active account
                txn_type = random.choice(["TRANSFER", "CASH_OUT"])
                amount   = round(balance * random.uniform(0.02, 0.4), 2)
                new_org  = balance - amount
                old_dest = random.choice([10000, 50000, 250000])
                new_dest = old_dest + amount

            features          = build_features(txn_type, amount, balance, new_org, old_dest, new_dest)
            score, reasons    = predict(features)
            is_fraud          = score >= setting.threshold

            txn = Transaction.objects.create(
                sender_id=     "C" + str(random.randint(100000000, 999999999)),
                receiver_id=   "C" + str(random.randint(100000000, 999999999)),
                txn_type=      txn_type,
                amount=        amount,
                old_balance_org=balance,
                new_balance_org=new_org,
                old_balance_dest=old_dest,
                new_balance_dest=new_dest,
                timestamp=     when,
                risk_score=    score,
                is_fraud=      is_fraud,
            )

            if is_fraud:
                FraudAlert.objects.create(
                    transaction=    txn,
                    shap_explanation=reasons,
                    created_at=     when,
                )

        self.stdout.write("Demo data created.")
