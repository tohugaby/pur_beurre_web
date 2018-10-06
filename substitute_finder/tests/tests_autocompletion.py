"""
Auto completion tests.
"""
import os
from django.test import TestCase

from substitute_finder.helpers import create_corpus, get_unigrams, get_ngrams
from substitute_finder.models import Category, Product
from substitute_finder.tests.test_helpers import get_categories_data_with_mock, get_products_data_with_mock


class AutoCompletionTestCase(TestCase):
    """
    Test auto completion helpers
    """

    # fixtures = ['./fixtures/test_data']

    def setUp(self):
        self.fake_data_path = os.path.join(
            os.path.dirname(__file__), 'fake_data')
        data = get_categories_data_with_mock(self.fake_data_path, 'categories_short')

        Category.insert_data(data)

        data = get_products_data_with_mock(self.fake_data_path, 'products', nb_files=3)

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
