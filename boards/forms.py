from django import forms
from django.forms.models import inlineformset_factory
from colorfield.fields import ColorField
from colorfield.widgets import ColorWidget
from django.forms.widgets import TextInput


from .models import Bar, CardComment, Card, CardLabel


class BarForm(forms.ModelForm):
    class Meta:
        model = Bar
        fields = ('title',)


class CardForm(forms.ModelForm):
    class Meta:
        model = Card
        fields = ('bar', 'title', 'description', 'deadline')


class CardLabelForm(forms.ModelForm):
    class Meta:
        model = CardLabel
        fields = ('title', 'color')
        COLOR_CHOICES = ['#8b0000', '#ffff00', '#006400']
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