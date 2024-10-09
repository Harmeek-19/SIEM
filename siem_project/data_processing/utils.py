from django.utils import timezone
from datetime import timedelta

from api import models
from .models import SecurityEvent, Report

def generate_summary_report(report_type):
    end_date = timezone.now()
    if report_type == 'daily':
        start_date = end_date - timedelta(days=1)
    else:  # weekly
        start_date = end_date - timedelta(weeks=1)

    events = SecurityEvent.objects.filter(timestamp__range=(start_date, end_date))
    
    report_data = {
        'total_events': events.count(),
        'high_severity_events': events.filter(severity__gte=3).count(),
        'top_event_types': list(events.values('event_type').annotate(count=models.Count('id')).order_by('-count')[:5]),
    }

    report = Report.objects.create(
        report_type=report_type,
        date_range={'start': start_date.isoformat(), 'end': end_date.isoformat()},
        content=report_data
    )

    return report