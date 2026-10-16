"""
Dev-only settings using SQLite (no PostgreSQL or Redis needed).
Run with: DJANGO_SETTINGS_MODULE=config.settings.dev manage.py runserver
"""
from .base import *  # noqa

DEBUG = True
ALLOWED_HOSTS = ['*']

# Use SQLite so no DB install is needed for local dev
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Disable Redis/Channels for simple dev run
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# No Celery broker needed in dev
CELERY_TASK_ALWAYS_EAGER = True

CORS_ALLOW_ALL_ORIGINS = True

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
