from typing import Optional, Dict, TypeVar, Generic

from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Model
from django.http import HttpRequest

_ModelT = TypeVar("_ModelT", bound=Model)


class HideFromAdminIndexMixin(Generic[_ModelT]):
    """Mixin for hiding registered ModelAdmin instance from admin index."""

    def get_model_perms(self, request: WSGIRequest) -> Dict:
        """Return a dict of all perms for this model.

        Return empty dict thus hiding the model from admin index.
        """
        return {}


class DenyCreateMixin:
    """Миксин, запрещающий создание новой записи, через сайт администратора."""
    def has_add_permission(self, request: HttpRequest, obj: Optional[Model] = None) -> bool:
        """Проверка прав на добавление записи.

        Args:
            request: экземпляр объекта запроса.
            obj: экземпляр модели.

        Returns:
            False
        """
        return False


class DenyUpdateMixin:
    """Миксин, запрещающий изменение записи, через сайт администратора."""
    def has_change_permission(self, request: HttpRequest, obj: Optional[Model] = None) -> bool:
        """Проверка прав на изменение записи.

        Args:
            request: экземпляр объекта запроса.
            obj: экземпляр модели.

        Returns:
            False
        """
        return False


class DenyDeleteMixin:
    """Миксин, запрещающий удаление записи, через сайт администратора."""
    def has_delete_permission(self, request: HttpRequest, obj: Optional[Model] = None) -> bool:
        """Проверка прав на удаление записи.

        Args:
            request: экземпляр объекта запроса.
            obj: экземпляр модели.

        Returns:
            False
        """
        return False


class DenyCUDMixin(DenyCreateMixin, DenyUpdateMixin, DenyDeleteMixin):
    """Миксин, запрещающий создание, изменение и удаление записи, через сайт администратора."""
    pass