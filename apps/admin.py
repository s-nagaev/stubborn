import os
from typing import Any, Optional, cast

from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import User
from django.core.handlers.wsgi import WSGIRequest
from django.utils.safestring import mark_safe

from apps import inlines, models
from apps.forms import ResourceStubForm
from apps.mixins import DenyCUDMixin, HideFromAdminIndexMixin
from apps.utils import prettify_json_html, prettify_string_to_html


@admin.register(models.Application)
class ApplicationAdmin(admin.ModelAdmin):
    readonly_fields = ['owner']
    list_display = ('name', 'slug', 'resources_count', 'short_desc')
    fields = ('name', 'description', 'slug', 'owner')
    inlines = [inlines.LogsInline]
    change_form_template = 'admin/apps/application/change_form.html'

    class Media:
        css = {
            'all': ('admin/css/application.css',)
        }

    def save_model(self, request: WSGIRequest, obj: models.Application, *args: Any, **kwargs: Any) -> None:
        """Save model with current user fixation in the owner field.

        Args:
            request: WSGIRequest instance.
            obj: model instance.
        """
        obj.owner = cast(User, request.user)
        super().save_model(request, obj, *args, **kwargs)

    @staticmethod
    @admin.display(description='Resources')
    def resources_count(obj: models.Application) -> int:
        """Return related resource stubs count.

        Args:
            obj: model instance.

        Returns:
            Related resource stubs count.
        """
        return obj.resources.count()

    @staticmethod
    @admin.display(description='Description')
    def short_desc(obj: models.Application) -> Optional[str]:
        """Return the first 50 symbols of the description.

        Args:
            obj: model instance.

        Returns:
            Short version of the description.
        """
        if obj.description and len(obj.description) > 50:
            return f'{obj.description[:50]}...'
        return obj.description


@admin.register(models.ResourceStub)
class ResourceStubAdmin(HideFromAdminIndexMixin, admin.ModelAdmin):
    form = ResourceStubForm
    list_display = ('uri_with_slash', 'method', 'response', 'description', 'full_url')

    @staticmethod
    @admin.display(description='URI')
    def uri_with_slash(obj: models.ResourceStub) -> str:
        """Add the leading slash to URI.

        Args:
            obj: model instance.

        Returns:
            URI with the leading slash.
        """
        return f'/{obj.uri}'

    @staticmethod
    @admin.display(description='Full URL')
    def full_url(obj: models.ResourceStub) -> str:
        """Compose the full URL of the application resource.

        Args:
            obj: model instance.

        Returns:
            The full application resource URL.
        """
        url = os.path.join(settings.DOMAIN, obj.application.slug, obj.uri)
        return mark_safe(f'<a href={url}>{url}</a>')


@admin.register(models.ResponseStub)
class ResponseStubAdmin(HideFromAdminIndexMixin, admin.ModelAdmin):
    list_display = ('status_code', 'format', 'timeout', 'has_headers', 'has_body', 'description')

    @staticmethod
    @admin.display(description='Has Body', boolean=True)
    def has_body(obj: models.ResponseStub) -> bool:
        """Response body existence flag.

        Args:
            obj: model instance.

        Returns:
            True if the response stub has a body set up, False otherwise.
        """
        return bool(obj.body)

    @staticmethod
    @admin.display(description='Has Headers', boolean=True)
    def has_headers(obj: models.ResponseStub) -> bool:
        """Response headers existence flag.

        Args:
            obj: model instance.

        Returns:
            True if the response stub has a headers set up, False otherwise.
        """
        return bool(obj.headers)


@admin.register(models.RequestLog)
class RequestLogAdmin(DenyCUDMixin, HideFromAdminIndexMixin, admin.ModelAdmin):
    fields = (
        'created_at',
        'resource',
        'pretty_params',
        'pretty_request_headers',
        'pretty_request_body',
        'pretty_response_headers',
        'pretty_response_body',
        'ipaddress',
        'x_real_ip',
        'response'
    )
    list_display = ('created_at', 'get_method', 'url', 'get_remote_ip', 'resource', 'get_resource_desc')
    readonly_fields = (
        'pretty_params',
        'pretty_request_headers',
        'pretty_request_body',
        'pretty_response_headers',
        'pretty_response_body'
    )

    @staticmethod
    @admin.display(description='Query params')
    def pretty_params(obj: models.RequestLog) -> str:
        """Prettify query params.

        Args:
            obj: model instance.

        Returns:
            HTML with the style block containing nice-looking query params.
        """
        params_prettified = prettify_json_html(obj.params)
        return mark_safe(params_prettified)

    @staticmethod
    @admin.display(description='Request Headers')
    def pretty_request_headers(obj: models.RequestLog) -> str:
        """Prettify request headers.

        Args:
            obj: model instance.

        Returns:
            HTML with the style block containing nice-looking request headers.
        """
        headers_prettified = prettify_json_html(obj.request_headers)
        return mark_safe(headers_prettified)

    @staticmethod
    @admin.display(description='Response Headers')
    def pretty_response_headers(obj: models.RequestLog) -> str:
        """Prettify response headers.

        Args:
            obj: model instance.

        Returns:
            HTML with the style block containing nice-looking response headers.
        """
        headers_prettified = prettify_json_html(obj.response_headers)
        return mark_safe(headers_prettified)

    @staticmethod
    @admin.display(description='Request Body')
    def pretty_request_body(obj: models.RequestLog) -> str:
        """Prettify request body.

        Args:
            obj: model instance.

        Returns:
            HTML with the style block containing nice-looking request body.
        """
        if obj.request_body is not None:
            return prettify_string_to_html(obj.request_body)
        return ''

    @staticmethod
    @admin.display(description='Response Body')
    def pretty_response_body(obj: models.RequestLog) -> str:
        """Prettify response body.

        Args:
            obj: model instance.

        Returns:
            HTML with the style block containing nice-looking response body.
        """
        if obj.response_body is not None:
            return prettify_string_to_html(obj.response_body)
        return ''

    @staticmethod
    @admin.display(description='Description')
    def get_resource_desc(obj: models.RequestLog) -> str:
        """Getter fot the resource description.

        Args:
            obj: RequestLog instance.

        Returns:
            String containing the resource description.
        """
        return obj.resource.description or ''

    @staticmethod
    @admin.display(description='Method')
    def get_method(obj: models.RequestLog) -> str:
        """Getter fot the resource method.

        Args:
            obj: RequestLog instance.

        Returns:
            String containing the resource method.
        """
        return obj.resource.method

    @staticmethod
    @admin.display(description='Remote IP/X-Real-IP')
    def get_remote_ip(obj: models.RequestLog) -> str:
        """Getter fot the client's IP address.

        Making a combination of the received client's IP address and X_REAL_IP header.

        Args:
            obj: RequestLog instance.

        Returns:
            String containing the client's IP addresses.
        """
        return f'{obj.ipaddress}/{obj.x_real_ip}'
