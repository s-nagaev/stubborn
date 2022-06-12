import json

from django import forms


class Editor(forms.Textarea):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attrs['class'] = 'html-editor'

    def render(self, name, value, attrs=None, renderer=None):
        if isinstance(value, dict):
            value = json.dumps(value, indent=4, ensure_ascii=False)
        else:
            try:
                value = json.dumps(json.loads(value), indent=4, ensure_ascii=False)
            except Exception:
                pass

        return super().render(name, value, attrs, renderer)

    class Media:
        css = {
            'all': (
                '/static/vendor/codemirror_5.65.5/css/codemirror.css',
                '/static/vendor/codemirror_5.65.5/css/seti.css'
            )
        }
        js = (
            '/static/vendor/codemirror_5.65.5/js/codemirror.min.js',
            '/static/vendor/codemirror_5.65.5/js/modes/javascript.min.js',
            '/static/admin/js/widgets/codemirror-init.js'
        )
