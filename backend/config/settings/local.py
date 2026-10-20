"""
Local development settings.
Debug=True, uses local PostgreSQL (or SQLite fallback).
"""
from .base import *  # noqa

DEBUG = True

ALLOWED_HOSTS = ['*']

# Override DB to a local Postgres for dev convenience
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'scrap_market_db',
        'USER': 'scrapi_admin',
        'PASSWORD': 'secure_password123',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

CORS_ALLOW_ALL_ORIGINS = True

# Run Celery tasks inline when Redis is not running locally
CELERY_TASK_ALWAYS_EAGER = True
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
