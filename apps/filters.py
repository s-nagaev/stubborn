from typing import Any, Generator, Union
from uuid import UUID

from django.contrib.admin import SimpleListFilter
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _

from apps.models import ResourceStub


class MultiSelectFilter(SimpleListFilter):
    @property
    def multiselect_value(self) -> set[str]:
        value = self.value()
        if value is None:
            return set()
        return set(value.split(','))

    def choices(self, changelist: Any) -> Generator[dict[str, Union[bool, str]], None, None]:

        yield {
            'selected': len(self.multiselect_value) == 0,
            'query_string': changelist.get_query_string(remove=[self.parameter_name]),
            'display': _('All'),
        }

        for lookup, title in self.lookup_choices:
            lookup = str(lookup)
            is_selected = lookup in self.multiselect_value
            query_values = self.multiselect_value.copy()

            query_values.remove(lookup) if is_selected else query_values.add(lookup)

            if query_values:
                query_string = changelist.get_query_string({self.parameter_name: ','.join(query_values)})
            else:
                query_string = changelist.get_query_string(remove=[self.parameter_name])

            yield {
                'selected': is_selected,
                'query_string': query_string,
                'display': title,
            }


class ResourceFilter(MultiSelectFilter):
    title = 'Resource'
    parameter_name = 'resource_slug'

    def lookups(self, request: WSGIRequest, model_admin: Any) -> list[tuple[Any, str]]:
        query_params = request.GET.dict()
        app_id = query_params.get('application')

        if not app_id:
            return []

        return [(res.id, res.slug) for res in ResourceStub.objects.filter(application__pk=app_id).order_by('slug')]

    def queryset(self, request: WSGIRequest, queryset: QuerySet) -> QuerySet:
        value = self.value()
        if value is None:
            return queryset

        return queryset.filter(resource__pk__in=[UUID(v) for v in value.split(',')])
