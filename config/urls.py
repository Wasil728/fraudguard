from django.contrib import admin
from django.urls import include, path

from alerts.views import alert_list, alert_update
from core.api import metrics, trend
from transactions.views import check_transaction

urlpatterns = [
    path("admin/",                    admin.site.urls),
    path("api/transactions/",         check_transaction),
    path("api/alerts/",               alert_list),
    path("api/alerts/<int:pk>/",      alert_update),
    path("api/analytics/trend/",      trend),
    path("api/analytics/metrics/",    metrics),
    path("",                          include("core.urls")),
]
