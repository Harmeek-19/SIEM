# data_processing/serializers.py

from rest_framework import serializers
from .models import SecurityEvent, ProcessedData, AggregatedMetric

class SecurityEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecurityEvent
        fields = '__all__'
        ref_name = "DataProcessing_SecurityEventSerializer"
        read_only_fields = ('reported_by',)
    def create(self, validated_data):
        # Ensure the event_id is unique
        event_id = validated_data.get('event_id')
        existing_event = SecurityEvent.objects.filter(event_id=event_id).first()
        if existing_event:
            return existing_event
        return SecurityEvent.objects.create(**validated_data)
    def validate(self, data):
        # Add any additional validation here
        return data

class ProcessedDataSerializer(serializers.ModelSerializer):
    event_type = serializers.CharField(source='security_event.event_type')
    timestamp = serializers.DateTimeField(source='security_event.timestamp')

    class Meta:
        model = ProcessedData
        fields = ['id', 'event_type', 'timestamp', 'risk_score', 'anomaly_detected']

        
class AggregatedMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = AggregatedMetric
        fields = '__all__'

from rest_framework import serializers
from .models import Report

class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['id', 'report_type', 'date_range', 'content', 'created_at']