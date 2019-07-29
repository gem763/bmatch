from django.db import models
from django.conf import settings
from django.urls import reverse_lazy
# from django.core.urlresolvers import reverse_lazy
import json
import requests
import numpy as np
from collections import OrderedDict
from custom_user.models import AbstractEmailUser

# Create your models here.


class Option(models.Model):
    idwords_default = [
        {"럭셔리": "럭셔리 고급 호화 과시 명품 luxury 비싼 고가 expensive pricy pricey",
         "캐주얼": "캐주얼 캐쥬얼 casual 스타일리시 스타일리쉬 stylish"},
        {"유니크": "유니크 독특 독창 unique 개성 only 참신 신선 특이 아이디어 철학",
         "대중성": "대중 popular 널리 흔한 massive mass 대중성"},
        {"정통성": "정통 클래식 classic 품격 약속 신뢰 믿음 예측 견고 품질 안정",
         "트렌디": "트렌디 트랜디 트렌드 트랜드 유행 trend trendy 변화 새로운 민감 예민 신상 최신"},
        {"포멀": "포멀 formal 노멀 normal 평범 일상 무난 기본 베이스 베이직 base basic",
         "액티브": "화제 인기 hot 튀는 액티브 active 앞서가는 실험 과감 선도 선구 대담"}
    ]

    optname = models.CharField(max_length=120, default='init')
    idwords = models.TextField(default=json.dumps(idwords_default, ensure_ascii=False))
    api = models.CharField(max_length=120, default='http://127.0.0.1:8080/api')
    id_scaletype = models.IntegerField(default='0')

    def __str__(self):
        return self.optname


class BigIdAbstract(models.Model):
    id = models.BigAutoField(primary_key=True)

    class Meta:
        abstract = True


class CustomEmailUser(AbstractEmailUser, BigIdAbstract):
    pass


class Hashtag(BigIdAbstract):
    hashtag = models.CharField(max_length=120)
    def __str__(self):
        return self.hashtag


class Page(models.Model):
    name = models.CharField(max_length=120)
    created_at = models.DateTimeField(auto_now_add=True)
    nlikes = models.IntegerField(default='0')

    class Meta:
        abstract = True


class Brand(Page):#models.Model):
    fullname_kr = models.CharField(max_length=120, blank=True, null=True)
    fullname_en = models.CharField(max_length=120, blank=True, null=True)
    keywords = models.TextField(default='')
    website = models.CharField(max_length=200, blank=True, null=True)
    origin = models.CharField(max_length=50, blank=True, null=True)
    awareness = models.FloatField(default=0)
    category = models.CharField(max_length=120, blank=True, null=True)
    description = models.TextField(default='', blank=True, null=True)
    history = models.TextField(default='', blank=True, null=True)
    logo = models.ImageField(upload_to='brand_logos', default='') # 로고는 필수 (null=True 하면 안됨)

    def __str__(self):
        return self.fullname_en.capitalize()


class Post(BigIdAbstract):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='posts/%Y/%m/%d/origin')
    content = models.TextField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    brands_related = models.ManyToManyField(Brand, blank=True)

    def __str__(self):
        return '{created_at} {email}'.format(created_at=self.created_at, email=self.user.email)

    def get_absolute_url(self):
        url = reverse_lazy('post_detail', kwargs={'pk':self.pk})
        return url


class Profile(BigIdAbstract):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    profile_image = models.ImageField(default='', max_length=500)

    worldcup = models.TextField(blank=True, null=True, default='{}')
    initial_awared = models.TextField(blank=True, null=True)
    # awareness = models.TextField(blank=True, null=True, default='{}')

    brand_likes = models.ManyToManyField(Brand, blank=True, related_name='brand_likes_set')
    post_likes = models.ManyToManyField(Post, blank=True, related_name='post_likes_set')
    brand_bookmarks = models.ManyToManyField(Brand, blank=True, related_name='brand_bookmarks_set')
    post_bookmarks = models.ManyToManyField(Post, blank=True, related_name='post_bookmarks_set')

    myfavorite = models.ForeignKey(Brand, blank=True, null=True, on_delete=models.SET_NULL, related_name='myfavorite_set')
    level_tested = models.ManyToManyField(Brand, blank=True, related_name='leveltested_set')

    def __str__(self):
        return self.user.email

    # def get_likes2(self):
    #     return [] if (self.likes is None) | (self.likes == '') else [w.strip() for w in self.likes.split(',')]

    def update_actions(self, action, add=None, remove=None):
        if action=='brand_like':
            pool = self.brand_likes
            obj = Brand.objects

        elif action=='brand_bookmark':
            pool = self.brand_bookmarks
            obj = Brand.objects

        elif action=='post_like':
            pool = self.post_likes
            obj = Post.objects

        elif action=='post_bookmark':
            pool = self.post_bookmarks
            obj = Post.objects

        if (add is not None) and (remove is None):
            pool.add(obj.get(pk=add))

        elif (add is None) and (remove is not None):
            pool.remove(obj.get(pk=remove))

    def get_actions(self, action, pk=None):
        if action=='brand_like':
            actions = self.brand_likes

        elif action=='brand_bookmark':
            actions = self.brand_bookmarks

        elif action=='post_like':
            actions = self.post_likes

        elif action=='post_bookmark':
            actions = self.post_bookmarks

        if pk is None:
            return actions.all()

        else:
            return actions.get(pk=pk)

    def like_this(self, obj):
        type = obj.__class__.__name__.lower()
        action = type + '_like'
        return self.get_actions(action, pk=obj.pk) is not None

    def bookmark_this(self, obj):
        type = obj.__class__.__name__.lower()
        action = type + '_bookmark'
        return self.get_actions(action, pk=obj.pk) is not None

    def get_likes(self, type):
        if type=='brand':
            return self.brand_likes.all()

        elif type=='post':
            return self.post_likes.all()

    def get_worldcupped(self):
        worldcupped = []
        for bnames in json.loads(self.worldcup).keys():
            worldcupped += bnames.split('-')
        return set(worldcupped)


    def get_awared(self):
        # _likes = self.get_likes()
        _likes = self.get_likes('brand').values_list('name', flat=True)
        _worldcupped = self.get_worldcupped()
        awared = set(_likes) | _worldcupped
        return awared

    def awareness(self):
        awared = self.get_awared()
        brands = Brand.objects.all()
        bawareness = set(brands.values_list('awareness', flat=True))

        my_awareness = OrderedDict()
        for _baware in bawareness:
            _brands = brands.filter(awareness=_baware)
            _brands_awared = _brands.filter(name__in=awared)
            my_awareness[int(_baware)] = len(_brands_awared)/len(_brands)
            # my_awareness[int(_baware)] = '{}%'.format(round(len(_brands_awared)/len(_brands) * 100))

        # print(my_awareness)
        return my_awareness


    def _weighting(self, like=1, morelike=1):
        weights = {}
        likes = self.get_likes('brand').values_list('name', flat=True)
        for pair,selected in json.loads(self.worldcup).items():
            for b in pair.split('-'):
                add = 1
                if b==selected: add += like
                if b in likes: add += morelike
                # if b in self.get_likes(): add += morelike
                weights[b] = weights[b] + add if b in weights else add
        return weights


    def weights(self, like=1, morelike=1):
        w = self._weighting(like=like, morelike=morelike)
        w_sum = sum(w.values())
        return {k:v/w_sum for k,v in w.items()}


    def identify(self, idty_all, like=1, morelike=1):
        score = {}
        weights = self._weighting(like=like, morelike=morelike)

        for bname, w in weights.items():
            if bname in idty_all:
                for k,v in idty_all[bname].items():
                    score[k] = score[k] + v*w if k in score else v*w

        return self._minmax_scale(score, max=100, min=30)
        # score_sum = sum(score.values())
        # return {k:round(v/score_sum*100) for k,v in score.items()}

    def _minmax_scale(self, dic, max=100, min=0):
        keys = dic.keys()
        x = np.array(list(dic.values()))
        x = np.interp(x, (x.min(), x.max()), (min, max))

        return {k:int(v) for k,v in zip(keys, x)}




class CommentBrand(BigIdAbstract):
    brand = models.ForeignKey(Brand, blank=True, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{created_at} {email}'.format(created_at=self.created_at, email=self.user.email)


class CommentPost(BigIdAbstract):
    post = models.ForeignKey(Post, blank=True, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{created_at} {email}'.format(created_at=self.created_at, email=self.post.user.email)

    def get_absolute_url(self):
        url = reverse_lazy('post_detail', kwargs={'pk':self.post.pk})
        return url


def feed_image_path(instance, filename):
    return 'feed_images/{memb}/{auth}/{file}'.format(memb=instance.membership, auth=instance.author, file=filename)


class Feed(BigIdAbstract):
    membership = models.ForeignKey(Brand, blank=True, null=True, on_delete=models.SET_NULL)
    author = models.ForeignKey(Profile, blank=True, null=True, on_delete=models.SET_NULL)
    timestamp = models.DateTimeField(auto_now_add=True)
    nlikes = models.IntegerField(default='0')
    content = models.TextField(max_length=1000, null=True, blank=True)
    hashtags = models.ManyToManyField(Hashtag, blank=True)
    feed_image = models.ImageField(upload_to=feed_image_path)

    def __str__(self):
        return '{timestamp} {author}'.format(timestamp=self.timestamp, author=self.author)


# class Page(models.Model):
#     brand = models.ManyToManyField(Brand, blank=True)
#     master = models.ForeignKey(Profile, blank=True, null=True, on_delete=models.SET_NULL) # 요건 유저가 feed를 생성할때마다 업데이트 하면 되겠다
#     created_at = models.DateTimeField(auto_now_add=True)
#     nlikes = models.IntegerField(default='0')
#     page_image = models.ImageField(upload_to='brand_logos', default='')
#     name = models.CharField(max_length=120)
#     description = models.TextField(default='', blank=True, null=True)
