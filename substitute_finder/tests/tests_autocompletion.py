"""
Auto completion tests.
"""
import os
import requests_mock
from django.test import TestCase

from substitute_finder.helpers import create_corpus, get_unigrams, get_ngrams
from substitute_finder.models import Category, Product


class AutoCompletionTestCase(TestCase):
    """
    Test auto completion helpers
    """

    # fixtures = ['./fixtures/test_data']

    def setUp(self):
        self.fake_data_path = os.path.join(
            os.path.dirname(__file__), 'fake_data')
        with open(os.path.join(self.fake_data_path, 'categories_short.json'), 'r') as file:
            fake_data_categories = file.read()
        with requests_mock.Mocker() as mock:
            mock.get(Category.get_list_api_url(), text=fake_data_categories)
            data = Category.get_api_data_list()

        Category.insert_data(data)

        with open(os.path.join(self.fake_data_path, 'products1.json'), 'r') as file:
            fake_data_products_1 = file.read()
        with open(os.path.join(self.fake_data_path, 'products2.json'), 'r') as file:
            fake_data_products_2 = file.read()
        with open(os.path.join(self.fake_data_path, 'products3.json'), 'r') as file:
            fake_data_products_3 = file.read()

        with requests_mock.Mocker() as mock:
            mock.get(Product.get_list_api_url(1), text=fake_data_products_1)
            mock.get(Product.get_list_api_url(2), text=fake_data_products_2)
            mock.get(Product.get_list_api_url(3), text=fake_data_products_3)
            data = Product.get_api_data_list()

        Product.insert_data(data)

    def test_create_corpus(self):
        """
        Test corpus creation.
        :return:
        """
        corpus = create_corpus()
        self.assertIsInstance(corpus, list)
        get_unigrams(corpus)
        get_ngrams(corpus, 3)
