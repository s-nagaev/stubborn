import random

import factory
from django.contrib.auth import get_user_model
from faker import Faker

from apps import models

fake = Faker()
Faker.seed(random.randint(1, 1024))
user_model = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    username = fake.word()

    class Meta:
        model = user_model
        django_get_or_create = ('username',)


class ApplicationFactory(factory.django.DjangoModelFactory):
    slug = fake.slug()

    class Meta:
        model = models.Application
        django_get_or_create = ('slug',)


class ResponseStubFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.ResponseStub


class ResourceStubFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.ResourceStub


class RequestLog(factory.django.DjangoModelFactory):
    class Meta:
        model = models.RequestLog


class ResourceHook(factory.django.DjangoModelFactory):
    class Meta:
        model = models.ResourceHook


class RequestStub(factory.django.DjangoModelFactory):
    class Meta:
        model = models.RequestStub
