import logging
import os
from pprint import pprint

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count

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

    def handle(self, *args, **options):
        """
        Allow to get data from api or from cache and insert them into database.
        """

        # Count initial data
        LOGGER.info("Nb products before update: %s" % Product.objects.all().count())
        LOGGER.info("Nb categories before update: %s" % Category.objects.all().count())

        # Deal with Category
        data = Category.get_api_data_list(from_cache=options['from_cache'])
        Category.insert_data(data)

        # Deal with Product
        # Define initial variables
        data_exists = True
        start_page = 1
        if os.path.exists('last_page.txt'):
            with open('last_page.txt', 'r') as lp_file:
                start_page = int(lp_file.read())
        if options['start_page']:
            start_page = options['start_page']
        actual_page = start_page

        # Loop on data recovery and integration for Product
        while data_exists:
            data = Product.get_api_data_list(nb_pages=1, start_page=actual_page, from_cache=options['from_cache'])
            Product.insert_data(data)

            # Check if loop should continue according to page constraints
            data_exists = True if data else False
            if data_exists and options['nb_pages'] and actual_page >= start_page + options['nb_pages']:
                data_exists = False

            # Prepare next page number
            actual_page += 1

            # Save last recoverd page number
            with open('last_page.txt', 'w') as lp_file:
                lp_file.write(str(actual_page - 1))

        # Reset page counter save
        with open('last_page.txt', 'w') as lp_file:
            lp_file.write(str(1))

        # Remove useless Category and Product instances
        Product.objects.filter(nutrition_grade_fr='').delete()
        Category.objects.annotate(product_count=Count('product')).filter(product_count__lte=1).delete()
        Category.objects.filter(product__isnull=True).delete()
        Product.objects.filter(categories_tags=None).delete()

        # Count final data
        LOGGER.info("Nb products after update: %s" % Product.objects.all().count())
        LOGGER.info("Nb categories after update: %s" % Category.objects.all().count())
