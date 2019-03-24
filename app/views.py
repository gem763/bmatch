from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.views.generic.list import ListView
from django.db.models import Q
from django.conf import settings
from chartjs.views.lines import BaseLineChartView
from el_pagination.views import AjaxListView
from django.views.generic import View
from app.models import Brand, Profile
from app.utils import brand_from_wiki, Gtrend, brandinfo, brandinfos
import time
import json
import math
import glob
import os
import pandas as pd
import requests
import random
from itertools import combinations
from django.contrib.staticfiles.storage import staticfiles_storage


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

    return HttpResponse('updated')


def brand_detail(request, bname):
    brand = Brand.objects.get(name=bname)
    brand.identity = json.loads(brand.identity)

    for idty in brand.identity:
        idty['key0'], idty['key1'] = idty['key'].split('-')

    simbrands_top, simbrands_bottom = _simbrands(mybname=bname, top_min=0.5, bottom_max=0)
    simwords = _simwords(brand.keywords, min=0.5, topn=100, amp=10)
    return render(request, 'app/brand_detail.html', {'brand':brand, 'simbrands_top':simbrands_top[1:], 'simbrands_bottom':simbrands_bottom, 'simwords':simwords})


def rating(request):
    howmany = 10
    bnames = list(Brand.objects.values_list('name', flat=True))
    comb = list(combinations(bnames, 2))  #[set(_comb) for _comb in combinations(bnames, 2)]
    pairs = random.sample(comb, howmany)
    return render(request, 'app/rating.html', {'pairs':pairs})


class RatingView(AjaxListView):
    context_object_name = 'pairs'
    template_name = 'app/rating.html'
    page_template = 'app/rating_page.html'
    howmany = 500

    def get_queryset(self):
        bnames = list(Brand.objects.values_list('name', flat=True))
        comb = list(combinations(bnames, 2))
        return random.sample(comb, self.howmany)


def profiling(request):
    try:
        profile = Profile.objects.get(user__email=request.user.email)
        # return HttpResponse(profile.user.last_login)
        return HttpResponseRedirect(reverse('home'))
    except:
        profile = Profile()
        profile.user = request.user
        profile.save()
        # return HttpResponse(profile.user.email)
        return HttpResponseRedirect(reverse('home'))


def me(request):
    profile = Profile.objects.get(user__email=request.user.email)
    myidentity = {k:round(v*100) for k,v in profile.identify().items()}
    # print(myidentity)
    return render(request, 'app/me.html', {'myidentity':myidentity})
    # return HttpResponse(profile.identify())


def sharing(request):
    return render(request, 'app/sharing.html')

def analysis(request):
    return render(request, 'app/analysis.html')


def _simbrands(qry=None, mybname=None, top_min=0.5, bottom_max=0):
    _top = None
    _bottom = None
    brands = Brand.objects
    keywords_dict = _keywords_dict(brands)

    url = api + '/simbrands'
    data = {'brands':json.dumps(keywords_dict)}

    if (qry is None) & (mybname is not None):
        data['mybname'] = mybname

    elif (qry is not None) & (mybname is None):
        data['qry'] = qry

    else:
        return _top, _bottom

    res = requests.post(url, data=data).json()

    def _put_scores(scores):
        simbrands = brands.filter(name__in=scores.keys())

        for simbrand in simbrands:
            simbrand.score = scores[simbrand.name]

        return sorted(simbrands, key=lambda x:-x.score)


    if top_min is not None:
        _scores = {k:round(100*v) for k,v in res.items() if v > top_min}
        _top = _put_scores(_scores)

    if bottom_max is not None:
        _scores = {k:round(100*v) for k,v in res.items() if v < bottom_max}
        _bottom = _put_scores(_scores)

    return _top, _bottom


def _simwords(keywords, amp=10, min=0, topn=10):
    url = api + '/simwords'
    words = ' '.join([kw.strip() for kw in keywords.split(',')])
    data = {'w': words, 'min':min, 'topn':topn}
    req = requests.post(url, data=data)
    res = req.json()
    return {k:v**amp for k,v in res.items()}


# def _brandscore_to_qry(qry, keywords_dict):
#     url = api + '/search'
#     data = {'qry':qry, 'brands':json.dumps(keywords_dict)}
#     req = requests.post(url, data=data)
#     return req.json()


# 주어진 Brand 객체의 로고 이미지 주소
def _imgurl(brand):
    return os.path.join(settings.MEDIA_URL, str(brand.logo))


def _indexer(brands):
    return sorted(list({brand.name[0] for brand in brands.all()}))


def _search_helper(brands):
    return [{'title':brand.fullname_en, 'description':brand.fullname_kr, 'categories':brand.keywords, 'image':_imgurl(brand)} for brand in brands.all()]


# def _bnames_set(brands):
#     _bnames = [[brand.name, brand.fullname_en, brand.fullname_kr] + [kw.strip() for kw in brand.keywords.split(',')] for brand in brands.all()]
#     return set(sum(_bnames, []))


def _keywords_dict(brands):
    return {brand.name:[kw.strip() for kw in brand.keywords.split(',')] for brand in brands.all()}


def _in_bnames(qry, brands):
    for brand in brands.all():
        _candidates = {brand.name, brand.fullname_en, brand.fullname_kr} | {kw.strip() for kw in brand.keywords.split(',')}
        if qry in _candidates:
            return brand.name

    return None


class SaveLikeView(View):
    def get(self, request):
        try:
            like = request.GET.get('like', None)
            dontlike = request.GET.get('dontlike', None)
            profile = Profile.objects.get(user__email=request.user.email)
            likes_list = profile.get_likes()
            
            if (like is not None) and (dontlike is None):
                likes_list.append(like)

            elif (like is None) and (dontlike is not None):
                if dontlike in likes_list:
                    likes_list.remove(dontlike)

            profile.likes = ','.join(set(likes_list))
            profile.save()
            return JsonResponse({'success':True})

        except:
            return JsonResponse({'success':False})


class SaveWorldcupView(View):
    def get(self, request):
        try:
            more = request.GET.get('more', None)
            less = request.GET.get('less', None)
            profile = Profile.objects.get(user__email=request.user.email)
            worldcup = json.loads(profile.worldcup)
            key = '-'.join(sorted([more, less]))
            worldcup[key] = more
            profile.worldcup = json.dumps(worldcup)
            profile.save()
            return JsonResponse({'success':True})

        except:
            return JsonResponse({'success':False})


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
        recommend = None
        not_recommend = None

        # 쿼리가 없는 경우 (discover 초기 페이지)
        if self.qry is None:
            if (self.page is None) | (self.page=='all'):
                all = brands.order_by('name')

            elif self.page=='like':
                profile = Profile.objects.get(user__email=self.request.user.email)
                all = brands.filter(name__in=profile.get_likes()).order_by('name')

            else:
                _regex = r'^[' + self.page.replace(' ', '') + ']'
                all = brands.filter(fullname_en__iregex=_regex).order_by('name')

        else:
            bname = _in_bnames(self.qry, brands)
            # exact = brands.get(Q(name=self.qry) | Q(fullname_en=self.qry) | Q(fullname_kr=self.qry) | Q(keywords__icontains=self.qry))

            # 브랜드명(name, fullname_en, fullname_kr, keywords)이 입력된 경우
            if bname is not None:
                recommend, not_recommend = _simbrands(mybname=bname, top_min=0.5, bottom_max=0)

            else:
                recommend, not_recommend = _simbrands(qry=self.qry, top_min=0.5, bottom_max=0)

        return {
            'qry':self.qry,
            'indexer':indexer,
            'search_helper':search_helper,
            'all':all,
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
                'borderColor': '#21BA45',
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
