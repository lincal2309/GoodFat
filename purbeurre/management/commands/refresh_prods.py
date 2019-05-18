from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.shortcuts import get_list_or_404, get_object_or_404

import requests
import logging

from purbeurre.models import Category, Product

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    """
        Command to refresh product list
        For each 'used' category, il will refresh product_list from OFF database.

        The command will be launched once a week (cron task)
    """


    help = 'Refresh product list for Pur Beurre app'

    def add_arguments(self, parser):
        # Sets arguments and options
        #   - categories : liste of categories to be adde, optional
        #   - --unused : to set added catgories to 'unused'
        #   - --all : to update all existing and/or added catgories
        #       (--unused option is taken into account) 
        parser.add_argument('categories', nargs='*', type=str)

    def handle(self, *args, **options):
        cat_list = get_list_or_404(Category, used=True)

        # Delete all products
        Product.objects.filter(category__in=cat_list).delete()

        # For each category, load products from API
        for cat in cat_list:

            search_base_url = "https://fr.openfoodfacts.org/cgi/search.pl"
            querystring = {"action":"process", \
            "tagtype_0":"categories","tag_contains_0":"contains","tag_0":"boisson", \
            "tagtype_1":"countries","tag_contains_1":"contains","tag_1":"france", \
            "page_size":"100","json":"1"}

            product_list = []
                
            querystring["tag_0"] = cat.name
            req = requests.get(search_base_url, params=querystring)

            for product_attributes in req.json()["products"]:
                if "nutrition-score-fr_100g" in product_attributes["nutriments"]:
                    doublon = False
                    product_code = product_attributes["code"]
                    product_name = product_attributes["product_name"]

                    # Looking for the product already in the list
                    is_new = True
                    for new_prod in product_list:
                        if product_code == new_prod[0]:
                            is_new = False
                        elif product_name == new_prod[1]:
                            # Products having exactly the same name are excluded => need dedicate management rules to be integrated
                            doublon = True

                    if not doublon:
                        if is_new:
                            # For each attribute, test if it exists
                            ingredients = ""
                            sugars = calcium = fat = None
                            sugars_unit = calcium_unit = fat_unit = "N/A"
                            if "ingredients_text_fr" in product_attributes:
                                ingredients=product_attributes["ingredients_text_fr"]
                            if "sugars" in product_attributes["nutriments"]:
                                sugars = product_attributes["nutriments"]["sugars"]
                                sugars_unit = product_attributes["nutriments"]["sugars_unit"]
                            if "calcium" in product_attributes["nutriments"]:
                                calcium = product_attributes["nutriments"]["calcium"]
                                calcium_unit = product_attributes["nutriments"]["calcium_unit"]
                            if "fat_value" in product_attributes["nutriments"]:
                                fat = product_attributes["nutriments"]["fat_value"]
                                fat_unit = product_attributes["nutriments"]["fat_unit"]

                            # Add values in database
                            new_product = Product(code=product_code, name=product_name, \
                                        description=product_attributes["ingredients_text_with_allergens"], \
                                        ingredients=ingredients, \
                                        nutrition_score=int(product_attributes["nutriments"]["nutrition-score-fr_100g"]), \
                                        nutrition_grade=product_attributes["nutrition_grade_fr"], \
                                        off_url=product_attributes["url"], img_url=product_attributes["image_url"], \
                                        sugars=sugars, sugars_unit=sugars_unit, \
                                        calcium=calcium, calcium_unit=calcium_unit, \
                                        fat=fat, fat_unit=fat_unit, \
                                        category=cat)
                            product_list.append((new_product.code, new_product.name, new_product.description))
                            
                            new_product.save()

        logger.info('Produits mis à jour', exc_info=True)
