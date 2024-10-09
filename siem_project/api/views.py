import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.throttling import UserRateThrottle
from django_ratelimit.decorators import ratelimit
from django.db.models import Count
from data_processing.models import SecurityEvent, ProcessedData
from alert_engine.models import Alert
from rest_framework import permissions
from .models import Log
from .serializers import AlertSerializer, LogSerializer, SecurityEventSerializer, ProcessedDataSerializer
from data_processing.anomaly_detection import ml_anomaly_detection
from data_processing.correlation_engine import correlate_events
from siem_project.permissions import IsOwnerOrAdmin
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenObtainPairView
from django.core.management import call_command
from threat_intelligence.tasks import update_threat_feeds
from threat_intelligence.models import IOC
from alert_engine.celery_tasks import generate_alerts
from data_processing.tasks import periodic_ml_anomaly_detection
from django.http import HttpResponse
from redis import Redis

logger = logging.getLogger(__name__)

class CustomUserRateThrottle(UserRateThrottle):
    rate = '5/minute'

class SecurityEventViewSet(viewsets.ModelViewSet):
    queryset = SecurityEvent.objects.all()
    serializer_class = SecurityEventSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
   
    def create(self, request, *args, **kwargs):
        logger.info(f"Received data: {request.data}")
        logger.info(f"User: {request.user}")
        logger.info(f"Auth: {request.auth}")
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            logger.info(f"Created security event: {serializer.data}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            logger.error(f"Validation error: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        serializer.save(reported_by=self.request.user)
        logger.info(f"Security event saved with ID: {serializer.instance.id}")

    @action(detail=False, methods=['get'])
    def summary(self, request):
        total_events = SecurityEvent.objects.count()
        events_by_type = SecurityEvent.objects.values('event_type').annotate(count=Count('event_type'))
        return Response({
            'total_events': total_events,
            'by_type': list(events_by_type)
        })

    def list(self, request, *args, **kwargs):
        limit = request.query_params.get('limit')
        queryset = self.get_queryset()
        if limit:
            queryset = queryset[:int(limit)]
        serializer = self.get_serializer(queryset, many=True)
        logger.debug(f"Request headers: {request.headers}")
        logger.debug(f"Request user: {request.user}")
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        events = self.get_queryset().order_by('-timestamp')[:10]
        serializer = self.get_serializer(events, many=True)
        return Response(serializer.data)

class ProcessedDataViewSet(viewsets.ModelViewSet):
    queryset = ProcessedData.objects.all()
    serializer_class = ProcessedDataSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    throttle_classes = [CustomUserRateThrottle]

    @action(detail=False, methods=['get'])
    def anomalies(self, request):
        anomalies = ProcessedData.objects.filter(anomaly_detected=True)
        serializer = self.get_serializer(anomalies, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def run_ml_detection(self, request):
        anomalies = ml_anomaly_detection()
        return Response({'anomalies_detected': len(anomalies)})

class LogViewSet(viewsets.ModelViewSet):
    queryset = Log.objects.all()
    serializer_class = LogSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    throttle_classes = [CustomUserRateThrottle]

class CorrelationViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    throttle_classes = [CustomUserRateThrottle]

    @action(detail=False, methods=['post'])
    def run_correlation(self, request):
        time_window = request.data.get('time_window', 60)
        correlated_events = correlate_events(time_window_minutes=time_window)
        return Response({'correlated_groups': len(correlated_events)})

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        logger.debug(f"Received token request: {request.data}")
        return super().post(request, *args, **kwargs)

def test_redis(request):
    try:
        redis_client = Redis(host='localhost', port=6379, db=0)
        redis_client.ping()
        return HttpResponse("Redis connection successful")
    except Exception as e:
        return HttpResponse(f"Redis connection failed: {str(e)}")

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_threat_feeds_view(request):
    task = update_threat_feeds.delay()
    return Response({"message": "Threat feed update task started", "task_id": str(task.id)})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_iocs(request):
    iocs = IOC.objects.all()[:100]  # Limit to 100 for performance
    data = [{"type": ioc.ioc_type, "value": ioc.value} for ioc in iocs]
    return Response(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_iocs(request):
    value = request.query_params.get('value', '')
    iocs = IOC.objects.filter(value__icontains=value)[:100]
    data = [{"type": ioc.ioc_type, "value": ioc.value} for ioc in iocs]
    return Response(data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_alerts_view(request):
    task = generate_alerts.delay()
    return Response({"message": "Alert generation task started", "task_id": str(task.id)})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_alerts(request):
    alerts = Alert.objects.all().order_by('-created_at')[:100]
    data = [{"id": alert.id, "title": alert.title, "severity": alert.severity} for alert in alerts]
    return Response(data)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def run_siem_test(request):
    try:
        call_command('test_siem')
        return Response({"message": "SIEM test completed successfully"})
    except Exception as e:
        return Response({"error": str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def run_ml_anomaly_detection(request):
    task = periodic_ml_anomaly_detection.delay()
    return Response({"message": "ML anomaly detection task started", "task_id": str(task.id)})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recent_security_events(request):
    events = SecurityEvent.objects.order_by('-timestamp')[:10]  # Get the 10 most recent events
    serializer = SecurityEventSerializer(events, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_anomalies(request):
    anomalies = ProcessedData.objects.filter(anomaly_detected=True)[:100]  # Limit to 100 for performance
    serializer = ProcessedDataSerializer(anomalies, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_anomaly_details(request, anomaly_id):
    try:
        anomaly = ProcessedData.objects.get(id=anomaly_id)
        security_event = anomaly.security_event
        data = {
            'id': anomaly.id,
            'event_type': security_event.event_type,
            'timestamp': security_event.timestamp,
            'risk_score': anomaly.risk_score,
            'source_ip': security_event.source_ip,
            'destination_ip': security_event.destination_ip,
            'description': security_event.description,
            'raw_data': security_event.raw_data
        }
        return Response(data)
    except ProcessedData.DoesNotExist:
        return Response({'error': 'Anomaly not found'}, status=status.HTTP_404_NOT_FOUND)