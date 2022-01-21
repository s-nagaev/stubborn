from rest_framework.renderers import BaseRenderer


class TextToXMLRenderer(BaseRenderer):
    media_type = 'application/xml'
    format = 'xml'
    charset = 'utf-8'
    render_style = 'text'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        data_header = f'<?xml version="1.0" encoding="{self.charset}"?>\n'
        return data_header + str(data)


class SimpleTextRenderer(BaseRenderer):
    media_type = 'application/text'
    format = 'text'
    charset = 'utf-8'
    render_style = 'text'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        if not data:
            return ''
        return data
