from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from purbeurre.models import Category


class Command(BaseCommand):
    """
        Command to initialize categories in Pur Beurre application.
        The command will parse category names and either update 'used'
            attribute of them or create them if they do not exist

        Syntax :
        python manage.py loadcats [cat1, cat2, ...] [--unused] [--all]

        Parameters :
            [cat1, cat2, ...] : One or more categories (strings). Use quotes
                                    if a category name has more than one word
                                By default, all new categories will be set to 'used'
                                    Use '--unused' option to set them to 'unused'
                                Optional if --all option is used

            [--unused] :    Use this option to turn all categories to be added
                                to "unused".
                            If omitted, 'used' attribute will be set to 'True'

            [--all] :   Updates all existing categories.
                        By default, 'used' attribute will be set to 'True'.
                        If [--unused] option is added, 'used' attribute will
                            be set to 'False'
    """


    help = 'Loads categories to init PurBeurre app'

    def add_arguments(self, parser):
        # Sets arguments and options
        #   - categories : liste of categories to be adde, optional
        #   - --unused : to set added catgories to 'unused'
        #   - --all : to update all existing and/or added catgories
        #       (--unused option is taken into account) 
        parser.add_argument('categories', nargs='*', type=str)
        parser.add_argument('--unused', action='store_true',
            help='Add unused category')
        parser.add_argument('--all', action='store_true',
            help='Update all categories')

    def handle(self, *args, **options):
        used = True
        if options['unused']:
            used = False
        if options['all']:
            Category.objects.filter().update(used=used)
            self.stdout.write("Toutes les catégories ont été mise à jour")
        
        for category in options['categories']:
            nb = Category.objects.filter(name=category).update(used=used)
            if nb == 0:
                new_cat = Category(name=category, used=used)
                new_cat.save()
                self.stdout.write("Catégorie '%s' créée" % new_cat)
            else:
                self.stdout.write("Catégorie '%s' mise à jour" % category)

