import ast
from time import sleep
from typing import Any

from django.shortcuts import get_object_or_404
from requests import JSONDecodeError
from rest_framework.renderers import JSONRenderer
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps import models
from apps.renderers import SimpleTextRenderer, TextToXMLRenderer
from apps.services import request_log_create, proxy_request, clean_headers


class ResponseStubView(APIView):
    renderer_classes = (TextToXMLRenderer, SimpleTextRenderer, JSONRenderer)

    @staticmethod
    def make_response(request: Request, **kwargs: Any):
        application = get_object_or_404(models.Application, slug=kwargs.get('app_slug', ''))
        resource = get_object_or_404(models.ResourceStub,
                                     application=application,
                                     uri=kwargs.get('resource_slug', ''),
                                     method=request.method)
        response_stub = resource.response
        request.accepted_renderer = response_stub.renderer

        if resource.proxy_destination_address:

            destination_response = proxy_request(
                incoming_request=request,
                destination_url=resource.proxy_destination_address
            )
            response_body = destination_response.content.decode()
            response_headers = clean_headers(dict(destination_response.headers))
            request_log_create(application=application,
                               resource_stub=resource,
                               request=request,
                               response_status_code=destination_response.status_code,
                               response_body=response_body,
                               response_headers=response_headers)

            try:
                response_body = destination_response.json()
            except JSONDecodeError:
                pass

            print('Response'.center(120, '.'))
            print('Status Code: ', destination_response.status_code)
            print('Body: ', response_body)
            from pprint import pprint
            pprint(response_headers)
            # print('Headers: ', response_headers)
            print('.' * 120)

            return Response(
                data=response_body,
                status=destination_response.status_code,
                headers=response_headers
            )

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
