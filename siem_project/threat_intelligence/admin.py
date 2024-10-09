from django.contrib import admin
from .models import ThreatFeed, IOC

@admin.register(ThreatFeed)
class ThreatFeedAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'last_updated')
    search_fields = ('name', 'url')

@admin.register(IOC)
class IOCAdmin(admin.ModelAdmin):
    list_display = ('ioc_type', 'value', 'source', 'threat_type', 'last_seen')
    list_filter = ('ioc_type', 'source', 'threat_type')
    search_fields = ('value', 'tags')
    date_hierarchy = 'last_seen'



