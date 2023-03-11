import pytest
from rest_framework.test import APIClient

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
