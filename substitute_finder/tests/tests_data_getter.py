import json
import os
from pprint import pprint
from django.test import TestCase
# from django.conf import settings

import requests
import requests_mock

#from substitute_finder.helpers import DataGetter, JSONDataToModelInstance
from substitute_finder.models import Product, Category


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
        self.FAKE_DATA_PATH = os.path.join(os.path.dirname(__file__),'fake_data')
        

    def test_get_data_for_category_list(self):
        with open(os.path.join(self.FAKE_DATA_PATH,'categories.json'),'r') as file:
            fake_data_categories = file.read()
        with requests_mock.Mocker() as m:
            m.get(Category.get_list_api_url(),text=fake_data_categories)    
            data =  Category.get_api_data_list()
            self.assertIsInstance(data,list)

    def test_get_data_for_category_element(self):
        data =  Category.get_api_data_element(self.category_id)
        self.assertIsNone(data)

    def test_get_data_for_product_list(self):
        with open(os.path.join(self.FAKE_DATA_PATH,'products1.json'),'r') as file:
            fake_data_products_1 = file.read()
        with open(os.path.join(self.FAKE_DATA_PATH,'products2.json'),'r') as file:
            fake_data_products_2 = file.read()
        with open(os.path.join(self.FAKE_DATA_PATH,'products3.json'),'r') as file:
            fake_data_products_3 = file.read()

        with requests_mock.Mocker() as m:
            m.get(Product.get_list_api_url(1),text=fake_data_products_1)
            m.get(Product.get_list_api_url(2),text=fake_data_products_2)
            m.get(Product.get_list_api_url(3),text=fake_data_products_3)
            data = Product.get_api_data_list(nb_pages=2)
            self.assertEqual(len(data),40)
            data = Product.get_api_data_list()
            self.assertEqual(len(data),60)

    def test_get_data_for_product_element(self):
        with open(os.path.join(self.FAKE_DATA_PATH,'3222472887966.json'),'r') as file:
            fake_data_product = file.read()
        with requests_mock.Mocker() as m:
            m.get(Product.get_element_api_url(self.product_id),text=fake_data_product)
            data = Product.get_api_data_element(self.product_id)
            self.assertIsInstance(data, dict)



# write file
#   - for a list
#   - for an element

# create model instances
#   - from a list of elements
#   - from an element


# first data recovery


# class FirstDataRecoveryTestCase(TestCase):

#     def setUp(self):
#         self.fake_data = json.dumps([
#             {
#                 "id": "3222472887966",
#                 "categories_hierarchy": ["en:plant-based-foods-and-beverages", "en:beverages", "en:plant-based-foods", "en:legumes-and-their-products", "en:plant-based-beverages", "en:milk-substitute", "en:plant-milks", "en:legume-milks", "en:soy-milks"],
#                 "image_front_url": "https://static.openfoodfacts.org/images/products/322/247/288/7966/front_fr.9.400.jpg",
#                 "generic_name_fr": "Boisson v\u00e9g\u00e9tale au soja issue de l'agriculture biologique st\u00e9rilis\u00e9e UHT",
#                 "product_name": "Boisson au Soja Nature",
#                 "nutrition_grades_tags": ["a"],
#                 "link": "http://www.casinodrive.fr/ecommerce/affichageDetailProduit/WE80205/F-47220-yaourts/P-52343--",
#                 "code": "3222472887966",
#                 "product_name_fr": "Boisson au Soja Nature",
#             },
#         ])

#     def test_first_data_recovery(self):
#         max_page = 1
#         with requests_mock.Mocker() as m:

#             new_getter = DataGetter(
#                 **settings.DATA_GETTER_PARAMETERS['products'])
#             new_getter.page_getter_limit = max_page
#             for page in range(max_page+1):
#                 m.get(new_getter.get_paginated_url(
#                     page), text=self.fake_data)
#                 json_data = json.dumps(new_getter.get_data(
#                     new_getter.get_paginated_url(page)))

#                 self.assertEqual(json_data, self.fake_data)
# data update


# class DataUpdate(TestCase):

#     def setUp(self):

#         self.id = 3222472887966
#         self.url = "https://fr.openfoodfacts.org/api/v0/produit/" + \
#             str(self.id)+".json"
#         self.fake_data = json.dumps({
#             "id": "3222472887966",
#             "categories_hierarchy": ["en:plant-based-foods-and-beverages", "en:beverages", "en:plant-based-foods", "en:legumes-and-their-products", "en:plant-based-beverages", "en:milk-substitute", "en:plant-milks", "en:legume-milks", "en:soy-milks"],
#             "image_front_url": "https://static.openfoodfacts.org/images/products/322/247/288/7966/front_fr.9.400.jpg",
#             "generic_name_fr": "Boisson v\u00e9g\u00e9tale au soja issue de l'agriculture biologique st\u00e9rilis\u00e9e UHT",
#             "product_name": "Boisson au Soja Nature",
#             "nutrition_grades_tags": ["a"],
#             "link": "http://www.casinodrive.fr/ecommerce/affichageDetailProduit/WE80205/F-47220-yaourts/P-52343--",
#             "code": "3222472887966",
#             "product_name_fr": "Boisson au Soja Nature",
#         })

#     def test_data_update(self):
#         with requests_mock.Mocker() as m:
#             new_getter = DataGetter(
#                 **settings.DATA_GETTER_PARAMETERS['product'], id=self.id)
#             m.get(self.url, text=self.fake_data)
#             json_data = json.dumps(new_getter.get_data(
#                 new_getter.get_paginated_url(1)))
#             new_getter.write_file()
#             self.assertEqual(json_data, self.fake_data)
        # new_getter = DataGetter(
        #         **settings.DATA_GETTER_PARAMETERS['product'], id=self.id)
        # print(new_getter.json_data_key)
        # data = new_getter.get_data(new_getter.get_paginated_url(1))
        # pprint(data.keys())
        # new_getter.write_file()


# class DataInsert(TestCase):
#     def setUp(self):
#         pass

#     def test_data_insert(self):

#         self.categories_path = settings.JSON_FILES_PATH['category']

#         # if not os.path.exists(self.categories_path):
#         new_getter = DataGetter(**settings.DATA_GETTER_PARAMETERS['category'])
#         # print(new_getter.get_paginated_url(1))
#         self.assertEqual(self.categories_path, new_getter.file_path)

#         data = new_getter.get_data(new_getter.get_paginated_url(1))
#         for el in data['tags']:
#             unused_keys = []
#             for key in el.keys():
#                 if key not in ('id', 'name', 'url'):
#                     unused_keys.append(key)

#             for unused_key in unused_keys:
#                 del el[unused_key]
#         for i in data['tags']:
#             print(i)
#             Category.objects.create(**i)
        # pprint(data)

        # with open(self.categories_path,'r') as file:
        #     data = json.loads(file)
        #     print(data)

        #json_to_model = JSONDataToModelInstance(self.categories_path,)
