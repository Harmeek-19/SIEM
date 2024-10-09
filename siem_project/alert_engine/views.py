from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Alert, AlertRule
from .serializers import AlertSerializer, AlertRuleSerializer

class AlertViewSet(viewsets.ModelViewSet):
    queryset = Alert.objects.all().order_by('-triggered_at')
    serializer_class = AlertSerializer
    permission_classes = [IsAuthenticated]

class AlertRuleViewSet(viewsets.ModelViewSet):
    queryset = AlertRule.objects.all()
    serializer_class = AlertRuleSerializer
    permission_classes = [IsAuthenticated]