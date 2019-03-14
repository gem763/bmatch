from django.db import models
from django.conf import settings

# Create your models here.

class Brand(models.Model):
    name = models.CharField(max_length=120)
    fullname_kr = models.CharField(max_length=120, blank=True, null=True)
    fullname_en = models.CharField(max_length=120, blank=True, null=True)
    keywords = models.TextField(default='')
    website = models.CharField(max_length=200, blank=True, null=True)
    origin = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(default='', blank=True, null=True)
    history = models.TextField(default='', blank=True, null=True)
    logo = models.ImageField(default='') # 로고는 필수 (null=True 하면 안됨)
    identity = models.TextField(default='{}', blank=True, null=True)
    cluster = models.CharField(max_length=50, blank=True, null=True)
    # wordfreq = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
