from .base import *  # noqa

# GENERAL
DEBUG = True
ALLOWED_HOSTS = ['*']

# APPS
# http://whitenoise.evans.io/en/latest/django.html#using-whitenoise-in-development
INSTALLED_APPS = ['whitenoise.runserver_nostatic', 'django_extensions'] + INSTALLED_APPS  # noqa F405

