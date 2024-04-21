import os.path
import random
import uuid

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator, URLValidator
from django.db import models
from django.db.models import UniqueConstraint
from django.utils.translation import gettext as _
from faker import Faker
from jinja2 import Template
from rest_framework.renderers import BaseRenderer, JSONRenderer

from apps.enums import Action, BodyFormat, InviterChoices, HTTPMethods, Lifecycle, ResponseChoices, TeamChoices
from apps.renderers import SimpleTextRenderer, TextToXMLRenderer
from apps.utils import is_json, str_to_dom_document


class BaseStubModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created at')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated at')

    class Meta:
        abstract = True


class AbstractHTTPObject(models.Model):
    body = models.TextField(verbose_name='Response Body', null=True, blank=True)
    description = models.CharField(max_length=30, verbose_name='Short Description', null=True, blank=True)
    format = models.CharField(
        max_length=10, choices=BodyFormat.choices, default=BodyFormat.PLAIN_TEXT.value, verbose_name='Format'
    )
    headers = models.JSONField(verbose_name='Headers', default=dict, blank=True)

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
        if self.is_json_format and not is_json(self.body_rendered):
            raise ValidationError(_('The body is not a valid JSON.'), code='invalid')
        if self.format == BodyFormat.XML.value and not str_to_dom_document(self.body_rendered):
            raise ValidationError(_('The body is not a valid XML.'), code='invalid')

    @property
    def body_rendered(self) -> str:
        """Get response body rendered with Jinja (if it contains template tags).

        Returns:
            Response body (ready to send).
        """
        if not self.body:
            return ''

        jinja_template = Template(self.body)
        return jinja_template.render(fake=Faker(), random=random)


# class Member(User):
#     User._meta.get_field('email')._unique = True
#     displayed_name = models.CharField(max_length=100, verbose_name='Displayed name', null=True, blank=True)
#     teams = models.ManyToManyField('Team', verbose_name='Teams', related_name='members')


class Application(BaseStubModel):
    description = models.TextField(verbose_name='Description', null=True, blank=True)
    name = models.CharField(max_length=50, verbose_name='Name', null=False)
    slug = models.SlugField(verbose_name='Slug', allow_unicode=True, null=False, unique=False)
    owner = models.ForeignKey(
        User,
        verbose_name='Application Owner',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='applications',
    )
    is_enabled = models.BooleanField(verbose_name='Enabled', default=True, null=False)

    class Meta:
        verbose_name = 'application'
        verbose_name_plural = 'applications'
        constraints = [
            models.UniqueConstraint(
                fields=['slug', 'name'], condition=models.Q(is_enabled=True), name='app_unique_enabled_slug'
            )
        ]

    def __str__(self) -> str:
        """Object's string representation.

        Returns:
            String representation.
        """
        return f'{self.name}'

    def copy(self) -> 'Application':
        """Creates a deep copy of Application object with resources, responses and webhooks.

        Returns:
            New Application object.
        """
        original_object_id = self.id
        self.pk = None

        original_object = Application.objects.get(pk=original_object_id)

        while Application.objects.filter(slug=self.slug):
            self.slug += '-copy'
        self.save()

        for resource in original_object.resources.all():
            resource.copy(application=self)

        related_objects = *original_object.requests.all(), *original_object.responses.all()
        for relation_obj in related_objects:
            relation_obj.pk = None
            setattr(relation_obj, 'application', self)
            relation_obj.save()
        return self

    def clean(self) -> None:
        super().clean()
        if self.slug.lower() in settings.RESERVED_APP_NAMES:
            raise ValidationError(
                _('This word is reserved and can not be used as an application slug. Please, choose another one.'),
                code='invalid',
            )


class ResponseStub(AbstractHTTPObject, BaseStubModel):
    status_code = models.PositiveSmallIntegerField(verbose_name='Status code', null=False)
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='responses',
    )
    creator = models.ForeignKey(
        User, verbose_name='Created by', null=True, blank=True, on_delete=models.SET_NULL, related_name='responses'
    )

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
    query_params = models.JSONField(verbose_name='Query Params', default=dict, blank=True)
    uri = models.URLField(verbose_name='URI', null=False)
    method = models.CharField(
        max_length=10,
        choices=HTTPMethods.choices,
        default=HTTPMethods.GET.value,
        verbose_name='HTTP Method',
    )

    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='requests',
    )
    creator = models.ForeignKey(
        User, verbose_name='Created by', null=True, blank=True, on_delete=models.SET_NULL, related_name='request'
    )

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
    description = models.TextField(verbose_name='Description', null=True, blank=True)
    method = models.CharField(
        max_length=10,
        choices=HTTPMethods.choices,
        default=HTTPMethods.GET.value,
        verbose_name='HTTP Method',
        null=True,
        blank=True,
    )
    proxy_destination_address = models.URLField(verbose_name='Proxy to', default=None, blank=True, null=True)
    response_type = models.CharField(
        max_length=30,
        choices=ResponseChoices.choices,
        default=ResponseChoices.CUSTOM.value,
        verbose_name='Response Type',
    )
    slug = models.SlugField(verbose_name='Slug', allow_unicode=True, null=False)
    tail = models.CharField(verbose_name='URL Tail', max_length=120, default='', blank=True)
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='resources',
    )
    response = models.ForeignKey(
        ResponseStub,
        verbose_name='Response',
        related_name='resources',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    creator = models.ForeignKey(
        User, verbose_name='Created by', null=True, blank=True, on_delete=models.SET_NULL, related_name='resources'
    )
    is_enabled = models.BooleanField(verbose_name='Enabled', default=True, null=False)
    inject_stubborn_headers = models.BooleanField(verbose_name='Inject Stubborn Headers', default=False)

    class Meta:
        verbose_name = 'resource'
        verbose_name_plural = 'resources'
        constraints = [
            models.UniqueConstraint(
                fields=['slug', 'method', 'tail', 'application'],
                condition=models.Q(is_enabled=True),
                name='unique_enabled_slug',
            )
        ]

    def __str__(self) -> str:
        """Object's string representation.

        Returns:
            String representation.
        """
        if not self.description:
            return f'{self.slug}'

        desc = f'{self.description[:10]}...' if len(self.description) > 10 else self.description[:10]
        return f'{self.slug} ({desc})'

    def copy(self, application: Application) -> 'ResourceStub':
        """Creates a copy of ResourceStub object with its hooks.

        Args:
            application: Application object for a new copy.

        Returns:
            New ResourceStub object.
        """
        hook_ids = self.hooks.all().values_list('id', flat=True)

        self.pk = None
        self.application = application
        self.save()

        for hook in ResourceHook.objects.filter(pk__in=hook_ids):
            hook.pk = None
            hook.resource = self
            hook.save()
        return self

    def clean(self) -> None:
        if not self.response and not self.proxy_destination_address:
            raise ValidationError(
                _('The resource stub must be created with the response or proxy instruction.'), code='invalid'
            )
        if self.tail:
            validator = URLValidator(message=_('Wrong URL tail format.'))
            url = os.path.join('https://test.com', self.slug, self.tail)
            validator(url)


class ResourceHook(BaseStubModel):
    action = models.CharField(max_length=10, choices=Action.choices, default=Action.WAIT.value)
    lifecycle = models.CharField(max_length=10, choices=Lifecycle.choices, default=Lifecycle.AFTER_REQUEST.value)
    order = models.PositiveSmallIntegerField(
        verbose_name='Order', default=1, validators=[MinValueValidator(1), MaxValueValidator(100)]
    )
    timeout = models.PositiveSmallIntegerField(
        verbose_name='Response Timeout', default=0, validators=[MaxValueValidator(100)]
    )
    request = models.ForeignKey(
        RequestStub,
        on_delete=models.deletion.CASCADE,
        blank=True,
        null=True,
        related_name='hooks',
    )
    resource = models.ForeignKey(
        ResourceStub,
        on_delete=models.deletion.CASCADE,
        blank=True,
        null=True,
        related_name='hooks',
    )

    def clean(self) -> None:
        if self.action == Action.WAIT and not self.timeout:
            raise ValidationError(_("'timeout' field is required if 'Action.WAIT' used"), code='invalid')

        if self.action == Action.WEBHOOK and not self.request:
            raise ValidationError(
                _("'request' field is required if 'Action.WEBHOOK' used"),
                code='invalid',
            )

    class Meta:
        verbose_name = 'hook'
        verbose_name_plural = 'hooks'
        ordering = ('order',)
        constraints = [
            UniqueConstraint(
                fields=[
                    "order",
                    "lifecycle",
                    "resource",
                ],
                name="unique_order_per_resource",
            ),
        ]


class RequestLog(BaseStubModel):
    destination_url = models.URLField(verbose_name='Proxied to', default=None, null=True, blank=True)
    ipaddress = models.GenericIPAddressField(verbose_name='Remote IP', default='127.0.0.1')
    method = models.CharField(verbose_name='Method', max_length=10, default=None, null=True, blank=True)
    params = models.JSONField(verbose_name='Query Params', default=dict, null=True, blank=True)
    proxied = models.BooleanField(verbose_name='Proxied', default=False, null=False, blank=False)
    request_body = models.TextField(verbose_name='Request Body', null=True, blank=True)
    request_headers = models.JSONField(verbose_name='Headers', default=dict, null=True, blank=True)
    response_body = models.TextField(verbose_name='Request Body', null=True, blank=True)
    response_headers = models.JSONField(verbose_name='Headers', default=dict, null=True, blank=True)
    status_code = models.IntegerField(verbose_name='Status Code', null=True, blank=True)
    url = models.URLField(verbose_name='URL Called', default=None, null=True, blank=True)
    x_real_ip = models.GenericIPAddressField(verbose_name='X-REAL-IP', default='127.0.0.1', null=True, blank=True)
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='logs',
    )
    resource = models.ForeignKey(
        ResourceStub,
        on_delete=models.deletion.CASCADE,
        blank=True,
        null=True,
        related_name='logs',
    )
    response = models.ForeignKey(
        ResponseStub,
        verbose_name='Response',
        related_name='logs',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = 'request log'
        verbose_name_plural = 'request logs'

    def __str__(self) -> str:
        """Object's string representation.

        Returns:
            String representation.
        """
        return f'Request Log Record #{self.id}'

    @property
    def response_format(self) -> str:
        content_type = self.response_headers.get('Content-Type', '')

        if 'json' in content_type:
            return BodyFormat.JSON
        if 'xml' in content_type:
            return BodyFormat.XML
        return BodyFormat.PLAIN_TEXT


class Team(BaseStubModel):
    name = models.CharField(verbose_name='Name', max_length=50, blank=False, null=False)
    slug = models.SlugField(verbose_name='Slug', allow_unicode=True, blank=False, null=False)
    owner = models.ForeignKey(
        User,
        verbose_name='Team Owner',
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name='team',
    )
    team_type = models.CharField(
        verbose_name='Team Type',
        choices=TeamChoices.choices,
        default=TeamChoices.PUBLIC.value,
        max_length=10
    )
    inviter = models.CharField(
        verbose_name='Inviter',
        choices=InviterChoices.choices,
        default=InviterChoices.OWNER.value,
        max_length=10
    )

    class Meta:
        verbose_name = 'team'
        verbose_name_plural = 'teams'
        constraints = [
            UniqueConstraint(
                fields=[
                    "owner",
                    "slug",
                ],
                name="unique_team_slug_per_owner",
            ),
        ]
