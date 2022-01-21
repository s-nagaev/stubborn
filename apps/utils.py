import ast
import json
from typing import Any, Dict, Optional
from xml.dom import minidom

from django.utils.safestring import mark_safe
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers import XmlLexer
from pygments.lexers.data import JsonLexer


def str_to_dict(string: str) -> Optional[dict]:
    """Convert dictionary-friendly string to python dict.

    Args:
        string: string which may contain dictionary.

    Returns:
        Python dict if conversion is possible, None otherwise.
    """
    try:
        return ast.literal_eval(string)
    except (ValueError, SyntaxError):
        return None


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


def prettify_json_html(dict_data: Dict[str, Any]) -> str:
    """Pretty JSON data for admin fields.

    Args:
        dict_data: data in the python dictionary format.

    Returns:
        HTML-code with pretty JSON and style.
    """
    json_string = json.dumps(dict_data, sort_keys=True, indent=2)
    formatter = HtmlFormatter()
    json_prettified = highlight(json_string, JsonLexer(), formatter)
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
    formatter = HtmlFormatter()
    xml_prettified = highlight(xml_string, XmlLexer(), formatter)
    style = f'<style>{formatter.get_style_defs()}</style>'
    return xml_prettified + style


def prettify_string_to_html(string: str) -> str:
    """Pretty data for admin fields.

    Generates HTML data with styles for a pretty display of the XML or JSON data.
    If the string is not XML-friendly or JSON-friendly, it'll be returned without any modifications.

    Args:
        string: string data for displaying in the admin site.

    Returns:
        A string containing HTML code or marked safe original string.
    """
    if dict_data := str_to_dict(string):
        return mark_safe(prettify_json_html(dict_data))
    elif dom_doc := str_to_dom_document(string):
        return mark_safe(prettify_xml_html(dom_doc))
    return mark_safe(string)
