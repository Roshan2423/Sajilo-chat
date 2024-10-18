from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import MyModel

class CustomSignupForm(UserCreationForm):
    username = forms.CharField(max_length=150, label='Username')  # Added username field
    first_name = forms.CharField(max_length=30, label='First Name')
    last_name = forms.CharField(max_length=30, label='Last Name')
    email = forms.EmailField(max_length=254, label='Email Address')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')  # Included 'username'

    def save(self, commit=True):
        user_data = {
            'username': self.cleaned_data['username'],  # Use the provided username
            'first_name': self.cleaned_data['first_name'],
            'last_name': self.cleaned_data['last_name'],
            'email': self.cleaned_data['email'],
            'password': self.cleaned_data['password1'],
        }
        if commit:
            user = User.objects.create_user(**user_data)
            return user
        else:
            return User(**user_data)

class MyModelForm(forms.ModelForm):
    class Meta:
        model = MyModel
        fields = ['name', 'description']
