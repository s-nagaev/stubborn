from django.urls import re_path

from apps.views import ResponseStubView

urlpatterns = [
    re_path(r'^(?P<app_slug>[\w-]+)/(?P<resource_slug>[\w-]+)/$', ResponseStubView.as_view()),
]
