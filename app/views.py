from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.views.generic.list import ListView
from django.db.models import Q
from django.conf import settings
# from django.contrib import messages
from chartjs.views.lines import BaseLineChartView
from el_pagination.views import AjaxListView
from app.models import Brand
from app.utils import brand_from_wiki, Gtrend, brandinfo, brandinfos
import time
import json
import math
import glob
import os
import pandas as pd
import requests
from django.contrib.staticfiles.storage import staticfiles_storage
# from django.views.decorators.csrf import csrf_exempt


# api = 'http://127.0.0.1:8080/api'
api = 'http://bmatchsupport.pythonanywhere.com/api'


def intro(request):
    return render(request, 'app/intro.html')

def searched(request):
    search = request.GET.get('search', '')

    # if search:
    #     return BrandListView.as_view(contains=search)
    #return render(request, 'searched.html')
    return BrandListView.as_view()

def db_update(request, category):
    names = Brand.objects.all().values_list('name', flat=True)
    wiki = brand_from_wiki(category, names_db=names, limit=None)
    #wiki = brand_from_wiki('Category:High_fashion_brands', names_db=names, limit=None)

    for k,v in wiki.items():
        Brand.objects.create(
            name=k,
            logo_url=v['logo'],
            description=v['desc'],
        )

    #brands = Brand.objects.exclude(logo_url='')
    return HttpResponse('updated') #render(request, 'rating.html', {'brands':brands})

# def discover(request):
#     # if request.user.is_authenticated:
#     #     messages.info(request, "Welcome")
#
#     #brands = Brand.objects.all()#filter(pk__range=(0,50)) #all()
#     brands = Brand.objects.order_by('-name')
#     return render(request, 'discover.html', {'brands':brands})

def brand_detail(request, bname):
    brand = Brand.objects.get(name=bname)
    brand.identity = json.loads(brand.identity)
    keywords = [kw.strip() for kw in brand.keywords.split(',')]
    brand.wordfreq = _simwords(keywords, amp=10)
    # brand.wordfreq = _simwords_to_brand([bname, brand.fullname_kr.replace(' ','')], amp=10)

    for idty in brand.identity:
        idty['key0'], idty['key1'] = idty['key'].split('-')

    keywords_dict = _keywords_dict(Brand.objects)
    simbrands_score = {k:round(100*v) for k,v in _simbrands(bname, keywords_dict).items() if v>0.5}

    simbrands = Brand.objects.filter(name__in=simbrands_score.keys())
    for simbrand in simbrands:
        simbrand.score = simbrands_score[simbrand.name]

    # simbrands = Brand.objects.filter(cluster=brand.cluster).exclude(name=brand.name)
    # for simbrand in simbrands:
    #     try:
    #         simbrand.score = round(simbrands_score[simbrand.name]*100)
    #     except:
    #         simbrand.score = -100

    simbrands = sorted(simbrands, key=lambda x:-x.score)
    return render(request, 'app/brand_detail.html', {'brand':brand, 'simbrands':simbrands, 'simbrands_score':simbrands_score})


def me(request):
    return render(request, 'app/me.html')

def sharing(request):
    return render(request, 'app/sharing.html')

def analysis(request):
    return render(request, 'app/analysis.html')


def search(request, qry):
    bnames = ' '.join([brand.name for brand in Brand.objects.all()])
    url_base = 'http://127.0.0.1:8080/api/search/?'
    url = url_base + 'q=' + qry + '&b=' + bnames
    req = requests.get(url)
    res = json.loads(req.text)
    # res = dict(sorted(res.items(), key=lambda x: x[1])[:20])
    return JsonResponse({k:v for k,v in res.items() if v>0.5})


def _simbrands(mybname, keywords_dict):
    # baseurl = api + '/simbrands/?my={my}&brands={brands}'
    # url = baseurl.format(my=mybname, brands=json.dumps(keywords_dict))
    # req = requests.get(url)

    url = api + '/simbrands'
    data = {'my':mybname, 'brands':json.dumps(keywords_dict)}
    req = requests.post(url, data=data)
    # return json.loads(req.text)
    return req.json()

# @csrf_exempt
def _simwords(words, amp=None):
    # baseurl = api + '/simwords/?w={w}'
    # url = baseurl.format(w=' '.join(words))
    # req = requests.get(url)

    url = api + '/simwords'
    data = {'w': ' '.join(words)}
    req = requests.post(url, data=data)
    res = req.json() #json.loads(req.text)
    return {k:v**amp for k,v in res.items()}


def _brandscore_to_qry(qry, keywords_dict):
    # baseurl = api + '/search/?qry={qry}&brands={brands}'
    # url = baseurl.format(qry=qry, brands=json.dumps(keywords_dict))
    # req = requests.get(url)

    url = api + '/search'
    data = {'qry':qry, 'brands':json.dumps(keywords_dict)}
    req = requests.post(url, data=data)
    # print('----------------------------', req.text)
    # return json.loads(req.text)
    return req.json()


# 주어진 Brand 객체의 로고 이미지 주소
def _imgurl(brand):
    return os.path.join(settings.MEDIA_URL, str(brand.logo))


# 주어진 Brands <QuerySet>에 대하혀, 특정 필드 출력
# def _brands_by_field(brands, f):
#     return [getattr(brand, f) for brand in brands.all()]

def _indexer(brands):
    return sorted(list({brand.name[0] for brand in brands.all()}))


def _search_helper(brands):
    return [{'title':brand.fullname_en, 'description':brand.fullname_kr, 'categories':brand.keywords, 'image':_imgurl(brand)} for brand in brands.all()]


def _bnames_set(brands):
    _bnames = [[brand.name, brand.fullname_en, brand.fullname_kr] + [kw.strip() for kw in brand.keywords.split(',')] for brand in brands.all()]
    return set(sum(_bnames, []))


def _keywords_dict(brands):
    return {brand.name:[kw.strip() for kw in brand.keywords.split(',')] for brand in brands.all()}


class DiscoverView(AjaxListView):
    context_object_name = 'brands'
    template_name = 'app/discover.html'
    page_template = 'app/discover_page.html'
    qry = None
    page = None

    def get_queryset(self):
        brands = Brand.objects
        indexer = _indexer(brands)
        search_helper = _search_helper(brands)

        all = None
        exact = None
        similar = None
        recommend = None
        not_recommend = None

        # 쿼리가 없는 경우 (discover 초기 페이지)
        if self.qry is None:
            if (self.page is None) | (self.page=='all'):
                all = brands.order_by('name')
            else:
                _regex = r'^[' + self.page.replace(' ', '') + ']'
                all = brands.filter(fullname_en__iregex=_regex).order_by('name')

        # 브랜드명(name, fullname_en, fullname_kr, keywords)이 입력된 경우
        elif self.qry in _bnames_set(brands):
            exact = brands.get(Q(name=self.qry) | Q(fullname_en=self.qry) | Q(fullname_kr=self.qry) | Q(keywords__icontains=self.qry))
            similar = brands.filter(cluster=exact.cluster).exclude(name=exact.name).order_by('name')

        # 여러가지 키워드들이 입력된 경우
        else:
            keywords_dict = _keywords_dict(brands)
            scores = _brandscore_to_qry(self.qry, keywords_dict)
            _recommend = [k for k,v in scores.items() if v>0.4]
            _not_recommend = [k for k,v in scores.items() if v<0]

            recommend = brands.filter(name__in=_recommend).order_by('name')
            not_recommend = brands.filter(name__in=_not_recommend).order_by('name')

        return {
            'qry':self.qry,
            'indexer':indexer,
            'search_helper':search_helper,
            'all':all,
            'exact':exact,
            'similar':similar,
            'recommend':recommend,
            'not_recommend':not_recommend
        }


    def get(self, request):
        q = request.GET.get('q', None)
        if q is not None:
            self.qry = q.strip()

        p = request.GET.get('p', None)
        if p is not None:
            self.page = p.lower()

        return super().get(request)


class BrandListView(AjaxListView):
    context_object_name = 'brand_list'
    template_name = 'app/brand_list.html'
    page_template = 'app/brand_list_page.html'

    def get_queryset(self):
        qs = Brand.objects.exclude(logo_url='')
        search = self.request.GET.get('search')

        if search:
            q_objects = Q()
            for kwd in search.split(' '):
                if kwd!='': q_objects.add(Q(name__icontains=kwd), Q.OR)
            qs = qs.filter(q_objects)

        return qs


# def bnames(request):
#     brands = Brand.objects.all()
#     return JsonResponse([{'name':brand.name, 'value':brand.name, 'logo':brand.logo} for brand in brands], safe=False)
    #return JsonResponse([{'title':brand.name} for brand in brands], safe=False)


def gtrend(request, brand_name):
    _gtrend = Gtrend(brand_name)
    trend = _gtrend.trend()
    queries = _gtrend.queries()

    query_top_data = queries['top'].rename(columns={'query':'key'}).iloc[:5].to_dict('record')
    query_rising_data = queries['rising'].rename(columns={'query':'key'}).iloc[:5]#.to_dict('record')
    query_rising_data['value'] = (query_rising_data['value']/query_rising_data['value'].iloc[0]*100).astype(int)
    query_rising_data = query_rising_data.to_dict('record')

    trend_data = {
        'type': 'line',
        'data': {
            'labels': list(trend.index.date),
            'datasets': [{
                'label': brand_name,
                'data': list(trend[brand_name]),
                'borderColor': '#21BA45', #'#2ecc40', #
            }],
        },

        'options': {
            'elements': {
                'point': {'radius': 0},
                'line': {'fill':False},
            },
            'scales': {
                'xAxes': [{
                    'type': 'time',
                    'time': {
                        'unit':'month',
                        'displayFormats': {'month':'YYYY.MM'},
                    },
                    'gridLines': {'display':False,},
                }],
                'yAxes': [{'gridLines': {'display':False},}],
            },

            'legend': {'display': False,}
        }
    }

    return JsonResponse({
        'trend_data':trend_data,
        'query_top_data':query_top_data,
        'query_rising_data':query_rising_data
    })
