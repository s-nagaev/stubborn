from django.urls import reverse

from apps.models import ResourceStub


def get_url(resource_stub: ResourceStub) -> str:
    application = resource_stub.application
    url = reverse('apps:stub-url', kwargs={'app_slug': application.slug, 'resource_slug': f'/{resource_stub.slug}'})
    return url
