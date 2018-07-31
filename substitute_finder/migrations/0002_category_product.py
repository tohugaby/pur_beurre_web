# Generated by Django 2.0.7 on 2018-07-31 18:39

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('substitute_finder', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category_name', models.CharField(max_length=300, verbose_name='catégorie')),
            ],
            options={
                'verbose_name': 'Catégorie',
                'verbose_name_plural': 'Catégories',
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_name', models.CharField(max_length=300, verbose_name='nom du produit')),
                ('description', models.CharField(max_length=1000, verbose_name='description')),
                ('open_food_facts_url', models.URLField(max_length=1000, verbose_name='url OpenFoodFacts')),
                ('first_seller', models.CharField(max_length=300, verbose_name='vendeur')),
                ('nutrition_grade', models.CharField(max_length=1, verbose_name='score nutritionnel')),
                ('last_updated', models.DateTimeField(auto_now=True, verbose_name='dernière mise à jour')),
                ('categories', models.ManyToManyField(to='substitute_finder.Category', verbose_name='categories')),
                ('users', models.ManyToManyField(related_name='favorite', to=settings.AUTH_USER_MODEL, verbose_name='utilisateurs')),
            ],
            options={
                'verbose_name': 'Produit',
                'verbose_name_plural': 'Produits',
            },
        ),
    ]