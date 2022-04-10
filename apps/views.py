import ast
from time import sleep
from typing import Any, cast

from django.shortcuts import get_object_or_404
from requests import JSONDecodeError
from rest_framework.renderers import JSONRenderer
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_xml.renderers import XMLRenderer

from apps import models
from apps.models import ResponseStub
from apps.renderers import SimpleTextRenderer, TextToXMLRenderer
from apps.services import proxy_request, request_log_create
from apps.utils import clean_headers


class ResponseStubView(APIView):
    renderer_classes = (JSONRenderer, TextToXMLRenderer, SimpleTextRenderer, XMLRenderer)

    @staticmethod
    def make_response(request: Request, **kwargs: Any) -> Response:
        application = get_object_or_404(models.Application, slug=kwargs.get('app_slug', ''))
        resource = get_object_or_404(models.ResourceStub,
                                     application=application,
                                     uri=kwargs.get('resource_slug', ''),
                                     method=request.method)
        request.accepted_renderer = JSONRenderer()

        if resource.proxy_destination_address:
            destination_response = proxy_request(
                incoming_request=request,
                destination_url=resource.proxy_destination_address
            )
            response_body = destination_response.content.decode()
            response_headers = clean_headers(dict(destination_response.headers))

            content_type = response_headers['Content-Type']

            if 'application/xml' in content_type:
                request.accepted_renderer = XMLRenderer()

            if 'text/html' in content_type:
                request.accepted_renderer = SimpleTextRenderer()

            request_log_create(application=application,
                               resource_stub=resource,
                               request=request,
                               response_status_code=destination_response.status_code,
                               response_body=response_body,
                               response_headers=response_headers,
                               proxied=True,
                               destination_url=resource.proxy_destination_address)

            try:
                response_body = destination_response.json()
            except JSONDecodeError:
                pass

            return Response(
                data=response_body,
                status=destination_response.status_code,
                headers=response_headers
            )

        response_stub = cast(ResponseStub, resource.response)
        request.accepted_renderer = response_stub.renderer

        request_log_create(application=application,
                           resource_stub=resource,
                           response_stub=response_stub,
                           request=request,
                           response_status_code=response_stub.status_code,
                           response_body=response_stub.body,
                           response_headers=response_stub.headers)

        sleep(response_stub.timeout)

        if response_stub.is_json_format:
            response_data = ast.literal_eval(response_stub.body or '')
        else:
            response_data = response_stub.body

        return Response(
            data=response_data,
            status=response_stub.status_code,
            headers=response_stub.headers
        )

    @staticmethod
    def get(request: Request, **kwargs: Any) -> Response:
        return ResponseStubView.make_response(request=request, **kwargs)

    @staticmethod
    def post(request: Request, **kwargs: Any) -> Response:
        return ResponseStubView.make_response(request=request, **kwargs)

    @staticmethod
    def put(request: Request, **kwargs: Any) -> Response:
        return ResponseStubView.make_response(request=request, **kwargs)

    @staticmethod
    def patch(request: Request, **kwargs: Any) -> Response:
        return ResponseStubView.make_response(request=request, **kwargs)

    @staticmethod
    def delete(request: Request, **kwargs: Any) -> Response:
        return ResponseStubView.make_response(request=request, **kwargs)
