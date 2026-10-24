from django.db import models
from django.utils import timezone


class Transaction(models.Model):
    TYPE_CHOICES = [("TRANSFER", "Transfer"), ("CASH_OUT", "Cash out")]

    sender_id = models.CharField(max_length=50)
    receiver_id = models.CharField(max_length=50)
    txn_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    amount = models.FloatField()
    old_balance_org = models.FloatField()   # sender balance before
    new_balance_org = models.FloatField()   # sender balance after
    old_balance_dest = models.FloatField()  # receiver balance before
    new_balance_dest = models.FloatField()  # receiver balance after
    timestamp = models.DateTimeField(default=timezone.now)
    risk_score = models.FloatField(default=0)   # 0 to 100
    is_fraud = models.BooleanField(default=False)

    class Meta:
        ordering = ["-timestamp"]
