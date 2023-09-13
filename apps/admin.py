import os
from typing import Any, Optional, cast

from django.conf import settings
from django.contrib import admin, messages
from django.contrib.admin.options import IS_POPUP_VAR
from django.contrib.auth.models import User
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponseRedirect
from django.urls import reverse
from django.utils.safestring import mark_safe
from rangefilter.filters import DateTimeRangeFilterBuilder

from apps import inlines, models
from apps.actions import change_satus, duplicate
from apps.enums import ResponseChoices
from apps.filters import ResourceFilter
from apps.forms import ResourceStubForm, ResponseStubForm, WebHookRequestForm
from apps.inlines import ResourceHookAdminInline
from apps.mixins import (
    AddApplicationRelatedObjectMixin,
    DenyCreateMixin,
    DenyUpdateMixin,
    HideFromAdminIndexMixin,
    RelatedCUDManagerMixin,
    SaveByCurrentUserMixin,
)
from apps.services import turn_off_same_resource_stub
from apps.utils import end_of_the_day_today, prettify_data_to_html, prettify_json_html, start_of_the_day_today


@admin.register(models.Application)
class ApplicationAdmin(admin.ModelAdmin):
    readonly_fields = ('owner',)
    list_display = ('name', 'slug', 'resources_count', 'short_desc')
    fields = ('name', 'description', 'slug', 'owner')
    inlines = [inlines.LogsInline]
    change_form_template = 'admin/apps/application/change_form.html'
    ordering = ('name',)

    class Media:
        css = {'all': ('admin/css/application.css',)}

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
class RequestStubAdmin(
    HideFromAdminIndexMixin,
    RelatedCUDManagerMixin,
    SaveByCurrentUserMixin,
    AddApplicationRelatedObjectMixin,
    admin.ModelAdmin,
):
    fields = (
        'name',
        'headers',
        'body',
        'query_params',
        'uri',
        'method',
        'format',
        'description',
        'application',
        'creator',
    )
    readonly_fields = ('creator',)
    search_fields = (
        'description',
        'uri',
        'method',
    )
    form = WebHookRequestForm
    no_add_related = ('application',)
    no_edit_related = ('application',)
    ordering = ('-created_at',)
    actions = (duplicate,)

    def response_add(self, request: HttpRequest, obj: models.RequestStub, post_url_continue: Optional[str] = None):
        """Return to the application page after adding.

        Args:
            request: HttpRequest instance.
            obj: model instance.
            post_url_continue: default redirection URL.

        Returns:
            HttpResponse instance.
        """
        if IS_POPUP_VAR in request.POST:
            return super().response_add(request, obj, post_url_continue)
        return HttpResponseRedirect(reverse('admin:apps_application_change', args=(obj.application.pk,)))

    def delete_model(self, request: HttpRequest, obj: models.RequestStub):
        application = obj.application
        obj.delete()
        return HttpResponseRedirect(reverse('admin:apps_application_change', args=(application.pk,)))


@admin.register(models.ResourceStub)
class ResourceStubAdmin(
    HideFromAdminIndexMixin, RelatedCUDManagerMixin, AddApplicationRelatedObjectMixin, admin.ModelAdmin
):
    form = ResourceStubForm
    readonly_fields = ('creator',)
    list_display = ('is_enabled', 'get_method', 'uri_with_slash', 'response', 'description', 'full_url', 'proxied')
    no_add_related = ('application',)
    no_edit_related = ('application',)
    no_delete_related = ('application',)
    inlines = (ResourceHookAdminInline,)
    ordering = (
        '-is_enabled',
        'slug',
        '-created_at',
    )
    actions = (change_satus, duplicate)
    list_display_links = ('get_method',)

    class Media:
        js = (
            'admin/js/resource/responseSwitcher.js',
            'admin/js/resource/hooksSwitcher.js',
        )

    def save_model(self, request: HttpRequest, obj: models.ResourceStub, *args: Any, **kwargs: Any) -> None:
        if not obj.is_enabled:
            super().save_model(request, obj, *args, **kwargs)

        if turned_off_resource := turn_off_same_resource_stub(resource_stub=obj):
            admin_url = reverse('admin:apps_resourcestub_change', args=(turned_off_resource.pk,))
            msg = mark_safe(f'A same resource stub has been disabled. <a href={admin_url}>Click here to check it.</a>')
            messages.info(request=request, message=msg)
        super().save_model(request, obj, *args, **kwargs)

    @staticmethod
    @admin.display(description='method')
    def get_method(obj: models.ResourceStub) -> str:
        if obj.response_type == ResponseChoices.PROXY_GLOBAL:
            return 'ANY'
        return obj.method or '-'

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

    def response_add(
        self, request: HttpRequest, obj: models.ResourceStub, post_url_continue: Optional[str] = None
    ) -> HttpResponseRedirect:
        """Return to the application page after adding.

        Args:
            request: HttpRequest instance.
            obj: model instance.
            post_url_continue: default redirection URL.

        Returns:
            HttpResponse instance.
        """
        return HttpResponseRedirect(reverse('admin:apps_application_change', args=(obj.application.pk,)))

    def delete_model(self, request: HttpRequest, obj: models.ResourceStub):
        application = obj.application
        obj.delete()
        return HttpResponseRedirect(reverse('admin:apps_application_change', args=(application.pk,)))

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
    readonly_fields = ('creator',)
    list_display = ('id', 'status_code', 'format', 'has_headers', 'has_body', 'description', 'created_at')
    fields = ('headers', 'body', 'status_code', 'format', 'description', 'application', 'creator')
    no_add_related = ('application',)
    no_edit_related = ('application',)
    ordering = ('-created_at',)
    actions = (duplicate,)

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
        if IS_POPUP_VAR in request.POST:
            return super().response_add(request, obj, post_url_continue)
        return HttpResponseRedirect(reverse('admin:apps_application_change', args=(obj.application.pk,)))

    def delete_model(self, request: HttpRequest, obj: models.ResponseStub):
        application = obj.application
        obj.delete()
        return HttpResponseRedirect(reverse('admin:apps_application_change', args=(application.pk,)))


@admin.register(models.RequestLog)
class RequestLogAdmin(DenyCreateMixin, DenyUpdateMixin, HideFromAdminIndexMixin, admin.ModelAdmin):
    change_form_template = 'admin/apps/request_log/change_form.html'

    fields = (
        'created_at',
        'method',
        'url',
        'destination_url',
        'pretty_request_headers',
        'pretty_params',
        'pretty_request_body',
        'status_code',
        'pretty_response_headers',
        'pretty_response_body',
        'ipaddress',
        'x_real_ip',
        'resource',
        'response',
    )
    list_display = (
        'created_at',
        'method',
        'status_code',
        'url',
        'get_remote_ip',
        'resource',
        'proxied',
    )
    readonly_fields = (
        'pretty_params',
        'pretty_request_headers',
        'pretty_request_body',
        'pretty_response_headers',
        'pretty_response_body',
    )
    search_fields = (
        'id',
        'url',
        'params',
        'request_body',
        'request_headers',
        'response_body',
        'response_headers',
        'ipaddress',
        'x_real_ip',
    )
    list_filter = (
        (
            'created_at',
            DateTimeRangeFilterBuilder(
                title="Created at",
                default_start=start_of_the_day_today(),
                default_end=end_of_the_day_today(),
            ),
        ),
        ResourceFilter,
        'status_code',
        'proxied',
        'method',
    )
    ordering = ('-created_at',)

    class Media:
        css = {'all': ('admin/css/application.css',)}

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        params = request.GET.dict()
        application_id = cast(Optional[str], params.get('application'))
        if not application_id:
            return super().get_queryset(request)

        return models.RequestLog.objects.filter(application__pk=application_id)

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
    @admin.display(description='Remote IP / X-Real-IP')
    def get_remote_ip(obj: models.RequestLog) -> str:
        """Getter fot the client's IP address.

        Making a combination of the received client's IP address and X_REAL_IP header.

        Args:
            obj: RequestLog instance.

        Returns:
            String containing the client's IP addresses.
        """
        return f'{obj.ipaddress} / {obj.x_real_ip}'

    def delete_model(self, request: HttpRequest, obj: models.RequestLog):
        application = obj.application
        obj.delete()
        return HttpResponseRedirect(reverse('admin:apps_application_change', args=(application.pk,)))
