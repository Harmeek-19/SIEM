from django.db import models
from django.conf import settings
from django.utils import timezone

class AlertRule(models.Model):
    SEVERITY_CHOICES = [
        (1, 'Low'),
        (2, 'Medium'),
        (3, 'High'),
        (4, 'Critical'),
    ]
    name = models.CharField(max_length=100)
    description = models.TextField()
    condition = models.TextField()
    severity = models.IntegerField(choices=SEVERITY_CHOICES, default=2)
    enabled = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    

class Alert(models.Model):
    SEVERITY_CHOICES = [
        (1, 'Low'),
        (2, 'Medium'),
        (3, 'High'),
        (4, 'Critical'),
    ]
    title = models.CharField(max_length=200, default='Alert')
    description = models.TextField(default='No description provided')
    created_at = models.DateTimeField(default=timezone.now)
    severity = models.IntegerField(choices=SEVERITY_CHOICES, default=2)
    rule = models.ForeignKey(AlertRule, on_delete=models.CASCADE)
    triggered_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, default='New')


    def __str__(self):
        return self.title

class AlertNotification(models.Model):
    SEVERITY_CHOICES = [
        (1, 'Low'),
        (2, 'Medium'),
        (3, 'High'),
        (4, 'Critical'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    severity_level = models.IntegerField(choices=SEVERITY_CHOICES)
    email_notification = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_severity_level_display()} alerts"