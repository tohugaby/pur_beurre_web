from django import forms
from django.forms.utils import ErrorList

from .models import CustomUser


class ParagrapheErrorList(ErrorList):
    def __str__(self):
        return self.as_divs()

    def as_divs(self):
        if not self:
            return ''
        return '<p>%s</p>' % ''.join(['<p>%s</p>' % e for e in self])


class CustomLoginForm(forms.Form):
    email = forms.EmailField(
        label="email",
        widget=forms.EmailInput(
            attrs={'class': 'form-control', 'placeholder': 'Email'}
        ),
        required=True)
    password = forms.CharField(
        label="mot de passe",
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'Mot de passe'}
        ),
        required=True)


class AccountCreateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['email', 'username','first_name', 'last_name','password']
        widgets = {
            'email':forms.EmailInput( attrs={'class': 'form-control', 'placeholder': 'Email'}), 
            'username': forms.TextInput( attrs={'class': 'form-control', 'placeholder': 'Pseudo'}),
            'first_name':forms.TextInput( attrs={'class': 'form-control', 'placeholder': 'Prénom'}), 
            'last_name':forms.TextInput( attrs={'class': 'form-control', 'placeholder': 'Nom'}),
            'password': forms.PasswordInput( attrs={'class': 'form-control', 'placeholder': 'Mot de passe'})
        }
