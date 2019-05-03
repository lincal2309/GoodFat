# -*-coding:Utf-8 -*

from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=150)
    used = models.BooleanField(verbose_name = "Sélectionnée")

    class Meta:
        verbose_name = "Catégorie"

    def __str__(self):
        return self.name

class Product(models.Model):
    code = models.CharField(max_length=50)
    name = models.CharField(max_length=150)
    description = models.TextField()
    ingredients = models.TextField(null=True)
    nutrition_score = models.IntegerField()
    nutrition_grade = models.CharField(max_length=1)
    img_url = models.URLField(max_length=200, null=True)
    off_url = models.URLField(max_length=200)
    sugars = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    sugars_unit = models.CharField(max_length=5, null=True)
    calcium = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    calcium_unit = models.CharField(max_length=5, null=True)
    fat = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    fat_unit = models.CharField(max_length=5, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Produit"

    def __str__(self):
        return self.name

class UserProduct(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    substitute = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="substitute")


    class Meta:
        verbose_name = "Utilisateur"
        constraints = [models.UniqueConstraint(fields=['user', 'product', 'substitute'], name='substitut_unique')]

    def __str__(self):
        return self.user.username
