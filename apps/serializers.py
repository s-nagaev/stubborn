from datetime import datetime
from typing import Any, List, Tuple

from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from pytz import utc
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.models import Application, RequestStub, ResourceHook, ResourceStub, ResponseStub


class UserSerializer(serializers.ModelSerializer):
    """User model serializer."""
    username = serializers.CharField(required=False, allow_blank=True)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    is_staff = serializers.BooleanField(required=True)
    is_active = serializers.BooleanField(required=True)
    date_joined = serializers.DateTimeField(required=False, default=datetime.utcnow().replace(tzinfo=utc))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_staff', 'is_active', 'date_joined']


class RequestStubSerializer(serializers.ModelSerializer):
    """RequestStub model serializer."""
    name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    query_params = serializers.JSONField(required=False, allow_null=False)
    uri = serializers.URLField(required=False, allow_null=False)
    method = serializers.CharField(required=False, allow_null=False)
    creator = UserSerializer(required=False, allow_null=True)

    class Meta:
        model = RequestStub
        fields = ['name', 'query_params', 'uri', 'method', 'creator']

    def create(self, validated_data: dict[str, Any]) -> RequestStub:
        """RequestStub creation.
        args:
            validated_data: Object with request stub validated data.
        returns:
            A RequestStub object.
        """
        try:
            creator_data, creator = validated_data.pop('creator', None), None
            if creator_data:
                creator, was_created = User.objects.get_or_create(**creator_data)

            request_stub = RequestStub.objects.create(
                **validated_data,
                creator=creator
            )
        except IntegrityError as error:
            raise ValidationError(error)
        return request_stub


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
    creator = UserSerializer(required=False, allow_null=True)
    is_enabled = serializers.BooleanField(required=False, allow_null=False)
    inject_stubborn_headers = serializers.BooleanField(required=False, allow_null=False)
    hooks = ResourceHookSerializer(many=True, required=False, allow_null=True)

    class Meta:
        model = ResourceStub
        fields = ['description', 'method', 'proxy_destination_address', 'response_type', 'slug', 'tail', 'creator',
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
    creator = UserSerializer(required=False, allow_null=True)
    resources = ResourceStubSerializer(many=True, required=False, allow_null=True)

    class Meta:
        model = ResponseStub
        fields = ['status_code', 'creator', 'resources']

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
    owner = UserSerializer(required=False, allow_null=True)
    responses = ResponseStubSerializer(many=True, required=False, allow_null=True)

    class Meta:
        model = Application
        fields = ['description', 'name', 'slug', 'owner', 'responses']

    @staticmethod
    def save_owner(owner_data: dict[str, Any]) -> Tuple[User, bool]:
        """Save owner or get the existing one.
        args:
            owner_data: Object with owner data.
        returns:
            User object.
            Flag describing if user was created. True if was created.
        """
        try:
            owner, was_created = User.objects.get_or_create(**owner_data)
        except IntegrityError as error:
            raise ValidationError(error)
        return owner, was_created

    @staticmethod
    def save_responses(responses_data: List[dict[str, Any]], application: Application) -> List[ResponseStub]:
        """Save or update application's responses.
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
        """Application creation with all but logs nested fields.
        args:
            validated_data: Object with application validated data.
        returns:
            An Application object.
        """
        owner_data, owner = validated_data.pop('owner', None), None
        responses_data = validated_data.pop('responses', [])

        if owner_data:
            owner, was_created = self.save_owner(owner_data)

        try:
            application = Application.objects.create(
                **validated_data,
                owner=owner
            )
            responses_list = self.save_responses(responses_data, application)

            application.responses.set(responses_list)
        except IntegrityError as error:
            raise ValidationError(error)

        return application

    def update(self, old_application: Application, validated_data: dict[str, Any]) -> Application:
        """Update Application with all but logs nested fields.
        args:
            validated_data: Object with application validated data.
        returns:
            An Application object.
        """
        owner_data, owner = validated_data.pop('owner', None), None
        try:
            if owner_data:
                owner, was_created = User.objects.get_or_create(**owner_data)
        except IntegrityError as error:
            raise ValidationError(error)
        # old_application.save(**validated_data, owner=owner)
        return old_application
