from typing import Dict, Generic, Optional, TypeVar

from django.db.models import Model
from django.http import HttpRequest

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
