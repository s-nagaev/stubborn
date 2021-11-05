import json

from typing import Any, cast

from django.contrib import admin
from django.contrib.auth.models import User
from django.core.handlers.wsgi import WSGIRequest
from django.utils.safestring import mark_safe

from apps import inlines, models
from apps.mixins import HideFromAdminIndexMixin, DenyCUDMixin
from apps.utils import prettify_json_html

@admin.register(models.Application)
class ApplicationAdmin(admin.ModelAdmin):
    readonly_fields = ['owner']
    fields = ('name', 'description', 'slug', 'owner')
    inlines = [inlines.LogsInline]
    change_form_template = 'admin/application/change_form.html'

    class Media:
        css = {
            'all': ('admin/css/application.css',)
        }

    def save_model(self, request: WSGIRequest, obj: models.Application, *args: Any, **kwargs: Any) -> None:
        """Saving model with current user fixation in the owner field.

        Args:
            request: WSGIRequest instance.
            obj: model instance.
        """
        obj.owner = cast(User, request.user)
        super().save_model(request, obj, *args, **kwargs)


@admin.register(models.ResourceStub)
class ResourceStubAdmin(HideFromAdminIndexMixin, admin.ModelAdmin):
    list_display = ('method', 'uri', 'description', 'response')
    list_filter = ('application',)


@admin.register(models.ResponseStub)
class ResponseStubAdmin(HideFromAdminIndexMixin, admin.ModelAdmin):
    pass


@admin.register(models.RequestLog)
class RequestLogAdmin(DenyCUDMixin, HideFromAdminIndexMixin, admin.ModelAdmin):
    fields = ('created_at', 'resource', 'pretty_params', 'pretty_request_body', 'pretty_headers', 'ipaddress',
              'x_real_ip', 'response')
    readonly_fields = ('pretty_headers', 'pretty_params', 'pretty_request_body')

    @staticmethod
    @admin.display(description='Headers')  # type: ignore
    def pretty_headers(obj: models.RequestLog) -> str:
        headers_prettified = prettify_json_html(obj.headers)
        return mark_safe(headers_prettified)

    @staticmethod
    @admin.display(description='Query params')  # type: ignore
    def pretty_params(obj: models.RequestLog) -> str:
        params_prettified = prettify_json_html(obj.params)
        return mark_safe(params_prettified)

    @staticmethod
    @admin.display(description='Request body')  # type: ignore
    def pretty_request_body(obj: models.RequestLog) -> str:
        body_prettified = prettify_json_html(obj.body)
        return mark_safe(body_prettified)
