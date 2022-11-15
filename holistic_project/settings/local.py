import os

from .base import *  # noqa: F401,F403

# Django Settings
# =============================================================

SECRET_KEY = 'django-insecure-q(vd70m6c#^$mls(1e*q7*x=7s^w5$&2a)yn+tslas%((tz4_1'
DEBUG = True

ALLOWED_HOSTS = ['*']

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': os.environ.get('DB_HOST', 'postgres'),
        'NAME': os.environ.get('DB_NAME', 'studi_holistik'),
        'USER': os.environ.get('DB_USER', 'studi_holistik'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}
