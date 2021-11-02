from typing import Any

from django.conf import settings
from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from apps import mixins, models


class ResourcesInline(mixins.DenyUpdateMixin, mixins.DenyDeleteMixin, admin.TabularInline):
    model = models.ResourceStub
    classes = ('collapse',)
    show_change_link = True
    extra = 0


class LogsInline(mixins.DenyCUDMixin, admin.TabularInline):
    model = models.RequestLog
    parent_model = models.Application
    fk_name = 'application'
    template = 'admin/inlines/request_log_tabular.html'
    fields = ('created_at', 'get_remote_ip', 'resource_method', 'resource', 'get_resource_desc')
    readonly_fields = ('created_at', 'get_resource_desc', 'get_remote_ip')
    # classes = ('collapse',)
    show_change_link = False
    extra = 0
    ordering = ('-pk',)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Инициализация и установка titles."""
        setattr(self.get_resource_desc, 'short_description', 'Description')
        setattr(self.get_remote_ip, 'short_description', 'Remote IP/X-Real-IP')
        super().__init__(*args, **kwargs)

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        queryset = super().get_queryset(request)
        ids = queryset.order_by('-id').values('pk')[:settings.REQUEST_LOGS_INLINE_LIMIT]
        qs = self.model.objects.filter(pk__in=ids).order_by('-id')
        return qs

    @staticmethod
    def get_resource_desc(obj: models.RequestLog) -> str:
        return obj.resource.description

    @staticmethod
    def get_remote_ip(obj: models.RequestLog) -> str:
        return f'{obj.ipaddress}/{obj.x_real_ip}'