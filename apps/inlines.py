from django.conf import settings
from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.urls import reverse
from django.utils.safestring import mark_safe

from apps import mixins, models


class ResourceHookAdminInline(admin.TabularInline):
    extra = 0
    model = models.ResourceHook
    # ToDo Filter by application
    autocomplete_fields = ('request', )


class ResourcesInline(mixins.DenyUpdateMixin, mixins.DenyDeleteMixin, admin.TabularInline):
    model = models.ResourceStub
    classes = ('collapse',)
    show_change_link = True
    extra = 0
    fields = ('method', 'slug', 'description', 'response')
    readonly_fields = ('get_url', )

    @staticmethod
    @admin.display(description='Description')
    def get_url(obj: models.RequestLog) -> str:
        """Getter for the resource description.

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
    template = 'admin/apps/request_log/inlines/tabular.html'
    fields = ('created_at', 'method', 'url', 'get_remote_ip', 'resource', 'status_code')
    readonly_fields = ('created_at', 'url', 'get_remote_ip')
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
        default_queryset = super().get_queryset(request)
        application_id = request.resolver_match.kwargs.get('object_id')
        if not application_id:
            return default_queryset
        queryset = default_queryset.filter(application_id=application_id)
        ids = queryset.order_by('-id').values('pk')[:settings.REQUEST_LOGS_INLINE_LIMIT]
        return self.model.objects.filter(pk__in=ids).order_by('-pk')

    @staticmethod
    @admin.display(description='Remote IP/X-Real-IP')
    def get_remote_ip(obj: models.RequestLog) -> str:
        """Getter for the client's IP address.

        Making a combination of the received client's IP address and X_REAL_IP header.

        Args:
            obj: RequestLog instance.

        Returns:
            String containing the client's IP addresses.
        """
        return f'{obj.ipaddress}/{obj.x_real_ip}'
