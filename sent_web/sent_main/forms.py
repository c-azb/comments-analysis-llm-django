
from django import forms
import re

class LoginForm(forms.Form):
    username_or_email = forms.CharField(
        min_length=3,
        label='Email or Username',
        widget=forms.TextInput(attrs={
            'class':'form-control',
            'placeholder':'email or username'
        }))
    password = forms.CharField(min_length=3,
                               label='Password',
                               widget=forms.PasswordInput(attrs={
                                   'class':'form-control',
                                   'placeholder':'password'
                               }))

from django.contrib.auth.forms import UserCreationForm
#from django.contrib.auth.models import User
from accounts.models import CustomUser

class RegistrationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add custom attributes to each field
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({
                'class': 'form-control',
                'placeholder': self.fields[field_name].label
            })

        # Optional: Rename labels
        self.fields['email'].label = "Email address"

    def clean_username(self):
        username = self.cleaned_data.get('username')
        invalid_characters = re.findall('[^a-zA-Z ]',username)
        if len(invalid_characters) > 0:
            raise forms.ValidationError(f"Invalid characters: {invalid_characters}")
        match_ = re.match('[a-zA-Z ]{3,15}',username)
        if match_ == None or match_.group(0) != username:
             raise forms.ValidationError("Invalid username.")
        return username
    
    def clean_password1(self):
        #removed from AUTH_PASSWORD_VALIDATORS in settings.py for simplification and flexibility
        psw1 = self.cleaned_data.get('password1')
        match_ = re.match('[\w\d\s!@#$%&*()]{3,15}',psw1)
        if match_ == None or match_.group(0) != psw1:
            raise forms.ValidationError("Invalid password")
        return psw1
    
    def clean_password2(self):
        psw2 = self.cleaned_data.get('password2')
        psw1 = self.cleaned_data.get('password1')
        if psw1 != psw2:
            raise forms.ValidationError("Passwords don\'t match...")
        return psw2