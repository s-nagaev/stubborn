from django.contrib.auth.models import User
from django.db import models

from apps.enums import HTTPMethods


class Application(models.Model):
    name = models.CharField(max_length=50, verbose_name='Name', null=False)
    description = models.TextField(verbose_name='Description', null=True, blank=True)
    slug = models.SlugField(verbose_name='Slug', allow_unicode=True, null=False, unique=True)
    owner = models.ForeignKey(User, verbose_name='Application Owner', null=True, blank=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'application'
        verbose_name_plural = 'applications'

    def __str__(self) -> str:
        """Object's string representation.

        Returns:
            String representation.
        """
        return f'{self.name}'


class ResponseStub(models.Model):
    status_code = models.PositiveSmallIntegerField(verbose_name='Status code', null=False)
    headers = models.JSONField(verbose_name='Headers', default=dict, blank=True)
    body = models.TextField(verbose_name='Response Body', null=True, blank=True)
    timeout = models.PositiveSmallIntegerField(verbose_name='Response Timeout', default=0)
    description = models.CharField(max_length=30, verbose_name='Short Description', null=True, blank=True)
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='responses')

    class Meta:
        verbose_name = 'response'
        verbose_name_plural = 'responses'

    def __str__(self) -> str:
        """Object's string representation.

        Returns:
            String representation.
        """
        if self.description:
            return f'{self.status_code} {self.description}'
        return f'{self.status_code}'


class ResourceStub(models.Model):
    uri = models.SlugField(verbose_name='URI', allow_unicode=True, null=False)
    response = models.ForeignKey(ResponseStub, verbose_name='Response', related_name='resources',
                                 on_delete=models.CASCADE, null=False)
    description = models.TextField(verbose_name='Description', null=True, blank=True)
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='resources')
    method = models.CharField(max_length=10, choices=HTTPMethods.choices, verbose_name='HTTP Method')

    class Meta:
        verbose_name = 'resource'
        verbose_name_plural = 'resources'
        unique_together = ('uri', 'method')

    def __str__(self) -> str:
        """Object's string representation.

        Returns:
            String representation.
        """
        return f'{self.uri}'


class RequestLog(models.Model):
    params = models.JSONField(verbose_name='Query Params', default=dict, null=True, blank=True)
    body = models.JSONField(verbose_name='Request Body', default=dict, null=True, blank=True)
    headers = models.JSONField(verbose_name='Headers', default=dict, null=True, blank=True)
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='logs')
    resource = models.ForeignKey(ResourceStub, on_delete=models.CASCADE, related_name='logs')
    ipaddress = models.GenericIPAddressField(verbose_name='Remote IP', default='127.0.0.1')
    x_real_ip = models.GenericIPAddressField(verbose_name='X-REAL-IP', default='127.0.0.1', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Received at')
    response = models.ForeignKey(ResponseStub, verbose_name='Response', null=True, blank=True, on_delete=models.CASCADE,
                                 related_name='logs')

    class Meta:
        verbose_name = 'request log'
        verbose_name_plural = 'request logs'

    def __str__(self) -> str:
        """Object's string representation.

        Returns:
            String representation.
        """
        return f'{self.resource.method} /{self.resource.uri} {self.resource.response.status_code}'
