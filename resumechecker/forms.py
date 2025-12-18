from django import forms
from .models import Resume
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm


class ResumeForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ['file','job']


class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']


