from django.urls import path, include
from rest_framework.routers import DefaultRouter

from threat_intelligence import views
from .views import IOCViewSet, ThreatFeedViewSet

router = DefaultRouter()
router.register(r'iocs', IOCViewSet)
router.register(r'threat-feeds', ThreatFeedViewSet)

urlpatterns = [
    path('', include(router.urls)),
        path('iocs/', views.ioc_list, name='ioc_list'),
]