from django.contrib import admin

from .models import Category, CustomUser, Product

# Register your models here.


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    pass


class CustomUserInline(admin.TabularInline):
    model = Product.users.through
    verbose_name = 'Utilistateur'
    verbose_name_plural = 'Utilisateurs'


class CategoryInline(admin.TabularInline):
    model = Product.categories_tags.through
    verbose_name = 'Catégorie'
    verbose_name_plural = 'Catégories'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    search_fields = ['code', 'product_name', 'generic_name']
    list_filter = ['nutrition_grade_fr', 'categories_tags']
    inlines = [CustomUserInline, CategoryInline]
    exclude = ('users', 'categories_tags')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ['name', ]


@admin.register(Product.users.through)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['product','customuser']
