from data_processing.models import SecurityEvent
from django.db.models import Count
from django.utils import timezone
from django.conf import settings
from datetime import timedelta

def correlate_events(time_window_minutes=60):
    end_time = timezone.now()
    start_time = end_time - timedelta(minutes=time_window_minutes)
    
    events = SecurityEvent.objects.filter(timestamp__range=(start_time, end_time))
    
    failed_logins = events.filter(event_type='LOGIN', description__icontains='failed')
    
    threshold = 3 if settings.TEST_MODE else 5
    suspicious_ips = failed_logins.values('source_ip').annotate(count=Count('source_ip')).filter(count__gte=threshold)
    
    correlated_events = []
    for ip in suspicious_ips:
        correlated_events.append({
            'type': 'Potential Brute Force Attack',
            'source_ip': ip['source_ip'],
            'count': ip['count'],
            'events': failed_logins.filter(source_ip=ip['source_ip'])
        })
    
    port_scans = events.filter(event_type='FIREWALL', description__icontains='port scan')
    suspicious_port_scanners = port_scans.values('source_ip').annotate(count=Count('source_ip')).filter(count__gte=10)
    
    for ip in suspicious_port_scanners:
        correlated_events.append({
            'type': 'Potential Port Scanning Activity',
            'source_ip': ip['source_ip'],
            'count': ip['count'],
            'events': port_scans.filter(source_ip=ip['source_ip'])
        })
    
    return correlated_events

def generate_incident_report(correlated_events):
    report = "Incident Report\n\n"
    for event in correlated_events:
        report += f"Type: {event['type']}\n"
        report += f"Source IP: {event['source_ip']}\n"
        report += f"Event Count: {event['count']}\n"
        report += "Detailed Events:\n"
        for detailed_event in event['events']:
            report += f"  - {detailed_event.timestamp}: {detailed_event.description}\n"
        report += "\n"
    return report

def get_correlation_summary():
    end_time = timezone.now()
    start_time = end_time - timedelta(hours=24)
    
    summary = {
        'total_correlated_events': 0,
        'brute_force_attempts': 0,
        'port_scanning_activities': 0,
        'other_correlations': 0
    }
    
    correlated_events = correlate_events(time_window_minutes=1440)  # 24 hours
    
    for event in correlated_events:
        summary['total_correlated_events'] += 1
        if event['type'] == 'Potential Brute Force Attack':
            summary['brute_force_attempts'] += 1
        elif event['type'] == 'Potential Port Scanning Activity':
            summary['port_scanning_activities'] += 1
        else:
            summary['other_correlations'] += 1
    
    return summary