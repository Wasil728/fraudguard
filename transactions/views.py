from rest_framework.decorators import api_view
from rest_framework.response import Response

from alerts.models import FraudAlert
from core.models import RiskSetting
from ml.predictor import build_features, predict
from .models import Transaction


@api_view(["POST"])
def check_transaction(request):
    data = request.data

    # 1. Read the values sent by the form and check that they are valid
    try:
        txn_type    = data["txn_type"]
        sender_id   = data["sender_id"]
        receiver_id = data["receiver_id"]
        amount      = float(data["amount"])
        old_org     = float(data["old_balance_org"])
        new_org     = float(data["new_balance_org"])
        old_dest    = float(data["old_balance_dest"])
        new_dest    = float(data["new_balance_dest"])
    except (KeyError, ValueError, TypeError):
        return Response(
            {"error": "Please fill every field with valid numbers."},
            status=400,
        )

    if txn_type not in ("TRANSFER", "CASH_OUT"):
        return Response(
            {"error": "Type must be TRANSFER or CASH_OUT."},
            status=400,
        )

    if amount <= 0 or min(old_org, new_org, old_dest, new_dest) < 0:
        return Response(
            {"error": "Amount must be above 0 and balances cannot be negative."},
            status=400,
        )

    # 2. Ask the model for a risk score and the reasons
    features = build_features(txn_type, amount, old_org, new_org, old_dest, new_dest)
    score, reasons = predict(features)

    # 3. Is the score at or above the alert threshold (set on the Settings page)?
    threshold = RiskSetting.get_setting().threshold
    is_fraud  = score >= threshold

    # 4. Save the transaction in the database
    txn = Transaction.objects.create(
        sender_id=sender_id,
        receiver_id=receiver_id,
        txn_type=txn_type,
        amount=amount,
        old_balance_org=old_org,
        new_balance_org=new_org,
        old_balance_dest=old_dest,
        new_balance_dest=new_dest,
        risk_score=score,
        is_fraud=is_fraud,
    )

    # 5. If it looks risky, also create an alert
    if is_fraud:
        FraudAlert.objects.create(transaction=txn, shap_explanation=reasons)

    # 6. Send the answer back to the web page
    return Response({
        "risk_score":  score,
        "is_fraud":    is_fraud,
        "threshold":   threshold,
        "explanation": reasons,
    })
