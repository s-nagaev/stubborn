import json
import os
from json import JSONDecodeError
from typing import Any, Dict, Optional, cast

import requests
from django.conf import settings
from django.db.models import QuerySet
from django.http import Http404
from django.shortcuts import get_object_or_404
from requests import Response
from rest_framework.request import Request
from rest_framework.response import Response as RestResponse
from rest_framework_xml.renderers import XMLRenderer

from apps import enums, hooks, models
from apps.enums import ResponseChoices
from apps.models import Application, RequestLog, ResourceStub, ResponseStub
from apps.renderers import SimpleTextRenderer
from apps.utils import clean_headers


def request_log_create(
    application: Application,
    resource_stub: ResourceStub,
    request: Request,
    response_stub: ResponseStub = None,
    response_status_code: int = None,
    response_body: str = None,
    response_headers: Dict = None,
    proxied: bool = False,
    destination_url: str = None,
) -> RequestLog:
    log_record = RequestLog.objects.create(
        url=os.path.join(settings.DOMAIN_DISPLAY, request.META.get('PATH_INFO')[1:]),
        application=application,
        resource=resource_stub,
        response=response_stub,
        method=request.method,
        params=request.query_params,
        request_body=request.body.decode(),
        request_headers=dict(request.headers),
        status_code=response_status_code,
        response_body=response_body,
        response_headers=response_headers,
        ipaddress=request.META.get('REMOTE_ADDR'),
        x_real_ip=request.headers.get('X-REAL-IP'),
        proxied=proxied,
        destination_url=destination_url,
    )
    return log_record


def proxy_request(incoming_request: Request, destination_url: str) -> Response:
    """Making a request identical to received one to the destination URL.

    Args:
        incoming_request: incoming request instance.
        destination_url: a remote server URL request "proxy" to.

    Returns:
        Destinations server's response.
    """
    method = incoming_request.method
    query_params = incoming_request.query_params
    body = incoming_request.body.decode()
    headers = clean_headers(incoming_request.headers)

    destination_response = requests.request(
        method=method, url=destination_url, params=query_params, headers=headers, data=body.encode('utf8')
    )

    return destination_response


def get_regular_response(application, request, resource) -> RestResponse:
    hooks.before_request(resource)
    response_stub = cast(ResponseStub, resource.response)
    request.accepted_renderer = response_stub.renderer
    response_body = response_stub.body_rendered

    request_log_create(
        application=application,
        resource_stub=resource,
        response_stub=response_stub,
        request=request,
        response_status_code=response_stub.status_code,
        response_body=response_body,
        response_headers=response_stub.headers,
    )

    if response_stub.is_json_format:
        response_data = json.loads(response_body) or ''
    else:
        response_data = response_body

    hooks.after_request(resource)
    try:
        return RestResponse(data=response_data, status=response_stub.status_code, headers=response_stub.headers)
    finally:
        if resource.resourcehook_set.filter(lifecycle=enums.Lifecycle.AFTER_RESPONSE).exists():
            hooks.after_response(resource.pk)


def get_third_party_service_response(
    application: Application, request: Request, resource: ResourceStub, tail: Optional[str] = None
) -> RestResponse:
    if tail and resource.response_type == ResponseChoices.PROXY_CURRENT:
        raise Http404()

    destination_address = str(resource.proxy_destination_address)
    remote_url = os.path.join(destination_address, tail) if tail else destination_address

    hooks.before_request(resource)
    destination_response = proxy_request(incoming_request=request, destination_url=remote_url)
    hooks.after_request(resource)
    response_body = destination_response.content.decode()
    response_headers = clean_headers(dict(destination_response.headers))

    content_type = response_headers.get('Content-Type', 'application/json')  # assume that

    if '/xml' in content_type:
        request.accepted_renderer = XMLRenderer()

    if 'text/html' in content_type:
        request.accepted_renderer = SimpleTextRenderer()

    request_log_create(
        application=application,
        resource_stub=resource,
        request=request,
        response_status_code=destination_response.status_code,
        response_body=response_body,
        response_headers=response_headers,
        proxied=True,
        destination_url=remote_url,
    )

    try:
        response_body = destination_response.json()
    except JSONDecodeError:
        pass

    try:
        return RestResponse(data=response_body, status=destination_response.status_code, headers=response_headers)
    finally:
        if resource.resourcehook_set.filter(lifecycle=enums.Lifecycle.AFTER_RESPONSE).exists():
            hooks.after_response(resource.pk)


def get_resource_from_request(request: Request, kwargs: Dict[Any, Any]) -> ResourceStub:
    slug = kwargs.get('resource_slug', '')
    tail = kwargs.get('tail', '')

    application = get_object_or_404(models.Application, slug=kwargs.get('app_slug', ''))
    resources: QuerySet[ResourceStub] = models.ResourceStub.objects.filter(
        application=application,
        slug=slug,
    )

    if resource := resources.filter(
        method=request.method, tail=tail, response_type=ResponseChoices.CUSTOM
    ).last():  # custom response
        return resource

    if resource := resources.filter(
        method=request.method, tail=tail, response_type=ResponseChoices.PROXY_CURRENT
    ).last():  # proxy specific URL
        return resource

    if resource := resources.filter(response_type=ResponseChoices.PROXY_GLOBAL).last():  # global proxy
        return resource

    raise Http404('No stub resource found.')
