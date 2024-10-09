from django.db.models import Count
from django.shortcuts import render
from data_processing.models import SecurityEvent
from threat_intelligence.models import IOC

def dashboard(request):
    recent_events = SecurityEvent.objects.order_by('-timestamp')[:10]
    ioc_count = IOC.objects.count()
    event_count = SecurityEvent.objects.count()
    
    severity_distribution = SecurityEvent.objects.values('severity').annotate(count=Count('severity'))
    severity_data = {item['severity']: item['count'] for item in severity_distribution}
    
    return render(request, 'dashboard/home.html', {
        'recent_events': recent_events,
        'ioc_count': ioc_count,
        'event_count': event_count,
        'severity_data': severity_data,
    })