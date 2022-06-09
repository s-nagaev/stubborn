import os
from typing import Any, Optional, cast

from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponseRedirect
from django.urls import reverse
from django.utils.safestring import mark_safe

from apps import inlines, models
from apps.forms import ResourceStubForm, ResponseStubForm
from apps.mixins import DenyCreateMixin, DenyUpdateMixin, HideFromAdminIndexMixin, RelatedCUDManagerMixin
from apps.utils import prettify_data_to_html, prettify_json_html


@admin.register(models.Application)
class ApplicationAdmin(admin.ModelAdmin):
    readonly_fields = ('owner', )
    list_display = ('name', 'slug', 'resources_count', 'short_desc')
    fields = ('name', 'description', 'slug', 'owner')
    inlines = [inlines.LogsInline]
    change_form_template = 'admin/apps/application/change_form.html'

    class Media:
        css = {
            'all': ('admin/css/application.css',)
        }

    def get_inlines(self, request: HttpRequest, obj: models.Application = None):
        """Hook for specifying custom inlines.

        Args:
            request: HttpRequest instance.
            obj: model instance.

        Returns:
            List containing InlineModelAdmin objects if there is Application object data, empty list otherwise.
        """
        return self.inlines if obj else []

    def save_model(self, request: HttpRequest, obj: models.Application, *args: Any, **kwargs: Any) -> None:
        """Save model with current user fixation in the owner field.

        Args:
            request: HttpRequest instance.
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


@admin.register(models.RequestStub)
class RequestStubAdmin(HideFromAdminIndexMixin, RelatedCUDManagerMixin, admin.ModelAdmin):
    search_fields = ('description', 'uri', 'method', )


class ResourceHookAdminInline(admin.TabularInline):
    extra = 0
    model = models.ResourceHook
    # ToDo Filter by application
    autocomplete_fields = ('request', )


@admin.register(models.ResourceStub)
class ResourceStubAdmin(HideFromAdminIndexMixin, RelatedCUDManagerMixin, admin.ModelAdmin):
    form = ResourceStubForm
    readonly_fields = ('creator', )
    list_display = ('method', 'uri_with_slash', 'response', 'description', 'full_url', 'proxied')
    no_add_related = ('application', 'response',)
    no_edit_related = ('application',)
    inlines = (ResourceHookAdminInline, )

    class Media:
        js = ('admin/js/resource/responseSwitcher.js',)

    @staticmethod
    @admin.display(description='URI')
    def uri_with_slash(obj: models.ResourceStub) -> str:
        """Add the leading slash to URI.

        Args:
            obj: model instance.

        Returns:
            URI with the leading slash.
        """
        return f'/{obj.slug}'

    @staticmethod
    @admin.display(description='Full URL')
    def full_url(obj: models.ResourceStub) -> str:
        """Compose the full URL of the application resource.

        Args:
            obj: model instance.

        Returns:
            The full application resource URL.
        """
        url = os.path.join(settings.DOMAIN_DISPLAY, obj.application.slug, obj.slug, obj.tail)
        return mark_safe(f'<a href={url}>{url}</a>')

    def response_add(self, request: HttpRequest, obj: models.ResourceStub, post_url_continue: Optional[str] = None):
        """Return to the application page after adding.

        Args:
            request: HttpRequest instance.
            obj: model instance.
            post_url_continue: default redirection URL.

        Returns:
            HttpResponse instance.
        """
        return HttpResponseRedirect(reverse("admin:apps_application_change", args=(obj.application.pk,)))

    @staticmethod
    @admin.display(boolean=True, description='Proxied')
    def proxied(obj: models.ResourceStub) -> bool:
        """Get the request proxy status.

        Args:
            obj: model instance.

        Returns:
            True if the request is proxied, False otherwise.
        """
        return bool(obj.proxy_destination_address)


@admin.register(models.ResponseStub)
class ResponseStubAdmin(HideFromAdminIndexMixin, RelatedCUDManagerMixin, admin.ModelAdmin):
    form = ResponseStubForm
    readonly_fields = ('creator', )
    list_display = ('id', 'status_code', 'format', 'has_headers', 'has_body', 'description')
    no_add_related = ('application', )
    no_edit_related = ('application', )

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

    def response_add(self, request: HttpRequest, obj: models.ResponseStub, post_url_continue: Optional[str] = None):
        """Return to the application page after adding.

        Args:
            request: HttpRequest instance.
            obj: model instance.
            post_url_continue: default redirection URL.

        Returns:
            HttpResponse instance.
        """
        return HttpResponseRedirect(reverse("admin:apps_application_change", args=(obj.application.pk,)))


@admin.register(models.RequestLog)
class RequestLogAdmin(DenyCreateMixin, DenyUpdateMixin, HideFromAdminIndexMixin, admin.ModelAdmin):
    change_form_template = 'admin/apps/request_log/change_form.html'

    fields = (
        'created_at',
        'destination_url',
        'pretty_request_headers',
        'pretty_params',
        'pretty_request_body',
        'pretty_response_headers',
        'pretty_response_body',
        'ipaddress',
        'x_real_ip',
        'resource',
        'response'
    )
    list_display = ('created_at', 'method', 'url', 'get_remote_ip', 'resource', 'get_resource_desc', 'proxied')
    readonly_fields = (
        'pretty_params',
        'pretty_request_headers',
        'pretty_request_body',
        'pretty_response_headers',
        'pretty_response_body'
    )

    class Media:
        css = {
            'all': ('admin/css/application.css',)
        }

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
            return prettify_data_to_html(obj.request_body)
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
            return prettify_data_to_html(obj.response_body)
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
        if not obj.resource:
            return ''
        return obj.resource.description or ''

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
        return f'{obj.ipaddress} / {obj.x_real_ip}'
