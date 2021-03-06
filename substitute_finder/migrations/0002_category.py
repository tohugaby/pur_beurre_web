# Generated by Django 2.1 on 2018-08-14 09:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('substitute_finder', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.CharField(max_length=300, primary_key=True, serialize=False, verbose_name='identifiant')),
                ('name', models.CharField(max_length=300, verbose_name='nom')),
                ('url', models.URLField(max_length=300, verbose_name='url')),
            ],
            options={
                'verbose_name': 'Catégorie',
                'verbose_name_plural': 'Catégories',
            },
        ),
    ]
