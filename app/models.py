from django.db import models
from django.conf import settings
import json

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

    def __str__(self):
        return self.name

    def get_id(self):
        return {i['key']:i['value'] for i in json.loads(self.identity)}


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    worldcup = models.TextField(blank=True, null=True, default='{}')
    likes = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.email

    def get_likes(self):
        return [] if self.likes is None else [w.strip() for w in self.likes.split(',')]


    def _weighting(self, like=1, morelike=1):
        weights = {}
        for pair,selected in json.loads(self.worldcup).items():
            for b in pair.split('-'):
                add = 1
                if b==selected: add += like
                if b in self.get_likes(): add += morelike

                weights[b] = weights[b] + add if b in weights else add
        return weights

    def identify(self, like=2, morelike=3):
        score = {}
        brands = Brand.objects
        weights = self._weighting(like=like, morelike=morelike)

        for bname, w in weights.items():
            for k,v in brands.get(name=bname).get_id().items():
                score[k] = score[k] + v*w if k in score else v*w

        score_sum = sum(score.values())
        return {k:v/score_sum for k,v in score.items()}
