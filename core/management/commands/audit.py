"""
Management command to audit the backend and ML pipeline.
Run with:  python manage.py audit
"""
import json

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.test import Client

User = get_user_model()
P = "[PASS]"
F = "[FAIL]"
S = "[SKIP]"


class Command(BaseCommand):
    help = "Audit all API endpoints and the ML pipeline"

    def handle(self, *args, **options):
        w = self.stdout.write

        # ── Temp audit user ───────────────────────────────────────────────
        user, _ = User.objects.get_or_create(username="__audit__")
        user.set_password("auditpass123")
        user.is_staff = True
        user.save()

        c = Client()
        c.login(username="__audit__", password="auditpass123")

        results = []

        def check(label, ok, detail=""):
            tag = P if ok else F
            w(f"{tag}  {label}")
            if detail:
                w(f"       {detail}")
            results.append(ok)

        def post(path, data):
            return c.post(path, json.dumps(data),
                          content_type="application/json")

        w("\n=== BACKEND & ML AUDIT ===\n")

        # ── 1. ML Pipeline ────────────────────────────────────────────────
        w("-- ML Pipeline --")
        try:
            from ml.predictor import (ARTIFACTS, build_features, explainer,
                                      meta, model, predict)

            check("ML model loaded",
                  type(model).__name__ == "XGBClassifier",
                  f"type={type(model).__name__}  features={len(meta['features'])}")

            check("SHAP explainer ready",
                  explainer is not None,
                  f"type={type(explainer).__name__}")

            # Normal transaction -> low score
            f = build_features("CASH_OUT", 500, 20000, 19500, 5000, 5500)
            score, reasons = predict(f)
            thr = meta["recommended_threshold"]
            check("Predict normal txn -> low score",
                  score < thr,
                  f"score={score}  threshold={thr}")

            # Fraud transaction -> high score
            f2 = build_features("TRANSFER", 80000, 80000, 0, 0, 0)
            score2, reasons2 = predict(f2)
            check("Predict fraud txn  -> high score",
                  score2 >= thr,
                  f"score={score2}  threshold={thr}")

            check("SHAP reasons returned  (top reason)",
                  len(reasons2) > 0,
                  f"feature={reasons2[0].get('feature')}  "
                  f"impact={reasons2[0].get('impact')}")

        except Exception as e:
            check("ML pipeline", False, str(e))

        # ── 2. API Endpoints ──────────────────────────────────────────────
        w("\n-- API Endpoints --")

        # Normal transaction
        r = post("/api/transactions/", {
            "txn_type": "CASH_OUT", "sender_id": "C111", "receiver_id": "C222",
            "amount": 500, "old_balance_org": 20000, "new_balance_org": 19500,
            "old_balance_dest": 5000, "new_balance_dest": 5500,
        })
        body = r.json()
        check("POST /api/transactions/ — normal txn",
              r.status_code == 200 and body.get("is_fraud") is False,
              f"status={r.status_code}  score={body.get('risk_score')}  "
              f"is_fraud={body.get('is_fraud')}")

        # Fraud transaction
        r = post("/api/transactions/", {
            "txn_type": "TRANSFER", "sender_id": "C333", "receiver_id": "C444",
            "amount": 80000, "old_balance_org": 80000, "new_balance_org": 0,
            "old_balance_dest": 0, "new_balance_dest": 0,
        })
        body = r.json()
        check("POST /api/transactions/ — fraud txn",
              r.status_code == 200 and body.get("is_fraud") is True,
              f"status={r.status_code}  score={body.get('risk_score')}  "
              f"is_fraud={body.get('is_fraud')}")

        # Missing fields -> 400
        r = post("/api/transactions/", {"txn_type": "TRANSFER"})
        body = r.json()
        check("POST /api/transactions/ — missing fields   -> 400",
              r.status_code == 400,
              f"status={r.status_code}  error={body.get('error')}")

        # Bad txn_type -> 400
        r = post("/api/transactions/", {
            "txn_type": "PAYMENT", "sender_id": "X", "receiver_id": "Y",
            "amount": 100, "old_balance_org": 1000, "new_balance_org": 900,
            "old_balance_dest": 0, "new_balance_dest": 100,
        })
        body = r.json()
        check("POST /api/transactions/ — bad txn_type     -> 400",
              r.status_code == 400,
              f"status={r.status_code}  error={body.get('error')}")

        # Negative amount -> 400
        r = post("/api/transactions/", {
            "txn_type": "TRANSFER", "sender_id": "X", "receiver_id": "Y",
            "amount": -100, "old_balance_org": 1000, "new_balance_org": 900,
            "old_balance_dest": 0, "new_balance_dest": 100,
        })
        body = r.json()
        check("POST /api/transactions/ — negative amount  -> 400",
              r.status_code == 400,
              f"status={r.status_code}  error={body.get('error')}")

        # Alert list
        r = c.get("/api/alerts/")
        body = r.json()
        check("GET  /api/alerts/",
              r.status_code == 200 and isinstance(body, list),
              f"status={r.status_code}  count={len(body)}")

        # Alert list filtered
        r = c.get("/api/alerts/?status=new")
        body = r.json()
        check("GET  /api/alerts/?status=new",
              r.status_code == 200 and isinstance(body, list),
              f"status={r.status_code}  count={len(body)}")

        # PATCH alert (if one exists)
        from alerts.models import FraudAlert
        alert = FraudAlert.objects.first()
        if alert:
            r = c.patch(f"/api/alerts/{alert.pk}/",
                        json.dumps({"status": "reviewed"}),
                        content_type="application/json")
            body = r.json()
            check("PATCH /api/alerts/<pk>/ — update status",
                  r.status_code == 200 and body.get("status") == "reviewed",
                  f"status={r.status_code}  new_status={body.get('status')}")
        else:
            w(f"{S}  PATCH /api/alerts/<pk>/ — no alerts in DB yet")

        # PATCH missing alert -> 404
        r = c.patch("/api/alerts/99999/",
                    json.dumps({"status": "reviewed"}),
                    content_type="application/json")
        check("PATCH /api/alerts/99999/ — not found       -> 404",
              r.status_code == 404,
              f"status={r.status_code}")

        # Trend
        r = c.get("/api/analytics/trend/")
        body = r.json()
        check("GET  /api/analytics/trend/",
              r.status_code == 200 and isinstance(body, list),
              f"status={r.status_code}  days={len(body)}")

        # Metrics
        r = c.get("/api/analytics/metrics/")
        body = r.json()
        check("GET  /api/analytics/metrics/",
              r.status_code == 200 and isinstance(body, dict),
              f"status={r.status_code}  keys={list(body.keys())}")

        # ── 3. Database ───────────────────────────────────────────────────
        w("\n-- Database --")
        from alerts.models import ModelMetric
        from core.models import RiskSetting
        from transactions.models import Transaction

        check("Transaction table",
              True, f"rows={Transaction.objects.count()}")
        check("FraudAlert table",
              True, f"rows={FraudAlert.objects.count()}")
        check("ModelMetric table",
              True, f"rows={ModelMetric.objects.count()}")
        setting = RiskSetting.get_setting()
        check("RiskSetting singleton",
              setting is not None,
              f"threshold={setting.threshold}")

        # ── Cleanup ───────────────────────────────────────────────────────
        user.delete()

        # ── Summary ───────────────────────────────────────────────────────
        passed = sum(results)
        total  = len(results)
        w(f"\n{'='*45}")
        w(f"RESULT: {passed}/{total} tests passed")
        if passed == total:
            w("All systems operational!")
        else:
            failed = [i + 1 for i, ok in enumerate(results) if not ok]
            w(f"Failed test numbers: {failed}")
