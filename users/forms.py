from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import MyUser


class MyUserCreationForm(UserCreationForm):

    class Meta:
        model = MyUser
        fields = ('email', 'first_name', 'last_name', 'password1', 'password2')


class MyUserChangeForm(UserChangeForm):

    class Meta:
        model = MyUser
        fields = ('email', 'first_name', 'last_name')