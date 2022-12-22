from .base import *  # noqa

# GENERAL
DEBUG = False

# LOGGING
LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {"verbose": {"format": "%(levelname)s %(asctime)s %(module)s " "%(process)d %(thread)d %(message)s"}},
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        }
    },
    "root": {"level": "DEBUG", "handlers": ["console"]},
    "loggers": {
        'django.request': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        "django.db.backends": {
            "level": "DEBUG",
            "handlers": ["console"],
            "propagate": False,
        },
        "django.security.DisallowedHost": {
            "level": "ERROR",
            "handlers": ["console"],
            "propagate": False,
        },
        'parso.python.diff': {
            'level': 'INFO',
            'handlers': ['console'],
            'propagate': False,
        },
    },
}
