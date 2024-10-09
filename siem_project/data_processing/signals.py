# data_processing/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import SecurityEvent, ProcessedData
from .anomaly_detection import detect_anomalies, update_aggregated_metrics

@receiver(post_save, sender=SecurityEvent)
def process_security_event(sender, instance, created, **kwargs):
    if created:
        risk_score, is_anomaly = detect_anomalies(instance)
        
        ProcessedData.objects.create(
            security_event=instance,
            risk_score=risk_score,
            anomaly_detected=is_anomaly
        )
        
        update_aggregated_metrics(instance.event_type, risk_score, is_anomaly)