from typing import Any

from django.forms import ModelForm

from apps.models import ResourceStub, ResponseStub


class ResourceStubForm(ModelForm):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        if data := kwargs.get('initial'):
            self.fields['response'].queryset = ResponseStub.objects.filter(application__pk=data.get('application', -1))
        elif self.instance and hasattr(self.instance, 'application'):
            self.fields['response'].queryset = ResponseStub.objects.filter(application=self.instance.application)
        else:
            self.fields['response'].queryset = ResponseStub.objects.none()

    class Meta:
        model: ResourceStub
        exclude = ('application',)
