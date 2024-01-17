from typing import OrderedDict

from apps.models import Application, ResponseStub
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class UserSerializer(serializers.Serializer):
    """User model serializer."""
    username = serializers.CharField(required=False, allow_blank=True)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    is_staff = serializers.BooleanField(required=True)
    is_active = serializers.BooleanField(required=True)
    date_joined = serializers.DateTimeField(required=True)


class RequestStubSerializer(serializers.Serializer):
    """RequestStub model serializer."""
    name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    query_params = serializers.JSONField(required=False, allow_null=False)
    uri = serializers.URLField(required=False, allow_null=False)
    method = serializers.CharField(required=False, allow_null=False)
    creator = UserSerializer(required=False, allow_null=True)


class ResourceHookSerializer(serializers.Serializer):
    """ResourceHook model serializer."""
    action = serializers.CharField(required=False, allow_null=False)
    lifecycle = serializers.CharField(required=False, allow_null=False)
    order = serializers.IntegerField(required=False, allow_null=False)
    timeout = serializers.IntegerField(required=False, allow_null=False)
    request = RequestStubSerializer(required=False, allow_null=True)


class ResourceStubSerializer(serializers.Serializer):
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


class ResponseStubSerializer(serializers.ModelSerializer):
    """ResponseStub model serializer."""
    status_code = serializers.IntegerField(required=True, allow_null=False)
    creator = UserSerializer(required=False, allow_null=True)
    resources = ResourceStubSerializer(many=True, required=False, allow_null=True)

    class Meta:
        model = ResponseStub
        fields = ['status_code', 'creator', 'resources']

    # def create(self, validated_data: OrderedDict) -> ResponseStub:
    #     """ResponseStub creation.
    #     args:
    #         validated_data: Ordered dict object with response stub validated data.
    #     returns:
    #         An ResponseStub object.
    #     """
    #     response = ResponseStub.objects.create(
    #         **validated_data
    #     )
    #     return response


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

    def create(self, validated_data: OrderedDict) -> Application:
        """Application creation with all but logs nested fields.
        args:
            validated_data: Ordered dict object with application validated data.
        returns:
            An Application object.
        """
        owner_data, owner = validated_data.pop('owner', None), None
        responses_data, responses_list = validated_data.pop('responses', []), []

        try:
            if owner_data:
                owner, was_created = User.objects.get_or_create(**owner_data)
        except IntegrityError as error:
            raise ValidationError(error)

        try:
            application = Application.objects.create(
                **validated_data,
                owner=owner
            )
            if responses_data:
                for response_data in responses_data:
                    response = ResponseStubSerializer(data=response_data)
                    response.is_valid()
                    response_object = response.save(application=application)
                    responses_list.append(response_object)

            application.responses.set(responses_list)
        except IntegrityError as error:
            raise ValidationError(error)

        return application
