from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SignUpForm(UserCreationForm):
    real_name = forms.CharField(max_length=16, required=False, help_text='Zorunlu değil')
    email = forms.EmailField(max_length=254, help_text='Ulaşabildiğiniz bir email adresi girin')
    dogum_yili = forms.DateField(help_text='Zorunlu')

    class Meta:
        model = User
        fields = ('username', 'real_name', 'dogum_yili', 'email', 'password1', 'password2', )
