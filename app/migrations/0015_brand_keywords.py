# Generated by Django 2.1.5 on 2019-03-13 08:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0014_brand_history'),
    ]

    operations = [
        migrations.AddField(
            model_name='brand',
            name='keywords',
            field=models.TextField(default=''),
        ),
    ]
