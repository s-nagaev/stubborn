import json
from typing import Any

from django.forms import ModelForm

from apps.models import Application, ResourceStub, ResponseStub
from apps.wigdets import Editor


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
        fields = ['response_type', 'method', 'slug', 'tail', 'response', 'proxy_destination_address', 'description',
                  'application']


class ResponseStubForm(ModelForm):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields['body'].strip = False

        print(dir(self.fields['headers'])) # = json.dumps(self.fields['headers'], indent=4)

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
