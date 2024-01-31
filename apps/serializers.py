from typing import Any, List, Optional

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
        args:
            validated_data: Object with resource hook validated data.
        returns:
            A ResourceHook object.
        """
        try:
            request_data, request = validated_data.pop('request', None), None
            application = validated_data.pop('application', None)

            if request_data:
                serialized_request = RequestStubSerializer(data=request_data)
                serialized_request.is_valid()
                request = serialized_request.save(application=application)

            resource_hook = ResourceHook.objects.create(
                **validated_data,
                request=request
            )
        except IntegrityError as error:
            raise ValidationError(error)
        return resource_hook


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

    class Meta:
        model = ResourceStub
        fields = ['description', 'method', 'proxy_destination_address', 'response_type', 'slug', 'tail',
                  'is_enabled', 'inject_stubborn_headers', 'hooks']

    def create(self, validated_data: dict[str, Any]) -> ResourceStub:
        """ResourceStub creation.
        args:
            validated_data: Object with resource stub validated data.
        returns:
            A ResourceStub object.
        """
        hooks_data, hooks_list = validated_data.pop('hooks', []), []

        try:
            resource = ResourceStub.objects.create(**validated_data)

            for hook_data in hooks_data:
                serialized_hook = ResourceHookSerializer(data=hook_data)
                serialized_hook.is_valid()
                hook = serialized_hook.save(resource=resource,
                                            application=resource.application)
                hooks_list.append(hook)

            resource.hooks.set(hooks_list)
        except IntegrityError as error:
            raise ValidationError(error)
        return resource


class ResponseStubSerializer(serializers.ModelSerializer):
    """ResponseStub model serializer."""
    status_code = serializers.IntegerField(required=True, allow_null=False)
    resources = ResourceStubSerializer(many=True, required=False, allow_null=True)

    class Meta:
        model = ResponseStub
        fields = ['status_code', 'resources']

    def create(self, validated_data: dict[str, Any]) -> ResponseStub:
        """ResponseStub creation.
        args:
            validated_data: Object with response stub validated data.
        returns:
            A ResponseStub object.
        """
        resources_data, resources_list = validated_data.pop('resources', []), []

        try:
            response = ResponseStub.objects.create(**validated_data)

            for resource_data in resources_data:
                serialized_resource = ResourceStubSerializer(data=resource_data)
                serialized_resource.is_valid()
                resource = serialized_resource.save(response=response, application=response.application)
                resources_list.append(resource)
            response.resources.set(resources_list)
        except IntegrityError as error:
            raise ValidationError(error)
        return response


class ApplicationSerializer(serializers.ModelSerializer):
    """Application model serializer."""
    description = serializers.CharField(required=False, allow_null=True)
    name = serializers.CharField(required=True, allow_null=False)
    slug = serializers.CharField(required=True, allow_null=False)
    responses = ResponseStubSerializer(many=True, required=False, allow_null=True)

    class Meta:
        model = Application
        fields = ['description', 'name', 'slug', 'responses']

    @staticmethod
    def save_responses(responses_data: List[dict[str, Any]], application: Application) -> List[ResponseStub]:
        """Save application's responses.
        args:
            responses_data:  Object with responses data.
            application: Application instance.
        returns:
            List of ResponseStubs.
        """
        responses_list = []
        for response_data in responses_data:
            serialized_response = ResponseStubSerializer(data=response_data)
            serialized_response.is_valid()
            response = serialized_response.save(application=application)
            responses_list.append(response)
        return responses_list

    def create(self, validated_data: dict[str, Any]) -> Application:
        """Application creation with all but logs and users info nested fields.
        args:
            validated_data: Object with application validated data.
        returns:
            An Application object.
        """
        responses_data = validated_data.pop('responses', [])

        try:
            application = Application.objects.create(
                **validated_data,
            )
            responses_list = self.save_responses(responses_data, application)

            application.responses.set(responses_list)
        except IntegrityError as error:
            raise ValidationError(error)

        return application

    def update(self, application: Application, validated_data: dict[str, Any]) -> Optional[Application]:
        """Update Application with all but logs and users info nested fields.
        args:
            application: Application object.
            validated_data: Object with application validated data.
        returns:
            An Application object.
        """
        responses_data = validated_data.pop('responses', [])

        if application and responses_data:
            application.responses.all().delete()
            responses_list = self.save_responses(responses_data, application)
            application.responses.set(responses_list)

        return application
