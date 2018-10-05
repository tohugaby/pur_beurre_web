import json
import os
from django.conf import settings
from django.core.management import call_command
from django.test import TestCase, override_settings
from io import StringIO

from substitute_finder.models import Category, Product

TEST_JSON_CACHE_DATA_PATH = os.path.join(os.path.dirname(__file__), settings.JSON_DIR_NAME)


@override_settings(JSON_DIR_PATH=TEST_JSON_CACHE_DATA_PATH)
class ApiToDbTestCase(TestCase):
    MAX_NB_PAGES = 3

    def setUp(self):
        self.clean_json_files()

    def get_category_json_test_file(self):
        """
        Recover category json test file from OpenfoodFacts
        """
        Category.get_api_data_list(from_cache=False)

    def get_product_json_test_files(self):
        """
        Recover category json test file from OpenfoodFacts
        """
        Product.get_api_data_list(nb_pages=self.MAX_NB_PAGES, start_page=1, from_cache=False)

    def clean_json_files(self):
        """
        Clean category file by removing useless categories. Allows faster tests.
        """
        try:
            to_keep_categories = []

            # Open product files to list categories to keep
            for nb in range(1, self.MAX_NB_PAGES + 1):
                file_path = os.path.join(TEST_JSON_CACHE_DATA_PATH, 'product_list_%s.json' % str(nb))
                with open(file_path, 'r') as product_file:
                    data = json.loads(product_file.read())
                    for product in data:
                        if 'categories_tags' in product.keys():
                            for category in product['categories_tags']:
                                to_keep_categories.append(category)
            to_keep_categories = set(to_keep_categories)

            # Read actual category list and clean it.
            categories = []
            with open(os.path.join(TEST_JSON_CACHE_DATA_PATH, 'category_list.json'), 'r') as category_file:
                categories = json.loads(category_file.read())
            new_categories = list(filter(lambda cat: cat['id'] in to_keep_categories, categories))
            with open(os.path.join(TEST_JSON_CACHE_DATA_PATH, 'category_list.json'), 'w') as new_category_file:
                new_category_file.write(json.dumps(new_categories))

        # recover test file if missing or if empty
        except (FileNotFoundError, json.decoder.JSONDecodeError) as file_or_json_exc:

            self.get_category_json_test_file()
            self.get_product_json_test_files()
            self.clean_json_files()

        except (KeyError, Exception) as other_exc:
            raise other_exc

    def test_api_to_db_with_nb_pages(self):
        self.assertEqual(Category.objects.count(), 0)
        self.assertEqual(Product.objects.count(), 0)
        out = StringIO()
        options = {
            'start_page': 1,
            'nb_pages': 2,
            'from_cache': True,
            'grumpy_mode': False
        }
        call_command('api_to_db', stdout=out, **options)
        self.assertNotEqual(Category.objects.count(), 0)
        self.assertNotEqual(Product.objects.count(), 0)

    def test_api_to_db_with_grumpy_mode(self):
        before_nb_cat = Category.objects.count()
        before_nb_prod = Product.objects.count()
        self.assertEqual(before_nb_cat, 0)
        self.assertEqual(before_nb_prod, 0)

        out = StringIO()
        options = {
            'start_page': 1,
            'nb_pages': 2,
            'from_cache': True,
            'grumpy_mode': False
        }
        call_command('api_to_db', stdout=out, **options)
        no_grumpy_mode_nb_cat = Category.objects.count()
        no_grumpy_mode_nb_prod = Product.objects.count()
        self.assertNotEqual(no_grumpy_mode_nb_cat, 0)
        self.assertNotEqual(no_grumpy_mode_nb_prod, 0)

        options['grumpy_mode'] = True

        call_command('api_to_db', stdout=out, **options)
        grumpy_mode_nb_cat = Category.objects.count()
        grumpy_mode_nb_prod = Product.objects.count()
        self.assertNotEqual(grumpy_mode_nb_cat, 0)
        self.assertNotEqual(grumpy_mode_nb_prod, 0)

        self.assertTrue(no_grumpy_mode_nb_cat >= grumpy_mode_nb_cat >= before_nb_cat)
        self.assertTrue(no_grumpy_mode_nb_prod >= grumpy_mode_nb_prod >= before_nb_prod)
