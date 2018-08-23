import os

import requests
import requests_mock
from django.test import TestCase

from substitute_finder.helpers import create_corpus,get_unigrams,get_ngrams
from substitute_finder.models import Category, Product


class AutoCompletionTestCase(TestCase):

    # fixtures = ['./fixtures/test_data']

    def setUp(self):
        self.FAKE_DATA_PATH = os.path.join(
            os.path.dirname(__file__), 'fake_data')
        with open(os.path.join(self.FAKE_DATA_PATH, 'categories_short.json'), 'r') as file:
            fake_data_categories = file.read()
        with requests_mock.Mocker() as m:
            m.get(Category.get_list_api_url(), text=fake_data_categories)
            data = Category.get_api_data_list()

        Category.insert_data(data)

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

    def test_create_corpus(self):
        corpus = create_corpus()
        self.assertIsInstance(corpus, list)
        get_unigrams(corpus)
        get_ngrams(corpus, 3)
        

