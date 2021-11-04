from typing import Any

from django.conf import settings
from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.urls import reverse
from django.utils.safestring import mark_safe

from apps import mixins, models


class ResourcesInline(mixins.DenyUpdateMixin, mixins.DenyDeleteMixin, admin.TabularInline):
    model = models.ResourceStub
    classes = ('collapse',)
    show_change_link = True
    extra = 0
    # template = 'admin/inlines/resources_tabular.html'
    fields = ('method', 'uri', 'description', 'response')
    readonly_fields = ('get_url', )

    @staticmethod
    @admin.display(description='Description')  # type: ignore
    def get_url(obj: models.RequestLog) -> str:
        """Getter fot the resource description.

        Args:
            obj: RequestLog instance.

        Returns:
            String containing the resource description.
        """
        resource_url = reverse("admin:apps_resourcestub_change", args=(obj.pk,))
        return mark_safe(f'<a href="{resource_url}" class="inlineviewlink">Change</a>')


class LogsInline(mixins.DenyCUDMixin, admin.TabularInline):
    model = models.RequestLog
    parent_model = models.Application
    fk_name = 'application'
    template = 'admin/inlines/request_log_tabular.html'
    fields = ('created_at', 'get_remote_ip', 'get_method', 'resource', 'get_resource_desc')
    readonly_fields = ('created_at', 'get_method', 'get_resource_desc', 'get_remote_ip')
    # classes = ('collapse',)
    show_change_link = False
    extra = 0

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        """Return a QuerySet of the last X log instances that can be viewed by the admin site.

        This is used by changelist_view.

        Args:
            request: HttpRequest instance.

        Returns:
            QuerySet containing recent logs.
        """
        queryset = super().get_queryset(request)
        ids = queryset.order_by('-id').values('pk')[:settings.REQUEST_LOGS_INLINE_LIMIT]
        return self.model.objects.filter(pk__in=ids).order_by('-pk')

    @staticmethod
    @admin.display(description='Description')  # type: ignore
    def get_resource_desc(obj: models.RequestLog) -> str:
        """Getter fot the resource description.

        Args:
            obj: RequestLog instance.

        Returns:
            String containing the resource description.
        """
        return obj.resource.description

    @staticmethod
    @admin.display(description='Method')  # type: ignore
    def get_method(obj: models.RequestLog) -> str:
        """Getter fot the resource method.

        Args:
            obj: RequestLog instance.

        Returns:
            String containing the resource method.
        """
        return obj.resource.method

    @staticmethod
    @admin.display(description='Remote IP/X-Real-IP')  # type: ignore
    def get_remote_ip(obj: models.RequestLog) -> str:
        """Getter fot the client's IP address.

        Making a combination of the received client's IP address and X_REAL_IP header.

        Args:
            obj: RequestLog instance.

        Returns:
            String containing the client's IP addresses.
        """
        return f'{obj.ipaddress}/{obj.x_real_ip}'
