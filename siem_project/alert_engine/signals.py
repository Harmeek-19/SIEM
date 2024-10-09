from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.apps import apps

User = get_user_model()

@receiver(post_migrate)
def init_scheduler(sender, **kwargs):
    if sender.name == 'alert_engine':
        from .scheduler import start_scheduler
        start_scheduler(sender, **kwargs)

@receiver(post_save, sender=User)
def create_alert_notification(sender, instance, created, **kwargs):
    if created:
        AlertNotification = apps.get_model('alert_engine', 'AlertNotification')
        AlertNotification.objects.create(
            user=instance,
            severity_level=2,  # Default to Medium severity
            email_notification=True
        )