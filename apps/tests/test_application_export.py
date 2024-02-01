import io
import json
from uuid import uuid4

import pytest

from apps.tests.data import create_application


@pytest.mark.django_db
class TestApplicationExport:
    def test_export_application_to_file(self, api_client):
        """Test exporting Application to a file."""
        application = create_application()
        response = api_client.get(f'/srv/export/{application.id}/')

        assert response.status_code == 200
        with io.BytesIO(response.content) as bytes_content:
            decoded_response_content = bytes_content.read().decode('utf-8')

        assert decoded_response_content is not None
        jsonyfied_application = json.loads(decoded_response_content)

        assert jsonyfied_application is not None
        assert jsonyfied_application['description'] == application.description
        assert jsonyfied_application['slug'] == application.slug
        assert jsonyfied_application['name'] == application.name

    def test_export_not_existing_application(self, api_client):
        """Test exporting not existing Application."""
        response = api_client.get(f'/srv/export/{uuid4()}/')

        assert response.status_code == 404
        assert response.json() == {'detail': 'Not found.'}
