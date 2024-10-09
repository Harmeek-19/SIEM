# data_processing/admin.py

from django.contrib import admin
from .models import SecurityEvent, ProcessedData, AggregatedMetric

@admin.register(SecurityEvent)
class SecurityEventAdmin(admin.ModelAdmin):
    list_display = ('event_id', 'event_type', 'severity', 'timestamp')
    list_filter = ('event_type', 'severity', 'timestamp')
    search_fields = ('event_id', 'description')

@admin.register(ProcessedData)
class ProcessedDataAdmin(admin.ModelAdmin):
    list_display = ('security_event', 'processed_at', 'risk_score', 'anomaly_detected')
    list_filter = ('processed_at', 'anomaly_detected')
    search_fields = ('security_event__event_id',)

@admin.register(AggregatedMetric)
class AggregatedMetricAdmin(admin.ModelAdmin):
    list_display = ('metric_name', 'metric_value', 'start_time', 'end_time')
    list_filter = ('metric_name', 'start_time', 'end_time')
    search_fields = ('metric_name',)