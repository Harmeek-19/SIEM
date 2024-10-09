from django.apps import AppConfig

class DataProcessingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'data_processing'

    def ready(self):
        import data_processing.signals  # noqa
        import data_processing.tasks  # noqa