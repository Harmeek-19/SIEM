from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SecurityEventViewSet, 
    ProcessedDataListView, 
    AggregatedMetricListView,
    ReportViewSet,
    initiate_log_collection,
    stop_log_collection,
    check_task_status,
)

router = DefaultRouter()
router.register(r'security-events', SecurityEventViewSet, basename='security-events')
router.register(r'processed-data', ProcessedDataListView)
router.register(r'aggregated-metrics', AggregatedMetricListView)
router.register(r'reports', ReportViewSet, basename='reports')

urlpatterns = [
    path('', include(router.urls)),
    path('initiate-log-collection/', initiate_log_collection, name='initiate_log_collection'),
    path('stop-log-collection/', stop_log_collection, name='stop_log_collection'),
    path('check-task-status/<str:task_id>/', check_task_status, name='check_task_status'),
]