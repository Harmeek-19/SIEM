import json
from channels.generic.websocket import AsyncWebsocketConsumer
from data_processing.models import SecurityEvent, ProcessedData
from django.db.models import Count
from asgiref.sync import sync_to_async

class DashboardConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        action = text_data_json['action']

        if action == 'get_recent_events':
            events = await self.get_recent_events()
            await self.send(text_data=json.dumps({
                'action': 'recent_events',
                'events': events
            }))
        elif action == 'get_event_summary':
            summary = await self.get_event_summary()
            await self.send(text_data=json.dumps({
                'action': 'event_summary',
                'summary': summary
            }))

    @sync_to_async
    def get_recent_events(self):
        events = SecurityEvent.objects.order_by('-timestamp')[:10]
        return [{'id': e.id, 'event_type': e.event_type, 'severity': e.severity, 'timestamp': e.timestamp.isoformat()} for e in events]

    @sync_to_async
    def get_event_summary(self):
        summary = SecurityEvent.objects.values('event_type').annotate(count=Count('id'))
        return list(summary)