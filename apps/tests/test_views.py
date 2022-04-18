import json

import pytest

from apps.tests.data import create_application, create_resource_stub, create_response_stub
from apps.tests.utils import get_url


@pytest.mark.django_db
class TestResponseStub:
    @pytest.mark.parametrize('method', ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD', 'OPTIONS'])
    def test_response_with_allowed_request(self, method, api_client):
        application = create_application()
        response_stub = create_response_stub(application=application, status_code=200)
        resource = create_resource_stub(application=application, response=response_stub, method=method)
        response = api_client.generic(method=method, path=get_url(resource))
        assert response.status_code == 200

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

    def test_regular_request_logging(self, api_client):
        application = create_application()
        response_stub = create_response_stub(
            application=application,
            status_code=200,
            headers={'Custom-Serverside-Header': 'Serverside Header Value'},
            body=json.dumps({'Status': 'OK'})
        )
        resource = create_resource_stub(application=application, response=response_stub, method='POST')

        request_params = '?param1=value1&param2=value2'
        request_data = {
            'field_1': 'some data',
            'field_2': 'some another data',
            'field_3': 100500,
        }

        response = api_client.post(
            path=f'{get_url(resource)}{request_params}',
            data=json.dumps(request_data),
            content_type='application/json',
            HTTP_CUSTOM_CLIENT_HEADER='Custom Header Value'
        )
        assert response.status_code == 200

        request_log = resource.logs.last()
        assert request_log is not None
        assert request_log.application == application
        assert request_log.response == response_stub
        assert request_log.params == {'param1': 'value1', 'param2': 'value2'}
        assert request_log.request_body is not None
        assert json.loads(request_log.request_body) == request_data
        assert request_log.response_body is not None
        assert json.loads(request_log.response_body) == {'Status': 'OK'}
        assert request_log.method == 'POST'
        assert request_log.response_headers == {'Custom-Serverside-Header': 'Serverside Header Value'}
        assert request_log.request_headers.get('Custom-Client-Header') == 'Custom Header Value'

    def test_response_body_sent(self, api_client):
        application = create_application()
        response_stub = create_response_stub(
            application=application,
            status_code=200,
            body=json.dumps({'Status': 'OK'}),
            format='JSON'
        )
        resource = create_resource_stub(application=application, response=response_stub, method='GET')
        response = api_client.get(path=get_url(resource))
        assert response.status_code == 200
        assert response.json() == {'Status': 'OK'}

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
