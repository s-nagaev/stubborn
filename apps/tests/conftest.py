import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

from apps.tests.application_json_mock import JSON_data
from apps.tests.data import create_user


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def api_client_user() -> APIClient:
    user = create_user()
    client = APIClient()
    client.force_login(user=user)

    yield client

    client.logout()


@pytest.fixture
def mocked_application_file() -> SimpleUploadedFile:
    return SimpleUploadedFile(
        'application_dump.json',
        str.encode(JSON_data)
    )
