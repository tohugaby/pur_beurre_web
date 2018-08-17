"""
Define substitute_finder models
"""

import copy
import json
import logging
import os

import requests
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

__author__ = 'Tom Gabrièle'

LOGGER = logging.getLogger(__name__)


class CustomUser(AbstractUser):
    """
    Define a user identified by his/her email address.
    """
    email = models.EmailField('email address', unique=True)

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


class FromApiUpdateMixin:
    """
    Mixin that allow to managed data recovery and integration from opentfoodfacts api to database model.
    """

    # These variables must be defined in models so that mixin methods work.
    list_url_template = ''
    element_url_template = ''
    paginated_data = True
    list_data_key = ''
    element_data_key = ''

    @classmethod
    def get_list_api_url(cls, page: int=1):
        """
        Allow to generate url for list of data recovery according to pagination class attribute and page parameter.
            :param page: number of page to read from api
            :type page: int
        """

        if cls.paginated_data:
            # Deal with paginated data list
            return cls.list_url_template.format(page=page)

        return cls.list_url_template

    @classmethod
    def get_element_api_url(cls, id: str):
        """
        Allow to generate url for an element recovery according to its id.
            :param id: id of element to read from api
            :type id: str
        """

        if cls.element_url_template:
            return cls.element_url_template.format(id=id)

    @classmethod
    def get_api_data_list(cls, nb_pages: int=None, start_page: int=1, from_cache: bool=False):
        """
        Get data list from web api for model according to number of pages and start page constraints. 
        Allow to get data from cache when it's possible.
            :param nb_pages : for paginated data list, indicate the max number of page to recover
            :type nb_pages: int
            :param start_page: for paginated data list, indicate the index of the page to start recovery from
            :type start_page: int
            :param from_cache: if data have been already recoverered, it's possible to work with cached data
            :type from_cache: bool
        """

        data = []

        # Deal with paginated data list
        if cls.paginated_data:
            page = start_page
            go_next_page = True

            # Loop until there are no more data or until asked number of pages recovered is raised
            while go_next_page:
                cleaned_data = []
                suffix = '_list_%s.json' % page
                file_path = os.path.join(settings.JSON_DIR_PATH, "%s%s" % (cls._meta.model_name, suffix))

                # Work with cached data when available
                if from_cache and os.path.exists(file_path):
                    LOGGER.info("GETTING data for %s from cache for page %s " % (cls._meta.model_name, page))
                    with open(file_path, 'r') as file:
                        cleaned_data = json.loads(file.read())

                # Work with web api
                else:
                    LOGGER.info("GETTING data for %s from %s" % (cls._meta.model_name, cls.get_list_api_url(page=page)))
                    page_data = requests.get(cls.get_list_api_url(page=page))
                    temp_data = page_data.json()
                    cleaned_data = temp_data[cls.list_data_key]

                    # Save recovered data into cache
                    cls.write_api_data(cleaned_data, custom_suffix=page)

                    # check if there are no more pages after.
                    if temp_data['skip'] + temp_data['page_size'] >= temp_data['count']:
                        go_next_page = False

                # Prepare next page recovery
                page += 1

                # After page increasing check if loop should continue according to nb_pages parameter
                if nb_pages and page >= nb_pages + start_page:
                    go_next_page = False

                # Add data from the page to data list
                data += cleaned_data

        # Deal with non paginated data list
        else:
            suffix = '_list.json'
            file_path = os.path.join(settings.JSON_DIR_PATH, "%s%s" % (cls._meta.model_name, suffix))

            # Work with cached data when available
            if from_cache and os.path.exists(file_path):
                LOGGER.info("GETTING data for %s from cache" % cls._meta.model_name)
                with open(file_path, 'r') as file:
                    cleaned_data = json.loads(file.read())

            # Work with web api
            else:
                LOGGER.info("GETTING data for %s from %s" % (
                    cls._meta.model_name, cls.get_list_api_url()))
                page_data = requests.get(cls.get_list_api_url())
                temp_data = page_data.json()
                cleaned_data = temp_data[cls.list_data_key]

            # Save recovered data into cache
            cls.write_api_data(cleaned_data)

            # Add data from the page to data list
            data += cleaned_data

        return data

    @classmethod
    def get_api_data_element(cls, id: str):
        """
        Get data from api for an element according to its id.
            :param id: element id
            :type id: str 
        """

        # Check if api url exists for element
        if cls.get_element_api_url(id):
            LOGGER.info("GETTING data for %s from %s" % (cls._meta.model_name, cls.get_element_api_url(id)))
            data = requests.get(cls.get_element_api_url(id))
            temp_data = data.json() 
            cleaned_data = temp_data
            return cleaned_data[cls.element_data_key]

    @classmethod
    def write_api_data(cls, data: list or dict, custom_suffix: str=''):
        """
        Write provided data into a file named according to type of provided data and custom suffix.
            :param data: data collection to write in file
            :type data: list or dict 
            :param custom_suffix: a suffix to custom file name
            :type custom_suffix: str
        """

        # Base suffix
        suffix_extension = '.json'

        # Custom suffix
        if custom_suffix:
            suffix_extension = "_%s.json" % custom_suffix
        suffix = suffix_extension

        # Change suffix according to type of provided data
        if isinstance(data, list):
            suffix = '_list%s' % suffix_extension

        # Check and create storage directory if it doesn't exists
        if not os.path.exists(settings.JSON_DIR_PATH):
            os.mkdir(settings.JSON_DIR_PATH)

        # Define file path
        file_path = os.path.join(
            settings.JSON_DIR_PATH, "%s%s" % (cls._meta.model_name, suffix))

        # Write data into file
        with open(file_path, 'w') as file:
            file.write(json.dumps(data))
        return file_path

    @classmethod
    def insert_data(cls, data: list or dict):
        """
        Create as many model instances as needed according to data provided
            :param data: data collection to insert in database
            :type data: list or dict
        """

        LOGGER.info("CREATE/UPDATE data for %s " % cls._meta.model_name)
        
        # Define model field names
        field_names = [f.name for f in cls._meta.get_fields()]
        
        # Define primary key name
        primary_key_field_name = cls._meta.pk.name
        
        # Define many to many field names
        many_to_many_field_names = [f.name for f in cls._meta.many_to_many]
        
        cleaned_data = []
        data_list = []
        
        # Insert data dict into a list
        if isinstance(data, dict):
            data_list.append(data)
        else:
            data_list = data

        # Deal with data list
        for d in data_list:
            
            # List keys from element in list which are not used by model
            unused_keys = [
                key for key in d.keys() if key not in field_names]
            
            # Find value of primary key
            pk_value = d[primary_key_field_name]

            many_to_many_data = []
            
            # Remove unused keys from element
            for key in unused_keys:
                del d[key]
            
            # Store keys and values from many to many fields
            for key in many_to_many_field_names:
                if key in d.keys():
                    many_to_many_data.append({key: d.pop(key)})
            
            # Create or update element in database
            new_element, created = cls.objects.update_or_create(pk=pk_value, defaults=d)
            
            # Add many to many fields values
            for many_to_many_element in many_to_many_data:
                for key, values in many_to_many_element.items():
                    field = getattr(new_element, key)
                    for value in values:
                        field.add(value)
            
            LOGGER.info("JUST %s %s in %s " % ("CREATE" if created else "UPDATE", new_element, cls._meta.model_name))


class Product(FromApiUpdateMixin, models.Model):
    """
    Define a Product.
    """

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
    """
    Define a category of product.
    """

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
