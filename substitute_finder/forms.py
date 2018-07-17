from django import forms
from django.forms.utils import ErrorList


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
