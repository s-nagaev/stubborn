import json
from pygments import highlight
from pygments.lexers.data import JsonLexer
from pygments.formatters.html import HtmlFormatter

from typing import Any, cast, Dict

from django.contrib import admin
from django.contrib.auth.models import User
from django.core.handlers.wsgi import WSGIRequest
from django.urls import reverse
from django.utils.safestring import mark_safe

from apps import inlines, models
from apps.mixins import HideFromAdminIndexMixin, DenyCUDMixin


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
    fields = ('created_at', 'resource', 'params', 'body', 'prettify_headers', 'ipaddress',
              'x_real_ip', 'response')
    readonly_fields = ('prettify_headers', )

    @staticmethod
    @admin.display(description='Headers')  # type: ignore
    def prettify_headers(obj: models.RequestLog) -> str:
        headers_string = json.dumps(obj.headers, sort_keys=True, indent=2)
        formatter = HtmlFormatter()
        headers_prettified = highlight(headers_string, JsonLexer(), formatter)
        style = f'<style>{formatter.get_style_defs()}</style>'
        return mark_safe(headers_prettified + style)




