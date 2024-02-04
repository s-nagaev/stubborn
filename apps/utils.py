import json
import logging
import os
import threading
from datetime import datetime
from functools import wraps
from json import JSONDecodeError
from typing import Any
from uuid import UUID
from xml.dom import minidom

from django.conf import settings
from django.utils import timezone
from django.utils.safestring import mark_safe
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers import XmlLexer
from pygments.lexers.data import JsonLexer
from pygments.lexers.html import HtmlLexer
from rest_framework.request import Request

from apps.styles import StubbornDark

logger = logging.getLogger(__name__)


def is_json(string: str) -> bool:
    """Check if the string is json-friendly.

    Args:
        string: string for checking.

    Returns:
        True if the string is JSON, False otherwise.
    """
    try:
        json.loads(string)
    except (JSONDecodeError, TypeError):
        return False
    return True


def str_to_dom_document(string: str) -> minidom.Document | None:
    """Convert xml-friendly string to xml minidom Document.

    Args:
        string: xml-friendly string.

    Returns:
        Minidom Document if conversion is possible, None otherwise.
    """
    try:
        return minidom.parseString(string)
    except Exception:
        return None


def prettify_json_html(data: str | dict[str, Any]) -> str:
    """Pretty JSON data for admin fields.

    Args:
        data: json-friendly string or python dictionary.

    Returns:
        HTML-code with pretty JSON and style.
    """
    if isinstance(data, dict):
        json_string_with_indents = json.dumps(data, sort_keys=True, indent=2, ensure_ascii=False)
    elif isinstance(data, str):
        json_string_with_indents = json.dumps(json.loads(data), sort_keys=True, indent=2, ensure_ascii=False)
    else:
        raise ValueError(f'Unsupported data type received: {type(data)}. String or Dict expected.')

    formatter = HtmlFormatter(style=StubbornDark)
    json_prettified = highlight(json_string_with_indents, JsonLexer(), formatter)
    style = f'<style>{formatter.get_style_defs()}</style>'
    return json_prettified + style


def prettify_xml_html(dom_document: minidom.Document) -> str:
    """Pretty XML data for admin fields.

    Args:
        dom_document: minidom Document instance.

    Returns:
        HTML-code with pretty XML and style.
    """
    xml_string = dom_document.toprettyxml(indent=' ')
    formatter = HtmlFormatter(style=StubbornDark)
    xml_prettified = highlight(xml_string, XmlLexer(), formatter)
    style = f'<style>{formatter.get_style_defs()}</style>'
    return xml_prettified + style


def prettify_html_html(html_document: str) -> str:
    """Pretty HTML data for admin fields.

    Args:
        html_document: HTML-code of the page.

    Returns:
        HTML-code with pretty XML and style.
    """
    formatter = HtmlFormatter(style=StubbornDark)
    xml_prettified = highlight(html_document, HtmlLexer(), formatter)
    style = f'<style>{formatter.get_style_defs()}</style>'
    return xml_prettified + style


def prettify_data_to_html(data: str | dict[str, Any]) -> str:
    """Pretty data for admin fields.

    Generates HTML data with styles for a pretty display of the XML or JSON data.
    If the string is not XML-friendly or JSON-friendly, it'll be returned without any modifications.

    Args:
        data: string data for displaying in the admin site.

    Returns:
        A string containing HTML code or marked safe original string.
    """
    if isinstance(data, dict) or is_json(data):
        return mark_safe(prettify_json_html(data))
    elif dom_doc := str_to_dom_document(data):
        return mark_safe(prettify_xml_html(dom_doc))
    if data.startswith('<!DOCTYPE html>'):
        return mark_safe(prettify_html_html(data))
    return mark_safe(data)


def clean_headers(headers: dict[str, str]) -> dict[str, str]:
    """Remove unwilling headers: hop-by-hop headers and some client- and server-side specific headers.

    Hop-by-hop headers are meaningful only for a single transport-level connection,
    and are not stored by caches or forwarded by proxies.
    See more at: https://www.w3.org/Protocols/rfc2616/rfc2616-sec13.html#sec13.5.1

    Args:
        headers: dictionary containing request/response headers.

    Returns:
        Headers dictionary without unwilling headers.
    """

    hop_by_hop_headers = [
        'connection',
        'keep-alive',
        'proxy-authenticate',
        'proxy-authorization',
        'te',
        'trailer',
        'transfer-encoding',
        'upgrade',
    ]

    throw_out_headers = ['host', 'server', 'content-length', 'content-encoding']

    unwanted_headers = hop_by_hop_headers + throw_out_headers
    headers = dict(headers)
    headers_names = list(headers.keys())
    for header_name in headers_names:
        if header_name.lower() in unwanted_headers:
            headers.pop(header_name)

    return headers


def run_in_separate_thread(func):
    """Decorated function will be called in separate thread.

    Args:
        func: function to decorate.

    Returns:
        Thread object instead of execution result.
    """

    @wraps(func)
    def run(*args, **kwargs) -> threading.Thread:
        logger.info(f"Run function {func.__name__} from {func.__module__} in separate thread")

        t = threading.Thread(target=func, args=args, kwargs=kwargs)
        t.name = f"{func.__module__}.{func.__name__}"
        t.daemon = True
        t.start()
        return t

    return run


def log_request(request_logger: logging.Logger, request: Request) -> None:
    """Log the incoming request data.

    Args:
        request_logger: logger instance.
        request: Django REST Framework request instance.
    """

    try:
        method = request.method.upper()
        query_params = request.query_params or 'empty'
        body = json.loads(request.body.decode()) if request.body else 'empty'
        url = request.get_full_path()
        headers = request.headers
        request_logger.info(
            f'Incoming request: {method} {url}. Body: {body}. Params: {query_params}. Headers: {headers}.'
        )
    except Exception as e:
        request_logger.error(f'Could not log an incoming request due to exception: {e}')


def log_response(
    response_logger: logging.Logger,
    resource_type: str,
    status_code: int,
    request_log_id: UUID,
    body: dict[str, Any] | str = 'empty',
    headers: dict[str, str] | str = 'empty',
) -> None:
    """Log the returning response data.

    Args:
        response_logger: logger instance.
        resource_type: request type (STUB or PROXY).
        status_code: response status code.
        request_log_id: request log record ID.
        body: response body (if exists).
        headers: response headers (if exists).
    """
    try:
        log_message = (
            f'Returning {resource_type} response: Status: {status_code}. '
            f'Body: {body}. '
            f'Headers: {headers}. Request Log Record: {request_log_id}.'
        )
        response_logger.info(log_message)
    except Exception as e:
        response_logger.error(f'Could not log response data due to exception: {e}')


def start_of_the_day_today() -> datetime:
    today = timezone.datetime.today()
    return timezone.datetime(year=today.year, month=today.month, day=today.day, tzinfo=today.tzinfo)


def end_of_the_day_today() -> datetime:
    today = timezone.datetime.today()
    return timezone.datetime(
        year=today.year, month=today.month, day=today.day, tzinfo=today.tzinfo, hour=23, minute=59, second=59
    )


def add_stubborn_headers(initial_headers: dict[str, str], log_id: str | UUID) -> dict[str, str]:
    stubborn_headers = {
        "Stubborn-Log-Id": str(log_id),
        "Stubborn-Log-Url": os.path.join(settings.DOMAIN_DISPLAY, "admin/apps/requestlog", str(log_id)),
    }

    return initial_headers | stubborn_headers
