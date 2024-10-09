from django.test import TestCase
from .models import AlertRule, Alert
from data_processing.models import SecurityEvent

class AlertEngineTestCase(TestCase):
    def setUp(self):
        self.rule = AlertRule.objects.create(name="Test Rule", condition="LOGIN", severity=3)
        self.event = SecurityEvent.objects.create(event_type="LOGIN", severity=3)

    def test_alert_generation(self):
        from .celery_tasks import generate_alerts
        generate_alerts()
        self.assertEqual(Alert.objects.count(), 1)