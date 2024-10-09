# tests/test_data_processing.py

from django.test import TestCase
from django.utils import timezone
from data_processing.models import SecurityEvent, ProcessedData
from data_processing.tasks import process_security_event
from data_processing.anomaly_detection import detect_anomalies, calculate_cvss_score
from data_processing.correlation_engine import correlate_events, generate_incident_report

class SecurityEventTestCase(TestCase):
    def setUp(self):
        self.event = SecurityEvent.objects.create(
            event_type='LOGIN',
            source_ip='192.168.1.1',
            timestamp=timezone.now(),
            severity=3,
            description='Failed login attempt'
        )

    def test_process_security_event(self):
        result = process_security_event(self.event.id)
        self.assertIsNotNone(result)
        processed_data = ProcessedData.objects.filter(security_event=self.event).first()
        self.assertIsNotNone(processed_data)
        self.assertIsInstance(processed_data.risk_score, float)
        self.assertIsInstance(processed_data.anomaly_detected, bool)

    def test_anomaly_detection(self):
        risk_score, is_anomaly = detect_anomalies(self.event)
        self.assertIsInstance(risk_score, float)
        self.assertIsInstance(is_anomaly, bool)
        self.assertGreaterEqual(risk_score, 0)
        self.assertLessEqual(risk_score, 10)

    def test_cvss_score_calculation(self):
        cvss_score = calculate_cvss_score(self.event)
        self.assertIsInstance(cvss_score, float)
        self.assertGreaterEqual(cvss_score, 0)
        self.assertLessEqual(cvss_score, 10)

    def test_correlation_engine(self):
        # Create multiple events to trigger correlation
        for i in range(5):
            SecurityEvent.objects.create(
                event_type='LOGIN',
                source_ip='192.168.1.2',
                timestamp=timezone.now(),
                severity=3,
                description='Failed login attempt'
            )
        
        correlated_events = correlate_events(time_window_minutes=5)
        self.assertIsInstance(correlated_events, list)
        self.assertGreater(len(correlated_events), 0)
        
        report = generate_incident_report(correlated_events)
        self.assertIsInstance(report, str)
        self.assertIn('Potential Brute Force Attack', report)

    def test_anomaly_detection_with_historical_data(self):
        # Create historical data
        for i in range(10):
            event = SecurityEvent.objects.create(
                event_type='LOGIN',
                source_ip=f'192.168.1.{i}',
                timestamp=timezone.now() - timezone.timedelta(hours=i),
                severity=2,
                description='Normal login attempt'
            )
            ProcessedData.objects.create(
                security_event=event,
                risk_score=5.0,
                anomaly_detected=False
            )
        
        # Create an anomalous event
        anomalous_event = SecurityEvent.objects.create(
            event_type='LOGIN',
            source_ip='192.168.1.100',
            timestamp=timezone.now(),
            severity=4,
            description='Suspicious login attempt'
        )
        
        risk_score, is_anomaly = detect_anomalies(anomalous_event)
        self.assertGreater(risk_score, 7.5)  # Assuming normal risk scores are around 5.0
        self.assertTrue(is_anomaly)

# Add more test cases for other functions and edge cases