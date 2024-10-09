# authentication/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    ROLES = (
        ('admin', 'Admin'),
        ('analyst', 'Analyst'),
    )
    role = models.CharField(max_length=10, choices=ROLES, default='analyst')
    is_verified = models.BooleanField(default=False)
    groups = models.ManyToManyField(
            'auth.Group',
            related_name='customuser_set',
            blank=True,
            help_text='The groups this user belongs to.',
            verbose_name='groups'
        )
    user_permissions = models.ManyToManyField(
            'auth.Permission',
            related_name='customuser_permissions_set',
            blank=True,
            help_text='Specific permissions for this user.',
            verbose_name='user permissions'
        )