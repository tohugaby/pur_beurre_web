"""
substitute_finder app forms.
"""
from django import forms
from django.contrib.auth import authenticate
from django.forms.utils import ErrorList

from substitute_finder.models import Comment
from .models import CustomUser


class ParagraphErrorList(ErrorList):
    """
    Custom error to return paragraphs instead of list.
    """

    def __str__(self):
        return self.as_divs()

    def as_divs(self):
        """
        return html formated error.
        """
        if not self:
            return ''
        return '<p>%s</p>' % ''.join(['<p>%s</p>' % e for e in self])


class CustomLoginForm(forms.Form):
    """
    Custom login form that waits for email as username.
    """
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

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        user = authenticate(username=email, password=password)
        if not user or not user.is_active:
            raise forms.ValidationError("Identifiant ou mot de passe invalide.")
        return self.cleaned_data


class AccountCreateForm(forms.ModelForm):
    """
    Account Create form.
    """

    class Meta:
        model = CustomUser
        fields = ['email', 'username', 'first_name', 'last_name', 'password']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Pseudo'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénom'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Mot de passe'})
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class ProductsSearchForm(forms.Form):
    """
    Form used for product search.
    """
    product = forms.CharField(label="Recherche", widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Votre recherche'}), required=True)


class CreateOrUpdateCommentForm(forms.ModelForm):
    """
    Form to create a comment.
    """
    class Meta:
        model = Comment
        fields = ['comment_text', ]
        widgets = {
            'comment_text': forms.Textarea(
                attrs={'class': 'form-control', 'rows': "3", 'placeholder': 'Saisissez votre '
                                                                            'commentaire ici'}),
        }
