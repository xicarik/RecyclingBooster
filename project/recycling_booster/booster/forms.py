from django import forms
from django.forms import ModelForm
from django.core.validators import MaxValueValidator, MinValueValidator

from booster.models import *

class LoginForm(forms.Form):
    username = forms.CharField(max_length=32)
    password = forms.CharField(widget=forms.PasswordInput())

class RegisterForm(LoginForm):
    repeat_password = forms.CharField(widget=forms.PasswordInput())

class ContributionForm(forms.ModelForm):
    class Meta:
        model = Contribution
        fields = ('waste_type', 'adress', 'photo_url')

class RecycleSpotForm(forms.Form):
    latitude = forms.FloatField()
    longitude = forms.FloatField()
    point_type = forms.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(1)])
    waste_type = forms.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(7)])
    adress = forms.CharField(max_length=200)
    link = forms.CharField(max_length=500)

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
