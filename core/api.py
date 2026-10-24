from rest_framework.decorators import api_view
from rest_framework.response import Response

from alerts.models import ModelMetric
from transactions.models import Transaction


@api_view(["GET"])
def trend(request):
    """For each day: how many transactions and how many were flagged."""
    days = {}
    for t in Transaction.objects.all():
        day = t.timestamp.date().isoformat()    # for example "2026-10-12"
        if day not in days:
            days[day] = {"day": day, "total": 0, "fraud": 0}
        days[day]["total"] += 1
        if t.is_fraud:
            days[day]["fraud"] += 1

    result = []
    for day in sorted(days):                    # oldest day first
        result.append(days[day])
    return Response(result)


@api_view(["GET"])
def metrics(request):
    """The latest model results (precision, recall ...) as JSON."""
    m = ModelMetric.objects.order_by("-evaluated_at").first()
    if m is None:
        return Response({})
    return Response({
        "model_version": m.model_version,
        "precision":     m.precision,
        "recall":        m.recall,
        "f1_score":      m.f1_score,
        "pr_auc":        m.pr_auc,
    })
