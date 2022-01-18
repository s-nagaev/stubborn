import os

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext as _
from rest_framework.renderers import BaseRenderer, JSONRenderer

from apps.enums import BodyFormat, HTTPMethods
from apps.renderers import SimpleTextRenderer, TextToXMLRenderer
from apps.utils import str_to_dict, str_to_dom_document


class Application(models.Model):
    name = models.CharField(max_length=50, verbose_name='Name', null=False)
    description = models.TextField(verbose_name='Description', null=True, blank=True)
    slug = models.SlugField(verbose_name='Slug', allow_unicode=True, null=False, unique=True)
    owner = models.ForeignKey(User, verbose_name='Application Owner', null=True, blank=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'application'
        verbose_name_plural = 'applications'

    def __str__(self) -> str:
        """Object's string representation.

        Returns:
            String representation.
        """
        return f'{self.name}'


class ResponseStub(models.Model):
    status_code = models.PositiveSmallIntegerField(verbose_name='Status code', null=False)
    headers = models.JSONField(verbose_name='Headers', default=dict, blank=True)
    body = models.TextField(verbose_name='Response Body', null=True, blank=True)
    timeout = models.PositiveSmallIntegerField(verbose_name='Response Timeout', default=0)
    description = models.CharField(max_length=30, verbose_name='Short Description', null=True, blank=True)
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='responses')
    format = models.CharField(max_length=10, choices=BodyFormat.choices, default=BodyFormat.PLAIN_TEXT.value,
                              verbose_name='Format')

    class Meta:
        verbose_name = 'response'
        verbose_name_plural = 'responses'

    def __str__(self) -> str:
        """Object's string representation.

        Returns:
            String representation.
        """
        if self.description:
            return f'{self.status_code} {self.description}'
        return f'{self.status_code}'

    @property
    def renderer(self) -> BaseRenderer:
        """Return renderer for current format of response.

        Returns:
            Renderer instance.

        Raises:
            ValueError if there is no renderer connected with the current response format.
        """
        if self.format == BodyFormat.JSON.value:
            return JSONRenderer()
        if self.format == BodyFormat.XML.value:
            return TextToXMLRenderer()
        if self.format == BodyFormat.PLAIN_TEXT.value:
            return SimpleTextRenderer()
        raise ValueError(f'Not set renderer for the response body formant: {self.format}')

    @property
    def is_json_format(self) -> bool:
        """Return JSON format flag.

        Returns:
            True if the format is JSON, False otherwise.
        """
        return self.format == BodyFormat.JSON.value

    def clean(self) -> None:
        if not self.body:
            return
        if self.is_json_format and not str_to_dict(self.body):
            raise ValidationError(_('The body is not a valid JSON.'), code='invalid')
        if self.format == BodyFormat.XML.value and not str_to_dom_document(self.body):
            raise ValidationError(_('The body is not a valid XML.'), code='invalid')


class ResourceStub(models.Model):
    uri = models.SlugField(verbose_name='URI', allow_unicode=True, null=False)
    response = models.ForeignKey(ResponseStub, verbose_name='Response', related_name='resources',
                                 on_delete=models.CASCADE, null=False)
    description = models.TextField(verbose_name='Description', null=True, blank=True)
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='resources')
    method = models.CharField(max_length=10, choices=HTTPMethods.choices, default=HTTPMethods.GET.value,
                              verbose_name='HTTP Method')

    class Meta:
        verbose_name = 'resource'
        verbose_name_plural = 'resources'
        unique_together = ('uri', 'method')

    def __str__(self) -> str:
        """Object's string representation.

        Returns:
            String representation.
        """
        return f'{self.uri}'


class RequestLog(models.Model):
    params = models.JSONField(verbose_name='Query Params', default=dict, null=True, blank=True)
    request_body = models.TextField(verbose_name='Request Body', null=True, blank=True)
    request_headers = models.JSONField(verbose_name='Headers', default=dict, null=True, blank=True)
    response_body = models.TextField(verbose_name='Request Body', null=True, blank=True)
    response_headers = models.JSONField(verbose_name='Headers', default=dict, null=True, blank=True)
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='logs')
    resource = models.ForeignKey(ResourceStub, on_delete=models.CASCADE, related_name='logs')
    response = models.ForeignKey(ResponseStub, verbose_name='Response', null=True, blank=True, on_delete=models.CASCADE,
                                 related_name='logs')
    ipaddress = models.GenericIPAddressField(verbose_name='Remote IP', default='127.0.0.1')
    x_real_ip = models.GenericIPAddressField(verbose_name='X-REAL-IP', default='127.0.0.1', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Received at')

    class Meta:
        verbose_name = 'request log'
        verbose_name_plural = 'request logs'

    def __str__(self) -> str:
        """Object's string representation.

        Returns:
            String representation.
        """
        return self.url

    @property
    def url(self) -> str:
        return os.path.join(settings.DOMAIN, 'api', self.application.slug, self.resource.uri)
