from typing import Dict

import requests
from requests import Response
from rest_framework.request import Request

from apps.models import Application, RequestLog, ResourceStub, ResponseStub


def request_log_create(application: Application,
                       resource_stub: ResourceStub,
                       request: Request,
                       response_stub: ResponseStub = None,
                       response_status_code: int = None,
                       response_body: str = None,
                       response_headers: Dict = None) -> RequestLog:
    log_record = RequestLog.objects.create(
        application=application,
        resource=resource_stub,
        response=response_stub,
        params=request.query_params,
        request_body=request.body.decode(),
        request_headers=dict(request.headers),
        status_code=response_status_code,
        response_body=response_body,
        response_headers=response_headers,
        ipaddress=request.META.get('REMOTE_ADDR'),
        x_real_ip=request.headers.get('X-REAL-IP')
    )
    return log_record


def normalize_request_headers(headers: Dict[str, str]) -> Dict[str, str]:
    pass

def clean_response_headers(headers: Dict[str, str]) -> Dict[str, str]:
    pass


def clean_headers(headers: Dict[str, str]) -> Dict[str, str]:
    """Hop-by-hop headers are meaningful only for a single transport-level connection,
    and are not stored by caches or forwarded by proxies.
    See more at: https://www.w3.org/Protocols/rfc2616/rfc2616-sec13.html#sec13.5.1

    Args:
        headers: dictionary containing request/response headers.

    Returns:
       Headers dictionary without hop-by-hop headers.
    """

    hop_by_hop_headers = [
        'connection',
        'keep-alive',
        'proxy-authenticate',
        'proxy-authorization',
        'te',
        'trailers',
        'transfer-encoding',
        'upgrade',
    ]

    throw_out_headers = [
        'host',
        'server',
        'content-length',
        'content-encoding'
    ]

    unwanted_headers = hop_by_hop_headers + throw_out_headers
    headers = dict(headers)
    headers_names = list(headers.keys())
    for header_name in headers_names:
        if header_name.lower() in unwanted_headers:
            headers.pop(header_name)

    return headers


def proxy_request(incoming_request: Request, destination_url: str) -> Response:
    """Making a request identical to received one to the destination URL.

    Args:
        incoming_request: incoming request instance.
        destination_url: a remote server URL request "proxy" to.

    Returns:
        Destinations server's response.
    """
    method = incoming_request.method
    query_params = None#incoming_request.query_params
    body = None#incoming_request.body.decode()
    headers = clean_headers(incoming_request.headers)

    print('Request'.center(120, '-'))
    print('Method: ', method)
    print('URL: ', destination_url)
    print('Query Params: ', query_params)
    print('Request Body: ', body)
    print('Headers: ', headers)
    print('-' * 120)

    destination_response = requests.request(
        method=method,
        url=destination_url,
        params=query_params,
        headers=headers,
        data=body
    )
    return destination_response
