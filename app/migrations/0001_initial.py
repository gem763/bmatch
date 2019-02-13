# Generated by Django 2.1.5 on 2019-02-01 01:44

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
                ('category', models.CharField(max_length=120)),
                ('price', models.IntegerField(default=1)),
                ('origin', models.CharField(max_length=120)),
                ('logo_url', models.CharField(max_length=120)),
                ('description', models.TextField()),
            ],
        ),
    ]
