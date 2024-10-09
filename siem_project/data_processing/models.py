# data_processing/models.py

from django.db import models
from django.utils import timezone
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.conf import settings

class SecurityEvent(models.Model):
    EVENT_TYPES = (
        ('LOGIN', 'Login Attempt'),
        ('FIREWALL', 'Firewall Event'),
        ('IDS', 'Intrusion Detection'),
        ('MALWARE', 'Malware Detection'),
        ('FORWARD', 'Forwarded Event'),
        ('DNS', 'DNS Event'),
        ('DHCP', 'DHCP Event'),
        ('AUTH', 'Authentication Event'),
        ('VPN', 'VPN Event'),
        ('TIMESYNC', 'Time Synchronization'),
        ('SYSTEM', 'System Event'),
    )
    SEVERITY_LEVELS = (
        (1, 'Low'),
        (2, 'Medium'),
        (3, 'High'),
        (4, 'Critical'),
    )
    event_id = models.CharField(max_length=100, unique=True)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    source_ip = models.GenericIPAddressField(null=True, blank=True)
    destination_ip = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    severity = models.IntegerField(choices=SEVERITY_LEVELS)
    description = models.TextField()
    raw_data = models.JSONField()
    reported_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.event_type} - {self.event_id}"


class AggregatedMetric(models.Model):
    metric_name = models.CharField(max_length=100)
    metric_value = models.FloatField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    dimension = models.JSONField()  # For storing multi-dimensional aggregations
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    class Meta:
        unique_together = ('metric_name', 'start_time', 'end_time', 'dimension')

    def __str__(self):
        return f"{self.metric_name}: {self.metric_value} ({self.start_time} to {self.end_time})"



class ProcessedData(models.Model):
    security_event = models.OneToOneField(SecurityEvent, on_delete=models.CASCADE, related_name='processed_data')
    processed_at = models.DateTimeField(auto_now_add=True)
    risk_score = models.FloatField()
    anomaly_detected = models.BooleanField(default=False)

    def __str__(self):
        return f"ProcessedData for {self.security_event.event_id}"
    


class Report(models.Model):
    REPORT_TYPES = (
        ('daily', 'Daily Summary'),
        ('weekly', 'Weekly Summary'),
    )
    report_type = models.CharField(max_length=10, choices=REPORT_TYPES)
    date_range = models.JSONField()  # Store start and end date
    content = models.JSONField()  # Store report data
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_report_type_display()} - {self.created_at.date()}"