import json
from typing import Any, Optional

from django import forms
from django.contrib.admin import AdminSite
from django.contrib.admin.views.main import IS_POPUP_VAR, TO_FIELD_VAR
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.db.models import ForeignObjectRel


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
                '/static/admin/css/seti.css'
            )
        }
        js = (
            '/static/vendor/codemirror_5.65.5/js/codemirror.min.js',
            '/static/vendor/codemirror_5.65.5/js/modes/javascript.min.js',
            '/static/admin/js/widgets/codemirror-init.js'
        )


class ExtendedRelatedFieldWidgetWrapper(RelatedFieldWidgetWrapper):
    template_name = 'admin/related_widget_wrapper.html'

    def __init__(
            self,
            widget: forms.Widget,
            rel: ForeignObjectRel,
            admin_site: AdminSite,
            can_add_related: Optional[bool],
            can_change_related: bool,
            can_delete_related: bool,
            can_view_related: bool,
            additional_url_params: dict[str, Any] = None
    ) -> None:
        super().__init__(
            widget, rel, admin_site, can_add_related, can_change_related, can_delete_related, can_view_related
        )
        self.additional_url_params = additional_url_params

    def get_context(self, name: str, value: Any, attrs: Optional[dict[str, Any]]) -> dict[str, Any]:

        rel_opts = self.rel.model._meta  # type: ignore
        info = (rel_opts.app_label, rel_opts.model_name)
        self.widget.choices = self.choices  # type: ignore
        params = {
            TO_FIELD_VAR: self.rel.get_related_field().name,
            IS_POPUP_VAR: 1
        }
        if self.additional_url_params:
            params.update(self.additional_url_params)

        url_params = '&'.join('%s=%s' % param for param in params.items())

        context = {
            'rendered_widget': self.widget.render(name, value, attrs),
            'is_hidden': self.is_hidden,
            'name': name,
            'url_params': url_params,
            'model': rel_opts.verbose_name,
            'can_add_related': self.can_add_related,
            'can_change_related': self.can_change_related,
            'can_delete_related': self.can_delete_related,
            'can_view_related': self.can_view_related,
        }
        if self.can_add_related:
            context['add_related_url'] = self.get_related_url(info, 'add')  # type: ignore
        if self.can_delete_related:
            context['delete_related_template_url'] = self.get_related_url(info, 'delete', '__fk__')  # type: ignore
        if self.can_view_related or self.can_change_related:
            context['change_related_template_url'] = self.get_related_url(info, 'change', '__fk__')  # type: ignore
        return context
