from django.db import models
from django.utils import timezone
from django.db import transaction
from django.db import models
from django.conf import settings
class ThreatFeed(models.Model):
    name = models.CharField(max_length=100)
    url = models.URLField()
    last_updated = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name

class IOC(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='iocs')
    ioc_type = models.CharField(max_length=50)
    value = models.TextField()
    source = models.CharField(max_length=100)
    first_seen = models.DateTimeField(default=timezone.now)
    last_seen = models.DateTimeField(default=timezone.now)
    threat_type = models.CharField(max_length=100)
    confidence = models.FloatField(default=0.5)
    tags = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    external_reference = models.URLField(blank=True, null=True)

    class Meta:
        unique_together = ('ioc_type', 'value')

    @classmethod
    def bulk_create_or_update(cls, ioc_list):
        with transaction.atomic():
            existing_iocs = {(ioc.ioc_type, ioc.value): ioc for ioc in cls.objects.all()}
            
            to_create = []
            to_update = []
            
            for item in ioc_list:
                key = (item['ioc_type'], item['value'])
                if key in existing_iocs:
                    ioc = existing_iocs[key]
                    for field, value in item['defaults'].items():
                        setattr(ioc, field, value)
                    to_update.append(ioc)
                else:
                    to_create.append(cls(ioc_type=item['ioc_type'], value=item['value'], **item['defaults']))
            
            cls.objects.bulk_create(to_create)
            if to_update:
                cls.objects.bulk_update(to_update, ['source', 'last_seen', 'threat_type', 'confidence', 'tags', 'description', 'external_reference'])
            
            return len(to_create), len(to_update)

    def __str__(self):
        return f"{self.ioc_type}: {self.value}"