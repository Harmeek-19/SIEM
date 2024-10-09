from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import render
from .models import IOC, ThreatFeed
from .serializers import IOCSerializer, ThreatFeedSerializer
from .tasks import update_threat_feeds

class IOCViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = IOC.objects.all()
    serializer_class = IOCSerializer

    @action(detail=False, methods=['get'])
    def search(self, request):
        value = request.query_params.get('value', None)
        if value:
            iocs = IOC.objects.filter(value__icontains=value)
            serializer = self.get_serializer(iocs, many=True)
            return Response(serializer.data)
        return Response({"error": "Please provide a value to search"}, status=status.HTTP_400_BAD_REQUEST)

class ThreatFeedViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ThreatFeed.objects.all()
    serializer_class = ThreatFeedSerializer

    @action(detail=False, methods=['post'])
    def update_feeds(self, request):
        task = update_threat_feeds.delay()
        return Response({
            "status": "Threat feeds update task started",
            "task_id": str(task.id)
        })

def ioc_list(request):
    iocs = IOC.objects.all().order_by('-last_seen')[:100]  # Get the 100 most recent IOCs
    return render(request, 'threat_intelligence/ioc_list.html', {'iocs': iocs})