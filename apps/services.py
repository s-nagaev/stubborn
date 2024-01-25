import json
import logging
import os
from typing import Any, TypeVar, cast

import requests
from django.conf import settings
from django.db.models import QuerySet
from django.http import Http404, HttpResponse as DjangoNativeResponse
from django.shortcuts import get_object_or_404
from requests import Response
from rest_framework.request import Request
from rest_framework.response import Response as RestFrameworkResponse

from apps import enums, hooks, models
from apps.enums import ResponseChoices
from apps.models import Application, RequestLog, ResourceStub, ResponseStub
from apps.utils import add_stubborn_headers, clean_headers, log_response, response_body_can_be_logged

logger = logging.getLogger(__name__)

StubbornSwitchableResource = TypeVar('StubbornSwitchableResource')


def request_log_create(
    application: Application,
    resource_stub: ResourceStub,
    request: Request,
    response_stub: ResponseStub = None,
    response_status_code: int = None,
    response_body: str = None,
    response_headers: dict = None,
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
        method=method,
        url=destination_url,
        params=query_params,
        headers=headers,
        data=body.encode('utf8'),
    )

    return destination_response


def get_regular_response(application: Application, request: Request, resource: ResourceStub) -> RestFrameworkResponse:
    hooks.before_request(resource)
    response_stub = cast(ResponseStub, resource.response)
    request.accepted_renderer = response_stub.renderer
    response_body = response_stub.body_rendered
    headers = response_stub.headers

    request_log_record = request_log_create(
        application=application,
        resource_stub=resource,
        response_stub=response_stub,
        request=request,
        response_status_code=response_stub.status_code,
        response_body=response_body,
        response_headers=headers,
    )

    if resource.inject_stubborn_headers:
        headers = add_stubborn_headers(initial_headers=response_stub.headers, log_id=request_log_record.id)
        request_log_record.response_headers = headers
        request_log_record.save()

    if response_stub.is_json_format:
        response_data = json.loads(response_body) if response_body else None
    else:
        response_data = response_body

    hooks.after_request(resource)

    log_response(
        response_logger=logger,
        resource_type='STUB',
        status_code=response_stub.status_code,
        request_log_id=request_log_record.id,
        body=response_data,
        headers=headers,
    )

    try:
        return RestFrameworkResponse(data=response_data, status=response_stub.status_code, headers=headers)
    finally:
        if resource.hooks.filter(lifecycle=enums.Lifecycle.AFTER_RESPONSE).exists():
            hooks.after_response(resource.pk)


def get_third_party_service_response(
    application: Application, request: Request, resource: ResourceStub, tail: str = None
) -> DjangoNativeResponse:
    if tail and resource.response_type == ResponseChoices.PROXY_CURRENT:
        raise Http404()

    destination_address = str(resource.proxy_destination_address)
    remote_url = os.path.join(destination_address, tail) if tail else destination_address

    hooks.before_request(resource)
    destination_response = proxy_request(incoming_request=request, destination_url=remote_url)
    hooks.after_request(resource)
    response_headers = clean_headers(dict(destination_response.headers))
    content_type = response_headers.get('Content-Type', 'application/json')  # assume that

    if response_body_can_be_logged(content_type=content_type):
        body_for_log = destination_response.content.decode()
    else:
        body_for_log = f"The {content_type} data is not logged."

    request_log_record = request_log_create(
        application=application,
        resource_stub=resource,
        request=request,
        response_status_code=destination_response.status_code,
        response_body=body_for_log,
        response_headers=response_headers,
        proxied=True,
        destination_url=remote_url,
    )

    if resource.inject_stubborn_headers:
        response_headers = add_stubborn_headers(initial_headers=response_headers, log_id=request_log_record.id)
        request_log_record.response_headers = response_headers
        request_log_record.save()

    log_response(
        response_logger=logger,
        resource_type='PROXY',
        status_code=destination_response.status_code,
        request_log_id=request_log_record.id,
        body=body_for_log,
        headers=str(response_headers),
    )

    try:
        return DjangoNativeResponse(
            content=destination_response.content, status=destination_response.status_code, headers=response_headers
        )
    finally:
        if resource.hooks.filter(lifecycle=enums.Lifecycle.AFTER_RESPONSE).exists():
            hooks.after_response(resource.pk)


def get_resource_from_request(request: Request, kwargs: dict[Any, Any]) -> ResourceStub:
    slug = kwargs.get('resource_slug', '')
    tail = kwargs.get('tail', '')

    application = get_object_or_404(models.Application, slug=kwargs.get('app_slug', ''))
    resources: QuerySet[ResourceStub] = models.ResourceStub.objects.filter(
        application=application, slug=slug, is_enabled=True
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


def get_same_enabled_resource_stub(reference_obj: ResourceStub) -> ResourceStub | None:
    same_stubs = ResourceStub.objects.filter(
        application=reference_obj.application,
        slug=reference_obj.slug,
        tail=reference_obj.tail,
        method=reference_obj.method,
        is_enabled=True,
    )
    if same_stubs.exists():
        return same_stubs.last()
    return None


def get_same_enabled_application(reference_obj: Application) -> Application | None:
    same_stubs = Application.objects.filter(
        slug=reference_obj.slug,
        name=reference_obj.name,
        is_enabled=True,
    )
    if same_stubs.exists():
        return same_stubs.last()
    return None


def turn_off_same_resource(resource: Application | ResourceStub) -> Application | ResourceStub | None:
    """Find & disable the same resource stub or application as provided.

    Args:
        resource: Application or ResourceStub instance.

    Returns:
        Disabled Application or ResourceStub instance if it exists, None otherwise.
    """
    same_resource: Application | ResourceStub | None
    if isinstance(resource, Application):
        same_resource = get_same_enabled_application(reference_obj=resource)
    elif isinstance(resource, ResourceStub):
        same_resource = get_same_enabled_resource_stub(reference_obj=resource)
    else:
        raise ValueError(
            f"Wrong resource provided: {type(resource)}. Only Application or ResourceStub instance allowed."
        )

    if not same_resource:
        return None

    same_resource.is_enabled = False
    same_resource.save()
    same_resource.refresh_from_db()
    return same_resource
