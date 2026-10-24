from django.db import models


# A one-row table that stores the alert threshold.
class RiskSetting(models.Model):
    threshold = models.IntegerField(default=50)

    def get_setting():
        """Return the one settings row (create it if it does not exist yet)."""
        setting, created = RiskSetting.objects.get_or_create(id=1)
        return setting
