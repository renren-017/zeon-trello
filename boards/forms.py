from django import forms
from django.forms.models import inlineformset_factory
from colorfield.fields import ColorField
from colorfield.widgets import ColorWidget
from django.forms.widgets import TextInput, SelectDateWidget
from django.forms import DateTimeInput

from .models import Column, CardComment, Card, Mark


class BarForm(forms.ModelForm):
    class Meta:
        model = Column
        fields = ('title',)
        widgets = {
            'title': TextInput(attrs={'style': 'width: 100%; max-height: 100%', 'class': 'text-xs is-size-7',})
        }


class CardCreateForm(forms.ModelForm):
    class Meta:
        model = Card
        fields = ('title', 'description', 'deadline', 'checklist')
        widgets = {
            'deadline': DateTimeInput(attrs={"type": "datetime-local", })
        }


class CardUpdateForm(forms.ModelForm):
    class Meta:
        model = Card
        fields = ('bar', 'title', 'description', 'deadline')
        widgets = {
            'deadline': DateTimeInput(attrs={"type": "datetime-local", })
        }


class CardLabelForm(forms.ModelForm):
    class Meta:
        model = Mark
        fields = ('title', 'color')
        widgets = {
            'color': TextInput(attrs={"type": "color", })
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = CardComment
        fields = ('body',)