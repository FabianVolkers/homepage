from django.forms import ModelForm, ValidationError
from django.forms.widgets import TextInput
from .models import *


class IconForm(ModelForm):
    class Meta:
        model = Icon
        fields = '__all__'
        widgets = {
            'colour': TextInput(attrs={'type': 'color'}),
        }
