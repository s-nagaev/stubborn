import json
from typing import Union

from pygments import highlight
from pygments.lexers.data import JsonLexer
from pygments.formatters.html import HtmlFormatter


def prettify_json_html(data: Union[dict, str]) -> str:
    """Pretty JSON data for admin fields.

    Args:
        data: dict or JSON-ready string.

    Returns:
        HTML-code with pretty JSON and style.

    Raises:
        ValueError if the `data` is not a string or dictionary.
    """

    if isinstance(data, dict):
        json_string = json.dumps(data, sort_keys=True, indent=2)
    elif isinstance(data, str):
        json_string = json.dumps(json.loads(data), sort_keys=True, indent=2)
    else:
        raise ValueError(f'Unexpected data type received: {type(data)}. Expected types are: str, dict.')
    formatter = HtmlFormatter()
    json_prettified = highlight(json_string, JsonLexer(), formatter)
    style = f'<style>{formatter.get_style_defs()}</style>'
    return json_prettified + style
