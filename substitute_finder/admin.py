"""
substitute_finder admin
"""

from django.contrib import admin

from substitute_finder.models import Comment
from .models import Category, CustomUser, Product


# Register your models here.


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    """
    CustomUser admin config.
    """
    pass


class CustomUserInline(admin.TabularInline):
    """
    CustomUser for products inline admin config.
    """
    model = Product.users.through
    verbose_name = 'Utilistateur'
    verbose_name_plural = 'Utilisateurs'


class CategoryInline(admin.TabularInline):
    """
    Category for products inline admin config.
    """
    model = Product.categories_tags.through
    verbose_name = 'Catégorie'
    verbose_name_plural = 'Catégories'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Product admin config.
    """
    search_fields = ['code', 'product_name', 'generic_name']
    list_filter = ['nutrition_grade_fr', 'categories_tags']
    inlines = [CustomUserInline, CategoryInline]
    exclude = ('users', 'categories_tags')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Category admin config.
    """
    search_fields = ['name', ]


@admin.register(Product.users.through)
class FavoriteAdmin(admin.ModelAdmin):
    """
    Favorite admin config.
    """
    list_display = ['product', 'customuser']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    Comment admin config
    """
    list_display = ['user', 'product']
    search_fields = ['user__username', 'product__product_name']
