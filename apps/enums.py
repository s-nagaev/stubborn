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


class Lifecycle(TextChoices):
    BEFORE_REQUEST = 'before', 'Before request processed'
    AFTER_REQUEST = 'after_req', 'After request processed'
    AFTER_RESPONSE = 'after_resp', 'After response returned'


class Action(TextChoices):
    WAIT = 'wait', 'Wait'
    WEBHOOK = 'webhook', 'Webhook'


class TeamChoices(TextChoices):
    PUBLIC = 'public', 'Public'
    PRIVATE = 'private', 'Private'


class InviterChoices(TextChoices):
    OWNER = 'owner', 'Owner'
    EVERYBODY = 'everybody', 'Everybody'
