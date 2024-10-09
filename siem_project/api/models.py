# api/models.py
from django.db import models


class Log(models.Model):
    source = models.CharField(max_length=100)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

