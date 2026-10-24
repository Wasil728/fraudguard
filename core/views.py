from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from alerts.models import FraudAlert, ModelMetric
from transactions.models import Transaction
from .models import RiskSetting


@login_required
def dashboard(request):
    total   = Transaction.objects.count()
    flagged = Transaction.objects.filter(is_fraud=True).count()
    percent = round(flagged / total * 100, 2) if total > 0 else 0

    return render(request, "dashboard.html", {
        "total":   total,
        "flagged": flagged,
        "pct":     percent,
        "metric":  ModelMetric.objects.order_by("-evaluated_at").first(),
        "recent":  FraudAlert.objects.select_related("transaction")[:5],
    })


@login_required
def simulator(request):
    return render(request, "simulator.html")


@login_required
def alerts_page(request):
    return render(request, "alerts.html")


@login_required
def alert_detail(request, pk):
    alert = get_object_or_404(FraudAlert, pk=pk)
    return render(request, "alert_detail.html", {"alert": alert})


@login_required
def analytics(request):
    metric = ModelMetric.objects.order_by("-evaluated_at").first()
    return render(request, "analytics.html", {"metric": metric})


@login_required
def settings_page(request):
    setting = RiskSetting.get_setting()

    if request.method == "POST":            # the Save button was pressed
        try:
            value = int(request.POST.get("threshold"))
        except (TypeError, ValueError):
            value = setting.threshold

        setting.threshold = max(1, min(99, value))  # keep it between 1 and 99
        setting.save()
        messages.success(request, "Threshold updated.")
        return redirect("settings")

    return render(request, "settings.html", {"setting": setting})
