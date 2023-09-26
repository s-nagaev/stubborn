import pytest

from apps.actions import change_satus, duplicate
from apps.models import Application, ResourceStub
from apps.tests.data import (
    create_application,
    create_request_stub,
    create_resource_hook,
    create_resource_stub,
    create_response_stub,
)


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

    def test_duplicate_application(self):
        application = create_application()

        for _ in range(3):
            create_request_stub(application=application)
            create_response_stub(application=application)
            create_resource_stub(application=application)

        resource = application.resources.first()
        assert resource
        create_resource_hook(resource=resource)

        queryset = Application.objects.filter(id=application.id)
        duplicate(model_admin=None, request=None, queryset=queryset)
        duplicated_application = Application.objects.order_by('created_at').last()

        assert duplicated_application
        assert application.id != duplicated_application.id
        assert application.slug + '-copy' == duplicated_application.slug

        resources_queryset = application.resources.all()
        copied_resources_queryset = duplicated_application.resources.all()
        assert resources_queryset.count() == copied_resources_queryset.count()
        application_resources_shortcuts = {
            str(obj.description) + str(obj.method)
            for obj in resources_queryset
        }
        copied_application_resources_shortcuts = {
            str(obj.description) + str(obj.method)
            for obj in copied_resources_queryset
        }
        assert application_resources_shortcuts == copied_application_resources_shortcuts

        copied_resources_queryset = ResourceStub.objects.filter(application=duplicated_application,
                                                                method=resource.method,
                                                                description=resource.description)
        assert copied_resources_queryset
        assert copied_resources_queryset.count() == 1
        assert copied_resources_queryset[0].hooks.count() == 1

        requests_queryset = application.requests.all()
        copied_requests_queryset = duplicated_application.requests.all()
        assert requests_queryset.count() == copied_requests_queryset.count()
        assert {obj.name for obj in requests_queryset} == {obj.name for obj in copied_requests_queryset}

        responses_queryset = application.responses.all()
        copied_responses_queryset = duplicated_application.responses.all()
        assert responses_queryset.count() == copied_responses_queryset.count()

        responses_shortcuts = {
            str(obj.status_code) + str(obj.description) for obj in responses_queryset
        }
        copied_responses_shortcuts = {
            str(obj.status_code) + str(obj.description) for obj in copied_responses_queryset
        }
        assert responses_shortcuts == copied_responses_shortcuts

    def test_duplicate_two_applications(self):
        create_application()
        create_application()
        queryset = Application.objects.all()
        assert queryset.count() == 2
        duplicate(model_admin=None, request=None, queryset=queryset)
        assert Application.objects.count() == 4
