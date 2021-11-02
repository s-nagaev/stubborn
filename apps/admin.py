from typing import Any, cast, Dict

from django.contrib import admin
from django.contrib.auth.models import User
from django.core.handlers.wsgi import WSGIRequest

from apps import inlines, models
from apps.mixins import HideFromAdminIndexMixin, DenyCUDMixin


@admin.register(models.Application)
class ApplicationAdmin(admin.ModelAdmin):
    readonly_fields = ['owner']
    inlines = [inlines.LogsInline, inlines.ResourcesInline]
    pass

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
    pass


@admin.register(models.ResponseStub)
class ResponseStubAdmin(HideFromAdminIndexMixin, admin.ModelAdmin):
    pass


@admin.register(models.RequestLog)
class RequestLogAdmin(DenyCUDMixin, HideFromAdminIndexMixin, admin.ModelAdmin):
    pass
