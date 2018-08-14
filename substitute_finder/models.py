from pprint import pprint

from django.db import models
from django.contrib.auth.models import AbstractUser


import requests

# Create your models here.


class CustomUser(AbstractUser):
    email = models.EmailField('email address', unique=True)

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


class FromApiUpdateMixin:
    list_url_template = ''
    element_url_template = ''
    paginated_data = True
    list_data_key = ''
    element_data_key = ''

    @classmethod
    def get_list_api_url(cls, page=1):
        if cls.paginated_data:
            return cls.list_url_template.format(page=page)
        return cls.list_url_template

    @classmethod
    def get_element_api_url(cls, id):
        if cls.element_url_template:
            return cls.element_url_template.format(id=id)

    @classmethod
    def get_api_data_list(cls, nb_pages=None):
        data = []
        if cls.paginated_data:
            page = 1
            go_next_page = True
            while go_next_page:
                print(cls.get_list_api_url(page=page))
                page_data = requests.get(cls.get_list_api_url(page=page))
                temp_data = page_data.json()
                
                # check if there are no more pages after.
                if temp_data['skip']+temp_data['page_size'] >= temp_data['count']:
                    go_next_page = False
                
                page += 1
                # after page increasing check if loop should continue according to nb_pages parameter
                if nb_pages and page > nb_pages:
                    go_next_page = False
                data+=temp_data[cls.list_data_key]
        else:
            print(cls.get_list_api_url())
            page_data = requests.get(cls.get_list_api_url())
            temp_data = page_data.json()
            data+=temp_data[cls.list_data_key]
        return data


    @classmethod
    def get_api_data_element(cls, id):
        if cls.get_element_api_url(id):
            print(cls.get_element_api_url(id))
            data = requests.get(cls.get_element_api_url(id))
            return data.json()


class Product(FromApiUpdateMixin, models.Model):

    list_url_template = 'https://fr.openfoodfacts.org/lieu-de-vente/france/lieu-de-fabrication/france/{page}.json'
    element_url_template = 'https://fr.openfoodfacts.org/api/v0/produit/{id}.json'
    list_data_key = 'products'
    element_data_key = 'product'

    code = models.CharField(
        primary_key=True, verbose_name='identifiant', max_length=300)
    product_name = models.CharField(
        verbose_name='nom du produit', max_length=300)
    generic_name = models.CharField(
        verbose_name='description', max_length=1000)
    url = models.URLField(
        verbose_name='url OpenFoodFacts', max_length=1000)
    stores = models.CharField(verbose_name='vendeur', max_length=300)
    nutrition_grade_fr = models.CharField(
        verbose_name='score nutritionnel', max_length=1)
    last_updated = models.DateTimeField(
        verbose_name='dernière mise à jour', auto_now=True)
    categories = models.ManyToManyField(
        to='Category', verbose_name='categories')
    users = models.ManyToManyField(
        to='CustomUser', related_name='favorite', verbose_name='utilisateurs')

    class Meta:
        verbose_name = 'Produit'
        verbose_name_plural = 'Produits'

    def __str__(self):
        return self.product_name


class Category(FromApiUpdateMixin, models.Model):

    list_url_template = 'https://fr.openfoodfacts.org/categories.json'
    element_url_template = None
    paginated_data = False
    list_data_key = 'tags'

    id = models.CharField(
        primary_key=True, verbose_name='identifiant', max_length=300)
    name = models.CharField(verbose_name='nom', max_length=300)
    url = models.URLField(verbose_name='url', max_length=300)

    class Meta:
        verbose_name = 'Catégorie'
        verbose_name_plural = 'Catégories'

    def __str__(self):
        return self.name
