import os.path

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator, URLValidator
from django.db import models
from django.db.models import UniqueConstraint
from django.utils.translation import gettext as _
from rest_framework.renderers import BaseRenderer, JSONRenderer

from apps.enums import Action, BodyFormat, HTTPMethods, Lifecycle, ResponseChoices
from apps.renderers import SimpleTextRenderer, TextToXMLRenderer
from apps.utils import is_json, str_to_dom_document


class BaseStubModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created at')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated at')

    class Meta:
        abstract = True


class AbstractHTTPObject(models.Model):
    headers = models.JSONField(verbose_name='Headers', default=dict, blank=True)
    body = models.TextField(verbose_name='Response Body', null=True, blank=True)
    description = models.CharField(max_length=30, verbose_name='Short Description', null=True, blank=True)
    format = models.CharField(max_length=10, choices=BodyFormat.choices, default=BodyFormat.PLAIN_TEXT.value,
                              verbose_name='Format')

    class Meta:
        abstract = True

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
        if self.is_json_format and not is_json(self.body):
            raise ValidationError(_('The body is not a valid JSON.'), code='invalid')
        if self.format == BodyFormat.XML.value and not str_to_dom_document(self.body):
            raise ValidationError(_('The body is not a valid XML.'), code='invalid')


class Application(BaseStubModel):
    name = models.CharField(max_length=50, verbose_name='Name', null=False)
    description = models.TextField(verbose_name='Description', null=True, blank=True)
    slug = models.SlugField(verbose_name='Slug', allow_unicode=True, null=False, unique=True)
    owner = models.ForeignKey(User, verbose_name='Application Owner', null=True, blank=True, on_delete=models.CASCADE,
                              related_name='applications')

    class Meta:
        verbose_name = 'application'
        verbose_name_plural = 'applications'

    def __str__(self) -> str:
        """Object's string representation.

        Returns:
            String representation.
        """
        return f'{self.name}'


class ResponseStub(AbstractHTTPObject, BaseStubModel):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='responses')
    status_code = models.PositiveSmallIntegerField(verbose_name='Status code', null=False)
    creator = models.ForeignKey(User, verbose_name='Created by', null=True, blank=True, on_delete=models.SET_NULL,
                                related_name='responses')

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


class RequestStub(AbstractHTTPObject, BaseStubModel):
    name = models.CharField(max_length=30, null=True, blank=True)
    uri = models.URLField(verbose_name='URI', null=False)
    query_params = models.JSONField(verbose_name='Query Params', default=dict, blank=True)
    method = models.CharField(
        max_length=10,
        choices=HTTPMethods.choices,
        default=HTTPMethods.GET.value,
        verbose_name='HTTP Method',
    )

    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='request')
    creator = models.ForeignKey(User, verbose_name='Created by', null=True, blank=True, on_delete=models.SET_NULL,
                                related_name='request')

    class Meta:
        verbose_name = 'request'
        verbose_name_plural = 'requests'

    def __str__(self) -> str:
        """Object's string representation.

        Returns:
            String representation.
        """
        return f'{self.method} {self.uri}'


class ResourceStub(BaseStubModel):
    response_type = models.CharField(max_length=30, choices=ResponseChoices.choices,
                                     default=ResponseChoices.CUSTOM.value, verbose_name='Response Type')
    slug = models.SlugField(verbose_name='Slug', allow_unicode=True, null=False)
    tail = models.CharField(verbose_name='URL Tail', max_length=120, default='', blank=True)
    response = models.ForeignKey(ResponseStub, verbose_name='Response', related_name='resources',
                                 on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField(verbose_name='Description', null=True, blank=True)
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='resources')
    method = models.CharField(max_length=10, choices=HTTPMethods.choices, default=HTTPMethods.GET.value,
                              verbose_name='HTTP Method', null=True, blank=True)
    proxy_destination_address = models.URLField(verbose_name='Proxy to', default=None, blank=True, null=True)
    creator = models.ForeignKey(User, verbose_name='Created by', null=True, blank=True, on_delete=models.SET_NULL,
                                related_name='resources')

    class Meta:
        verbose_name = 'resource'
        verbose_name_plural = 'resources'
        unique_together = ('slug', 'method', 'tail')

    def __str__(self) -> str:
        """Object's string representation.

        Returns:
            String representation.
        """
        return f'{self.slug}'

    def clean(self) -> None:
        if not self.response and not self.proxy_destination_address:
            raise ValidationError(_('The resource stub must be created with the response or proxy instruction.'),
                                  code='invalid')
        if self.tail:
            validator = URLValidator(message=_('Wrong URL tail format.'))
            url = os.path.join('https://test.com', self.slug, self.tail)
            validator(url)


class ResourceHook(BaseStubModel):
    lifecycle = models.CharField(max_length=10, choices=Lifecycle.choices, default=Lifecycle.AFTER_REQUEST.value)
    action = models.CharField(max_length=10, choices=Action.choices, default=Action.WAIT.value)
    timeout = models.PositiveSmallIntegerField(
        verbose_name='Response Timeout',
        default=0,
        validators=[
            MaxValueValidator(100),
        ],
    )
    request = models.ForeignKey(RequestStub, on_delete=models.deletion.CASCADE, blank=True, null=True)
    resource = models.ForeignKey(ResourceStub, on_delete=models.deletion.CASCADE, blank=True, null=True)
    order = models.PositiveSmallIntegerField(
        verbose_name='Order',
        default=1,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(100),
        ],
    )

    def clean(self) -> None:
        if self.action == Action.WAIT and not self.timeout:
            raise ValidationError(_("'timeout' field is required if 'Action.WAIT' used"), code='invalid')

        if self.action == Action.WEBHOOK and not self.request:
            raise ValidationError(_("'request' field is required if 'Action.WEBHOOK' used"), code='invalid',)

    class Meta:
        verbose_name = 'hook'
        verbose_name_plural = 'hooks'
        ordering = ('order', )
        constraints = [
            UniqueConstraint(
                fields=["order", "lifecycle", "resource", ],
                name="unique_order_per_resource",
            ),
        ]


class RequestLog(models.Model):
    url = models.URLField(verbose_name='URL Called', default=None, null=True, blank=True)
    params = models.JSONField(verbose_name='Query Params', default=dict, null=True, blank=True)
    request_body = models.TextField(verbose_name='Request Body', null=True, blank=True)
    request_headers = models.JSONField(verbose_name='Headers', default=dict, null=True, blank=True)
    response_body = models.TextField(verbose_name='Request Body', null=True, blank=True)
    response_headers = models.JSONField(verbose_name='Headers', default=dict, null=True, blank=True)
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='logs')
    resource = models.ForeignKey(ResourceStub, null=True, blank=True, on_delete=models.SET_NULL, related_name='logs')
    response = models.ForeignKey(ResponseStub, verbose_name='Response', null=True, blank=True,
                                 on_delete=models.SET_NULL, related_name='logs')
    ipaddress = models.GenericIPAddressField(verbose_name='Remote IP', default='127.0.0.1')
    x_real_ip = models.GenericIPAddressField(verbose_name='X-REAL-IP', default='127.0.0.1', null=True, blank=True)
    proxied = models.BooleanField(verbose_name='Proxied', default=False, null=False, blank=False)
    destination_url = models.URLField(verbose_name='Proxied to', default=None, null=True, blank=True)
    status_code = models.IntegerField(verbose_name='Status Code', null=True, blank=True)
    method = models.CharField(verbose_name='Method', max_length=10, default=None, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Received at')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated at')

    class Meta:
        verbose_name = 'request log'
        verbose_name_plural = 'request logs'

    def __str__(self) -> str:
        """Object's string representation.

        Returns:
            String representation.
        """
        method = f'{self.method.upper()} ' if self.method else ''
        return f'{method}{self.url}'

    @property
    def response_format(self) -> str:
        content_type = self.response_headers.get('Content-Type')
        if 'json' in content_type:
            return BodyFormat.JSON
        if 'xml' in content_type:
            return BodyFormat.XML
        return BodyFormat.PLAIN_TEXT
