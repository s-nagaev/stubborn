import json

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.exceptions import ValidationError

from apps.models import Application
from apps.services import save_application_from_json_object
from apps.tests.application_json_mock import JSON_data
from apps.tests.data import create_application


@pytest.mark.django_db
class TestApplicationImport:
    def test_save_application_from_json_object(self, api_client):
        """Test correct application saving from a JSON object."""
        jsonyfied_application = json.loads(JSON_data)
        assert Application.objects.count() == 0

        save_application_from_json_object(jsonyfied_application)

        assert Application.objects.count() == 1
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

    def test_save_application_with_duplicated_application_slug_from_json_object(self, api_client):
        """Test application saving with a duplicated application_slug from a JSON object."""
        jsonyfied_application = json.loads(JSON_data)
        assert Application.objects.count() == 0

        save_application_from_json_object(jsonyfied_application)

        assert Application.objects.count() == 1
        jsonyfied_application['description'] = 'new description'
        with pytest.raises(ValidationError) as error:
            save_application_from_json_object(jsonyfied_application)
        assert '(application_slug, asdasd) already exists' in str(error.value)

    def test_update_application_from_json_object(self, api_client):
        """Test application updating from a JSON object."""
        jsonyfied_application = json.loads(JSON_data)
        assert Application.objects.count() == 0

        save_application_from_json_object(jsonyfied_application)

        assert Application.objects.count() == 1
        jsonyfied_application['description'] = 'new description'
        application = save_application_from_json_object(jsonyfied_application, update=True)

        assert Application.objects.count() == 1
        assert application is not None
        assert application.description == jsonyfied_application['description']

    @pytest.mark.parametrize('empty_field', ['name', 'slug'])
    def test_save_application_from_json_object_with_incorrect_data(self, api_client, empty_field):
        """Test incorrect fields Application saving from a JSON object."""
        assert Application.objects.count() == 0

        jsonyfied_application = {
            'description': 'asdasdasd',
            'name': 'asdasd',
            'slug': 'slug'
        }
        jsonyfied_application.pop(empty_field)

        with pytest.raises(ValidationError) as error:
            save_application_from_json_object(jsonyfied_application)
        assert f"'{empty_field}': [ErrorDetail(string='This field is required.'" in str(error.value)

    def test_correct_import_with_request(self, api_client, mocked_application_file):
        """Test Application import from a file with request."""
        assert Application.objects.count() == 0

        response = api_client.post('/srv/import/', {'file': mocked_application_file})

        assert response.status_code == 201
        application = Application.objects.first()
        assert application is not None

    def test_import_without_file_with_request(self, api_client):
        """Test Application import without file with request."""
        assert Application.objects.count() == 0

        response = api_client.post('/srv/import/')

        assert response.status_code == 400
        response_json = response.json()
        assert response_json is not None
        assert response_json['error'] == 'File object was not attached.'

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
        encoded_data = str.encode(json_data)

        mocked_application_file = SimpleUploadedFile('application_dump.json', encoded_data)

        response = api_client.post('/srv/import/', {'file': mocked_application_file, 'update': 'true'})

        assert response.status_code == 201
        assert Application.objects.count() == 1
        application = Application.objects.first()
        assert application is not None
        assert application.id == application_id

    def test_already_existing_application_import_with_request(self, api_client):
        """Test already existing Application import from a file with request."""
        application = create_application(slug='test-slug', name='test_name')
        assert Application.objects.count() == 1

        application_data = {
            'description': application.description,
            'name': application.name,
            'slug': application.slug
        }
        json_data = json.dumps(application_data)
        encoded_data = str.encode(json_data)

        mocked_application_file = SimpleUploadedFile('application_dump.json', encoded_data)

        response = api_client.post('/srv/import/', {'file': mocked_application_file})

        assert response.status_code == 400
        response_json = response.json()
        assert response_json is not None
        assert '(slug, name)=(test-slug, test_name) already exists.' in response_json[0]
