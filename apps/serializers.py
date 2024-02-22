from typing import Any, Optional

from django.db.utils import IntegrityError
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.models import Application, RequestStub, ResourceHook, ResourceStub, ResponseStub


class RequestStubSerializer(serializers.ModelSerializer):
    """RequestStub model serializer."""

    name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    query_params = serializers.JSONField(required=False, allow_null=False)
    uri = serializers.URLField(required=False, allow_null=False)
    method = serializers.CharField(required=False, allow_null=False)

    class Meta:
        model = RequestStub
        fields = ['name', 'query_params', 'uri', 'method']


class ResourceHookSerializer(serializers.ModelSerializer):
    """ResourceHook model serializer."""

    action = serializers.CharField(required=False, allow_null=False)
    lifecycle = serializers.CharField(required=False, allow_null=False)
    order = serializers.IntegerField(required=False, allow_null=False)
    timeout = serializers.IntegerField(required=False, allow_null=False)
    request = RequestStubSerializer(required=False, allow_null=True)

    class Meta:
        model = ResourceHook
        fields = ['action', 'lifecycle', 'order', 'timeout', 'request']

    def create(self, validated_data: dict[str, Any]) -> ResourceHook:
        """ResourceHook creation.

        Args:
            validated_data: Object with resource hook validated data.

        Returns:
            A ResourceHook object.
        """
        try:
            request_data = validated_data.pop('request', None)
            request_object = None
            application = validated_data.pop('application', None)

            if request_data:
                serialized_request = RequestStubSerializer(data=request_data)
                serialized_request.is_valid()
                request_object = serialized_request.save(application=application, creator=application.owner)

            resource_hook = ResourceHook.objects.create(**validated_data, request=request_object)
        except IntegrityError as error:
            raise ValidationError(error)
        return resource_hook


class ResponseStubSerializer(serializers.ModelSerializer):
    """ResponseStub model serializer."""

    status_code = serializers.IntegerField(required=True, allow_null=False)

    class Meta:
        model = ResponseStub
        fields = ['status_code']


class ResourceStubSerializer(serializers.ModelSerializer):
    """ResourceStub model serializer."""

    description = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    method = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    proxy_destination_address = serializers.URLField(required=False, allow_blank=True, allow_null=True)
    response_type = serializers.CharField(required=False, allow_null=False)
    slug = serializers.SlugField(required=False, allow_null=False)
    tail = serializers.CharField(required=False, allow_blank=True)
    is_enabled = serializers.BooleanField(required=False, allow_null=False)
    inject_stubborn_headers = serializers.BooleanField(required=False, allow_null=False)
    hooks = ResourceHookSerializer(many=True, required=False, allow_null=True)
    response = ResponseStubSerializer(required=False, allow_null=True)

    class Meta:
        model = ResourceStub
        fields = [
            'description',
            'method',
            'proxy_destination_address',
            'response_type',
            'slug',
            'tail',
            'is_enabled',
            'inject_stubborn_headers',
            'hooks',
            'response',
        ]

    def create(self, validated_data: dict[str, Any]) -> ResourceStub:
        """ResourceStub creation.

        Args:
            validated_data: Object with resource stub validated data.

        Returns:
            A ResourceStub object.
        """
        hooks_data = validated_data.pop('hooks', [])
        hooks_list = []
        response_data = validated_data.pop('response', None)

        try:
            resource = ResourceStub.objects.create(**validated_data)
            resource.creator = resource.application.owner
            resource.save()

            for hook_data in hooks_data:
                serialized_hook = ResourceHookSerializer(data=hook_data)
                serialized_hook.is_valid()
                hook = serialized_hook.save(resource=resource, application=resource.application)
                hooks_list.append(hook)

            resource.hooks.set(hooks_list)

            if response_data:
                serialized_response = ResponseStubSerializer(data=response_data)
                serialized_response.is_valid()
                resource.response = serialized_response.save(application=resource.application, creator=resource.creator)
                resource.save()
        except IntegrityError as error:
            raise ValidationError(error)
        return resource


class ApplicationSerializer(serializers.ModelSerializer):
    """Application model serializer."""

    description = serializers.CharField(required=False, allow_null=True)
    name = serializers.CharField(required=True, allow_null=False)
    slug = serializers.CharField(required=True, allow_null=False)
    resources = ResourceStubSerializer(many=True, required=False, allow_null=True)
    responses = ResponseStubSerializer(many=True, required=False, allow_null=True)
    requests = RequestStubSerializer(many=True, required=False, allow_null=True)

    class Meta:
        model = Application
        fields = ['description', 'name', 'slug', 'resources', 'responses', 'requests']

    @staticmethod
    def make_dependency_object_list(
        validated_data: list[dict[str, Any]], application: Application, serializer: serializers.ModelSerializer
    ) -> list[Any]:
        """Make a dependencies list to be associated with a given Application.

        Args:
            validated_data:  Object with validated dependency data.
            application: Application instance.
            serializer: Dependency object serializer.

        Returns:
            List of dependency objects.
        """
        dependency_object_list = []
        for data in validated_data:
            serialized_response = serializer(data=data)
            serialized_response.is_valid()
            dependency_object = serialized_response.save(application=application, creator=application.owner)
            dependency_object_list.append(dependency_object)
        return dependency_object_list

    def create(self, validated_data: dict[str, Any]) -> Application:
        """Application creation with all but logs and users info nested fields.

        Args:
            validated_data: Object with application validated data.

        Returns:
            An Application object.
        """
        resources_data = validated_data.pop('resources', [])
        responses_data = validated_data.pop('responses', [])
        requests_data = validated_data.pop('requests', [])

        try:
            application = Application.objects.create(**validated_data)

            resources_list = self.make_dependency_object_list(resources_data, application, ResourceStubSerializer)
            application.resources.set(resources_list)

            responses_list = self.make_dependency_object_list(responses_data, application, ResponseStubSerializer)
            application.responses.set(responses_list)

            requests_list = self.make_dependency_object_list(requests_data, application, RequestStubSerializer)
            application.requests.set(requests_list)

        except IntegrityError as error:
            raise ValidationError(error)

        return application

    def update(self, application: Application, validated_data: dict[str, Any]) -> Optional[Application]:
        """Update Application with all but logs and users info nested fields.

        Args:
            application: Application object.
            validated_data: Object with application validated data.

        Returns:
            An Application object.
        """
        resources_data = validated_data.pop('resources', [])
        responses_data = validated_data.pop('responses', [])
        requests_data = validated_data.pop('requests', [])

        application.resources.all().delete()
        application.responses.all().delete()
        application.requests.all().delete()

        if application:
            resources_list = self.make_dependency_object_list(resources_data, application, ResourceStubSerializer)
            application.resources.set(resources_list)

            responses_list = self.make_dependency_object_list(responses_data, application, ResponseStubSerializer)
            application.responses.set(responses_list)

            requests_list = self.make_dependency_object_list(requests_data, application, RequestStubSerializer)
            application.requests.set(requests_list)

        for field in validated_data.keys():
            setattr(application, field, validated_data[field])
        application.save()

        return application
