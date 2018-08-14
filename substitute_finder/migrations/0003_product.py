# Generated by Django 2.1 on 2018-08-14 09:42

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('substitute_finder', '0002_category'),
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('code', models.CharField(max_length=300, primary_key=True, serialize=False, verbose_name='identifiant')),
                ('product_name', models.CharField(max_length=300, verbose_name='nom du produit')),
                ('generic_name', models.CharField(max_length=1000, verbose_name='description')),
                ('url', models.URLField(max_length=1000, verbose_name='url OpenFoodFacts')),
                ('stores', models.CharField(max_length=300, verbose_name='vendeur')),
                ('nutrition_grade_fr', models.CharField(max_length=1, verbose_name='score nutritionnel')),
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
