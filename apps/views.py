import ast
from time import sleep
from typing import Any

from django.shortcuts import get_object_or_404
from rest_framework.renderers import JSONRenderer
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps import models
from apps.renderers import SimpleTextRenderer, TextToXMLRenderer
from apps.services import request_log_create


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

        request_log_create(application=application,
                           resource_stub=resource,
                           response_stub=response_stub,
                           request=request)

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
