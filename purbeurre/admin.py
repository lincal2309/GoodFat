# -*-coding:Utf-8 -*

from django.contrib import admin
from .models import Category, Product, UserProduct

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'used')
    list_filter = ('name', 'used')
    ordering = ('name', 'used')
    search_fields = ('name',)

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'category', 'nutrition_score', 'nutrition_grade')
    list_filter = ('category',)
    ordering = ('name', 'category', 'nutrition_score')
    search_fields = ('name',  'code')

class UserProductAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'substitute')
    list_filter = ('user',)

admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(UserProduct, UserProductAdmin)