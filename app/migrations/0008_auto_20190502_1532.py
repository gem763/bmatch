# Generated by Django 2.1.5 on 2019-05-02 15:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_auto_20190430_1602'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='awareness',
            field=models.TextField(blank=True, default='{}', null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='initial_awared',
            field=models.TextField(blank=True, null=True),
        ),
    ]
