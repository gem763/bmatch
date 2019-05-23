from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.views.generic.list import ListView
from django.db.models import Q
from django.conf import settings
from chartjs.views.lines import BaseLineChartView
from el_pagination.views import AjaxListView
from django.views.generic import View
from .forms import PostForm, CommentPostForm
from app.models import Brand, Profile, Option, Post, CommentPost
from app.utils import brand_from_wiki, Gtrend, brandinfo, brandinfos
from django.contrib.auth.decorators import login_required
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

optname = 'init'
# api = 'http://127.0.0.1:8080/api'
# api = 'http://bmatchsupport.pythonanywhere.com/api'


class CommentPostActionsView(View):
    def get(self, request):
        try:
            pk = request.GET.get('pk', None)
            action = request.GET.get('action', None)

            if action=='edit':
                pass

            elif action=='delete':
                commentpost = CommentPost.objects.get(pk=pk)
                commentpost.delete()

            return JsonResponse({'success':True})

        except:
            return JsonResponse({'success':False})


# @login_required
def commenting_post(request, pk):
    if request.method=='POST':
        form = CommentPostForm(request.POST)

        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.post = get_object_or_404(Post, pk=pk)
            obj.save()
            return redirect(obj)


def posts(request):
    if request.method=='GET':
        type = request.GET.get('type', 'all')
        return render(request, 'app/posts.html', {'type':type})


def posts_sub(request):
    if request.method=='GET':
        type = request.GET.get('type', None)

        if type is not None:
            posts = Post.objects

            if type=='all':
                posts = posts.all()

            elif type=='my':
                posts = posts.filter(user__email=request.user.email)

            return render(request, 'app/posts_sub.html', {'posts':posts.order_by('-created_at')})


@login_required
def posting(request):
    if request.method=='GET':
        form = PostForm()
        return render(request, 'app/posting.html', {'form':form})

    elif request.method=='POST':
        form = PostForm(request.POST, request.FILES)

        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            return redirect(obj)


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'app/post_detail.html', {'post':post})


def get_opt():
    return Option.objects.get(optname=optname)


def home(request):
    return render(request, 'app/home.html')


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
    brand.simbrands = _simbrands(bname=bname, top_min=60, bottom_max=10, n_max=20)
    brand.simwords = _simwords(bname, min=0.5, topn=100, amp=10)
    brand.identity = _identity(bname=bname)
    return render(request, 'app/brand_detail.html', {'brand':brand})


def myfavorite(request):
    _candidates = list(Brand.objects.all())[:40]
    random.shuffle(_candidates)
    n = int(len(_candidates)/2)
    left = _candidates[:n]
    right = _candidates[n:]
    candidates = {'left':left, 'right':right}
    return render(request, 'app/myfavorite.html', {'candidates':candidates})

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
        brands = Brand.objects

        if self.request.user.is_authenticated:
            bnames = []
            myawareness = Profile.objects.get(user__email=self.request.user.email).awareness()
            for level, score in myawareness.items():
                _bnames = brands.filter(awareness=level).values_list('name', flat=True)
                _n = round(len(_bnames) * score)
                bnames += random.sample(list(_bnames), _n)

        else:
            bnames = list(brands.values_list('name', flat=True))

        comb = list(combinations(bnames, 2))
        _howmany = self.howmany if len(comb)>self.howmany else len(comb)
        return random.sample(comb, _howmany)
        # return random.sample(comb, self.howmany)


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
    idty_all = _identity(weights=profile.weights())
    myidentity = profile.identify(idty_all)
    myawareness = dict(profile.awareness())
    myposts = Post.objects.filter(user__email=request.user.email).order_by('-created_at')
    return render(request, 'app/me.html', {'myidentity':myidentity, 'myawareness':myawareness, 'myposts':myposts})


def sharing(request):
    return render(request, 'app/sharing.html')

def analysis(request):
    return render(request, 'app/analysis.html')


def _simbrands(qry=None, bname=None, top_min=50, bottom_max=0, n_max=20):
    sims = {}
    url = get_opt().api + '/simbrands'

    if (qry is None) & (bname is not None):
        data = {'bname':bname}

    elif (qry is not None) & (bname is None):
        data = {'qry':qry}

    else:
        return sims

    res = requests.post(url, data=data).json()
    if len(res)==0: return sims
    scored = _scored_brands(res)

    if top_min is not None:
        _top = [br for br in scored if br.score > top_min]
        sims['top'] = sorted(_top, key=lambda b:-b.score)[:n_max]

    if bottom_max is not None:
        _bottom = [br for br in scored if br.score < bottom_max]
        sims['bottom'] = sorted(_bottom, key=lambda b:b.score)[:n_max]

    return sims


def _scored_brands(scores):
    scored = []
    for brand in Brand.objects.all():
        if brand.name in scores:
            brand.score = round(scores[brand.name]*100)
            scored.append(brand)

    return scored


def _simwords(bname, amp=10, min=0, topn=10):
    url = get_opt().api + '/simwords'
    data = {'bname': bname, 'min': min, 'topn': topn}
    req = requests.post(url, data=data)
    res = req.json()
    return {k:v**amp for k,v in res.items()}


def identity(request, bname, weights=None):
    return JsonResponse(_identity(bname=bname, weights=weights))


def _identity(bname=None, weights=None):
    opt = get_opt()
    url = opt.api + '/identity'
    idwords = opt.idwords
    id_scaletype = opt.id_scaletype

    if bname is None:
        # data = {'idwords':idwords, 'id_scaletype':id_scaletype, 'weights':weights}
        data = {'idwords':idwords, 'id_scaletype':id_scaletype, 'weights':json.dumps(weights)}

    else:
        data = {'bname':bname, 'idwords':idwords, 'id_scaletype':id_scaletype}

    req = requests.post(url, data=data)
    return req.json()



# 주어진 Brand 객체의 로고 이미지 주소
def _imgurl(brand):
    return os.path.join(settings.MEDIA_URL, str(brand.logo))


def _indexer(brands):
    return sorted(list({brand.name[0] for brand in brands.all()}))


# def _search_helper(brands):
#     return [{'title':brand.fullname_en, 'description':brand.fullname_kr, 'categories':brand.keywords, 'image':_imgurl(brand)} for brand in brands.all()]


def search_helper(request):
    helper = [
        {'title':brand.fullname_en, 'description':brand.fullname_kr, 'categories':brand.keywords, 'image':_imgurl(brand)}
        for brand in Brand.objects.all()
    ]
    return JsonResponse(helper, safe=False)


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



def discover(request):
    brands = Brand.objects.all()
    suggestions = random.sample(list(brands), 8)
    hottrendnow = Post.objects.all().order_by('-created_at')[:16]

    # 현재는 Social keywords 가 특정 브랜드로 들어가 있는데,
    # 향후, 트위터 real-time으로 불러오는 기능이 있어야함
    socialwords = _simwords('crocs', min=0.5, topn=100, amp=10)
    return render(request, 'app/discover.html', {'suggestions':suggestions, 'hottrendnow':hottrendnow, 'socialwords':socialwords})


class LibraryView(AjaxListView):
    context_object_name = 'brands'
    template_name = 'app/library.html'
    page_template = 'app/library_page.html'
    qry = None
    page = None

    def get_queryset(self):
        brands = Brand.objects
        indexer = _indexer(brands)
        # search_helper = _search_helper(brands)

        all = None
        simbrands = None

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
                simbrands = _simbrands(bname=bname, top_min=60, bottom_max=10, n_max=20)

            else:
                simbrands = _simbrands(qry=self.qry, top_min=60, bottom_max=10, n_max=20)


        return {
            'qry': self.qry,
            'indexer': indexer,
            # 'search_helper':search_helper,
            'all': all,
            'simbrands': simbrands,
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
    query_rising_data = queries['rising'].rename(columns={'query':'key'}).iloc[:5]
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



# def _simbrands_old(qry=None, bname=None, top_min=0.5, bottom_max=0):
#     _top = None
#     _bottom = None
#     brands = Brand.objects
#
#     url = get_opt().api + '/simbrands'
#     data = {}
#
#     if (qry is None) & (bname is not None):
#         data['bname'] = bname
#
#     elif (qry is not None) & (bname is None):
#         data['qry'] = qry
#
#     else:
#         return _top, _bottom
#
#     res = requests.post(url, data=data).json()
#
#     def _put_scores(scores):
#         simbrands = brands.filter(name__in=scores.keys())
#
#         for simbrand in simbrands:
#             simbrand.score = scores[simbrand.name]
#
#         return sorted(simbrands, key=lambda x:-x.score)
#
#
#     if top_min is not None:
#         _scores = {k:round(100*v) for k,v in res.items() if v > top_min}
#         _top = _put_scores(_scores)
#
#     if bottom_max is not None:
#         _scores = {k:round(100*v) for k,v in res.items() if v < bottom_max}
#         _bottom = _put_scores(_scores)
#
#     return _top, _bottom



# def _simbrands_old(qry=None, mybname=None, top_min=0.5, bottom_max=0):
#     _top = None
#     _bottom = None
#     brands = Brand.objects
#     keywords_dict = _keywords_dict(brands)
#
#     url = get_opt().api + '/simbrands'
#     data = {'brands':json.dumps(keywords_dict)}
#
#     if (qry is None) & (mybname is not None):
#         data['mybname'] = mybname
#
#     elif (qry is not None) & (mybname is None):
#         data['qry'] = qry
#
#     else:
#         return _top, _bottom
#
#     res = requests.post(url, data=data).json()
#
#     def _put_scores(scores):
#         simbrands = brands.filter(name__in=scores.keys())
#
#         for simbrand in simbrands:
#             simbrand.score = scores[simbrand.name]
#
#         return sorted(simbrands, key=lambda x:-x.score)
#
#
#     if top_min is not None:
#         _scores = {k:round(100*v) for k,v in res.items() if v > top_min}
#         _top = _put_scores(_scores)
#
#     if bottom_max is not None:
#         _scores = {k:round(100*v) for k,v in res.items() if v < bottom_max}
#         _bottom = _put_scores(_scores)
#
#     return _top, _bottom
