import ast
import json
from time import sleep
from typing import Any

from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps import models


class ResponseStubView(APIView):

    @staticmethod
    def make_response(request: Request, **kwargs: Any):
        app = get_object_or_404(models.Application, slug=kwargs.get('app_slug', ''))
        resource = get_object_or_404(models.ResourceStub,
                                     application=app,
                                     uri=kwargs.get('resource_slug', ''),
                                     method=request.method)
        response = resource.response

        models.RequestLog.objects.create(
            params=request.query_params,
            body=json.loads(request.body) if request.body else None,
            headers=dict(request.headers),
            application=app,
            resource=resource,
            response=response,
            ipaddress=request.META.get('REMOTE_ADDR'),
            x_real_ip=request.headers.get('X-REAL-IP')
        )
        sleep(response.timeout)

        return Response(
            data=ast.literal_eval(response.body or ''),
            status=response.status_code,
            headers=response.headers
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
