from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings
import logging

from .models import Alert

logger = logging.getLogger(__name__)


@shared_task(name='alert_engine.tasks.generate_alerts')
def generate_alerts():
    from .models import AlertRule, Alert
    from data_processing.models import SecurityEvent
    from django.db.models import Q
    
    alert_rules = AlertRule.objects.filter(enabled=True)
    alerts_generated = 0
    logger.info(f"Checking {alert_rules.count()} alert rules")
    for rule in alert_rules:
        if rule.condition == "ML_ANOMALY":
            # ML anomalies are handled separately in the ML task
            continue
        events = SecurityEvent.objects.filter(
            Q(event_type=rule.condition) | Q(severity=rule.severity),
            timestamp__gte=timezone.now() - timezone.timedelta(hours=1)
        )
        logger.info(f"Found {events.count()} events matching rule: {rule.name}")
        if events.exists():
            alert = Alert.objects.create(
                rule=rule,
                title=f"Alert: {rule.name}",
                description=f"Triggered by rule: {rule.description}",
                severity=rule.severity,
                created_at=timezone.now(),
                status='New'
            )
            alerts_generated += 1
            
            # Send email alerts to appropriate users
            send_alert_emails.delay(alert.id)

    logger.info(f"Generated {alerts_generated} alerts")
    return f"Generated {alerts_generated} alerts"

@shared_task
def check_alert_rules():
    return generate_alerts()


@shared_task(name='alert_engine.tasks.send_daily_alert_summary')
def send_daily_alert_summary():
    start_date = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = start_date + timezone.timedelta(days=1)
    
    alerts = Alert.objects.filter(created_at__range=(start_date, end_date))
    
    if alerts.exists() or settings.SEND_EMPTY_ALERT_SUMMARY:
        subject = f"Daily Alert Summary - {start_date.date()}"
        html_message = render_to_string('emails/daily_alert_summary.html', {'alerts': alerts, 'date': start_date.date()})
        
        send_mail(
            subject,
            '',
            settings.DEFAULT_FROM_EMAIL,
            [settings.ADMIN_EMAIL],  # This should now be correct
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"Sent daily alert summary for {start_date.date()} with {alerts.count()} alerts to {settings.ADMIN_EMAIL}")
    else:
        logger.info(f"No alerts to send for {start_date.date()}")


@shared_task(name='alert_engine.tasks.send_alert_emails')
def send_alert_emails(alert_id):
    from .models import Alert, AlertNotification
    from django.core.mail import send_mail
    from django.template.loader import render_to_string
    from django.conf import settings
    from .models import Alert, AlertNotification
    # Rest of the function remains the same
    logger.info(f"Attempting to send email for alert ID: {alert_id}")
    try:
        alert = Alert.objects.get(id=alert_id)
        logger.info(f"Found alert: {alert}")
        notifications = AlertNotification.objects.filter(
            severity_level__lte=alert.severity,
            email_notification=True
        )
        logger.info(f"Found {notifications.count()} matching notifications")
        
        for notification in notifications:
            subject = f"SIEM Alert: {alert.title}"
            
            # Render the email template
            html_message = render_to_string('alert_email.html', {'alert': alert})
            
            # Send the email
            try:
                send_mail(
                    subject,
                    '',  # Plain text version (empty as we're using HTML)
                    settings.DEFAULT_FROM_EMAIL,
                    [notification.user.email],
                    html_message=html_message,
                    fail_silently=False,
                )
                logger.info(f"Email sent to {notification.user.email}")
            except Exception as e:
                logger.error(f"Failed to send email to {notification.user.email}: {str(e)}")
        
        logger.info(f"Alert emails sent for alert ID: {alert_id}")
    except Alert.DoesNotExist:
        logger.error(f"Alert with ID {alert_id} not found")
    except Exception as e:
        logger.error(f"Error sending alert emails for alert ID {alert_id}: {str(e)}")