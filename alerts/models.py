from django.conf import settings
from django.db import models
from django.utils import timezone

from transactions.models import Transaction


class FraudAlert(models.Model):
    STATUS_CHOICES = [
        ("new", "New"),
        ("reviewed", "Reviewed"),
        ("dismissed", "Dismissed"),
    ]

    # one alert belongs to exactly one transaction
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE)
    shap_explanation = models.JSONField(default=list)   # the reasons, saved as a list
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="new")
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]


class ModelMetric(models.Model):
    model_version = models.CharField(max_length=50)
    precision = models.FloatField()
    recall = models.FloatField()
    f1_score = models.FloatField()
    pr_auc = models.FloatField()
    evaluated_at = models.DateTimeField(default=timezone.now)
