import os
from typing import Dict

import requests
from django.conf import settings
from requests import Response
from rest_framework.request import Request

from apps.models import Application, RequestLog, ResourceStub, ResponseStub
from apps.utils import clean_headers


def request_log_create(application: Application,
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
        url=os.path.join(settings.DOMAIN_DISPLAY, application.slug, resource_stub.uri),
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
        destination_url=destination_url
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
        data=body
    )
    return destination_response
