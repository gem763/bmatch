# Generated by Django 2.1.5 on 2019-03-15 05:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0016_auto_20190314_2355'),
    ]

    operations = [
        migrations.AddField(
            model_name='brand',
            name='score',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
