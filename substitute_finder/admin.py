from django.contrib import admin
from .models import CustomUser, Product, Category
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
    search_fields = ['product_name','description']
    list_filter = ['nutrition_grade','first_seller','categories']
    inlines = [CustomUserInline, CategoryInline]
    exclude = ('users', 'categories')



@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ['category_name',]


@admin.register(Product.users.through)
class FavoriteAdmin(admin.ModelAdmin):
    pass