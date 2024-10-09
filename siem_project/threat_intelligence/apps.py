from django.apps import AppConfig

class ThreatIntelligenceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'threat_intelligence'

    def ready(self):
        import threat_intelligence.signals  # noqa