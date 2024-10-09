from rest_framework import serializers
from .models import IOC, ThreatFeed

class IOCSerializer(serializers.ModelSerializer):
    class Meta:
        model = IOC
        fields = '__all__'

class ThreatFeedSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThreatFeed
        fields = '__all__'