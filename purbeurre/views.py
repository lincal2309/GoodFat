# -*-coding:Utf-8 -*
# from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from django.shortcuts import render, redirect, get_list_or_404, get_object_or_404
from django.urls import reverse
from django.db.models import Count
from django.views.generic import ListView, DetailView, CreateView
from django.views.generic.base import TemplateView
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage

import requests
import logging

from .models import Category, Product, UserProduct
from .forms import UserForm, UserCreateForm

logger = logging.getLogger(__name__)

class ProductDetail(DetailView):
    model = Product
    template_name = 'purbeurre/product.html'


# View for home page
# Checks if data need to be loaded and display home page's template
def home(request):

    # Test if any category is used (if not, the database cannot be loaded : redirect to admin panel)
    if Category.objects.filter(used=True).count() == 0:
        return redirect('admin/')

    # Remove products that could be in base if Category is not used (anymore)
    cat_list = get_list_or_404(Category, used=True)
    Product.objects.exclude(category__in=cat_list).delete()

    # Nb products for each category
    prods_cat = Category.objects.annotate(nb_prods=Count('product'))

    # For each category, load products from API if none yet in the database
    for cat in prods_cat:
        if cat.used == True and cat.nb_prods == 0:

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

    return render(request, 'purbeurre/index.html')


# View to display substitutes
# From search field, gets the search product and look for substitutes to display them

def substitutes(request, code='', page=1):
    no_product = False
    if request.method == 'POST':
        # First access : search list based on input keywords
        search_prod = request.POST['product']
        # Look for a product matching exactly user's request
        search_list = list(Product.objects.filter(name__iexact=search_prod))
        if not search_list:
            # If no matching product found, look for approching name
            search_list = list(Product.objects.filter(name__icontains=search_prod))
            if not search_list:
                no_product = True
                return render(request, 'purbeurre/index.html', locals())
        # If at least 1 product found, take the first one
        # The product could have several categories but product codes are the same
        product = search_list[0]
    else:
        #  Pagination access : product code read from URL
        #  A list is used as products may have more than 1 categories
        #    The first one is used, product code and attributes are the same for each category
        product = get_list_or_404(Product, code=code)[0]
    # Gets the first product corresponding to search words
    # Could be enhanced in proposing a list of products before looking for substitutes
    init_substitute_list = get_list_or_404(Product.objects.order_by('nutrition_score'), \
        category=product.category, nutrition_score__lt=product.nutrition_score)

    # Number of products to be displayed in the header
    nb_products = len(init_substitute_list)
    # Boolean used in the template to display or not "save" button
    suggest = True
    # Pagination - 6 products per page
    paginator = Paginator(init_substitute_list, 6)
    substitute_list = paginator.get_page(page)

    return render(request, 'purbeurre/product_list.html', locals())

@login_required
def save_substitute(request, page=1):
    # Like for substitutes, product is the first item of a list as the product code could have several categories
    product = get_list_or_404(Product, code=request.POST["product"])[0]
    substitute = get_object_or_404(Product, code=request.POST["subst"], category=product.category)
    obj, created = UserProduct.objects.get_or_create(user=request.user, product=product, substitute=substitute)
    if created:
        obj.save()

    logger.info('Nouveau produit enregistré', exc_info=True, extra={
        'request': request,
    })
    
    return redirect('purbeurre:substitutes', code=product.code, page=page)


@login_required
def account(request):
    return render(request, 'purbeurre/account.html', locals())

@login_required
def my_substitutes(request, page=1):
    my_substitute_list = list(UserProduct.objects.filter(user=request.user))
    no_product = False
    if not my_substitute_list:
        no_product = True
    else:
        # From UserProduct list, extracts substitutes to be displayed
        # Allows to use the same template as proposed substitute list in "substitutes" view
        init_substitute_list = [subst.substitute for subst in my_substitute_list]
        # Pagination - 6 products per page
        nb_products = len(init_substitute_list)
        # Boolean used in the template to display or not "save" button
        suggest = False
        paginator = Paginator(init_substitute_list, 6)
        substitute_list = paginator.get_page(page)

    return render(request, 'purbeurre/my_substitutes.html', locals())

# Create user view

def create_user(request):
    error = False

    if request.method == "POST":
        form = UserCreateForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            first_name = form.cleaned_data["first_name"]
            if User.objects.filter(username=username):
                user_exists = True
            else:
                User.objects.create_user(username=username, email=email, 
                    password=password, first_name=first_name)
                user = authenticate(username=username, password=password)
                login(request, user)
                return redirect('/')
    else:
        form = UserCreateForm()

    return render(request, 'purbeurre/sign_up.html', locals())


def login_user(request):
    error = False

    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return redirect('/')
            else:
                error = True
    else:
        form = UserForm()

    # print("===============================================")
    # print(request.GET)
    # print("===============================================")
    # if not error:
    #     return redirect(request.GET["next"])
    # else:
    return render(request, 'purbeurre/login.html', locals())

def logout_user(request):
    logout(request)
    return redirect('/')
