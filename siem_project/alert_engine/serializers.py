from rest_framework import serializers
from .models import Alert, AlertRule, AlertNotification

class AlertRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlertRule
        fields = ['id', 'name', 'description', 'condition', 'severity', 'enabled']

class AlertSerializer(serializers.ModelSerializer):
    rule = AlertRuleSerializer(read_only=True)
    rule_id = serializers.PrimaryKeyRelatedField(
        queryset=AlertRule.objects.all(), 
        source='rule', 
        write_only=True
    )

    class Meta:
        model = Alert
        fields = ['id', 'rule', 'rule_id', 'triggered_at', 'resolved_at', 'status', 'severity']
        read_only_fields = ['triggered_at']

class AlertNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        unique_together = ('user', 'severity_level')