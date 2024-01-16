from rest_framework import serializers


class UserSerializer(serializers.Serializer):
    """User model serializer."""
    pk = serializers.IntegerField(required=True)
    username = serializers.CharField(read_only=True)
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


class ResponseStubSerializer(serializers.Serializer):
    """ResponseStub model serializer."""
    status_code = serializers.IntegerField(required=True, allow_null=False)
    creator = UserSerializer(required=False, allow_null=True)
    resources = ResourceStubSerializer(many=True, required=False, allow_null=True)


class ApplicationSerializer(serializers.Serializer):
    """Application model serializer."""
    description = serializers.CharField(required=False, allow_null=True)
    name = serializers.CharField(required=True, allow_null=False)
    slug = serializers.CharField(required=True, allow_null=False)
    owner = UserSerializer()
    responses = ResponseStubSerializer(many=True, required=False, allow_null=True)