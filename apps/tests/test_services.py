from unittest.mock import MagicMock, patch

import pytest

from apps.services import get_same_enabled_resource_stub, proxy_request, turn_off_same_resource
from apps.tests.data import create_application, create_resource_stub


class TestProxy:
    @patch('requests.request', return_value=None)
    @pytest.mark.parametrize('request_method', ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
    def test_proxy_request_func(self, mocked_request_method, request_method):
        mocked_incoming_request = MagicMock()
        mocked_incoming_request.method = request_method
        mocked_incoming_request.query_params = {'param1': 'val1', 'param2': 'val2'}
        mocked_incoming_request.body.decode.return_value = '{"Status":"OK"}'
        mocked_incoming_request.headers = {'Content-Type': 'application/json'}

        destination_url = 'https://example.com/api/foo'

        proxy_request(incoming_request=mocked_incoming_request, destination_url=destination_url)

        mocked_request_method.assert_called_once()
        mocked_request_method.assert_called_with(
            method=request_method,
            url=destination_url,
            params={'param1': 'val1', 'param2': 'val2'},
            headers={'Content-Type': 'application/json'},
            data=b'{"Status":"OK"}',
        )

    @pytest.mark.django_db
    def test_get_same_enabled_resource_stub_resource_exists(self):
        application = create_application()
        slug = 'testslug'
        tail = 'some/tail/here'

        resource_disabled = create_resource_stub(
            application=application,
            method='GET',
            slug=slug,
            tail=tail,
            is_enabled=False,
        )
        resource_enabled = create_resource_stub(
            application=application, method='GET', slug=slug, tail=tail, is_enabled=True
        )

        same_stub = get_same_enabled_resource_stub(resource_disabled)

        assert same_stub
        assert same_stub == resource_enabled

    @pytest.mark.django_db
    def test_get_same_enabled_resource_stub_resource_doesnt_exist(self):
        application = create_application()
        resource_disabled = create_resource_stub(application=application, method='GET', is_enabled=False)

        for _ in range(10):
            create_resource_stub(application=application, method='GET', is_enabled=True)

        same_stub = get_same_enabled_resource_stub(resource_disabled)

        assert not same_stub

    @pytest.mark.django_db
    def test_turn_off_same_resource_stub_resource_exists(self):
        application = create_application()
        slug = 'testslug'
        tail = 'some/tail/here'

        resource_disabled = create_resource_stub(
            application=application,
            method='GET',
            slug=slug,
            tail=tail,
            is_enabled=False,
        )
        resource_enabled = create_resource_stub(
            application=application, method='GET', slug=slug, tail=tail, is_enabled=True
        )

        turned_off_resource = turn_off_same_resource(resource=resource_disabled)
        assert turned_off_resource

        resource_enabled.refresh_from_db()
        assert turned_off_resource == resource_enabled

    @pytest.mark.django_db
    def test_turn_off_same_resource_stub_resource_doesnt_exist(self):
        application = create_application()
        resource_disabled = create_resource_stub(application=application, method='GET', is_enabled=False)
        turned_off_resource = turn_off_same_resource(resource=resource_disabled)
        assert not turned_off_resource
