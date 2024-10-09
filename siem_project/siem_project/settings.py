# File: siem_project/settings.py

import os
from pathlib import Path
from datetime import timedelta
from celery.schedules import crontab

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-7+_(4qj-kbb1w%6s80t+_-vac6qg6kt)_-y01si+i1ydzt78qv')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost 127.0.0.1 [::1]').split(' ')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'api',
    'django_celery_beat',
    'django_celery_results',
    'channels',
    'drf_yasg',
    'alert_engine',
    'data_processing',
    'authentication',
    'threat_intelligence',
    'dashboard',
    'corsheaders',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ALLOW_ALL_ORIGINS = True 

ROOT_URLCONF = 'siem_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'siem_project.wsgi.application'
ASGI_APPLICATION = 'siem_project.asgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'trinetra',
        'USER': 'postgres',
        'PASSWORD': 'toor',
        'HOST': 'localhost',  # Use 'localhost' since PostgreSQL is exposed to the host
        'PORT': '5432',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom user model
AUTH_USER_MODEL = 'authentication.CustomUser'

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/day'
    }
}

# Simple JWT settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
}

# Celery settings
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60

# Celery Beat schedule
CELERY_BEAT_SCHEDULE = {
    'update-threat-feeds': {
        'task': 'threat_intelligence.tasks.update_threat_feeds',
        'schedule': 21600.0,  # Run every 6 hours
    },
    'run-ml-anomaly-detection': {
        'task': 'data_processing.tasks.periodic_ml_anomaly_detection',
        'schedule': timedelta(minutes=30),
    },
    'generate-alerts': {
        'task': 'alert_engine.tasks.generate_alerts',
        'schedule': 300.0,  # Run every 5 minutes
    },
    'cleanup-old-iocs': {
        'task': 'threat_intelligence.tasks.cleanup_old_iocs',
        'schedule': 86400.0,  # Run daily
    },
    'delete-old-events': {
        'task': 'data_processing.tasks.delete_old_events',
        'schedule': timedelta(days=1),  # Run daily at midnight
    },
    'send-daily-alert-summary': {
        'task': 'alert_engine.tasks.send_daily_alert_summary',
        'schedule': crontab(hour=0, minute=0),  # Run daily at midnight
    },
}

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'harmeeksingh729@gmail.com'
EMAIL_HOST_PASSWORD = 'nebr cyiu kcjx mrxm'  # This is not your Gmail account password
DEFAULT_FROM_EMAIL = 'harmeeksingh729@gmail.com'
ADMIN_EMAIL = 'harmeek1929@gmail.com'

# Channels
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [(os.environ.get('REDIS_HOST', 'redis'), 6379)],
        },
    },
}

# CORS settings
CORS_ALLOW_ALL_ORIGINS = True  # For development, restrict this in production
CORS_ALLOW_CREDENTIALS = True

# Elasticsearch settings
ELASTICSEARCH_HOST = os.environ.get('ELASTICSEARCH_HOST', 'elasticsearch')
ELASTICSEARCH_PORT = int(os.environ.get('ELASTICSEARCH_PORT', 9200))

# Base URL
BASE_URL = os.environ.get('BASE_URL', 'http://localhost:8000')

# Swagger settings
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    }
}

# Test mode (set to False in production)
TEST_MODE = os.environ.get('TEST_MODE', 'True') == 'True'

# Log collection interval (in seconds)
LOG_COLLECTION_INTERVAL = int(os.environ.get('LOG_COLLECTION_INTERVAL', 300))

APPEND_SLASH = True