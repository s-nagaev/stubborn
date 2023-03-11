import json
from unittest.mock import patch

import pytest
from django.urls import reverse
from django.utils import timezone

from apps import models
from apps.enums import Action, Lifecycle, ResponseChoices
from apps.tests.data import (
    create_application,
    create_request_stub,
    create_resource_hook,
    create_resource_stub,
    create_response_stub,
)
from apps.tests.utils import get_url


@pytest.mark.django_db
class TestResponseStub:
    @pytest.mark.parametrize('method', ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD'])
    def test_response_with_allowed_request(self, method, api_client):
        application = create_application()
        response_stub = create_response_stub(application=application, status_code=200)
        resource = create_resource_stub(application=application, response=response_stub, method=method)
        response = api_client.generic(method=method, path=get_url(resource))
        assert response.status_code == 200

    def test_response_disabled(self, api_client):
        application = create_application()
        response_stub = create_response_stub(application=application, status_code=200)
        resource = create_resource_stub(application=application, response=response_stub, method='GET', is_enabled=False)
        response = api_client.generic(method='GET', path=get_url(resource))
        assert response.status_code == 404

    @pytest.mark.parametrize('request_method', ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD'])
    def test_response_with_not_allowed_request(self, request_method, api_client):
        application = create_application()
        response_stub = create_response_stub(application=application, status_code=200)
        resource = create_resource_stub(application=application, response=response_stub, method=request_method)

        methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD']
        methods.remove(request_method)

        for method in methods:
            response = api_client.generic(method=method, path=get_url(resource))
            assert response.status_code == 404, f'Stubbed method: {request_method}. Request method: {method}.'

    def test_response_body_json(self, api_client):
        application = create_application()
        response_stub = create_response_stub(
            application=application,
            status_code=200,
            body=json.dumps({'Status': 'OK'}),
            format='JSON',
            headers={'Content-Type': 'application/json'},
        )
        resource = create_resource_stub(application=application, response=response_stub, method='GET')
        response = api_client.get(path=get_url(resource))
        assert response.status_code == 200
        assert response.json() == {'Status': 'OK'}

    def test_empty_response_body_json(self, api_client):
        application = create_application()
        response_stub = create_response_stub(
            application=application,
            status_code=200,
            format='JSON',
            headers={'Content-Type': 'application/json'},
        )
        resource = create_resource_stub(application=application, response=response_stub, method='GET')
        response = api_client.get(path=get_url(resource))
        assert response.status_code == 200

    def test_response_timeout(self, api_client):
        application = create_application()
        response_stub = create_response_stub(application=application, status_code=200)
        resource = create_resource_stub(application=application, response=response_stub, method='GET')
        create_resource_hook(
            lifecycle=Lifecycle.AFTER_REQUEST.value, action=Action.WAIT.value, timeout=2, resource=resource
        )
        before_request_time = timezone.now()
        response = api_client.get(path=get_url(resource))
        after_request_time = timezone.now()
        assert response.status_code == 200
        assert (after_request_time - before_request_time).seconds == 2

    def test_response_body_xml(self, api_client):
        application = create_application()
        response_stub = create_response_stub(
            application=application,
            status_code=200,
            body='<Response><Status>OK</Status></Response>',
            format='XML',
            headers={'Content-Type': 'application/xml'},
        )
        resource = create_resource_stub(application=application, response=response_stub, method='GET')
        response = api_client.get(path=get_url(resource))
        assert response.status_code == 200
        assert response.content.decode() == (
            '<?xml version="1.0" encoding="utf-8"?><Response><Status>OK</Status></Response>'
        )

    def test_response_body_text(self, api_client):
        application = create_application()
        response_stub = create_response_stub(
            application=application,
            status_code=200,
            body='Status: OK',
            format='PLAIN_TEXT',
            headers={'Content-Type': 'application/text'},
        )
        resource = create_resource_stub(application=application, response=response_stub, method='GET')
        response = api_client.get(path=get_url(resource))
        assert response.status_code == 200
        assert response.content.decode() == 'Status: OK'

    def test_response_headers_sent(self, api_client):
        application = create_application()
        response_stub = create_response_stub(
            application=application,
            status_code=200,
            headers={'Custom-Serverside-Header': 'Serverside Header Value'},
        )
        resource = create_resource_stub(application=application, response=response_stub, method='GET')
        response = api_client.get(path=get_url(resource))
        assert response.status_code == 200
        assert response.headers.get('Custom-Serverside-Header') == 'Serverside Header Value'

    @patch('requests.request')
    def test_proxy_resource_call_json_answer(self, mock_requests_post, api_client):
        mock_requests_post.return_value.status_code = 200
        mock_requests_post.return_value.json.return_value = {'Status': 'OK'}
        mock_requests_post.return_value.content.decode.return_value = '{"Status": "OK"}'
        mock_requests_post.return_value.headers = {
            'Custom-Serverside-Header': 'Some Value',
            'Content-Type': 'application/json',
        }

        application = create_application()
        resource = create_resource_stub(
            application=application,
            method='GET',
            proxy_destination_address='https://example.com/foo',
            response_type=ResponseChoices.PROXY_CURRENT,
        )

        response = api_client.get(path=get_url(resource))

        assert response.status_code == 200
        assert response.headers.get('Custom-Serverside-Header') == 'Some Value'
        assert response.headers.get('Content-Type') == 'application/json'

    @pytest.mark.parametrize('lifecycle', [Lifecycle.BEFORE_REQUEST.value, Lifecycle.AFTER_REQUEST.value])
    @patch('requests.request', return_value=None)
    def test_after_response_webhook_call(self, mocked_request, lifecycle, api_client):
        application = create_application()
        response_stub = create_response_stub(application=application, status_code=200)
        resource = create_resource_stub(application=application, response=response_stub, method='GET')
        hook_request = create_request_stub(
            application=application, method='GET', query_params={'a': 'b'}, uri='https://test.com'
        )
        create_resource_hook(
            lifecycle=lifecycle, action=Action.WEBHOOK.value, timeout=0, resource=resource, request=hook_request
        )
        response = api_client.get(path=get_url(resource))
        assert response.status_code == 200
        mocked_request.assert_called_once()
        mocked_request.assert_called_with(
            method='GET', url='https://test.com', params={'a': 'b'}, headers={}, data=None
        )


@pytest.mark.django_db
class TestLogging:
    @pytest.mark.parametrize('request_method', ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
    def test_regular_request_logging(self, request_method, api_client):
        application = create_application()
        response_stub = create_response_stub(
            application=application,
            status_code=200,
            headers={'Custom-Serverside-Header': 'Serverside Header Value'},
            body=json.dumps({'Status': 'OK'}),
        )
        resource = create_resource_stub(application=application, response=response_stub, method=request_method)

        request_params = '?param1=value1&param2=value2'
        request_body = {
            'field_1': 'some data',
            'field_2': 'some another data',
            'field_3': 100500,
        }
        payload = json.dumps(request_body) if request_method != 'GET' else ''

        response = api_client.generic(
            method=request_method,
            path=f'{get_url(resource)}{request_params}',
            data=payload,
            content_type='application/json',
            HTTP_CUSTOM_CLIENT_HEADER='Custom Header Value',
        )
        assert response.status_code == 200

        request_log = resource.logs.last()
        assert request_log is not None
        assert request_log.application == application
        assert request_log.response == response_stub
        assert not request_log.proxied
        assert request_log.params == {'param1': 'value1', 'param2': 'value2'}
        assert request_log.response_body is not None
        assert json.loads(request_log.response_body) == {'Status': 'OK'}
        assert request_log.method == request_method
        assert request_log.response_headers == {'Custom-Serverside-Header': 'Serverside Header Value'}
        assert request_log.request_headers.get('Custom-Client-Header') == 'Custom Header Value'

        if request_method == 'GET':
            assert request_log.request_body == ''
        else:
            assert request_log.request_body is not None
            assert json.loads(request_log.request_body) == request_body

    @patch("requests.request")
    @pytest.mark.parametrize('request_method', ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
    def test_proxy_request_logging(self, mock_requests_request, request_method, api_client):
        mock_requests_request.return_value.status_code = 200
        mock_requests_request.return_value.json.return_value = {'Status': 'OK'}
        mock_requests_request.return_value.content.decode.return_value = '{"Status": "OK"}'
        mock_requests_request.return_value.headers = {
            'Custom-Serverside-Header': 'Some Value',
            'Content-Type': 'application/json',
        }

        application = create_application()
        resource = create_resource_stub(
            application=application,
            method=request_method,
            proxy_destination_address='https://example.com/foo',
            response_type=ResponseChoices.PROXY_CURRENT,
        )
        request_params = '?param1=value1&param2=value2'
        request_body = {
            'field_1': 'some data',
            'field_2': 'some another data',
            'field_3': 100500,
        }
        payload = json.dumps(request_body) if request_method != 'GET' else ''

        response = api_client.generic(
            method=request_method,
            path=f'{get_url(resource)}{request_params}',
            data=payload,
            content_type='application/json',
            HTTP_CUSTOM_CLIENT_HEADER='Custom Header Value',
        )

        assert response.status_code == 200

        mock_requests_request.assert_called_once()
        request_log = resource.logs.last()
        assert request_log is not None
        assert request_log.application == application
        assert request_log.response is None
        assert request_log.proxied
        assert request_log.params == {'param1': 'value1', 'param2': 'value2'}
        assert request_log.response_body is not None
        assert json.loads(request_log.response_body) == {'Status': 'OK'}
        assert request_log.method == request_method
        assert request_log.response_headers.get('Custom-Serverside-Header') == 'Some Value'
        assert request_log.request_headers.get('Custom-Client-Header') == 'Custom Header Value'

        if request_method == 'GET':
            assert request_log.request_body == ''
        else:
            assert request_log.request_body is not None
            assert json.loads(request_log.request_body) == request_body


@pytest.mark.django_db
class TestServiceViews:
    def test_healthcheck(self, api_client):
        url = reverse('apps:alive')
        response = api_client.get(path=url)
        assert response.status_code == 200

    def test_stubit_success(self, api_client, api_client_user):
        application = create_application()
        response_stub = create_response_stub(
            application=application,
            status_code=200,
            body=json.dumps({'Status': 'OK'}),
        )
        resource = create_resource_stub(application=application, response=response_stub, method='POST')

        request_body = {
            'field': 'some data',
        }
        payload = json.dumps(request_body)

        response = api_client.post(
            path=get_url(resource),
            data=payload,
            content_type='application/json',
        )
        assert response.status_code == 200

        request_log = resource.logs.last()
        assert request_log

        stubit_response = api_client_user.post(path=reverse('apps:stub_it', args=(str(request_log.id),)))
        assert stubit_response.status_code == 302
        assert '/admin/apps/resourcestub/' in stubit_response.url

        new_resource_stub_id = stubit_response.url.split('/', 5)[4]

        new_resource_stub = models.ResourceStub.objects.get(id=new_resource_stub_id)
        assert new_resource_stub.application == resource.application
        assert new_resource_stub.slug == resource.slug
        assert new_resource_stub.method == resource.method
        assert new_resource_stub.tail == resource.tail

        assert new_resource_stub.response
        assert new_resource_stub.response.application == response_stub.application
        assert new_resource_stub.response.status_code == response_stub.status_code
        assert new_resource_stub.response.body == response_stub.body
        assert new_resource_stub.response.headers == response_stub.headers

    def test_stubit_unauthorized_user(self, api_client):
        application = create_application()
        response_stub = create_response_stub(application=application)
        resource = create_resource_stub(application=application, response=response_stub, method='GET')
        response = api_client.get(path=get_url(resource))
        assert response.status_code == 200

        request_log = resource.logs.last()
        assert request_log

        stubit_response = api_client.post(path=reverse('apps:stub_it', args=(str(request_log.id),)))
        assert stubit_response.status_code == 403
