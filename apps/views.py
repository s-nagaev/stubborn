from typing import Any, cast
from urllib.parse import urlparse

from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_xml.renderers import XMLRenderer

from apps import models
from apps.enums import ResponseChoices
from apps.renderers import SimpleTextRenderer, TextToXMLRenderer
from apps.services import get_regular_response, get_resource_from_request, get_third_party_service_response


class ResponseStubView(APIView):
    http_method_names = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options']
    renderer_classes = (JSONRenderer, TextToXMLRenderer, SimpleTextRenderer, XMLRenderer)

    @staticmethod
    def make_response(request: Request, **kwargs: Any) -> Response:
        application = get_object_or_404(models.Application, slug=kwargs.get('app_slug', ''))
        resource = get_resource_from_request(request, kwargs)
        request.accepted_renderer = JSONRenderer()

        if resource.response_type in (ResponseChoices.PROXY_CURRENT, ResponseChoices.PROXY_GLOBAL):
            return get_third_party_service_response(
                application=application, request=request, resource=resource, tail=kwargs.get('tail', '')
            )

        return get_regular_response(application=application, request=request, resource=resource)

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


class StubRequestView(APIView):
    """Stub selected request from the log view window.

    Composing the response stub according to the logged data.
    """

    http_method_names = ['post']
    renderer_classes = (JSONRenderer,)

    def post(self, request: Request, **kwargs: Any):
        log_id = kwargs.get('log_id', 0)
        log = get_object_or_404(models.RequestLog, pk=log_id)
        parsed_url = urlparse(log.url)
        path = cast(str, parsed_url.path)
        _, app_slug, resource_slug, tail = path.split('/', 3)

        response = models.ResponseStub.objects.create(
            status_code=cast(int, log.status_code),
            headers=log.response_headers,
            body=log.response_body,
            application=log.application,
            format=log.response_format,
            creator=request.user,
            description=f'(for {resource_slug})',
        )
        resource = models.ResourceStub.objects.create(
            response_type=ResponseChoices.CUSTOM,
            slug=resource_slug,
            tail=tail,
            response=response,
            description='Auto-created proxy stub',
            application=log.application,
            method=log.method,
            creator=request.user,
        )
        return redirect(reverse('admin:apps_resourcestub_change', args=(resource.pk,)))


class HealthCheckView(APIView):
    """Liveness probe for docker healthcheck, etc."""

    renderer_classes = (JSONRenderer,)

    @staticmethod
    def get(request: Request) -> Response:
        return Response(status=status.HTTP_200_OK)
