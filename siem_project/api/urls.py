from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SecurityEventViewSet, 
    ProcessedDataViewSet, 
    LogViewSet, 
    CorrelationViewSet, 
    CustomTokenObtainPairView,
    get_anomaly_details,
    test_redis, 
    run_siem_test,
    update_threat_feeds_view,
    get_iocs,
    search_iocs,
    generate_alerts_view,
    get_alerts,
    run_ml_anomaly_detection,
    recent_security_events,
    get_anomalies
)
from rest_framework_simplejwt.views import TokenRefreshView

router = DefaultRouter()
router.register(r'security-events', SecurityEventViewSet, basename='security-events')
router.register(r'processed-data', ProcessedDataViewSet)
router.register(r'logs', LogViewSet)
router.register(r'correlation', CorrelationViewSet, basename='correlation')

urlpatterns = [
    path('', include(router.urls)),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('test-redis/', test_redis, name='test_redis'),
    path('run-siem-test/', run_siem_test, name='run-siem-test'),
    path('threat-feeds/update/', update_threat_feeds_view, name='update_threat_feeds'),
    path('iocs/', get_iocs, name='get_iocs'),
    path('iocs/search/', search_iocs, name='search_iocs'),
    path('alerts/generate/', generate_alerts_view, name='generate_alerts'),
    path('alerts/', get_alerts, name='get_alerts'),
    path('run-ml-anomaly-detection/', run_ml_anomaly_detection, name='run_ml_anomaly_detection'),
    path('security-events/recent/', recent_security_events, name='recent_security_events'),
    path('anomalies/', get_anomalies, name='get_anomalies'),
    path('anomalies/<int:anomaly_id>/', get_anomaly_details, name='get_anomaly_details'),
]