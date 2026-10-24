from django.contrib import admin

from .models import FraudAlert, ModelMetric

admin.site.register(FraudAlert)
admin.site.register(ModelMetric)
