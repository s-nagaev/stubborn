from typing import TYPE_CHECKING, Any, Dict, Generic, Optional, Sequence, TypeVar, cast

from django import forms
from django.contrib.admin import ModelAdmin
from django.contrib.admin.options import InlineModelAdmin
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.contrib.auth.models import User
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Model
from django.forms import BaseModelFormSet
from django.http import HttpRequest

if TYPE_CHECKING:
    class ModelAdminTypeClass(ModelAdmin, InlineModelAdmin):
        ...
else:
    ModelAdminTypeClass = object

_ModelT = TypeVar("_ModelT", bound=Model)


class HideFromAdminIndexMixin(Generic[_ModelT]):
    """Mixin for hiding registered ModelAdmin instance from the admin index."""

    def get_model_perms(self, request: HttpRequest) -> Dict[str, bool]:
        """Return a dict of all perms for this model.

        Return empty dict thus hiding the model from admin index.

        Args:
            request: HttpRequest instance (not used).
        """
        return {}


class DenyCreateMixin:
    """Mixin for blocking the creation of a new record through the admin site."""
    def has_add_permission(self, request: HttpRequest, obj: Optional[Model] = None) -> bool:
        """Check user "add" permission.

        Args:
            request: HttpRequest instance,
            obj: Model instance.

        Returns:
            Always False.
        """
        return False


class DenyUpdateMixin:
    """Mixin for blocking the update of an existent record through the admin site."""
    def has_change_permission(self, request: HttpRequest, obj: Optional[Model] = None) -> bool:
        """Check user "change" permission.

        Args:
            request: HttpRequest instance,
            obj: Model instance.

        Returns:
            Always False.
        """
        return False


class DenyDeleteMixin:
    """Mixin for blocking the deletion of an existent record through the admin site."""
    def has_delete_permission(self, request: HttpRequest, obj: Optional[Model] = None) -> bool:
        """Check user "delete" permission.

        Args:
            request: HttpRequest instance,
            obj: Model instance.

        Returns:
            Always False.
        """
        return False


class DenyCUDMixin(DenyCreateMixin, DenyUpdateMixin, DenyDeleteMixin):
    """Mixin for blocking the CRUD functionality for a record through the admin site."""
    pass


class RelatedCUDManagerMixin(ModelAdminTypeClass):
    """Mixin for manipulations with the related object's create/edit/delete pictograms."""

    no_add_related: Sequence[str] = []
    no_edit_related: Sequence[str] = []
    no_delete_related: Sequence[str] = []

    def _get_field_widget(self, field_name: str, form: forms.ModelForm) -> RelatedFieldWidgetWrapper:
        """Get the widget object connected with the corresponding related object field.

        Args:
            field_name: the name of the field connected with the related object.
            form: the ModelForm instance.

        Returns:
            The instance if the related object field's widget.

        Raises:
            ValueError если поле не является ссылкой на другую модель.
        """
        field_widget = form.base_fields[field_name].widget
        if not isinstance(field_widget, RelatedFieldWidgetWrapper):
            raise ValueError(
                f"Unable to disable link for the field '{field_name}' "
                f"(this field doesn't connected with the related object)."
            )
        return field_widget

    def _remove_cud_links(self, form: forms.ModelForm) -> forms.ModelForm:
        """Turn off the create/edit/delete actions for related fields.

        Args:
            form: the ModelForm instance.

        Returns:
            The ModelForm instance.
        """
        for field_name in self.no_add_related:
            field_widget = self._get_field_widget(field_name=field_name, form=form)
            field_widget.can_add_related = False

        for field_name in self.no_edit_related:
            field_widget = self._get_field_widget(field_name=field_name, form=form)
            field_widget.can_change_related = False

        for field_name in self.no_delete_related:
            field_widget = self._get_field_widget(field_name=field_name, form=form)
            field_widget.can_delete_related = False

        return form

    def get_form(self,
                 request: WSGIRequest,
                 obj: Optional[_ModelT] = None,
                 change: bool = False,
                 **kwargs: Any) -> forms.ModelForm:
        """Remove CUD icons for related object fields in ModelAdmin.

        Args:
            request: instance of WSGIRequest.
            obj: instance of the current model.
            change: form update flag.

        Returns:
            Modified ModelForm instance.
        """
        form = super().get_form(request, obj, change, **kwargs)
        self._remove_cud_links(form)
        return form

    def get_formset(self, request: WSGIRequest, obj:  Optional[_ModelT] = None, **kwargs: Any) -> BaseModelFormSet:
        """Remove CUD icons for related object fields in InlineModelAdmin.

        Args:
            request: instance of WSGIRequest.
            obj: current Model instance.

        Returns:
            Modified FormSet instance.
        """
        formset = super().get_formset(request, obj, **kwargs)
        self._remove_cud_links(formset.form)
        return formset


class SaveByCurrentUserMixin(ModelAdmin):
    def save_model(self, request: HttpRequest, obj: Model, *args: Any, **kwargs: Any) -> None:
        """Save model with current user fixation in the owner field.

        Args:
            request: HttpRequest instance.
            obj: model instance.
        """
        if hasattr(obj, 'creator'):
            obj.creator = cast(User, request.user)  # type: ignore
        super().save_model(request, obj, *args, **kwargs)
