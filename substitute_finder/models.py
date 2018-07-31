from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class CustomUser(AbstractUser):
    email = models.EmailField('email address', unique=True)

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


class Product(models.Model):
    product_name = models.CharField(
        verbose_name='nom du produit', max_length=300)
    description = models.CharField(verbose_name='description', max_length=1000)
    open_food_facts_url = models.URLField(
        verbose_name='url OpenFoodFacts', max_length=1000)
    first_seller = models.CharField(verbose_name='vendeur', max_length=300)
    nutrition_grade = models.CharField(
        verbose_name='score nutritionnel', max_length=1)
    last_updated = models.DateTimeField(
        verbose_name='dernière mise à jour', auto_now=True)
    categories = models.ManyToManyField(to='Category', verbose_name='categories')
    users = models.ManyToManyField(to='CustomUser', related_name='favorite', verbose_name='utilisateurs')

    class Meta:
        verbose_name = 'Produit'
        verbose_name_plural = 'Produits'

    def __str__(self):
        return self.product_name


class Category(models.Model):
    category_name = models.CharField(verbose_name='catégorie', max_length=300)

    class Meta:
        verbose_name = 'Catégorie'
        verbose_name_plural = 'Catégories'
    

    def __str__(self):
        return self.category_name
