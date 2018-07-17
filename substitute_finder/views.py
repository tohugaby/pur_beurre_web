import logging

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomLoginForm, ParagrapheErrorList
# Create your views here.
LOGGER = logging.getLogger(__name__)


def index(request):
    """
    Home view
    """
    context = {}
    return render(request, 'substitute_finder/index.html', context)


def login_view(request):
    """
    View that manage login form 
    """
    context = {}
    if request.method == 'POST':
        form = CustomLoginForm(request.POST, error_class=ParagrapheErrorList)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('substitute_finder:index')
        else:
            LOGGER.error("bouuuuh")
            context['errors'] = form.errors.items()
    else:
        form = CustomLoginForm()

    context['form'] = form

    return render(request, 'registration/login.html', context)


def logout_view(request):
    """
    View that manage log out
    """
    logout(request)
    return redirect('substitute_finder:index')
