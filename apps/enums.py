from django.db.models import TextChoices


class HTTPMethods(TextChoices):
    GET = 'GET', 'GET'
    POST = 'POST', 'POST'
    PUT = 'PUT', 'PUT'
    PATCH = 'PATCH', 'PATCH'
    DELETE = 'DELETE', 'DELETE'


class BodyFormat(TextChoices):
    JSON = 'JSON', 'JSON'
    XML = 'XML', 'XML'
    PLAIN_TEXT = 'PLAIN_TEXT', 'Plain Text'
