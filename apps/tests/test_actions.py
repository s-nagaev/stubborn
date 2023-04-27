import pytest

from apps.actions import change_satus, duplicate
from apps.models import ResourceStub
from apps.tests.data import create_application, create_resource_stub


@pytest.mark.django_db
class TestActions:
    def test_invert_status(self):
        application = create_application()
        resource_1 = create_resource_stub(application=application, method='GET', is_enabled=True)
        resource_2 = create_resource_stub(application=application, method='GET', is_enabled=False)

        queryset = ResourceStub.objects.all()

        change_satus(model_admin=None, request=None, queryset=queryset)

        resource_1.refresh_from_db()
        resource_2.refresh_from_db()

        assert resource_1.is_enabled is False
        assert resource_2.is_enabled is True

    def test_invert_status_and_disable_enabled_resource(self):
        application = create_application()
        slug = 'testslug'
        tail = 'some/tail/here'

        resource_disabled = create_resource_stub(
            application=application,
            method='GET',
            slug=slug,
            tail=tail,
            is_enabled=False,
        )
        resource_enabled = create_resource_stub(
            application=application, method='GET', slug=slug, tail=tail, is_enabled=True
        )

        queryset = ResourceStub.objects.filter(id=resource_disabled.id)

        change_satus(model_admin=None, request=None, queryset=queryset)

        resource_disabled.refresh_from_db()
        resource_enabled.refresh_from_db()

        assert resource_disabled.is_enabled is True
        assert resource_enabled.is_enabled is False

    def test_duplicate_resource(self):
        application = create_application()
        slug = 'testslug'
        tail = 'some/tail/here'

        source_resource = create_resource_stub(
            application=application,
            method='GET',
            slug=slug,
            tail=tail,
            is_enabled=True,
        )

        queryset = ResourceStub.objects.filter(id=source_resource.id)

        duplicate(model_admin=None, request=None, queryset=queryset)
        duplicated_resource = ResourceStub.objects.order_by('created_at').last()

        assert duplicated_resource
        assert source_resource.pk != duplicated_resource.pk
        assert source_resource.slug == duplicated_resource.slug
        assert source_resource.tail == duplicated_resource.tail
        assert not duplicated_resource.is_enabled
