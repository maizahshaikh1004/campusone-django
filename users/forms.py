from django import forms
from .models import RegistrationRequest

class RegistrationRequestForm(forms.ModelForm):
    class Meta:
        model=RegistrationRequest
        fields=[
            "name",
            "email",
            "role",
            "department",
            "academic_class"
        ]

class LoginForm(forms.Form):
    username=forms.CharField(max_length=150)
    password=forms.CharField(widget=forms.PasswordInput)
    
    