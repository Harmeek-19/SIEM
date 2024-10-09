from django.db import transaction

def start_scheduler(sender, **kwargs):
    # Import models here to avoid circular imports
    from django_celery_beat.models import IntervalSchedule, PeriodicTask

    @transaction.atomic
    def initialize_scheduler():
        schedule, _ = IntervalSchedule.objects.get_or_create(
            every=60,
            period=IntervalSchedule.SECONDS,
        )
        PeriodicTask.objects.get_or_create(
            interval=schedule,
            name='Alert Engine Periodic Task',
            task='alert_engine.tasks.process_alerts',
        )

    # Use transaction.on_commit to ensure the database is ready
    transaction.on_commit(initialize_scheduler)