import copy
import json
import logging
import os

import requests
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
LOGGER = logging.getLogger(__name__)


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
    def get_api_data_list(cls, nb_pages=None, start_page=1, from_cache=False):
        data = []
        if cls.paginated_data:
            page = start_page
            go_next_page = True
            while go_next_page:
                cleaned_data = []
                suffix = '_list_%s.json' % page
                file_path = os.path.join(settings.JSON_DIR_PATH, "%s%s" % (cls._meta.model_name, suffix))
                if from_cache and os.path.exists(file_path):
                    LOGGER.info("Getting data for %s from cache for page %s " % (cls._meta.model_name, page))                 
                    with open(file_path, 'r') as file:
                        cleaned_data = json.loads(file.read())
                else:
                    LOGGER.info("Getting data for %s from %s" % (cls._meta.model_name, cls.get_list_api_url(page=page)))
                    page_data = requests.get(cls.get_list_api_url(page=page))
                    temp_data = page_data.json()
                    cleaned_data = temp_data[cls.list_data_key]
                    cls.write_api_data(cleaned_data, custom_suffix=page)

                    # check if there are no more pages after.
                    if temp_data['skip'] + temp_data['page_size'] >= temp_data['count']:
                        go_next_page = False

                page += 1
                # after page increasing check if loop should continue according to nb_pages parameter
                if nb_pages and page >= nb_pages + start_page:
                    go_next_page = False

                data += cleaned_data
        else:
            suffix = '_list.json'
            file_path = os.path.join(settings.JSON_DIR_PATH, "%s%s" % (cls._meta.model_name, suffix))
            if from_cache and os.path.exists(file_path):
                LOGGER.info("Getting data for %s from cache" % cls._meta.model_name)                 
                with open(file_path, 'r') as file:
                    cleaned_data = json.loads(file.read())
            else:
                LOGGER.info("Getting data for %s from %s" % (
                    cls._meta.model_name, cls.get_list_api_url()))
                page_data = requests.get(cls.get_list_api_url())
                temp_data = page_data.json()
                cleaned_data = temp_data[cls.list_data_key]
            cls.write_api_data(cleaned_data)
            data += cleaned_data
        return data

    @classmethod
    def get_api_data_element(cls, id):
        if cls.get_element_api_url(id):
            LOGGER.info("Getting data for %s from %s" % (
                cls._meta.model_name, cls.get_element_api_url(id)))
            data = requests.get(cls.get_element_api_url(id))
            return data.json()

    @classmethod
    def write_api_data(cls, data, custom_suffix=''):
        suffix_extension = '.json'
        if custom_suffix:
            suffix_extension = "_%s.json" % custom_suffix
        suffix = suffix_extension
        if isinstance(data, list):
            suffix = '_list%s' % suffix_extension

        file_path = os.path.join(
            settings.JSON_DIR_PATH, "%s%s" % (cls._meta.model_name, suffix))
        with open(file_path, 'w') as file:
            file.write(json.dumps(data))
        return file_path

    @classmethod
    def insert_data(cls, data):
        LOGGER.info("Create or update data for %s " % cls._meta.model_name)
        field_names = [f.name for f in cls._meta.get_fields()]
        primary_key_field_name = cls._meta.pk.name
        many_to_many_field_names = [f.name for f in cls._meta.many_to_many]
        cleaned_data = []
        if isinstance(data, list):
            for d in data:
                unused_keys = [
                    key for key in d.keys() if key not in field_names]
                many_to_many_data = []
                pk_value = d[primary_key_field_name]
                for key in unused_keys:
                    del d[key]
                for key in many_to_many_field_names:
                    if key in d.keys():
                        many_to_many_data.append({key: d.pop(key)})
                new_element, created = cls.objects.update_or_create(
                    pk=pk_value, defaults=d)
                for many_to_many_element in many_to_many_data:
                    for key, values in many_to_many_element.items():
                        field = getattr(new_element, key)
                        for value in values:
                            field.add(value)
                LOGGER.info("%s %s in %s " % (new_element, "created" if created else "updated", cls._meta.model_name))


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
    categories_tags = models.ManyToManyField(
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
    name = models.CharField(verbose_name='nom', max_length=1000)
    url = models.URLField(verbose_name='url', max_length=1000)

    class Meta:
        verbose_name = 'Catégorie'
        verbose_name_plural = 'Catégories'

    def __str__(self):
        return self.name
