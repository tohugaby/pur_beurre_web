"""
Tests for data getter tools.
"""
import json
import os
import requests_mock
from django.conf import settings
from django.test import TestCase

from substitute_finder.models import (Category, Product,
                                      find_dict_value_for_nested_key)
# get a data source urls for a model
#   - for a list
#   - for an element
from substitute_finder.tests.test_helpers import get_products_data_with_mock, get_categories_data_with_mock


class UrlGetterTestCase(TestCase):
    """
    Test url getters for elements and lists of data.
    """

    def setUp(self):
        self.category_id = 'en:plant-based-foods-and-beverages'
        self.product_id = '3222472887966'

    def test_get_url_for_category_list(self):
        """
        Test url getters for category list.
        :return:
        """
        url = Category.get_list_api_url()
        self.assertIsNotNone(url)

    def test_get_url_for_category_element(self):
        """
        Test url getters for category element.
        :return:
        """
        url = Category.get_element_api_url(element_id=self.category_id)
        self.assertIsNone(url)

    def test_get_url_for_product_list(self):
        """
        Test url getters for product list.
        :return:
        """
        url = Product.get_list_api_url(9)
        self.assertIsNotNone(url)
        self.assertIn('9', url)

    def test_get_url_for_product_element(self):
        """
        Test url getters for product element.
        :return:
        """
        url = Product.get_element_api_url(element_id=self.product_id)
        self.assertIsNotNone(url)


# get data
#   - for a list
#   - for an element

class DataGetterTestCase(TestCase):
    """
    Test data getters for elements and lists of data.
    """

    def setUp(self):
        self.category_id = 'en:plant-based-foods-and-beverages'
        self.product_id = '3222472887966'
        self.fake_data_path = os.path.join(
            os.path.dirname(__file__), 'fake_data')

    def test_get_data_for_category_list(self):
        """
        Test data getters for category list.
        :return:
        """
        data = get_categories_data_with_mock(self.fake_data_path, 'categories_short')
        self.assertIsInstance(data, list)

    def test_get_data_for_category_element(self):
        """
        Test data getters for category element.
        :return:
        """
        data = Category.get_api_data_element(self.category_id)
        self.assertIsNone(data)

    def test_get_data_for_product_list(self):
        """
        Test data getters for product list.
        :return:
        """

        data = get_products_data_with_mock(self.fake_data_path, 'products', nb_files=3, nb_pages=2)
        self.assertEqual(len(data), 40)

        data = get_products_data_with_mock(self.fake_data_path, 'products', nb_files=3)
        self.assertEqual(len(data), 60)

    def test_get_data_for_product_element(self):
        """
        Test data getters for product element.
        :return:
        """
        with open(os.path.join(self.fake_data_path, '3222472887966.json'), 'r') as file:
            fake_data_product = file.read()
        with requests_mock.Mocker() as mock:
            mock.get(Product.get_element_api_url(
                self.product_id), text=fake_data_product)
            data = Product.get_api_data_element(self.product_id)
            self.assertIsInstance(data, dict)


# write file
#   - for a list
#   - for an element


class DataWritterTestCase(TestCase):
    """
    Test data writter for elements and lists of data.
    """

    def setUp(self):
        self.fake_data_path = os.path.join(
            os.path.dirname(__file__), 'fake_data')
        self.product_id = '3222472887966'

    def tearDown(self):
        file_list = os.listdir(settings.JSON_DIR_PATH)
        for file in file_list:
            os.remove(os.path.join(settings.JSON_DIR_PATH, file))

    def test_write_file_for_category_list(self):
        """
        Test data writer for category list.
        :return:
        """
        # file_path = os.path.join(settings.JSON_DIR_PATH, "%s_list.json" % Category._meta.model_name)

        data = get_categories_data_with_mock(self.fake_data_path, 'categories_short')
        file = Category.write_api_data(data)
        self.assertTrue(os.path.exists(file))

    def test_write_file_for_product_list(self):
        """
        Test data writer for product list.
        :return:
        """
        # file_path = os.path.join(settings.JSON_DIR_PATH, "%s_list.json" % Product._meta.model_name)

        data = get_products_data_with_mock(self.fake_data_path, 'products', nb_files=3)
        file = Product.write_api_data(data)
        self.assertTrue(os.path.exists(file))

    def test_get_data_for_product_element(self):
        """
        Test data writer for product element.
        :return:
        """
        # file_path = os.path.join(settings.JSON_DIR_PATH, "%s.json" % Product._meta.model_name)

        with open(os.path.join(self.fake_data_path, '3222472887966.json'), 'r') as file:
            fake_data_product = file.read()
        with requests_mock.Mocker() as mock:
            mock.get(Product.get_element_api_url(
                self.product_id), text=fake_data_product)
            data = Product.get_api_data_element(self.product_id)
            file = Product.write_api_data(data)
            self.assertTrue(os.path.exists(file))


# create model instances
#   - from a list of elements
#   - from an element

class DataInsertTestCase(TestCase):
    """
    Test data insert.
    """

    def setUp(self):
        self.fake_data_path = os.path.join(
            os.path.dirname(__file__), 'fake_data')
        self.product_id = '3222472887966'

    def test_find_dict_key(self):
        """
        Test key finder.
        :return:
        """
        searched_key = "energy_100g"
        with open(os.path.join(self.fake_data_path, self.product_id + '.json')) as file:
            fake_data_product = json.loads(file.read())

        expected_result = fake_data_product['product']['nutriments'][searched_key]

        found_value = []
        for value in find_dict_value_for_nested_key(searched_key, fake_data_product):
            found_value.append(value)
        self.assertEqual(expected_result, found_value[0][1])

    def test_insert_category_list(self):
        """
        Test insert category list.
        :return:
        """
        nb_elements_before = Category.objects.count()

        data = get_categories_data_with_mock(self.fake_data_path, 'categories_short')

        Category.insert_data(data)
        nb_elements_after = Category.objects.count()
        self.assertGreater(nb_elements_after, nb_elements_before)

    def test_insert_product_list(self):
        """
        Test insert product list.
        :return:
        """
        data = get_categories_data_with_mock(self.fake_data_path, 'categories_short')

        Category.insert_data(data)

        nb_elements_before = Product.objects.count()

        data = get_products_data_with_mock(self.fake_data_path, 'products', nb_files=3)
        # test create
        Product.insert_data(data)
        nb_elements_after = Product.objects.count()
        self.assertGreater(nb_elements_after, nb_elements_before)

        # test update
        Product.insert_data(data)
        new_nb_elements_after = Product.objects.count()
        self.assertEqual(new_nb_elements_after, nb_elements_after)

    def test_insert_product_list_with_strict_mode(self):
        """
        Test insert products list with strict mode.
        :return:
        """
        data = get_categories_data_with_mock(self.fake_data_path, 'categories_short')

        Category.insert_data(data)

        nb_elements_before = Product.objects.count()

        data = get_products_data_with_mock(self.fake_data_path, 'products', nb_files=3)

        # test create
        Product.insert_data(data, strict_required_field_mode=True)
        nb_elements_after = Product.objects.count()
        self.assertGreater(nb_elements_after, nb_elements_before)

        # test update
        Product.insert_data(data)
        new_nb_elements_after = Product.objects.count()
        self.assertGreater(new_nb_elements_after, nb_elements_after)

    def test_insert_product_element(self):
        """
        Test insert products element.
        :return:
        """
        data = get_categories_data_with_mock(self.fake_data_path, 'categories_short')

        Category.insert_data(data)

        nb_elements_before = Product.objects.count()

        with open(os.path.join(self.fake_data_path, '3222472887966.json'), 'r') as file:
            fake_data_product = file.read()
        with requests_mock.Mocker() as mock:
            mock.get(Product.get_element_api_url(
                self.product_id), text=fake_data_product)
            data = Product.get_api_data_element(self.product_id)

        # test create
        Product.insert_data(data)
        nb_elements_after = Product.objects.count()
        self.assertGreater(nb_elements_after, nb_elements_before)

        # test update
        Product.insert_data(data)
        new_nb_elements_after = Product.objects.count()
        self.assertEqual(new_nb_elements_after, nb_elements_after)

    def test_short_cat(self):
        cat_ids = []

        with open(os.path.join(self.fake_data_path, 'products1.json'), 'r') as file:
            fake_data_products_1 = json.loads(file.read())
        with open(os.path.join(self.fake_data_path, 'products2.json'), 'r') as file:
            fake_data_products_2 = json.loads(file.read())
        with open(os.path.join(self.fake_data_path, 'products3.json'), 'r') as file:
            fake_data_products_3 = json.loads(file.read())

        for fd in [fake_data_products_1,fake_data_products_2, fake_data_products_3]:
            for prod in fd['products']:
                for cat in prod['categories_tags']:
                    cat_ids.append(cat)

        with open(os.path.join(self.fake_data_path, '3222472887966.json'), 'r') as file:
            fake_data_product = json.loads(file.read())

        for cat in fake_data_product['product']['categories_tags']:
            cat_ids.append(cat)

        cat_ids = set(cat_ids)

        with open(os.path.join(self.fake_data_path, 'categories.json'), 'r') as file:
            fake_data_categories = json.loads(file.read())

        new_cat_data = copy.copy(fake_data_categories)

        for cat in fake_data_categories['tags']:
            if cat['id'] not in cat_ids:
                new_cat_data['tags'].remove(cat)

        with open(os.path.join(self.fake_data_path, 'categories_short.json'), 'w') as file:
            file.write(json.dumps(new_cat_data))
        self.assertEqual(fake_data_categories.len(), new_cat_data.len())
        i = 0
        while i < fake_data_categories.len():
          self.assertEqual(fake_data_categories[i], new_cat_data[i + 1]) 
          i = i + 1
