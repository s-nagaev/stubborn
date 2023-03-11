from typing import Any

from django.forms import ModelForm

from apps.models import Application, RequestStub, ResourceStub, ResponseStub
from apps.wigdets import Editor


class ResourceStubForm(ModelForm):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        if args:
            return
        if data := kwargs.get('initial'):
            self.fields['response'].queryset = ResponseStub.objects.filter(application__pk=data.get('application'))
            self.fields['application'].queryset = Application.objects.filter(pk=data.get('application'))
            return
        elif self.instance and hasattr(self.instance, 'application'):
            self.fields['response'].queryset = ResponseStub.objects.filter(application=self.instance.application)
            self.fields['application'].queryset = Application.objects.filter(pk=self.instance.application.pk)
            return
        else:
            self.fields['response'].queryset = ResponseStub.objects.none()
            self.fields['application'].queryset = Application.objects.none()

    class Meta:
        model: ResourceStub
        fields = [
            'is_enabled',
            'response_type',
            'method',
            'slug',
            'tail',
            'response',
            'proxy_destination_address',
            'description',
            'application',
        ]


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
        fields = '__all__'
        widgets = {
            'headers': Editor(attrs={'style': 'width: 90%; height: 100%;'}),
            'body': Editor(attrs={'style': 'width: 90%; height: 100%;'}),
        }


class WebHookRequestForm(ModelForm):
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
        model: RequestStub
        fields = '__all__'
        widgets = {
            'headers': Editor(attrs={'style': 'width: 90%; height: 100%;'}),
            'body': Editor(attrs={'style': 'width: 50%; height: 50%;'}),
            'query_params': Editor(attrs={'style': 'width: 90%; height: 100%;'}),
        }
