import json
import os
from pprint import pprint

import requests
import requests_mock
from django.conf import settings
from django.test import TestCase

from substitute_finder.models import Category, Product

# get a data source urls for a model
#   - for a list
#   - for an element


class UrlGetterTestCase(TestCase):

    def setUp(self):
        self.category_id = 'en:plant-based-foods-and-beverages'
        self.product_id = '3222472887966'

    def test_get_url_for_category_list(self):
        url = Category.get_list_api_url()
        self.assertIsNotNone(url)

    def test_get_url_for_category_element(self):
        url = Category.get_element_api_url(id=self.category_id)
        self.assertIsNone(url)

    def test_get_url_for_product_list(self):
        url = Product.get_list_api_url(9)
        self.assertIsNotNone(url)
        self.assertIn('9', url)

    def test_get_url_for_product_element(self):
        url = Product.get_element_api_url(id=self.product_id)
        self.assertIsNotNone(url)


# get data
#   - for a list
#   - for an element

class DataGetterTestCase(TestCase):

    def setUp(self):
        self.category_id = 'en:plant-based-foods-and-beverages'
        self.product_id = '3222472887966'
        self.FAKE_DATA_PATH = os.path.join(
            os.path.dirname(__file__), 'fake_data')

    def test_get_data_for_category_list(self):
        with open(os.path.join(self.FAKE_DATA_PATH, 'categories.json'), 'r') as file:
            fake_data_categories = file.read()
        with requests_mock.Mocker() as m:
            m.get(Category.get_list_api_url(), text=fake_data_categories)
            data = Category.get_api_data_list()
            self.assertIsInstance(data, list)

    def test_get_data_for_category_element(self):
        data = Category.get_api_data_element(self.category_id)
        self.assertIsNone(data)

    def test_get_data_for_product_list(self):
        with open(os.path.join(self.FAKE_DATA_PATH, 'products1.json'), 'r') as file:
            fake_data_products_1 = file.read()
        with open(os.path.join(self.FAKE_DATA_PATH, 'products2.json'), 'r') as file:
            fake_data_products_2 = file.read()
        with open(os.path.join(self.FAKE_DATA_PATH, 'products3.json'), 'r') as file:
            fake_data_products_3 = file.read()

        with requests_mock.Mocker() as m:
            m.get(Product.get_list_api_url(1), text=fake_data_products_1)
            m.get(Product.get_list_api_url(2), text=fake_data_products_2)
            m.get(Product.get_list_api_url(3), text=fake_data_products_3)
            data = Product.get_api_data_list(nb_pages=2)
            self.assertEqual(len(data), 40)
            data = Product.get_api_data_list()
            self.assertEqual(len(data), 60)

    def test_get_data_for_product_element(self):
        with open(os.path.join(self.FAKE_DATA_PATH, '3222472887966.json'), 'r') as file:
            fake_data_product = file.read()
        with requests_mock.Mocker() as m:
            m.get(Product.get_element_api_url(
                self.product_id), text=fake_data_product)
            data = Product.get_api_data_element(self.product_id)
            self.assertIsInstance(data, dict)


# write file
#   - for a list
#   - for an element


class DataWritterTestCase(TestCase):
    def setUp(self):
        self.FAKE_DATA_PATH = os.path.join(
            os.path.dirname(__file__), 'fake_data')
        self.product_id = '3222472887966'

    def tearDown(self):
        # TODO: need to remove only test files
        file_list = os.listdir(settings.JSON_DIR_PATH)
        for f in file_list:
            os.remove(os.path.join(settings.JSON_DIR_PATH, f))

    def test_write_file_for_category_list(self):
        file_path = os.path.join(
            settings.JSON_DIR_PATH, "%s_list.json" % Category._meta.model_name)

        with open(os.path.join(self.FAKE_DATA_PATH, 'categories.json'), 'r') as file:
            fake_data_categories = file.read()
        with requests_mock.Mocker() as m:
            m.get(Category.get_list_api_url(), text=fake_data_categories)
            data = Category.get_api_data_list()
            file = Category.write_api_data(data)
            self.assertTrue(os.path.exists(file))

    def test_write_file_for_product_list(self):
        file_path = os.path.join(
            settings.JSON_DIR_PATH, "%s_list.json" % Product._meta.model_name)

        with open(os.path.join(self.FAKE_DATA_PATH, 'products1.json'), 'r') as file:
            fake_data_products_1 = file.read()
        with open(os.path.join(self.FAKE_DATA_PATH, 'products2.json'), 'r') as file:
            fake_data_products_2 = file.read()
        with open(os.path.join(self.FAKE_DATA_PATH, 'products3.json'), 'r') as file:
            fake_data_products_3 = file.read()

        with requests_mock.Mocker() as m:
            m.get(Product.get_list_api_url(1), text=fake_data_products_1)
            m.get(Product.get_list_api_url(2), text=fake_data_products_2)
            m.get(Product.get_list_api_url(3), text=fake_data_products_3)
            data = Product.get_api_data_list()
            file = Product.write_api_data(data)
            self.assertTrue(os.path.exists(file))

    def test_get_data_for_product_element(self):
        file_path = os.path.join(
            settings.JSON_DIR_PATH, "%s.json" % Product._meta.model_name)

        with open(os.path.join(self.FAKE_DATA_PATH, '3222472887966.json'), 'r') as file:
            fake_data_product = file.read()
        with requests_mock.Mocker() as m:
            m.get(Product.get_element_api_url(
                self.product_id), text=fake_data_product)
            data = Product.get_api_data_element(self.product_id)
            file = Product.write_api_data(data)
            self.assertTrue(os.path.exists(file))


# create model instances
#   - from a list of elements
#   - from an element

class DataInsertTestCase(TestCase):

    def setUp(self):
        self.FAKE_DATA_PATH = os.path.join(
            os.path.dirname(__file__), 'fake_data')
        self.product_id = '3222472887966'

    def test_insert_category_list(self):
        nb_elements_before = Category.objects.count()

        with open(os.path.join(self.FAKE_DATA_PATH, 'categories.json'), 'r') as file:
            fake_data_categories = file.read()
        with requests_mock.Mocker() as m:
            m.get(Category.get_list_api_url(), text=fake_data_categories)
            data = Category.get_api_data_list()

        Category.insert_data(data)
        nb_elements_after = Category.objects.count()
        self.assertGreater(nb_elements_after, nb_elements_before)

    def test_insert_product_list(self):

        with open(os.path.join(self.FAKE_DATA_PATH, 'categories.json'), 'r') as file:
            fake_data_categories = file.read()
        with requests_mock.Mocker() as m:
            m.get(Category.get_list_api_url(), text=fake_data_categories)
            data = Category.get_api_data_list()

        Category.insert_data(data)

        nb_elements_before = Product.objects.count()

        with open(os.path.join(self.FAKE_DATA_PATH, 'products1.json'), 'r') as file:
            fake_data_products_1 = file.read()
        with open(os.path.join(self.FAKE_DATA_PATH, 'products2.json'), 'r') as file:
            fake_data_products_2 = file.read()
        with open(os.path.join(self.FAKE_DATA_PATH, 'products3.json'), 'r') as file:
            fake_data_products_3 = file.read()

        with requests_mock.Mocker() as m:
            m.get(Product.get_list_api_url(1), text=fake_data_products_1)
            m.get(Product.get_list_api_url(2), text=fake_data_products_2)
            m.get(Product.get_list_api_url(3), text=fake_data_products_3)
            data = Product.get_api_data_list()

        Product.insert_data(data)
        nb_elements_after = Product.objects.count()
        self.assertGreater(nb_elements_after, nb_elements_before)
