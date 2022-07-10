from django.contrib.auth.models import User
from faker import Faker

from apps.enums import Action, Lifecycle, ResponseChoices
from apps.models import Application, ResourceHook, ResourceStub, ResponseStub
from apps.tests import factories

fake = Faker()


def create_user(**kwargs) -> User:
    kwargs.setdefault('username', fake.word())
    kwargs.setdefault('email', fake.safe_email())
    kwargs.setdefault('is_superuser', False)

    return factories.UserFactory.create(**kwargs)


def create_admin() -> User:
    return create_user(username='admin', is_superuser=True)


def create_application(**kwargs) -> Application:
    kwargs.setdefault('name', fake.word())
    kwargs.setdefault('description', fake.paragraph(nb_sentences=3))
    kwargs.setdefault('slug', fake.slug())
    kwargs.setdefault('owner', create_user())

    return factories.ApplicationFactory.create(**kwargs)


def create_response_stub(**kwargs) -> ResponseStub:
    kwargs.setdefault('status_code', 200)
    kwargs.setdefault('headers', {})
    kwargs.setdefault('body', '')
    kwargs.setdefault('description', fake.sentence(nb_words=3)[:30])
    kwargs.setdefault('application', create_application())

    return factories.ResponseStubFactory.create(**kwargs)


def create_resource_stub(**kwargs) -> ResourceStub:
    kwargs.setdefault('slug', fake.slug())
    kwargs.setdefault('description', fake.paragraph(nb_sentences=3))
    kwargs.setdefault('method', fake.http_method())
    kwargs.setdefault('application', create_application())
    kwargs.setdefault('response', create_response_stub())
    kwargs.setdefault('proxy_destination_address', None)
    kwargs.setdefault('response_type', ResponseChoices.CUSTOM)

    return factories.ResourceStubFactory.create(**kwargs)


def create_resource_hook(**kwargs) -> ResourceHook:
    kwargs.setdefault('lifecycle', Lifecycle.AFTER_REQUEST.value)
    kwargs.setdefault('action', Action.WAIT.value)
    kwargs.setdefault('timeout', 0)
    kwargs.setdefault('resource', create_resource_stub())
    kwargs.setdefault('order', 1)

    return factories.ResourceHook.create(**kwargs)
