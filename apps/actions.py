from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import QuerySet

from apps.services import turn_off_same_resource_stub


@admin.action(description='Enable / Disable')
def change_satus(model_admin: ModelAdmin, request: WSGIRequest, queryset: QuerySet) -> None:
    for obj in queryset:
        obj.refresh_from_db()
        obj.is_enabled = not obj.is_enabled

        if obj.is_enabled:
            turn_off_same_resource_stub(resource_stub=obj)
        obj.save()
