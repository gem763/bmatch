# Generated by Django 2.1.5 on 2019-05-30 18:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0016_profile_myfavorite'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='level_tested',
            field=models.ManyToManyField(blank=True, related_name='leveltested_set', to='app.Brand'),
        ),
    ]