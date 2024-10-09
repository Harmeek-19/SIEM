from django.apps import AppConfig

class AlertEngineConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'alert_engine'

    def ready(self):
        pass  # Remove any imports from here