"""
helpers for tests
"""
import os
import requests_mock

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
