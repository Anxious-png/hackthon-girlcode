from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from .models import UserProfile
from django.contrib.auth.forms import UserCreationForm

class UserSignupForm(UserCreationForm):
    password = forms.CharField(widget=forms.PasswordInput)
    
    class Meta:
        model = UserProfile
        fields = ['username', 'email', 'password', 'phonenumber', 'user_type']

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'autofocus': True}))
    password = forms.CharField(widget=forms.PasswordInput)
