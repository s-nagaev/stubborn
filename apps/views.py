import json
import logging
from typing import Any, cast
from urllib.parse import urlparse

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.safestring import mark_safe
from rest_framework import permissions, status
from rest_framework.authentication import SessionAuthentication
from rest_framework.renderers import JSONRenderer
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_xml.renderers import XMLRenderer

from apps import models
from apps.enums import ResponseChoices
from apps.renderers import SimpleTextRenderer, TextToXMLRenderer
from apps.serializers import ApplicationSerializer
from apps.services import (
    get_regular_response,
    get_resource_from_request,
    get_third_party_service_response,
    save_application_from_json_object,
)
from apps.utils import log_request

logger = logging.getLogger()


class ResponseStubView(APIView):
    http_method_names = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options']
    renderer_classes = (JSONRenderer, TextToXMLRenderer, SimpleTextRenderer, XMLRenderer)

    @staticmethod
    def make_response(request: Request, **kwargs: Any) -> Response:
        log_request(request_logger=logger, request=request)

        application = get_object_or_404(models.Application, slug=kwargs.get('app_slug', ''), is_enabled=True)
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

    authentication_classes = (SessionAuthentication,)
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['post']
    renderer_classes = (JSONRenderer,)

    def post(self, request: Request, **kwargs: Any):
        log_id = kwargs.get('log_id', 0)
        log = get_object_or_404(models.RequestLog, pk=log_id)
        parsed_url = urlparse(log.url)
        path = cast(str, parsed_url.path)

        path_parts = path.split('/', 3)

        if len(path_parts) == 3:
            _, _, resource_slug = path_parts
            tail = ''
        else:
            _, _, resource_slug, tail = path.split('/', 3)

        response, _ = models.ResponseStub.objects.get_or_create(
            status_code=cast(int, log.status_code),
            headers=log.response_headers,
            body=log.response_body,
            application=log.application,
            format=log.response_format,
            creator=request.user,
            description=f'(for {resource_slug})',
        )

        same_resource = models.ResourceStub.objects.filter(
            application=log.application, slug=resource_slug, tail=tail, method=log.method, is_enabled=True
        ).last()

        if same_resource:
            same_resource.is_enabled = False
            same_resource.save()
            admin_url = reverse('admin:apps_resourcestub_change', args=(same_resource.pk,))
            msg = mark_safe(f'A same resource stub has been disabled. <a href={admin_url}>Click here to check it.</a>')
            messages.info(request, msg)

        resource = models.ResourceStub.objects.create(
            response_type=ResponseChoices.CUSTOM,
            slug=resource_slug,
            tail=tail,
            response=response,
            description='Auto-created proxy stub',
            application=log.application,
            method=log.method,
            creator=request.user,
            is_enabled=True,
        )

        return redirect(reverse('admin:apps_resourcestub_change', args=(resource.pk,)))


class HealthCheckView(APIView):
    """Liveness probe for docker healthcheck, etc."""

    renderer_classes = (JSONRenderer,)

    @staticmethod
    def get(request: Request) -> Response:
        return Response(status=status.HTTP_200_OK)


class ExportToFile(APIView):
    """Export Application as a JSON file."""

    renderer_classes = (JSONRenderer,)

    @staticmethod
    def get(request: Request, application_id: str) -> Response:
        """Export Application by id as a JSON file.
        args:
            request: Request object.
            application_id: application's id.

        returns:
            JSON file with the application data.
        """

        application = get_object_or_404(models.Application, pk=application_id)
        serialized_data = ApplicationSerializer(application)
        file_name = f'{application.pk}-application-data.json'

        response = Response(
            data=serialized_data.data,
            content_type='application/json',
            headers={'Content-Disposition': f'attachment; filename={file_name}'},
        )
        return response


class ImportFromFile(APIView):
    """Import Application from a JSON file."""

    authentication_classes = (SessionAuthentication,)
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = (JSONRenderer,)

    @staticmethod
    def post(request: Request) -> Response:
        """Import Application from a JSON file.
        args:
            request: Request object.

        returns:
            201 status if successfully imported.
        """
        file_object = request.FILES.get('file')

        if not file_object:
            return Response(data={'error': 'File object was not attached.'}, status=status.HTTP_400_BAD_REQUEST)
        update = bool(request.data.get('update'))

        file_data = file_object.file.read()
        decoded_file_data = file_data.decode("utf-8")
        jsonyfied_file_data = json.loads(decoded_file_data)

        save_application_from_json_object(jsonyfied_file_data, update, user=request.user)

        return Response(status=status.HTTP_201_CREATED)
