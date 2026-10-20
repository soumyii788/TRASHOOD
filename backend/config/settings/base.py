"""
Base settings shared across all environments.
"""
import os
from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# -------------------------------------------------------------------
# Paths
# -------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # backend/

# -------------------------------------------------------------------
# Security
# -------------------------------------------------------------------
SECRET_KEY = os.environ.get('SECRET_KEY', 'change-me-in-production')
DEBUG = False
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# -------------------------------------------------------------------
# Installed Apps
# -------------------------------------------------------------------
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'channels',
    'drf_yasg',
]

LOCAL_APPS = [
    'apps.accounts',
    'apps.catalog',
    'apps.customers',
    'apps.notifications',
    'apps.pickups',
    'apps.tracking',
    'apps.wallet',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# -------------------------------------------------------------------
# Middleware
# -------------------------------------------------------------------
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

ROOT_URLCONF = 'config.urls'

# -------------------------------------------------------------------
# Templates
# -------------------------------------------------------------------
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

# -------------------------------------------------------------------
# ASGI / WSGI
# -------------------------------------------------------------------
ASGI_APPLICATION = 'config.asgi.application'
WSGI_APPLICATION = 'config.wsgi.application'

# -------------------------------------------------------------------
# Database – overridden per environment
# -------------------------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'scrap_market_db'),
        'USER': os.environ.get('DB_USER', 'scrapi_admin'),
        'PASSWORD': os.environ.get('DB_PASS', ''),
        'HOST': os.environ.get('DB_HOST', 'db'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# -------------------------------------------------------------------
# Cache (Redis)
# -------------------------------------------------------------------
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://redis:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
    }
}

# -------------------------------------------------------------------
# Channels (WebSockets)
# -------------------------------------------------------------------
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [os.environ.get('REDIS_URL', 'redis://redis:6379/1')],
        },
    },
}

# -------------------------------------------------------------------
# Celery
# -------------------------------------------------------------------
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://redis:6379/0')
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'

# -------------------------------------------------------------------
# Password validation
# -------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# -------------------------------------------------------------------
# Custom user model
# -------------------------------------------------------------------
AUTH_USER_MODEL = 'accounts.User'

# -------------------------------------------------------------------
# Internationalisation
# -------------------------------------------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# -------------------------------------------------------------------
# Static & Media
# -------------------------------------------------------------------
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'mediafiles'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# -------------------------------------------------------------------
# Marketplace
# -------------------------------------------------------------------
COLLECTOR_COMMISSION_RATE = os.environ.get('COLLECTOR_COMMISSION_RATE', '0.10')

# -------------------------------------------------------------------
# JWT
# -------------------------------------------------------------------
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=12),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# -------------------------------------------------------------------
# DRF
# -------------------------------------------------------------------
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# -------------------------------------------------------------------
# CORS
# -------------------------------------------------------------------
CORS_ALLOW_ALL_ORIGINS = False  # Tighten in production.py

# -------------------------------------------------------------------
# Swagger / drf-yasg
# -------------------------------------------------------------------
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
        }
    }
}
