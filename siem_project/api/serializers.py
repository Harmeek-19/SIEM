# api/serializers.py

from rest_framework import serializers
from alert_engine.models import Alert
from .models import Log
from data_processing.models import SecurityEvent
from data_processing.serializers import ProcessedDataSerializer
from alert_engine.serializers import  AlertSerializer


# api/serializers.py

from rest_framework import serializers
from data_processing.models import SecurityEvent

from rest_framework import serializers
from data_processing.models import SecurityEvent

class SecurityEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecurityEvent
        fields = ['id', 'event_id', 'event_type', 'source_ip', 'destination_ip', 'timestamp', 'severity', 'description', 'raw_data', 'reported_by']
        read_only_fields = ['id', 'reported_by']

    def validate(self, data):
        # Add any custom validation here
        if data.get('severity') not in [choice[0] for choice in SecurityEvent.SEVERITY_LEVELS]:
            raise serializers.ValidationError({"severity": "Invalid severity level"})
        
        if data.get('event_type') not in [choice[0] for choice in SecurityEvent.EVENT_TYPES]:
            raise serializers.ValidationError({"event_type": "Invalid event type"})
        
        return data


class LogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log
        fields = '__all__'

# Dummy serializers for auth views
class LogoutSerializer(serializers.Serializer):
    pass

class VerifyEmailSerializer(serializers.Serializer):
    key = serializers.CharField()