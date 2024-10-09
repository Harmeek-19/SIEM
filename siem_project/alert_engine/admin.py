
from django.contrib import admin
from .models import AlertRule, Alert, AlertNotification

admin.site.register(AlertRule)
admin.site.register(Alert)
admin.site.register(AlertNotification)