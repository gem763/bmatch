from django.db import models
from django.conf import settings

# Create your models here.

class Brand(models.Model):
    name = models.CharField(max_length=120)
    #category = models.CharField(max_length=120)
    #price = models.IntegerField(default=1)
    #origin = models.CharField(max_length=120)
    #logo = models.ImageField(blank=True)
    #logo_url = models.CharField(max_length=120)
    #description = models.TextField()
    logo = models.ImageField(blank=True)
    identity = models.TextField(blank=True, null=True)
    cluster = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.name
