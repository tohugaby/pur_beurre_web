"""
api_to_db command tests.
"""
import json
import os
from django.conf import settings
from django.core.management import call_command
from django.test import TestCase, override_settings
from io import StringIO

from substitute_finder.models import Category, Product, Comment, CustomUser

TEST_JSON_CACHE_DATA_PATH = os.path.join(os.path.dirname(__file__), settings.JSON_DIR_NAME)


class TestDataJSONCleaner:
    """
    An helper class to get test data and make them smaller.
    """

    def __init__(self, files_path, max_nb_pages=3):
        self.max_nb_pages = max_nb_pages
        self.files_path = files_path

    @staticmethod
    def get_category_json_test_file():
        """
        Recover category json test file from OpenfoodFacts
        """
        Category.get_api_data_list(from_cache=False)

    def get_product_json_test_files(self):
        """
        Recover category json test file from OpenfoodFacts
        """
        Product.get_api_data_list(nb_pages=self.max_nb_pages, start_page=1, from_cache=False)

    def clean_json_files(self):
        """
        Clean category file by removing useless categories. Allows faster tests.
        """
        try:
            to_keep_categories = []

            # Open product files to list categories to keep
            for page_number in range(1, self.max_nb_pages + 1):
                file_path = os.path.join(self.files_path, 'product_list_%s.json' % str(page_number))
                with open(file_path, 'r') as product_file:
                    data = json.loads(product_file.read())
                    for product in data:
                        if 'categories_tags' in product.keys():
                            for category in product['categories_tags']:
                                to_keep_categories.append(category)
            to_keep_categories = set(to_keep_categories)

            # Read actual category list and clean it.
            categories = []
            with open(os.path.join(self.files_path, 'category_list.json'), 'r') as category_file:
                categories = json.loads(category_file.read())
            new_categories = list(filter(lambda cat: cat['id'] in to_keep_categories, categories))
            with open(os.path.join(self.files_path, 'category_list.json'), 'w') as new_category_file:
                new_category_file.write(json.dumps(new_categories))

        # recover test file if missing or if empty
        except (FileNotFoundError, json.decoder.JSONDecodeError):

            self.get_category_json_test_file()
            self.get_product_json_test_files()
            self.clean_json_files()

        except (KeyError, Exception) as other_exc:
            raise other_exc


@override_settings(JSON_DIR_PATH=TEST_JSON_CACHE_DATA_PATH)
class ApiToDbTestCase(TestCase):
    """
    Test api_to_db command.
    """
    fixtures = ['test_data_custom_user.json', ]

    def test_api_to_db_with_nb_pages(self):
        """
        Test api_to_db command with number of pages.
        :return:
        """
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
        """
        Test api_to_db command with grumpy (strict) mode.
        :return:
        """
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

    def test_api_to_db_with_hard_reset(self):
        """
        Test api_to_db command with grumpy (strict) mode.
        :return:
        """
        before_nb_prod = Product.objects.count()
        self.assertEqual(before_nb_prod, 0)

        out = StringIO()
        options = {
            'start_page': 1,
            'nb_pages': 1,
            'from_cache': True,
            'grumpy_mode': True,
            'hard_reset': True
        }
        call_command('api_to_db', stdout=out, **options)
        nb_prod = Product.objects.count()
        self.assertNotEqual(nb_prod, 0)

        cat = Category.objects.first()
        first_prod = Product.objects.first()
        first_prod.categories_tags.add(cat)
        last_prod = Product.objects.last()
        last_prod.categories_tags.add(cat)

        user = CustomUser.objects.first()
        last_prod.users.add(user)
        last_prod.save()
        Comment.objects.create(product=first_prod, user=user, comment_text="texte du commentaire")

        options = {
            'start_page': 1,
            'nb_pages': 0,
            'from_cache': True,
            'grumpy_mode': True,
            'hard_reset': True
        }
        call_command('api_to_db', stdout=out, **options)
        nb_prod = Product.objects.count()
        self.assertEqual(nb_prod, 2)
