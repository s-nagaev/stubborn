from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import QuerySet

from apps.models import ResourceStub
from apps.services import turn_off_same_resource_stub


@admin.action(description='Enable / Disable')
def change_satus(model_admin: ModelAdmin, request: WSGIRequest, queryset: QuerySet) -> None:
    for obj in queryset:
        obj.refresh_from_db()
        obj.is_enabled = not obj.is_enabled

        if obj.is_enabled:
            turn_off_same_resource_stub(resource_stub=obj)
        obj.save()


@admin.action(description='Duplicate')
def duplicate(model_admin: ModelAdmin, request: WSGIRequest, queryset: QuerySet) -> None:
    for obj in queryset:
        obj.refresh_from_db()
        if isinstance(obj, ResourceStub):
            obj.is_enabled = False
        obj.pk = None
        obj.save()
