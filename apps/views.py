import ast
import json
from typing import Any

from django.shortcuts import get_object_or_404
from django.shortcuts import render

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps import models


@api_view(['GET', 'POST'])
def hello_world(request, **kwargs):
    print(kwargs)
    return Response(
        data={"status": "ok"},
        status=503,
        headers={}
    )


class ResponseStubView(APIView):

    @staticmethod
    def make_response(request: Request, **kwargs: Any):
        app = get_object_or_404(models.Application, slug=kwargs.get('app_slug', ''))
        resource = get_object_or_404(models.ResourceStub, uri=kwargs.get('resource_slug', ''), application=app)
        response = resource.response
        models.RequestLog.objects.create(
            params=request.query_params,
            body=json.loads(request.body) if request.body else None,
            headers=dict(request.headers),
            application=app,
            resource=resource,
            ipaddress=request.META.get('REMOTE_ADDR'),
            x_real_ip=request.headers.get('X-REAL-IP')
        )
        return Response(
            data=ast.literal_eval(response.body),
            status=response.status_code,
            headers=response.headers
        )

    @staticmethod
    def get(request: Request, **kwargs: Any) -> Response:
        return ResponseStubView.make_response(request=request, **kwargs)
