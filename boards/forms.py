from django import forms
from django.forms.models import inlineformset_factory
from colorfield.fields import ColorField
from colorfield.widgets import ColorWidget
from django.forms.widgets import TextInput, SelectDateWidget
from django.forms import DateTimeInput


from .models import Bar, CardComment, Card, CardLabel


class BarForm(forms.ModelForm):
    class Meta:
        model = Bar
        fields = ('title',)


class CardCreateForm(forms.ModelForm):
    class Meta:
        model = Card
        fields = ('title', 'description', 'deadline')
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
        model = CardLabel
        fields = ('title', 'color')
        widgets = {
            'color': TextInput(attrs={"type": "color", })
        }


labelFormset = inlineformset_factory(
    Card,
    CardLabel,
    form=CardLabelForm,
    extra=1,
    can_delete=False,
)


class CommentForm(forms.ModelForm):
    class Meta:
        model = CardComment
        fields = ('body',)