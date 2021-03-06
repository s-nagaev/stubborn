import json
import logging
import threading
from functools import wraps
from json import JSONDecodeError
from typing import Any, Dict, Optional, Union
from xml.dom import minidom

from django.utils.safestring import mark_safe
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers import XmlLexer
from pygments.lexers.data import JsonLexer

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


def str_to_dom_document(string: str) -> Optional[minidom.Document]:
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


def prettify_json_html(data: Union[str, Dict[str, Any]]) -> str:
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


def prettify_data_to_html(data: Union[str, Dict[str, Any]]) -> str:
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
    return mark_safe(data)


def clean_headers(headers: Dict[str, str]) -> Dict[str, str]:
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

    throw_out_headers = [
        'host',
        'server',
        'content-length',
        'content-encoding'
    ]

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
        t.setName(f"{func.__module__}.{func.__name__}")
        t.setDaemon(True)
        t.start()
        return t

    return run
