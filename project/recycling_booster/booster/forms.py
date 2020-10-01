from django import forms
from django.forms import ModelForm

from booster.models import Contribution

class LoginForm(forms.Form):
    username = forms.CharField(max_length=32)
    password = forms.CharField(widget=forms.PasswordInput())

class RegisterForm(LoginForm):
    repeat_password = forms.CharField(widget=forms.PasswordInput())

class ContributionForm(forms.ModelForm):
    class Meta:
        model = Contribution
        fields = ('waste_type', 'adress', 'photo_url')
