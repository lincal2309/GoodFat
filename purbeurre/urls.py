# -*-coding:Utf-8 -*

"""purbeurre URL Configuration"""

from django.contrib import admin
from django.urls import path
from django.views.generic import ListView, DetailView, TemplateView

from . import views
from .models import Product

app_name = "purbeurre"
urlpatterns = [
    path('', views.home, name='accueil'),
    path('substitutes/', views.substitutes, name='substitutes'),
    path('substitutes/<str:code>/<int:page>', views.substitutes, name='substitutes'),
    path('substitute/<int:pk>', views.ProductDetail.as_view(), name='substitute'),
    path('_subst/<int:page>', views.save_substitute, name='save_substitute'),
    path('my_substitutes/', views.my_substitutes, name='my_substitutes'),
    path('my_substitutes/<int:page>', views.my_substitutes, name='my_substitutes'),
    path('account/', views.account, name='account'),
    path('sign_up/', views.create_user, name='sign_up'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('legals/', TemplateView.as_view(template_name='purbeurre/legals.html'), name='legals')
]
