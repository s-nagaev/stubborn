import json

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.models import Application


@pytest.mark.django_db
class TestApplicationImport:
    def test_correct_import_with_request(self, api_client, mocked_application_file):
        """Test Application import from a file with request."""
        assert Application.objects.count() == 0

        response = api_client.post('/import/', {'file': mocked_application_file})

        assert response.status_code == 201
        application = Application.objects.first()
        assert application is not None

    def test_correct_import_structure_with_request(self, api_client, mocked_application_file):
        """Test Application import structure from a file with request."""
        assert Application.objects.count() == 0

        response = api_client.post('/import/', {'file': mocked_application_file})
        assert response.status_code == 201
        application = Application.objects.first()
        assert application is not None
        assert application.slug == 'application_slug'

        assert application.owner is not None
        assert application.owner.username == 'owner_user_name'

        assert application.responses.count() == 1
        application_response = application.responses.first()
        assert application_response is not None
        assert application_response.resources.count() == 1

        application_resource = application_response.resources.first()
        assert application_resource is not None
        assert application_resource.description == 'application_resource_description'
        assert application_resource.slug == 'application_resource_slug'

        assert application_resource.hooks.count() == 1

        hook = application_resource.hooks.first()
        assert hook is not None
        hook_request = hook.request
        assert hook_request is not None
        assert hook_request.name == 'hook_request_name'
        assert len(hook_request.query_params) == 2

        assert hook_request.creator is not None
        assert hook_request.creator.username == 'creator_name'

    @pytest.mark.parametrize('empty_field', ['name', 'slug'])
    def test_incorrect_import_with_request(self, api_client, empty_field):
        """Test Application import from a file with request."""
        assert Application.objects.count() == 0

        application_data = {
            'description': 'asdasdasd',
            'name': 'asdasd',
            'slug': 'slug'
        }
        application_data.pop(empty_field)
        json_data = json.dumps(application_data)

        mocked_application_file = SimpleUploadedFile(
            'application_dump.json',
            str.encode(json_data)
        )

        response = api_client.post('/import/', {'file': mocked_application_file})

        assert response.status_code == 400
        application = Application.objects.first()
        assert application is None


class TestApplicationExport:
    pass
