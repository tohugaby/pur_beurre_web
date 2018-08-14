from django.contrib import admin
from .models import CustomUser, Category , Product
# Register your models here.


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    pass


class CustomUserInline(admin.TabularInline):
    model = Product.users.through
    verbose_name = 'Utilistateur'
    verbose_name_plural = 'Utilisateurs'


class CategoryInline(admin.TabularInline):
    model = Product.categories.through
    verbose_name = 'Catégorie'
    verbose_name_plural = 'Catégories'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    search_fields = ['product_name','generic_name']
    list_filter = ['nutrition_grade_fr','stores','categories']
    inlines = [CustomUserInline, CategoryInline]
    exclude = ('users', 'categories')



@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ['name',]


@admin.register(Product.users.through)
class FavoriteAdmin(admin.ModelAdmin):
    pass