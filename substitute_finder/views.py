import logging
from itertools import chain, zip_longest
from pprint import pprint

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render

from .forms import AccountCreateForm, CustomLoginForm, ParagrapheErrorList, ProductsSearchForm
from .helpers import search_product
from .models import CustomUser, Product

# Create your views here.
LOGGER = logging.getLogger(__name__)


def index(request):
    """
    Home view
    """
    form = ProductsSearchForm()
    context = {'form': form}
    return render(request, 'substitute_finder/index.html', context)


def search(request, *args, **kwargs):
    """
    Search result view.
    """
    context = {}
    if request.method == 'POST':
        form = ProductsSearchForm(request.POST, error_class=ParagrapheErrorList)

        if form.is_valid():

            context['search'] = form.cleaned_data['product']

            result = search_product(request.POST['product'])

            print(len(result))
            context['products'] = [product[0] for product in result]

            if len(result) == 1:
                return render(request, 'substitute_finder/product.html', context)
            if len(result) == 0:
                messages.info(request, "Aucun produit de notre base de données ne correspond à votre recherche.")
            return render(request, 'substitute_finder/product_list.html', context)
        else:
            for key, value in form.errors.items():
                print(key)
                print(value)
                messages.error(request, value)

        return redirect("/")

    else:
        return redirect("/")


@login_required
def account(request):
    """
    Account view
    """
    return render(request, 'substitute_finder/account.html', {})


def create_account(request):
    """
    Page to create an account
    """
    context = {}
    if request.method == 'POST':
        form = AccountCreateForm(request.POST, error_class=ParagrapheErrorList)
        if form.is_valid():
            new_user = CustomUser.objects.create(**form.cleaned_data)
            login(request, new_user)
            return redirect('substitute_finder:index')
        else:
            context['errors'] = form.errors.items()
    else:
        form = AccountCreateForm()

    context['form'] = form

    return render(request, 'registration/create_account.html', context)


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
