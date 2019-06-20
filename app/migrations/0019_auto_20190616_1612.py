# Generated by Django 2.1.7 on 2019-06-16 16:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0018_post_hashtags'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='likes',
        ),
        migrations.AddField(
            model_name='profile',
            name='brand_bookmarks',
            field=models.ManyToManyField(blank=True, related_name='brand_bookmarks_set', to='app.Brand'),
        ),
        migrations.AddField(
            model_name='profile',
            name='post_bookmarks',
            field=models.ManyToManyField(blank=True, related_name='post_bookmarks_set', to='app.Post'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='brand_likes',
            field=models.ManyToManyField(blank=True, related_name='brand_likes_set', to='app.Brand'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='post_likes',
            field=models.ManyToManyField(blank=True, related_name='post_likes_set', to='app.Post'),
        ),
    ]