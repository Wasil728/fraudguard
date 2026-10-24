from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import FraudAlert


@api_view(["GET"])
def alert_list(request):
    """List alerts, newest first. Optional filter: /api/alerts/?status=new"""
    alerts = FraudAlert.objects.select_related("transaction")

    status = request.GET.get("status")
    if status:
        alerts = alerts.filter(status=status)

    result = []
    for a in alerts[:100]:              # only the latest 100
        result.append({
            "id":         a.id,
            "txn_type":   a.transaction.txn_type,
            "amount":     a.transaction.amount,
            "risk_score": a.transaction.risk_score,
            "status":     a.status,
        })
    return Response(result)


@api_view(["PATCH"])
def alert_update(request, pk):
    """Change the status of one alert (reviewed or dismissed)."""
    alert = get_object_or_404(FraudAlert, pk=pk)

    new_status = request.data.get("status")
    if new_status not in ("new", "reviewed", "dismissed"):
        return Response({"error": "Invalid status."}, status=400)

    alert.status = new_status
    alert.reviewed_by = request.user    # remember who reviewed it
    alert.save()

    return Response({"id": alert.id, "status": alert.status})
