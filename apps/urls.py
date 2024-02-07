from django.urls import path, re_path

from apps.views import ExportToFile, HealthCheckView, ImportFromFile, ResponseStubView, StubRequestView

urlpatterns = [
    path('log/<uuid:log_id>/stub/', StubRequestView.as_view(), name='stub_it'),
    path('srv/export/<application_id>/', ExportToFile.as_view(), name='export'),
    path('srv/import/', ImportFromFile.as_view(), name='import'),
    re_path(r'^srv/alive/?$', HealthCheckView.as_view(), name='alive'),
    re_path(r'^(?P<app_slug>[\w-]+)/?(?P<resource_slug>[\w-]+)?/?$', ResponseStubView.as_view(), name='stub-url'),
    re_path(
        r'^(?P<app_slug>[\w-]+)/?(?P<resource_slug>[\w-]+)?/?(?P<tail>.+)$',
        ResponseStubView.as_view(),
        name='full-proxy-url',
    ),

]
