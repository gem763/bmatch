# Generated by Django 2.1.5 on 2019-02-13 08:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_brand_logo'),
    ]

    operations = [
        migrations.AddField(
            model_name='brand',
            name='identity',
            field=models.TextField(blank=True, null=True),
        ),
    ]