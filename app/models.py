from django.db import models
from django.conf import settings
import json

# Create your models here.


class Option(models.Model):
    # idwords_default = [
    #     {'럭셔리': '럭셔리 고급 호화 과시 명품 luxury 비싼 고가 expensive pricy pricey',
    #      '캐주얼': '캐주얼 캐쥬얼 casual 스타일리시 스타일리쉬 stylish'},
    #     {'유니크': '유니크 독특 독창 unique 개성 only 참신 신선 특이 아이디어 철학',
    #      '대중성': '대중 popular 널리 흔한 massive mass 대중성'},
    #     {'정통성': '정통 클래식 classic 품격 약속 신뢰 믿음 예측 견고 품질 안정',
    #      '트렌디': '트렌디 트랜디 트렌드 트랜드 유행 trend trendy 변화 새로운 민감 예민 신상 최신'},
    #     {'포멀': '포멀 formal 노멀 normal 평범 일상 무난 기본 베이스 베이직 base basic',
    #      '액티브': '화제 인기 hot 튀는 액티브 active 앞서가는 실험 과감 선도 선구 대담'}
    # ]

    optname = models.CharField(max_length=120, default='')
    idwords = models.TextField(default='')
    api = models.CharField(max_length=120, default='http://127.0.0.1:8080/api')

    def __str__(self):
        return self.optname


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
    # cluster = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.name

    def get_id(self):
        return json.loads(self.identity)
        # return {i['key']:i['value'] for i in json.loads(self.identity)}



class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    worldcup = models.TextField(blank=True, null=True, default='{}')
    likes = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.email

    def get_likes(self):
        return [] if (self.likes is None) | (self.likes == '') else [w.strip() for w in self.likes.split(',')]

    def _weighting(self, like=1, morelike=1):
        weights = {}
        for pair,selected in json.loads(self.worldcup).items():
            for b in pair.split('-'):
                add = 1
                if b==selected: add += like
                if b in self.get_likes(): add += morelike
                weights[b] = weights[b] + add if b in weights else add
        return weights

    def identify(self, like=1, morelike=1):
        score = {}
        brands = Brand.objects
        weights = self._weighting(like=like, morelike=morelike)

        for bname, w in weights.items():
            for k,v in brands.get(name=bname).get_id().items():
                score[k] = score[k] + v*w if k in score else v*w

        score_sum = sum(score.values())
        return {k:round(v/score_sum*100) for k,v in score.items()}
