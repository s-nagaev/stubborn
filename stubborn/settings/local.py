from typing import List

from .base import *  # noqa

# GENERAL
DEBUG = True
ALLOWED_HOSTS = ['*']

# APPS
# http://whitenoise.evans.io/en/latest/django.html#using-whitenoise-in-development
INSTALLED_APPS: List[str] = ['django_extensions'] + INSTALLED_APPS  # noqa F405

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} ({module}) \t {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        }
    },
    'root': {'level': 'INFO', 'handlers': ['console']},
    'loggers': {
        'apps': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'django.request': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'django.db.backends': {
            'level': 'INFO',
            'handlers': ['console'],
            'propagate': False,
        },
        'django.security.DisallowedHost': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'parso.python.diff': {
            'level': 'INFO',
            'handlers': ['console'],
            'propagate': False,
        },
    },
}
