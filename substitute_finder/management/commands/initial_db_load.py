import logging
import os
from pprint import pprint

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count

from substitute_finder.models import Category, Product

LOGGER = logging.getLogger(__name__)


# TODO: add args to specify start page or resume mode . Need to store last page in file
# TODO: add a from cache option (from data stored locally)

class Command(BaseCommand):
    help = 'Get initial Categories and Products data from OpenFoodFacts API and load them into database'

    def handle(self, *args, **options):
        LOGGER.info("Nb products before update: %s" % Product.objects.all().count())
        LOGGER.info("Nb categories before update: %s" % Category.objects.all().count())
        data = Category.get_api_data_list(from_cache=True)
        Category.insert_data(data)
        data_exists = True

        start_page = 1
        if os.path.exists('last_page.txt'):
            with open('last_page.txt', 'r') as lp_file:
                start_page = int(lp_file.read())

        while data_exists:
            data = Product.get_api_data_list(nb_pages=1, start_page=start_page, from_cache=True)
            Product.insert_data(data)
            data_exists = True if data else False
            start_page += 1
            with open('last_page.txt', 'w') as lp_file:
                lp_file.write(str(start_page - 1))
        with open('last_page.txt', 'w') as lp_file:
            lp_file.write(str(1))
        Category.objects.annotate(product_count=Count('product')).filter(product_count__lte=1).delete()
        Category.objects.filter(product__isnull=True).delete()
        Product.objects.filter(categories_tags=None).delete()
        LOGGER.info("Nb products after update: %s" % Product.objects.all().count())
        LOGGER.info("Nb categories after update: %s" % Category.objects.all().count())
