from celery import shared_task
from celery.exceptions import Ignore
from celery.result import AsyncResult

from alert_engine.models import Alert, AlertRule
from .models import SecurityEvent, ProcessedData
from .log_collector import collect_logs
from .anomaly_detection import detect_anomalies, update_aggregated_metrics, run_ml_anomaly_detection
from django.utils import timezone
from datetime import timedelta
import logging
import time
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.tokens import RefreshToken
import requests
from alert_engine.celery_tasks import generate_alerts

logger = logging.getLogger(__name__)

def get_system_user_jwt_token():
    User = get_user_model()
    system_user = User.objects.get(username='system_user')
    refresh = RefreshToken.for_user(system_user)
    return str(refresh.access_token)

def get_auth_headers():
    return {'Authorization': f'Bearer {get_system_user_jwt_token()}'}

@shared_task(bind=True)
def collect_logs_task(self, user_id):
    try:
        token = get_system_user_jwt_token()
        headers = {'Authorization': f'Bearer {token}'}
        api_url = f"{settings.BASE_URL}/api/security-events/"
        
        while not self.request.called_directly:
            logs = collect_logs(limit=30)
            for log in logs:
                payload = {
                    'event_id': log['event_id'],
                    'event_type': log['event_type'],
                    'source_ip': log['source_ip'],
                    'destination_ip': log['destination_ip'],
                    'timestamp': log['timestamp'].isoformat(),
                    'severity': log['severity'],
                    'description': log['description'],
                    'raw_data': str(log['raw_data']),
                }
                logger.info(f"Sending payload: {payload}")
                response = requests.post(api_url, json=payload, headers=headers)
                logger.info(f"Response status: {response.status_code}")
                logger.info(f"Response content: {response.text}")
                if response.status_code != 201:
                    logger.error(f"Failed to create security event: {response.text}")
                else:
                    logger.info(f"Successfully created security event: {log['event_id']}")
            
            time.sleep(settings.LOG_COLLECTION_INTERVAL)
    except Exception as e:
        logger.error(f"Error in continuous log collection: {str(e)}", exc_info=True)
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise Ignore()

@shared_task
def manage_log_collection(action, user_id=None, task_id=None):
    headers = get_auth_headers()
    if action == 'start':
        if user_id is None:
            raise ValueError("user_id is required to start log collection")
        task = collect_logs_task.delay(user_id)
        return str(task.id)
    elif action == 'stop' and task_id:
        AsyncResult(task_id).revoke(terminate=True)
        return "Log collection stopped"
    else:
        return "Invalid action"

@shared_task
def process_security_event(event_id):
    headers = get_auth_headers()
    try:
        event = SecurityEvent.objects.get(id=event_id)
        risk_score, is_anomaly = detect_anomalies(event)
        
        ProcessedData.objects.create(
            security_event=event,
            risk_score=risk_score,
            anomaly_detected=is_anomaly
        )
        
        update_aggregated_metrics(event.event_type, risk_score, is_anomaly)
        
        logger.info(f"Successfully processed SecurityEvent {event_id}")
    except SecurityEvent.DoesNotExist:
        logger.error(f"SecurityEvent with ID {event_id} does not exist.")
    except Exception as e:
        logger.error(f"Error processing event {event_id}: {e}")

@shared_task
def periodic_ml_anomaly_detection():
    anomaly_count = run_ml_anomaly_detection()
    
    if anomaly_count > 0:
        # Create an alert for detected anomalies
        AlertRule.objects.get_or_create(
            name="ML Anomaly Detection",
            defaults={
                'description': "Alert for ML-detected anomalies",
                'condition': "ML_ANOMALY",
                'severity': 3,  # Adjust as needed
                'enabled': True
            }
        )
        
        Alert.objects.create(
            title=f"ML Detected {anomaly_count} Anomalies",
            description=f"ML anomaly detection found {anomaly_count} anomalies.",
            severity=3,  # Adjust as needed
            rule=AlertRule.objects.get(name="ML Anomaly Detection"),
            status='New'
        )
    
    logger.info(f"Detected {anomaly_count} anomalies using ML-based detection")
    return anomaly_count

@shared_task
def delete_old_events():
    headers = get_auth_headers()
    retention_days = 90  # Adjust as needed
    cutoff_date = timezone.now() - timedelta(days=retention_days)
    old_events = SecurityEvent.objects.filter(timestamp__lt=cutoff_date)
    deleted_count = old_events.count()
    old_events.delete()
    return f"Deleted {deleted_count} old events"