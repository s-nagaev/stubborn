from urllib.parse import parse_qs, parse_qsl, urlencode, urlparse, urlunparse

from django import template
from django.template import RequestContext

from apps.models import Application

register = template.Library()


@register.filter
def application_id_by_url(full_url: str) -> str | None:
    application_filter_query = 'application'
    parsed = urlparse(full_url)
    query_params = parse_qs(parsed.query)
    if application_filter_query not in query_params:
        return None
    return query_params[application_filter_query][0]


@register.filter
def application_name_by_id(application_id: int | str | None) -> str | None:
    if not application_id:
        return None
    app = Application.objects.get(pk=application_id)
    return app.name


@register.simple_tag(takes_context=True)
def add_with_filter(context: RequestContext, url: str) -> str:
    preserved_filters = context.get('preserved_filters')
    parsed_preserved_filters = dict(parse_qsl(preserved_filters))
    if '_changelist_filters' not in parsed_preserved_filters:
        return url

    parsed_changelist_filters = dict(parse_qsl(parsed_preserved_filters['_changelist_filters']))
    parsed_url = list(urlparse(url))
    parsed_url[4] = urlencode(parsed_changelist_filters)
    return urlunparse(parsed_url)
