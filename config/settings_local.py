import os

from config.settings import BASE_DIR

DEBUG = True
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    },
    'journals': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / os.path.join(BASE_DIR, 'jornal.sqlite3'),
    },
}

STATIC_URL = '/static/'
STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)

MEDIA_URL = 'media/'
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

INTERNAL_IPS = [
    "127.0.0.1",
]