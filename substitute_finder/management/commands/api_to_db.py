import logging
import os
from pprint import pprint

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count, Q

from substitute_finder.models import Category, Product

LOGGER = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Get initial Categories and Products data from OpenFoodFacts API and load them into database'

    def add_arguments(self, parser):

        # Named (optional) arguments

        parser.add_argument(
            '--start_page',
            action='store',
            dest='start_page',
            type=int,
            help='indicate from which page to start data load'
        )

        parser.add_argument(
            '--nb_pages',
            action='store',
            dest='nb_pages',
            type=int,
            help='indicate how many pages to load'
        )

        parser.add_argument(
            '--from_cache',
            action='store_true',
            dest='from_cache',
            help='will try to get data from cache if it exists instead of requesting api'
        )

        parser.add_argument(
            '--grumpy_mode',
            action='store_true',
            dest='grumpy_mode',
            help='enable a strict mode that delete elements with missing data'
        )

    def get_categories(self, from_cache: bool=False):
        """
        method in charge of getting categories.
        :param from_cache: indicates if data should be recovered from cache or not
        :type from_cache: bool
        """

        data = Category.get_api_data_list(from_cache=from_cache)
        Category.insert_data(data)

    def get_product(self, actual_page: int=1, from_cache: bool=False, grumpy_mode: bool=False):
        """
        """
        data = Product.get_api_data_list(nb_pages=1, start_page=actual_page, from_cache=from_cache)
        Product.insert_data(data, strict_required_field_mode=grumpy_mode)
        return bool(data)

    def database_cleanup(self, grumpy_mode: bool=False):
        """
        Clean database Product and Category tables after data recovery
        :param grumpy_mode: indicates if database should be cleaned with a strict control on important Product fields
        :type grumpy_mode: bool
        """

        if grumpy_mode:
            Product.objects.filter(Q(generic_name=None) | Q(energy_100g=None) | Q(sugars_100g=None) | Q(sodium_100g=None) |
                                   Q(carbohydrates_100g=None) | Q(salt_100g=None) | Q(proteins_100g=None) |
                                   Q(fat_100g=None) | Q(fiber_100g=None) | Q(saturated_fat_100g=None) |
                                   Q(nutrition_grade_fr=None) | Q(generic_name='') | Q(energy_100g='') | Q(sugars_100g='') |
                                   Q(sodium_100g='') | Q(carbohydrates_100g='') | Q(salt_100g='') |
                                   Q(proteins_100g='') | Q(fat_100g='') | Q(fiber_100g='') |
                                   Q(saturated_fat_100g='') | Q(nutrition_grade_fr='')).delete()

        Product.objects.filter(nutrition_grade_fr='').delete()
        Category.objects.annotate(product_count=Count('product')).filter(product_count__lte=1).delete()
        Category.objects.filter(product__isnull=True).delete()
        Product.objects.filter(categories_tags=None).delete()

    def get_recovery_state(self):
        """
        get recovery state from state file.
        """
        state = 1
        if os.path.exists('last_page.txt'):
            with open('last_page.txt', 'r') as lp_file:
                state = int(lp_file.read())
        return state

    def set_recovery_state(self, page: int=1):
        """
        Store recovery state in file.
        :param page: actual page
        :type page: int
        """
        with open('last_page.txt', 'w') as lp_file:
            lp_file.write(str(page))

    def handle(self, *args, **options):
        """
        Allow to get data from api or from cache and insert them into database.
        """

        # Count initial data
        LOGGER.info("Nb products before update: %s" % Product.objects.all().count())
        LOGGER.info("Nb categories before update: %s" % Category.objects.all().count())

        # Deal with Category
        self.get_categories(from_cache=options['from_cache'])

        # Deal with Product
        # Define initial variables
        data_exists = True
        start_page = self.get_recovery_state()

        if options['start_page']:
            start_page = options['start_page']
        actual_page = start_page

        # Loop on data recovery and integration for Product
        while data_exists:
            data_exists = self.get_product(actual_page=actual_page,
                                           from_cache=options['from_cache'], grumpy_mode=options['grumpy_mode'])

            # Check if loop should continue according to page constraints
            if data_exists and options['nb_pages'] and actual_page >= start_page + options['nb_pages']:
                data_exists = False

            # Prepare next page number
            actual_page += 1

            # Save last recoverd page number
            self.set_recovery_state(page=actual_page - 1)

        # Reset page counter save
        self.set_recovery_state()

        # Remove useless Category and Product instances
        self.database_cleanup(grumpy_mode=options['grumpy_mode'])

        # Count final data
        LOGGER.info("Nb products after update: %s" % Product.objects.all().count())
        LOGGER.info("Nb categories after update: %s" % Category.objects.all().count())
