import json

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.models import Application
from apps.tests.data import create_application


@pytest.mark.django_db
class TestApplicationImport:
    def test_correct_import_with_request(self, api_client, mocked_application_file):
        """Test Application import from a file with request."""
        assert Application.objects.count() == 0

        response = api_client.post('/srv/import/', {'file': mocked_application_file})

        assert response.status_code == 201
        application = Application.objects.first()
        assert application is not None

    def test_correct_import_structure_with_request(self, api_client, mocked_application_file):
        """Test Application import structure from a file with request."""
        assert Application.objects.count() == 0

        response = api_client.post('/srv/import/', {'file': mocked_application_file})
        assert response.status_code == 201
        application = Application.objects.first()
        assert application is not None
        assert application.slug == 'application_slug'

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

    @pytest.mark.parametrize('empty_field', ['name', 'slug'])
    def test_incorrect_import_with_request(self, api_client, empty_field):
        """Test incorrect fields Application import from a file with request."""
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

        response = api_client.post('/srv/import/', {'file': mocked_application_file})

        assert response.status_code == 400
        application = Application.objects.first()
        assert application is None

    def test_already_existing_application_import_with_request_for_updating(self, api_client, mocked_application_file):
        """Test already existing Application import from a file with request for updating."""
        assert Application.objects.count() == 0

        response = api_client.post('/srv/import/', {'file': mocked_application_file})
        assert response.status_code == 201
        application = Application.objects.first()

        assert application is not None

        application_id = application.id

        application_data = {
            'description': f"{application.description}123123",
            'name': f"{application.name}asdasd",
            'slug': application.slug
        }
        json_data = json.dumps(application_data)

        mocked_application_file = SimpleUploadedFile(
            'application_dump.json',
            str.encode(json_data)
        )

        response = api_client.post('/srv/import/', {'file': mocked_application_file, 'update': 'true'})

        assert response.status_code == 201
        assert Application.objects.count() == 1
        application = Application.objects.first()
        assert application is not None
        assert application.id == application_id

    def test_already_existing_application_import_with_request(self, api_client):
        """Test already existing Application import from a file with request."""
        application = create_application()
        assert Application.objects.count() == 1

        application_data = {
            'description': application.description,
            'name': application.name,
            'slug': application.slug
        }
        json_data = json.dumps(application_data)

        mocked_application_file = SimpleUploadedFile(
            'application_dump.json',
            str.encode(json_data)
        )

        response = api_client.post('/srv/import/', {'file': mocked_application_file})

        assert response.status_code == 400


class TestApplicationExport:
    pass
