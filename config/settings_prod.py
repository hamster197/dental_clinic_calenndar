import os
import environ

from config.settings import BASE_DIR

env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

DEBUG = env.bool('DEBUG')

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

DATABASES = {
    'default': {
        'ENGINE': os.environ.get('POSTGRES_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.environ.get('POSTGRES_DB', BASE_DIR / 'db.sqlite3'),
        'USER': os.environ.get('POSTGRES_USER', 'user'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'password'),
        'HOST': os.environ.get('POSTGRES_HOST', 'localhost'),
        'PORT': os.environ.get('POSTGRES_PORT', '5432'),
    },
    'journals': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / os.path.join(BASE_DIR, 'jornal.sqlite3'),
    },
}

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn=env('SENTY_URL'),
    integrations=[DjangoIntegration()],
    send_default_pii=True
)

# SECURE MODE SETTINGS
from .settings_secure import *
