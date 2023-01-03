from unittest.mock import MagicMock, patch

from apps.services import proxy_request


class TestProxy:
    @patch('requests.request', return_value=None)
    def test_proxy_request_func(self, mocked_request_method):
        mocked_incoming_request = MagicMock()
        mocked_incoming_request.method = 'POST'
        mocked_incoming_request.query_params = {'param1': 'val1', 'param2': 'val2'}
        mocked_incoming_request.body.decode.return_value = '{"Status":"OK"}'
        mocked_incoming_request.headers = {'Content-Type': 'application/json'}

        destination_url = 'https://example.com/api/foo'

        proxy_request(incoming_request=mocked_incoming_request, destination_url=destination_url)

        mocked_request_method.assert_called_once()
        mocked_request_method.assert_called_with(
            method='POST',
            url=destination_url,
            params={'param1': 'val1', 'param2': 'val2'},
            headers={'Content-Type': 'application/json'},
            data=b'{"Status":"OK"}',
        )
