import pytest
from django.utils.safestring import SafeString

from apps.utils import clean_headers, is_json, prettify_data_to_html, str_to_dom_document


class TestUtils:
    @pytest.mark.parametrize(
        'incoming_string',
        [
            '{"Some_key": "some val", "Some Another Key": "some another val"}',
            '[{"Some_key": "some val"}, {"Some Another Key": "some another val"}]',
            '{"one": {"two": 2}}'
        ]
    )
    def test_is_json_true(self, incoming_string):
        result = is_json(incoming_string)
        assert result

    def test_is_json_false(self):
        incoming_string = 'json-unfriendly string'
        result = is_json(incoming_string)
        assert not result

    def test_str_to_dom_document_success_conversion(self):
        incoming_string = '<Response><Status>OK</Status></Response>'
        result = str_to_dom_document(incoming_string)
        assert result
        assert result.toxml() == '<?xml version="1.0" ?><Response><Status>OK</Status></Response>'

    def test_str_to_dom_document_failed_conversion(self):
        incoming_string = 'XML-unfriendly string'
        result = str_to_dom_document(incoming_string)
        assert not result

    def test_prettify_string_to_html_wrong_string_type(self):
        incoming_string = 'Dictionary&XML-unfriendly string'
        result = prettify_data_to_html(incoming_string)
        assert isinstance(result, SafeString)
        assert result == 'Dictionary&XML-unfriendly string'

    @pytest.mark.parametrize(
        'incoming_string',
        [
            '<Response><Status>OK</Status></Response>',
            '{"Some_key": "some val"}',
            {"Some_key": "some val"}
        ]
    )
    def test_prettify_string_to_html_success_return_type(self, incoming_string):
        result = prettify_data_to_html(incoming_string)
        assert isinstance(result, SafeString)

    def test_clean_headers(self):
        incoming_headers = {
            'Connection': 'keep-alive',
            'Keep-Alive': 'timeout=5, max=1000',
            'Proxy-Authenticate': 'Basic',
            'Proxy-Authorization': 'Basic YWxhZGRpbjpvcGVuc2VzYW1l',
            'Host': 'example.com',
            'Content-Encoding': 'gzip',
            'Content-Length': '100',
            'Content-Type': 'text/html; charset=UTF-8',
            'TE': 'gzip',
            'Trailer': 'Expires',
            'Transfer-Encoding': 'gzip',
            'Upgrade': 'example/1, foo/2',
            'User-Agent': 'curl/7.64.1'
        }

        allowed_headers = clean_headers(incoming_headers)
        assert allowed_headers == {'Content-Type': 'text/html; charset=UTF-8', 'User-Agent': 'curl/7.64.1'}
