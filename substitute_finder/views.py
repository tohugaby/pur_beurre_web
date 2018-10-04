import logging
from itertools import chain, zip_longest
from pprint import pprint

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.paginator import Paginator
from django.db.models import Q, QuerySet
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render

from .forms import (AccountCreateForm, CustomLoginForm, ParagrapheErrorList,
                    ProductsSearchForm)
from .helpers import search_product
from .models import CustomUser, Product

# Create your views here.
LOGGER = logging.getLogger(__name__)


@login_required
def account_view(request):
    """
    Account view
    """
    return render(request, 'substitute_finder/account.html', {})


def create_account_view(request):
    """
    Page to create an account
    """
    context = {}
    if request.method == 'POST':
        form = AccountCreateForm(request.POST, error_class=ParagrapheErrorList)
        if form.is_valid():
            new_user = form.save()
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
            LOGGER.error("Error during login")
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


def index_view(request):
    """
    Home view
    """
    form = ProductsSearchForm()
    context = {'form': form}
    return render(request, 'substitute_finder/index.html', context)


def search_view(request, *args, **kwargs):
    """
    Search result view.
    """

    context = {
        "form": ProductsSearchForm()
    }
    if request.method == 'POST':
        form = ProductsSearchForm(request.POST, error_class=ParagrapheErrorList)

        if form.is_valid():
            search = form.cleaned_data['product']
            context['search'] = search
            request.session['last_search'] = search
            result = search_product(request.POST['product'])

            products = [product[0] for product in result]
            paginator = Paginator(products, settings.MAX_RESULT_PER_PAGE)

            context['products'] = paginator.get_page(1)

            request.session['last_products'] = [product[0].pk for product in result]
            if len(result) == 1:
                context['product'] = [product[0] for product in result][0]
                context['products'] = []
                return render(request, 'substitute_finder/product.html', context)
            if len(result) == 0:
                messages.info(request, "Aucun produit de notre base de données ne correspond à votre recherche.")

            return render(request, 'substitute_finder/product_list.html', context)
        else:
            for key, value in form.errors.items():

                messages.error(request, value)

        return redirect("/")

    else:
        if 'last_products' and 'last_search' in request.session:
            products = Product.objects.filter(pk__in=request.session['last_products'])
            paginator = Paginator(products, settings.MAX_RESULT_PER_PAGE)
            page = request.GET.get('page')
            context['products'] = paginator.get_page(page)
            context['search'] = request.session['last_search']
            return render(request, 'substitute_finder/product_list.html', context)
        else:
            return redirect("/")


def product_view(request, *args, **kwargs):
    """
    Product page view.
    """
    product = Product.objects.get(pk=kwargs['pk'])
    categories = product.categories_tags.all()

    products_query_list = []
    for category in categories:
        products_query_list.append(category.product_set.filter(
            nutrition_grade_fr__lt=product.nutrition_grade_fr, pk__in=request.session['last_products']).exclude(nutrition_grade_fr=''))
    # products = Product.objects.filter(
    #     nutrition_grade_fr__lt=product.nutrition_grade_fr, pk__in=request.session['last_products']).exclude(nutrition_grade_fr='').order_by('nutrition_grade_fr')
    products = sorted(list(set(chain(*products_query_list))), key=lambda x: x.nutrition_grade_fr)

    queryset_list = []
    for category in categories:
        queryset_list.append(category.product_set.filter(
            nutrition_grade_fr__lt=product.nutrition_grade_fr).exclude(pk__in=request.session['last_products']).exclude(nutrition_grade_fr=''))
    others = sorted(list(set(chain(*queryset_list))), key=lambda x: x.nutrition_grade_fr)

    paginator = Paginator(others, settings.MAX_RESULT_PER_PAGE)
    page = request.GET.get('page')

    grades = sorted([value['nutrition_grade_fr'] for value in Product.objects.values('nutrition_grade_fr').distinct()])

    context = {
        'product': product,
        'products': products,
        'others': paginator.get_page(page),
        'categories': categories,
        'grades': grades,
        "form": ProductsSearchForm()
    }
    return render(request, 'substitute_finder/product.html', context)


@login_required
def add_favorite_view(request, *args, **kwargs):
    """
    View that associate product to current user
    """
    product = Product.objects.get(pk=kwargs['pk'])
    product.users.add(request.user)

    return JsonResponse({request.user.pk: kwargs['pk']})


@login_required
def favorites_view(request):
    """
    View that displays user favorites
    """

    context = {
        "products": request.user.favorite.all(),
        "form": ProductsSearchForm()
    }

    return render(request, 'substitute_finder/favorites.html', context)


def legal_view(request):
    """
    View that displays legal stuff.
    """
    return render(request, 'substitute_finder/legal_stuff.html')
