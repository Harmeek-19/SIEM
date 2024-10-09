from itertools import count
from rest_framework import viewsets, permissions, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils import timezone
from datetime import timedelta
from celery.result import AsyncResult
from django.db.models import Count
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils import timezone
from datetime import timedelta

from .models import SecurityEvent, ProcessedData, AggregatedMetric, Report
from alert_engine.models import Alert
from .serializers import SecurityEventSerializer, ProcessedDataSerializer, AggregatedMetricSerializer, ReportSerializer

from .models import SecurityEvent, ProcessedData, AggregatedMetric, Report
from .serializers import SecurityEventSerializer, ProcessedDataSerializer, AggregatedMetricSerializer, ReportSerializer
from .tasks import collect_logs_task, manage_log_collection
from .utils import generate_summary_report

# Existing ViewSets
class SecurityEventViewSet(viewsets.ModelViewSet):
    queryset = SecurityEvent.objects.all()
    serializer_class = SecurityEventSerializer
    authentication_classes = [JWTAuthentication, TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SecurityEvent.objects.filter(reported_by=self.request.user).order_by('-timestamp')

    def perform_create(self, serializer):
        serializer.save(reported_by=self.request.user)


class ProcessedDataListView(viewsets.ReadOnlyModelViewSet):
    queryset = ProcessedData.objects.all()
    serializer_class = ProcessedDataSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]


class AggregatedMetricListView(viewsets.ReadOnlyModelViewSet):
    queryset = AggregatedMetric.objects.all()
    serializer_class = AggregatedMetricSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = AggregatedMetric.objects.filter(created_by=self.request.user)
        metric_name = self.request.query_params.get('metric_name')
        start_time = self.request.query_params.get('start_time')
        end_time = self.request.query_params.get('end_time')

        if metric_name:
            queryset = queryset.filter(metric_name=metric_name)
        if start_time:
            queryset = queryset.filter(start_time__gte=start_time)
        if end_time:
            queryset = queryset.filter(end_time__lte=end_time)

        return queryset

# Log Collection Endpoints
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def initiate_log_collection(request):
    user_id = request.user.id
    task = collect_logs_task.delay(user_id)
    return Response({"message": "Log collection initiated", "task_id": str(task.id)})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def stop_log_collection(request):
    task_id = request.data.get('task_id')
    if not task_id:
        return Response({"error": "Task ID is required"}, status=400)
    
    try:
        result = manage_log_collection.delay('stop', task_id)
        return Response({
            "message": "Log collection stop initiated",
            "result": str(result)
        })
    except Exception as e:
        return Response({
            "error": f"Failed to stop log collection: {str(e)}"
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_task_status(request, task_id):
    task_result = AsyncResult(task_id)
    if task_result.successful():
        return Response({
            "status": "completed",
            "result": task_result.result
        })
    elif task_result.failed():
        return Response({
            "status": "failed",
            "error": str(task_result.result)
        })
    elif task_result.status == 'PENDING':
        return Response({"status": "pending"})
    else:
        return Response({"status": task_result.status})

import json
from django.core.serializers.json import DjangoJSONEncoder

# Report Generation
import json
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.serializers.json import DjangoJSONEncoder
from .models import Report, SecurityEvent
from alert_engine.models import Alert
from .serializers import ReportSerializer
from django.core.mail import send_mail
from django.conf import settings

class ReportViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Report.objects.all().order_by('-created_at')
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def generate(self, request):
        report_type = request.data.get('report_type', 'daily')
        send_email = request.data.get('send_email', False)

        if report_type not in dict(Report.REPORT_TYPES):
            return Response({'error': 'Invalid report type'}, status=status.HTTP_400_BAD_REQUEST)
        
        end_date = timezone.now()
        if report_type == 'daily':
            start_date = end_date - timedelta(days=1)
        elif report_type == 'weekly':
            start_date = end_date - timedelta(weeks=1)
        else:
            return Response({'error': 'Invalid report type'}, status=status.HTTP_400_BAD_REQUEST)

        events = SecurityEvent.objects.filter(timestamp__range=[start_date, end_date])
        alerts = Alert.objects.filter(created_at__range=[start_date, end_date])

        report_data = {
            'report_type': report_type,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'total_events': events.count(),
            'total_alerts': alerts.count(),
            'event_types': list(events.values('event_type').annotate(count=Count('event_type'))),
            'alert_severities': list(alerts.values('severity').annotate(count=Count('severity'))),
        }

        report = Report.objects.create(
            report_type=report_type,
            date_range=json.dumps({'start_date': start_date.isoformat(), 'end_date': end_date.isoformat()}),
            content=json.dumps(report_data, cls=DjangoJSONEncoder)
        )

        if send_email:
            self.send_report_email(request.user, report)

        return Response(self.get_serializer(report).data, status=status.HTTP_201_CREATED)

    def send_report_email(self, user, report):
        subject = f"SIEM Report - {report.report_type.capitalize()}"
        message = f"""
        Hello {user.username},

        Your {report.report_type} SIEM report is ready.

        Report Details:
        - Type: {report.report_type}
        - Period: {json.loads(report.date_range)['start_date']} to {json.loads(report.date_range)['end_date']}
        - Total Events: {json.loads(report.content)['total_events']}
        - Total Alerts: {json.loads(report.content)['total_alerts']}

        Please log in to the SIEM dashboard to view the full report.

        Best regards,
        Your SIEM Team
        """
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [user.email]

        try:
            send_mail(subject, message, from_email, recipient_list)
        except Exception as e:
            # Log the error, but don't prevent report generation
            print(f"Failed to send email: {str(e)}")