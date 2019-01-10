"""
helpers for tests
"""
import copy
import json
import os
import requests_mock
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.support import ui

from substitute_finder.models import Product, Category


def get_products_data_with_mock(fake_data_path: str, file_name: str, nb_files=1, nb_pages=None):
    """
    Get products data with mock.
    :param fake_data_path:
    :param file_name:
    :param nb_files:
    :param nb_pages:
    :return:
    """
    file_name_list = ["%s%s.json" % (file_name, file_num) for file_num in range(1, nb_files + 1)]
    fake_data_products = []
    for filename in file_name_list:
        with open(os.path.join(fake_data_path, filename), 'r') as file:
            fake_data_products.append(file.read())

    with requests_mock.Mocker() as mock:
        for index, fake_data in enumerate(fake_data_products):
            mock.get(Product.get_list_api_url(index + 1), text=fake_data)
        if not nb_pages:
            data = Product.get_api_data_list()
        else:
            data = Product.get_api_data_list(nb_pages=nb_pages)

    return data


def get_categories_data_with_mock(fake_data_path: str, file_name: str):
    """
    Get categories data with mock.
    :param fake_data_path:
    :param file_name:
    :return:
    """
    with open(os.path.join(fake_data_path, '%s.json' % file_name), 'r') as file:
        fake_data_categories = file.read()
    with requests_mock.Mocker() as mock:
        mock.get(Category.get_list_api_url(), text=fake_data_categories)
        data = Category.get_api_data_list()

    return data


class CustomStaticLiveServerTestCase(StaticLiveServerTestCase):
    """
    Custom generic live TestCase class
    """

    @classmethod
    def setUpClass(cls):
        super(CustomStaticLiveServerTestCase, cls).setUpClass()
        cls.browser = webdriver.Firefox()
        cls.wait = ui.WebDriverWait(cls.browser, 1000)
        cls.check_live_server()

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super(CustomStaticLiveServerTestCase, cls).tearDownClass()

    @classmethod
    def get_element(cls, css_selector: str):
        """
        A shortcut to get an html element by css selector.
        :param css_selector: searched css selector
        :type css_selector: str
        """
        return cls.browser.find_element_by_css_selector(css_selector)

    @classmethod
    def check_live_server(cls):
        """
        Check if server is ok.
        """
        cls.browser.get(cls.live_server_url)
        assert "Pur Beurre" in cls.browser.title


def clean_categories_test_file():
    """
    function to rewrite categories_short.json according to products files. to make it smaller for tests
    :return:
    """
    fake_data_path = os.path.join(os.path.dirname(__file__), 'fake_data')

    from_product_list_cat_ids = []

    fake_data_products = get_products_data_with_mock(fake_data_path, 'products', nb_files=3)

    for prod in fake_data_products:
        for cat in prod['categories_tags']:
            from_product_list_cat_ids.append(cat)

    with open(os.path.join(fake_data_path, '3222472887966.json'), 'r') as file:
        fake_data_product = json.loads(file.read())

    for cat in fake_data_product['product']['categories_tags']:
        from_product_list_cat_ids.append(cat)

    fake_data_categories = get_categories_data_with_mock(fake_data_path, 'categories_short')

    from_categories_list_cat_ids = [cat['id'] for cat in fake_data_categories]

    if not set(sorted(from_product_list_cat_ids)) == set(sorted(from_categories_list_cat_ids)):

        new_cat_data = {'tags':copy.deepcopy(fake_data_categories)}

        for cat in fake_data_categories:
            if cat['id'] not in from_product_list_cat_ids:
                new_cat_data['tags'].remove(cat)

        with open(os.path.join(fake_data_path, 'categories_short.json'), 'w') as file:
            file.write(json.dumps(new_cat_data))
