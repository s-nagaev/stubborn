from typing import Any

from django.forms import ModelForm

from apps.models import Application, ResourceStub, ResponseStub


class ResourceStubForm(ModelForm):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        if args:
            return
        if data := kwargs.get('initial'):
            self.fields['response'].queryset = ResponseStub.objects.filter(application__pk=data.get('application'))
            self.fields['application'].queryset = Application.objects.filter(pk=data.get('application'))
        elif self.instance and hasattr(self.instance, 'application'):
            self.fields['response'].queryset = ResponseStub.objects.filter(application=self.instance.application)
            self.fields['application'].queryset = Application.objects.filter(pk=self.instance.application.pk)
        else:
            self.fields['response'].queryset = ResponseStub.objects.none()
            self.fields['application'].queryset = Application.objects.none()

    class Meta:
        model: ResourceStub


class ResponseStubForm(ModelForm):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields['body'].strip = False

        if args:
            return
        if data := kwargs.get('initial'):
            self.fields['application'].queryset = Application.objects.filter(pk=data.get('application'))
        elif self.instance and hasattr(self.instance, 'application'):
            self.fields['application'].queryset = Application.objects.filter(pk=self.instance.application.pk)
        else:
            self.fields['application'].queryset = Application.objects.none()

    class Meta:
        model: ResponseStub
