# Generated by Django 2.1.7 on 2019-03-10 09:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0010_auto_20190310_1822'),
    ]

    operations = [
        migrations.AlterField(
            model_name='brand',
            name='identity',
            field=models.TextField(default='{}'),
        ),
    ]