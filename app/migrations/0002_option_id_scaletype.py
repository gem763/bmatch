# Generated by Django 2.1.7 on 2019-04-10 16:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='option',
            name='id_scaletype',
            field=models.IntegerField(default='0'),
        ),
    ]
