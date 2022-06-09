from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class ResponseChoices(TextChoices):
    CUSTOM = 'CUSTOM', _('Custom Response')
    PROXY_CURRENT = 'PROXY_CURRENT', _('Proxy Specific URL')
    PROXY_GLOBAL = 'PROXY_GLOBAL', _('Global Proxy')


class HTTPMethods(TextChoices):
    GET = 'GET', 'GET'
    POST = 'POST', 'POST'
    PUT = 'PUT', 'PUT'
    PATCH = 'PATCH', 'PATCH'
    DELETE = 'DELETE', 'DELETE'
    HEAD = 'HEAD', 'HEAD'
    OPTIONS = 'OPTIONS', 'OPTIONS'


class BodyFormat(TextChoices):
    JSON = 'JSON', 'JSON'
    XML = 'XML', 'XML'
    PLAIN_TEXT = 'PLAIN_TEXT', 'Text'
