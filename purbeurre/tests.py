# -*-coding:Utf-8 -*

from django.test import TestCase, Client
from django.contrib.auth import authenticate, login
from django.urls import reverse
from django.db.models import Count
from django.contrib.auth.models import User
from django.core.paginator import Page
from django.core.management import call_command

from unittest import mock

import requests

from .models import Category, Product, UserProduct


def create_user():
    user = User.objects.create_user('toto', first_name='Toto', email='toto@mail.com', password='toto')
    # user.save()
    return user

def init_database():
        c1 = Category.objects.create(name="Catégorie 1", used=True)
        c2 = Category.objects.create(name="Catégorie 2", used=True)
        # Products in c1
        Product.objects.create(code=1, name="Produit 1", description="Description du produit 1",
            ingredients="Ingrédients du produit 1", nutrition_score = 1, nutrition_grade="a",
            img_url="http://img.produit1.off.fr/1", off_url="http://code.produit1.off.fr/1",
            category=c1)
        Product.objects.create(code=2, name="Produit 2", description="Description du produit 2",
            ingredients="Ingrédients du produit 2", nutrition_score = 2, nutrition_grade="b",
            img_url="http://img.produit1.off.fr/2", off_url="http://code.produit1.off.fr/2",
            category=c1)
        Product.objects.create(code=3, name="Produit 3", description="Description du produit 3",
            ingredients="Ingrédients du produit 3", nutrition_score = 2, nutrition_grade="a",
            img_url="http://img.produit1.off.fr/1", off_url="http://code.produit1.off.fr/1",
            category=c1)
        Product.objects.create(code=4, name="Produit 4", description="Description du produit 4",
            ingredients="Ingrédients du produit 4", nutrition_score = 3, nutrition_grade="b",
            img_url="http://img.produit1.off.fr/2", off_url="http://code.produit1.off.fr/2",
            category=c1)
        Product.objects.create(code=5, name="Produit 5", description="Description du produit 5",
            ingredients="Ingrédients du produit 5", nutrition_score = 4, nutrition_grade="a",
            img_url="http://img.produit1.off.fr/1", off_url="http://code.produit1.off.fr/1",
            category=c1)
        Product.objects.create(code=6, name="Produit 6", description="Description du produit 6",
            ingredients="Ingrédients du produit 6", nutrition_score = 5, nutrition_grade="b",
            img_url="http://img.produit1.off.fr/2", off_url="http://code.produit1.off.fr/2",
            category=c1)
        # Products in c2
        Product.objects.create(code=7, name="Produit 7", description="Description du produit 7",
            ingredients="Ingrédients du produit 7", nutrition_score = 1, nutrition_grade="a",
            img_url="http://img.produit1.off.fr/1", off_url="http://code.produit1.off.fr/1",
            category=c2)
        Product.objects.create(code=4, name="Produit 8", description="Description du produit 8",
            ingredients="Ingrédients du produit 8", nutrition_score = 2, nutrition_grade="b",
            img_url="http://img.produit1.off.fr/2", off_url="http://code.produit1.off.fr/2",
            category=c2)
        # Products in c1 for multiple pages list
        Product.objects.create(code=10, name="Produit 10", description="Description du produit 10",
            ingredients="Ingrédients du produit 10", nutrition_score = 10, nutrition_grade="a",
            img_url="http://img.produit1.off.fr/1", off_url="http://code.produit1.off.fr/1",
            category=c1)
        Product.objects.create(code=20, name="Produit 20", description="Description du produit 20",
            ingredients="Ingrédients du produit 20", nutrition_score = 20, nutrition_grade="b",
            img_url="http://img.produit1.off.fr/2", off_url="http://code.produit1.off.fr/2",
            category=c1)
        Product.objects.create(code=30, name="Produit 30", description="Description du produit 30",
            ingredients="Ingrédients du produit 30", nutrition_score = 20, nutrition_grade="a",
            img_url="http://img.produit1.off.fr/1", off_url="http://code.produit1.off.fr/1",
            category=c1)
        Product.objects.create(code=40, name="Produit 40", description="Description du produit 40",
            ingredients="Ingrédients du produit 40", nutrition_score = 30, nutrition_grade="b",
            img_url="http://img.produit1.off.fr/2", off_url="http://code.produit1.off.fr/2",
            category=c1)


class TestHome(TestCase):
    def test_no_category_in_database(self):
        # Check redirection to admin panel if no 'used' category
        response = self.client.get(reverse('purbeurre:accueil'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('admin', response.url)

    @mock.patch('requests.get')
    def test_update_product_list_according_to_categories_status(self, mock_get_off):
        # Check product updates in database according to category status :
        #   - remove products if catogory turned 'unused' or deleted
        #   - add product from API if catogory turned 'used' or added

        mock_response = mock.Mock()

        # Expected data returned from API
        # Enhancements : add products for additional test cases and add related tests :
        #   - Product(s) with empty property (related to detailsd info)
        #   - Product with no 'nutrition-score-fr_100g'
        expected_result = {
            "page": "1",
            "skip": 0,
            "products": [
                {
                    "ingredients_text_fr": "Eau gazéifiée, sucre, colorant : E150d, acidifiant : acide phosphorique, arômes naturels (extraits végétaux), dont caféine.",
                    "ingredients_text_with_allergens_fr": "Eau gazéifiée, sucre, colorant : E150d, acidifiant : acide phosphorique, arômes naturels (extraits végétaux), dont caféine.",
                    "nova_group": "4",
                    "generic_name_fr": "Soda aux extraits végétaux",
                    "ingredients_text_with_allergens": "Eau gazéifiée, sucre, colorant : E150d, acidifiant : acide phosphorique, arômes naturels (extraits végétaux), dont caféine.",
                    "generic_name": "Soda aux extraits végétaux",
                    "image_url": "https://static.openfoodfacts.org/images/products/544/900/000/0996/front_fr.348.400.jpg",
                    "nutrition_grades": "e",
                    "nutrition_grade_fr": "e",
                    "nutriments": {
                        "fat_serving": "0",
                        "sugars_unit": "g",
                        "fat_unit": "g",
                        "fat_100g": "0",
                        "saturated-fat": "0",
                        "nutrition-score-fr_100g": "14",
                        "sugars_value": 10.6,
                        "nova-group": "4",
                        "sodium_unit": "g",
                        "saturated-fat_100g": "0",
                        "fat_value": "0",
                        "sugars": 10.6,
                        "fat": "0",
                        "sugars_serving": "35",
                        "saturated-fat_value": "0",
                        "saturated-fat_unit": "g",
                        "saturated-fat_serving": "0",
                        "sugars_100g": 10.6
                    },
                    "lang": "fr",
                    "product_name_en": "Coca Cola",
                    "product_name": "Produit A - Catégorie 3",
                    "brands": "Coca-Cola",
                    "categories": "Catégorie 3",
                    "categories_lc": "fr",
                    "code": "10",
                    "ingredients_text": "Eau gazéifiée, sucre, colorant : E150d, acidifiant : acide phosphorique, arômes naturels (extraits végétaux), dont caféine.",
                    "url": "https://fr.openfoodfacts.org/produit/5449000000996/coca-cola",
                    "nova_groups": "4",
                    "product_name_fr": "Coca-Cola",
                    "image_front_url": "https://static.openfoodfacts.org/images/products/544/900/000/0996/front_fr.348.400.jpg"
                },
                {
                    "ingredients_text_fr": "Eau gazéifiée, sucre, colorant : E150d, acidifiant : acide phosphorique, arômes naturels (extraits végétaux), dont caféine.",
                    "ingredients_text_with_allergens_fr": "Eau gazéifiée, sucre, colorant : E150d, acidifiant : acide phosphorique, arômes naturels (extraits végétaux), dont caféine.",
                    "nova_group": "4",
                    "generic_name_fr": "Soda aux extraits végétaux",
                    "ingredients_text_with_allergens": "Eau gazéifiée, sucre, colorant : E150d, acidifiant : acide phosphorique, arômes naturels (extraits végétaux), dont caféine.",
                    "generic_name": "Soda aux extraits végétaux",
                    "image_url": "https://static.openfoodfacts.org/images/products/544/900/000/0996/front_fr.348.400.jpg",
                    "nutrition_grades": "e",
                    "nutrition_grade_fr": "e",
                    "nutriments": {
                        "fat_serving": "0",
                        "sugars_unit": "g",
                        "fat_unit": "g",
                        "fat_100g": "0",
                        "saturated-fat": "0",
                        "nutrition-score-fr_100g": "14",
                        "sugars_value": 10.6,
                        "nova-group": "4",
                        "sodium_unit": "g",
                        "saturated-fat_100g": "0",
                        "fat_value": "0",
                        "sugars": 10.6,
                        "fat": "0",
                        "sugars_serving": "35",
                        "saturated-fat_value": "0",
                        "saturated-fat_unit": "g",
                        "saturated-fat_serving": "0",
                        "sugars_100g": 10.6
                    },
                    "lang": "fr",
                    "product_name_en": "Coca Cola",
                    "product_name": "Produit B - Catégorie 3",
                    "brands": "Coca-Cola",
                    "categories": "Catégorie 3",
                    "categories_lc": "fr",
                    "code": "20",
                    "ingredients_text": "Eau gazéifiée, sucre, colorant : E150d, acidifiant : acide phosphorique, arômes naturels (extraits végétaux), dont caféine.",
                    "url": "https://fr.openfoodfacts.org/produit/5449000000996/coca-cola",
                    "nova_groups": "4",
                    "product_name_fr": "Coca-Cola",
                    "image_front_url": "https://static.openfoodfacts.org/images/products/544/900/000/0996/front_fr.348.400.jpg"
                },
                {
                    "ingredients_text_fr": "Eau gazéifiée, sucre, colorant : E150d, acidifiant : acide phosphorique, arômes naturels (extraits végétaux), dont caféine.",
                    "ingredients_text_with_allergens_fr": "Eau gazéifiée, sucre, colorant : E150d, acidifiant : acide phosphorique, arômes naturels (extraits végétaux), dont caféine.",
                    "nova_group": "4",
                    "generic_name_fr": "Soda aux extraits végétaux",
                    "ingredients_text_with_allergens": "Eau gazéifiée, sucre, colorant : E150d, acidifiant : acide phosphorique, arômes naturels (extraits végétaux), dont caféine.",
                    "generic_name": "Soda aux extraits végétaux",
                    "image_url": "https://static.openfoodfacts.org/images/products/544/900/000/0996/front_fr.348.400.jpg",
                    "nutrition_grades": "e",
                    "nutrition_grade_fr": "e",
                    "nutriments": {
                        "fat_serving": "0",
                        "sugars_unit": "g",
                        "fat_unit": "g",
                        "fat_100g": "0",
                        "saturated-fat": "0",
                        "nutrition-score-fr_100g": "14",
                        "sugars_value": 10.6,
                        "nova-group": "4",
                        "sodium_unit": "g",
                        "saturated-fat_100g": "0",
                        "fat_value": "0",
                        "sugars": 10.6,
                        "fat": "0",
                        "sugars_serving": "35",
                        "saturated-fat_value": "0",
                        "saturated-fat_unit": "g",
                        "saturated-fat_serving": "0",
                        "sugars_100g": 10.6
                    },
                    "lang": "fr",
                    "product_name_en": "Coca Cola",
                    "product_name": "Produit B - Catégorie 4",
                    "brands": "Coca-Cola",
                    "categories": "Catégorie 4",
                    "categories_lc": "fr",
                    "code": "20",
                    "ingredients_text": "Eau gazéifiée, sucre, colorant : E150d, acidifiant : acide phosphorique, arômes naturels (extraits végétaux), dont caféine.",
                    "url": "https://fr.openfoodfacts.org/produit/5449000000996/coca-cola",
                    "nova_groups": "4",
                    "product_name_fr": "Coca-Cola",
                    "image_front_url": "https://static.openfoodfacts.org/images/products/544/900/000/0996/front_fr.348.400.jpg"
                }                
                ]
            }
        #  Response data from mock
        mock_response.json.return_value = expected_result
        mock_response.status_code = 200
        #  Response from fake API
        mock_get_off.return_value = mock_response

        # Load fake data into database to test first features of the view
        c1 = Category.objects.create(name="Catégorie 1", used=True)     # Used category with 1 product : no change expected
        c2 = Category.objects.create(name="Catégorie 2", used=False)    # Unused category with 1 product : product suppression expected
        Category.objects.create(name="Catégorie 3", used=True)     # Used category with no product : API request expected
        Product.objects.create(code=1, name="Produit 1", description="Description du produit 1",
            ingredients="Ingrédients du produit 1", nutrition_score = 1, nutrition_grade="a",
            img_url="http://img.produit1.off.fr/1", off_url="http://code.produit1.off.fr/1",
            category=c1)
        Product.objects.create(code=2, name="Produit 2", description="Description du produit 2",
            ingredients="Ingrédients du produit 2", nutrition_score = 2, nutrition_grade="b",
            img_url="http://img.produit1.off.fr/2", off_url="http://code.produit1.off.fr/2",
            category=c2)


        # Call the view
        response = self.client.get(reverse('purbeurre:accueil'))
        self.assertEqual(response.status_code, 200)
        
        # Test one product has been removed
        prod_cats = Category.objects.annotate(nb_prods=Count('product'))
        for cat in prod_cats:
            if cat.name == "Catégorie 1":
                # First category : no change (1 product expected)
                self.assertEqual(cat.nb_prods, 1)
                prod_list = Product.objects.filter(category=cat)
                self.assertEqual(len(prod_list), 1)
                self.assertEqual(prod_list[0].name, 'Produit 1')
            elif cat.name == "Catégorie 2":
                # Second category : product deleted (0 product expected)
                self.assertEqual(cat.nb_prods, 0)
            elif cat.name == "Catégorie 3":
                # Third category : products attached to newly added category
                self.assertEqual(cat.nb_prods, 2)


class TestSubstitutes(TestCase):
    def setUp(self):
        # Initialize test data
        init_database()

    def test_no_product_found(self):
        # Test view when no product found matching the user's request
        response = self.client.post(reverse('purbeurre:substitutes'), {'product': 'toto'})
        # print(response.context)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['no_product'], True)
        self.assertContains(response, 'Aucun produit de substitution')

        # self.assertIn('/', response.url)

    def test_substitutes_list_simple_search(self):
        # Look for a product having 1 category
        # 1 product matching criteria
        response = self.client.post(reverse('purbeurre:substitutes'), {'product': 'Produit 2'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['no_product'], False)
        self.assertQuerysetEqual(response.context['search_list'], ['<Product: Produit 2>'])
        self.assertEqual(response.context['nb_products'], 1)
        self.assertQuerysetEqual(response.context['init_substitute_list'], ['<Product: Produit 1>'])
        self.assertQuerysetEqual(response.context['substitute_list'].object_list, ['<Product: Produit 1>'])
        self.assertEqual(response.context['substitute_list'].number, 1)

    def test_substitutes_list_medium_search(self):
        # Look for a product having 1 category
        # Anothe product with the same nutrition_score supposed to be excluded
        # 1 product matching criteria
        response = self.client.post(reverse('purbeurre:substitutes'), {'product': 'Produit 3'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['no_product'], False)
        self.assertQuerysetEqual(response.context['search_list'], ['<Product: Produit 3>'])
        self.assertEqual(response.context['nb_products'], 1)
        self.assertQuerysetEqual(response.context['init_substitute_list'], ['<Product: Produit 1>'])
        self.assertQuerysetEqual(response.context['substitute_list'].object_list, ['<Product: Produit 1>'])
        self.assertEqual(response.context['substitute_list'].number, 1)
        
    def test_substitutes_list_complex_search(self):
        # Look for a product having 2 categories
        # 3 products matching criteria
        response = self.client.post(reverse('purbeurre:substitutes'), {'product': 'Produit 4'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['no_product'], False)
        self.assertQuerysetEqual(response.context['search_list'], ['<Product: Produit 4>'])
        self.assertEqual(response.context['nb_products'], 3)
        self.assertQuerysetEqual(response.context['init_substitute_list'],
            ['<Product: Produit 1>', '<Product: Produit 3>', '<Product: Produit 2>'])
        self.assertQuerysetEqual(response.context['substitute_list'].object_list,
            ['<Product: Produit 1>', '<Product: Produit 3>', '<Product: Produit 2>'])
        self.assertEqual(response.context['substitute_list'].number, 1)
        
    def test_substitutes_list_multiple_pages(self):
        # Substitute list includes more than 6 products
        # 3 products matching criteria
        response = self.client.post(reverse('purbeurre:substitutes'), {'product': 'Produit 40'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['no_product'], False)
        self.assertQuerysetEqual(response.context['search_list'], ['<Product: Produit 40>'])
        self.assertEqual(response.context['search_list'][0].code, '40')
        self.assertEqual(response.context['nb_products'], 9)
        self.assertQuerysetEqual(response.context['substitute_list'].object_list,
            ['<Product: Produit 1>', '<Product: Produit 2>', '<Product: Produit 3>',
            '<Product: Produit 4>', '<Product: Produit 5>', '<Product: Produit 6>'])
        self.assertEqual(response.context['substitute_list'].number, 1)

    def test_display_second_page(self):
        # Test GET method of 'substitutes' view
        response = self.client.get('/substitutes/40/2')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['product'].code, '40')
        self.assertEqual(response.context['nb_products'], 9)
        self.assertQuerysetEqual(response.context['substitute_list'].object_list,
            ['<Product: Produit 10>', '<Product: Produit 30>', '<Product: Produit 20>'])
        self.assertEqual(response.context['substitute_list'].number, 2)


class TestSaveSubstitutes(TestCase):
    def setUp(self):
        # Initialize test data
        init_database()

    def test_save_no_login_user(self):
        #  No user logged in : the view should redirect to login view
        response = self.client.post('/_subst/2', {'product': '40', 'subst': '30'})
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_save_login_user(self):
        # Create a user and log it in before calling the view
        user = create_user()
        self.client.force_login(user)
        response = self.client.post('/_subst/2', {'product': '40', 'subst': '30'})
        self.assertEqual(response.status_code, 302)
        user_prod = UserProduct.objects.filter(user=user)
        self.assertEqual(len(user_prod), 1)
        self.assertEqual(user_prod[0].product.code, '40')
        self.assertEqual(user_prod[0].substitute.code, '30')
        self.assertEqual(response.url, '/substitutes/40/2')
    

class TestAccount(TestCase):
    def test_account_no_login_user(self):
        #  No user logged in : the view should redirect to login view
        response = self.client.get(reverse('purbeurre:account'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_account_login_user(self):
        # Create a user and log it in before calling the view
        user = create_user()
        self.client.force_login(user)
        response = self.client.get(reverse('purbeurre:account'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['user'].email, user.email)


class TestMySubstitutes(TestCase):
    def setUp(self):
        # Initialize test data
        init_database()

    def test_my_subst_no_login_user(self):
        #  No user logged in : the view should redirect to login view
        response = self.client.get(reverse('purbeurre:my_substitutes'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_my_subst_no_product_saved(self):
        #  No product saved : the view should display a message
        user = create_user()
        self.client.force_login(user)
        response = self.client.get(reverse('purbeurre:my_substitutes'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['no_product'], True)
        self.assertContains(response, 'aucun produit')

    def test_my_subst_display_substitutes(self):
        #  Test standard usage
        user = create_user()
        self.client.force_login(user)
        product = Product.objects.get(code='40')
        substitute = Product.objects.get(code='30')
        UserProduct.objects.create(user=user, product=product, substitute=substitute)
        response = self.client.get(reverse('purbeurre:my_substitutes'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['no_product'], False)
        self.assertEqual(response.context['nb_products'], 1)
        self.assertQuerysetEqual(response.context['init_substitute_list'], ['<Product: Produit 30>'])
        self.assertQuerysetEqual(response.context['substitute_list'].object_list, ['<Product: Produit 30>'])
        self.assertEqual(response.context['substitute_list'].number, 1)


class TestCreateUser(TestCase):
    def test_create_user(self):
        response = self.client.post(reverse('purbeurre:sign_up'), 
            {'username': 'toto', 'first_name': 'titi', 'email': 'toto@mail.com', 'password': 'toto'})
        new_user = User.objects.get(username='toto')
        self.assertEqual(new_user.is_authenticated, True)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')

    def test_attempt_to_create_user_with_already_existing_username(self):
        create_user()
        response = self.client.post(reverse('purbeurre:sign_up'), 
            {'username': 'toto', 'first_name': 'titi', 'email': 'toto@mail.com', 'password': 'toto'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['user_exists'], True)
        self.assertContains(response, "Nom d'utilisateur existant")

class TestLoginUser(TestCase):
    def test_login(self):
        create_user()
        response = self.client.post(reverse('purbeurre:login'), 
            {'username': 'toto', 'password': 'toto'})
        logged_user = User.objects.get(username='toto')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(logged_user.is_authenticated, True)

    def test_login_unknown_user(self):
        response = self.client.post(reverse('purbeurre:login'), 
            {'username': 'toto', 'password': 'toto'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['error'], True)
        self.assertContains(response, "Utilisateur inconnu")
 
    def test_already_logged_in(self):
        user = create_user()
        self.client.force_login(user)
        response = self.client.get(reverse('purbeurre:login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Vous êtes connecté")
        self.assertContains(response, user.username)

class TestLoadCats(TestCase):
    # Test loadcats.py command
    def test_add_category(self):
        # Add 1 category
        call_command('loadcats', 'Categorie test')
        cat = Category.objects.get(name='Categorie test')
        self.assertEqual(cat.used, True)

    def test_add_categories(self):
        # Add 2 categories
        call_command('loadcats', 'Categorie test 1', 'Categorie test 2')
        cat = Category.objects.get(name='Categorie test 1')
        self.assertEqual(cat.used, True)
        cat = Category.objects.get(name='Categorie test 2')
        self.assertEqual(cat.used, True)

    def test_unused_categories(self):
        call_command('loadcats', 'Categorie test', '--unused')
        cat = Category.objects.get(name='Categorie test')
        self.assertEqual(cat.used, False)

    def test_switch_all_existing_categories_to_used(self):
        Category.objects.create(name="Catégorie 1", used=True)
        Category.objects.create(name="Catégorie 2", used=False)

        call_command('loadcats', '--all')
        cats = Category.objects.filter()
        self.assertEqual(len(cats), 2)
        for cat in cats:
            self.assertEqual(cat.used, True)

    def test_switch_all_existing_categories_to_unused(self):
        Category.objects.create(name="Catégorie 1", used=True)
        Category.objects.create(name="Catégorie 2", used=False)

        call_command('loadcats', '--all', '--unused')
        cats = Category.objects.filter()
        self.assertEqual(len(cats), 2)
        for cat in cats:
            self.assertEqual(cat.used, False)

    def test_switch_all_categories_to_used(self):
        Category.objects.create(name="Catégorie 1", used=True)
        Category.objects.create(name="Catégorie 2", used=False)

        call_command('loadcats', 'Catégorie 3', '--all')
        cats = Category.objects.filter()
        self.assertEqual(len(cats), 3)
        for cat in cats:
            self.assertEqual(cat.used, True)

    def test_switch_all_categories_to_unused(self):
        Category.objects.create(name="Catégorie 1", used=True)
        Category.objects.create(name="Catégorie 2", used=False)

        call_command('loadcats', 'Catégorie 3', 'Catégorie 4', '--all', '--unused')
        cats = Category.objects.filter()
        self.assertEqual(len(cats), 4)
        for cat in cats:
            self.assertEqual(cat.used, False)


class TestLegals(TestCase):
    def test_legals(self):
        # Test template "legal information"
        response = self.client.get(reverse('purbeurre:legals'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Mentions légales")


class TestRefreshProds(TestCase):
    @mock.patch('requests.get')
    def test_refresh_product(self, mock_get_off):
        # Check product list refresh :
        #   - remove products if catogory turned 'used'
        #   - add products from API 

        mock_response = mock.Mock()

        # Expected data returned from API
        expected_result = {
            "page": "1",
            "skip": 0,
            "products": [
                {
                    "ingredients_text_fr": "Eau gazéifiée, sucre, colorant : E150d, acidifiant : acide phosphorique, arômes naturels (extraits végétaux), dont caféine.",
                    "ingredients_text_with_allergens_fr": "Eau gazéifiée, sucre, colorant : E150d, acidifiant : acide phosphorique, arômes naturels (extraits végétaux), dont caféine.",
                    "nova_group": "4",
                    "generic_name_fr": "Soda aux extraits végétaux",
                    "ingredients_text_with_allergens": "Eau gazéifiée, sucre, colorant : E150d, acidifiant : acide phosphorique, arômes naturels (extraits végétaux), dont caféine.",
                    "generic_name": "Soda aux extraits végétaux",
                    "image_url": "https://static.openfoodfacts.org/images/products/544/900/000/0996/front_fr.348.400.jpg",
                    "nutrition_grades": "e",
                    "nutrition_grade_fr": "e",
                    "nutriments": {
                        "fat_serving": "0",
                        "sugars_unit": "g",
                        "fat_unit": "g",
                        "fat_100g": "0",
                        "saturated-fat": "0",
                        "nutrition-score-fr_100g": "14",
                        "sugars_value": 10.6,
                        "nova-group": "4",
                        "sodium_unit": "g",
                        "saturated-fat_100g": "0",
                        "fat_value": "0",
                        "sugars": 10.6,
                        "fat": "0",
                        "sugars_serving": "35",
                        "saturated-fat_value": "0",
                        "saturated-fat_unit": "g",
                        "saturated-fat_serving": "0",
                        "sugars_100g": 10.6
                    },
                    "lang": "fr",
                    "product_name_en": "Coca Cola",
                    "product_name": "Produit A - Catégorie 1",
                    "brands": "Coca-Cola",
                    "categories": "Catégorie 1",
                    "categories_lc": "fr",
                    "code": "10",
                    "ingredients_text": "Eau gazéifiée, sucre, colorant : E150d, acidifiant : acide phosphorique, arômes naturels (extraits végétaux), dont caféine.",
                    "url": "https://fr.openfoodfacts.org/produit/5449000000996/coca-cola",
                    "nova_groups": "4",
                    "product_name_fr": "Coca-Cola",
                    "image_front_url": "https://static.openfoodfacts.org/images/products/544/900/000/0996/front_fr.348.400.jpg"
                },
                {
                    "ingredients_text_fr": "Eau gazéifiée, sucre, colorant : E150d, acidifiant : acide phosphorique, arômes naturels (extraits végétaux), dont caféine.",
                    "ingredients_text_with_allergens_fr": "Eau gazéifiée, sucre, colorant : E150d, acidifiant : acide phosphorique, arômes naturels (extraits végétaux), dont caféine.",
                    "nova_group": "4",
                    "generic_name_fr": "Soda aux extraits végétaux",
                    "ingredients_text_with_allergens": "Eau gazéifiée, sucre, colorant : E150d, acidifiant : acide phosphorique, arômes naturels (extraits végétaux), dont caféine.",
                    "generic_name": "Soda aux extraits végétaux",
                    "image_url": "https://static.openfoodfacts.org/images/products/544/900/000/0996/front_fr.348.400.jpg",
                    "nutrition_grades": "e",
                    "nutrition_grade_fr": "e",
                    "nutriments": {
                        "fat_serving": "0",
                        "sugars_unit": "g",
                        "fat_unit": "g",
                        "fat_100g": "0",
                        "saturated-fat": "0",
                        "nutrition-score-fr_100g": "14",
                        "sugars_value": 10.6,
                        "nova-group": "4",
                        "sodium_unit": "g",
                        "saturated-fat_100g": "0",
                        "fat_value": "0",
                        "sugars": 10.6,
                        "fat": "0",
                        "sugars_serving": "35",
                        "saturated-fat_value": "0",
                        "saturated-fat_unit": "g",
                        "saturated-fat_serving": "0",
                        "sugars_100g": 10.6
                    },
                    "lang": "fr",
                    "product_name_en": "Coca Cola",
                    "product_name": "Produit B - Catégorie 1",
                    "brands": "Coca-Cola",
                    "categories": "Catégorie 1",
                    "categories_lc": "fr",
                    "code": "20",
                    "ingredients_text": "Eau gazéifiée, sucre, colorant : E150d, acidifiant : acide phosphorique, arômes naturels (extraits végétaux), dont caféine.",
                    "url": "https://fr.openfoodfacts.org/produit/5449000000996/coca-cola",
                    "nova_groups": "4",
                    "product_name_fr": "Coca-Cola",
                    "image_front_url": "https://static.openfoodfacts.org/images/products/544/900/000/0996/front_fr.348.400.jpg"
                },
                {
                    "ingredients_text_fr": "Eau gazéifiée, sucre, colorant : E150d, acidifiant : acide phosphorique, arômes naturels (extraits végétaux), dont caféine.",
                    "ingredients_text_with_allergens_fr": "Eau gazéifiée, sucre, colorant : E150d, acidifiant : acide phosphorique, arômes naturels (extraits végétaux), dont caféine.",
                    "nova_group": "4",
                    "generic_name_fr": "Soda aux extraits végétaux",
                    "ingredients_text_with_allergens": "Eau gazéifiée, sucre, colorant : E150d, acidifiant : acide phosphorique, arômes naturels (extraits végétaux), dont caféine.",
                    "generic_name": "Soda aux extraits végétaux",
                    "image_url": "https://static.openfoodfacts.org/images/products/544/900/000/0996/front_fr.348.400.jpg",
                    "nutrition_grades": "e",
                    "nutrition_grade_fr": "e",
                    "nutriments": {
                        "fat_serving": "0",
                        "sugars_unit": "g",
                        "fat_unit": "g",
                        "fat_100g": "0",
                        "saturated-fat": "0",
                        "nutrition-score-fr_100g": "14",
                        "sugars_value": 10.6,
                        "nova-group": "4",
                        "sodium_unit": "g",
                        "saturated-fat_100g": "0",
                        "fat_value": "0",
                        "sugars": 10.6,
                        "fat": "0",
                        "sugars_serving": "35",
                        "saturated-fat_value": "0",
                        "saturated-fat_unit": "g",
                        "saturated-fat_serving": "0",
                        "sugars_100g": 10.6
                    },
                    "lang": "fr",
                    "product_name_en": "Coca Cola",
                    "product_name": "Produit B - Catégorie 2",
                    "brands": "Coca-Cola",
                    "categories": "Catégorie 2",
                    "categories_lc": "fr",
                    "code": "20",
                    "ingredients_text": "Eau gazéifiée, sucre, colorant : E150d, acidifiant : acide phosphorique, arômes naturels (extraits végétaux), dont caféine.",
                    "url": "https://fr.openfoodfacts.org/produit/5449000000996/coca-cola",
                    "nova_groups": "4",
                    "product_name_fr": "Coca-Cola",
                    "image_front_url": "https://static.openfoodfacts.org/images/products/544/900/000/0996/front_fr.348.400.jpg"
                }                
                ]
            }
        #  Response data from mock
        mock_response.json.return_value = expected_result
        mock_response.status_code = 200
        #  Response from fake API
        mock_get_off.return_value = mock_response

        # Load fake data into database to test first features of the view
        c1 = Category.objects.create(name="Catégorie 1", used=True)     # Used category with 1 product : 2 products expected
        c2 = Category.objects.create(name="Catégorie 2", used=False)    # Unused category with 1 product : no changes expected

        Product.objects.create(code=1, name="Produit 1", description="Description du produit 1",
            ingredients="Ingrédients du produit 1", nutrition_score = 1, nutrition_grade="a",
            img_url="http://img.produit1.off.fr/1", off_url="http://code.produit1.off.fr/1",
            category=c1)
        Product.objects.create(code=2, name="Produit 2", description="Description du produit 2",
            ingredients="Ingrédients du produit 2", nutrition_score = 2, nutrition_grade="b",
            img_url="http://img.produit1.off.fr/2", off_url="http://code.produit1.off.fr/2",
            category=c2)


        # Call the command
        call_command('refresh_prods')
        
        # Test one product has been removed
        prod_cats = Category.objects.annotate(nb_prods=Count('product'))
        for cat in prod_cats:
            if cat.name == "Catégorie 1":
                # First category : 2 products expected
                self.assertEqual(cat.nb_prods, 2)
                prod_list = Product.objects.filter(category=cat)
                self.assertEqual(len(prod_list), 2)
            elif cat.name == "Catégorie 2":
                # Second category : no change (1 product expected)
                self.assertEqual(cat.nb_prods, 1)
