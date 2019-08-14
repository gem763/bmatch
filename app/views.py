from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.views.generic.list import ListView
from django.db.models import Q
from django.conf import settings
from chartjs.views.lines import BaseLineChartView
from el_pagination.views import AjaxListView
# from el_pagination.decorators import page_template
from django.views.generic import View
from .forms import PostForm, CommentPostForm
from app.models import Brand, Profile, Option, Post, Feed, CommentPost, Hashtag, Channel
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
from collections import Counter
from django.template.loader import render_to_string



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
        screen = request.GET.get('screen', 'all')
        # interest = Profile.objects.get(user__email=request.user.email).values('name')
        # print(interest)
        return render(request, 'app/posts.html', {'screen':screen})


def suggestions():
    brands = Brand.objects.all()
    return random.sample(list(brands), 9)


def hottrendnow():
    return Post.objects.order_by('-created_at')[:15]


def allbrands():
    return Brand.objects.order_by('name')[:]


def allposts():
    return Post.objects.order_by('-created_at')


def myposts(email):
    return Post.objects.filter(user__email=email).order_by('-created_at')


def leveltest():
    brands = Brand.objects.all()
    return random.sample(list(brands), 20)


def blocks(request):
    template = 'app/baseblocks.html'
    page_template = 'app/baseblocks_page.html'
    screen_0 = 'all'
    ncols_0 = 'three'

    type = request.GET.get('type', None)
    screen = request.GET.get('screen', screen_0)
    ncols = request.GET.get('ncols', ncols_0)
    bname = request.GET.get('bname', None)
    keywords = request.GET.get('keywords', None)

    ctx = {'page_template':page_template, 'type':type, 'ncols':ncols}

    try:
        if type=='allbrands':
            ctx['blocks'] = allbrands()
            template = 'app/library.html'

            # 아랫부분이 반드시 필요하다: 스크롤 새로운 페이지 로딩될때의 템플릿을 의미하는듯
            if request.is_ajax():
                template = page_template

        elif type=='simbrands':
            simbrands = _simbrands(bname=bname, top_min=60, bottom_max=10, n_max=20)
            ctx['sims'] = simbrands['top']
            ctx['diffs'] = simbrands['bottom']
            template = 'app/simblocks.html'

        elif type=='leveltest':
            ctx['blocks'] = leveltest()

        elif type=='suggestions':
            ctx['blocks'] = suggestions()

        elif type=='posts':
            if screen=='all':
                ctx['blocks'] = allposts()

            elif screen=='my':
                ctx['blocks'] = myposts(request.user.email)

        elif type=='hottrendnow':
            ctx['blocks'] = hottrendnow()

        elif type=='feeds':
            ctx['blocks'] = feeds(keywords)[:]

        else:
            pass

    except:
        ctx['err'] = 'Something wrong'

    return render(request, template, ctx)


# @login_required
def newpost(request):
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


# @login_required
def editpost(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if request.method=='GET':
        form = PostForm(instance=post)
        return render(request, 'app/posting.html', {'form':form})

    elif request.method=='POST':
        form = PostForm(request.POST, request.FILES, instance=post)

        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            form.save_m2m()
            return redirect(obj)


def deletepost(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if request.method=='GET':
        post.delete()
        return HttpResponseRedirect(reverse('posts'))


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'app/post_detail.html', {'post':post})


def get_opt():
    return Option.objects.get(optname=optname)


def home(request):
    feeds_top = Feed.objects.exclude(image__exact='').distinct().order_by('-nlikes')[:5]

    channels_all = Channel.objects.all()
    _topch = list(channels_all.order_by('-nlikes'))[:5]

    # now = pd.Timestamp.now().tz_localize(None)
    now = pd.Timestamp(Feed.objects.order_by('timestamp').last().timestamp)
    _from = (now - pd.DateOffset(months=3)).date()
    _hashtags = Hashtag.objects.filter(feed__timestamp__date__gte=_from).exclude(feed__content__contains='카지노').values_list('hashtag', flat=True)
    _freq = dict(Counter(_hashtags).most_common(100))

    # print(_freq)
    return render(request, 'app/home.html', {'feeds_top':feeds_top, 'top_channels':_topch, 'hashtags_freq':_freq})


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
    #brand.simwords = _simwords(bname, min=0.5, topn=100, amp=10)
    #brand.identity = _identity(bname=bname)
    brand.feeds = list(Feed.objects.filter(membership__name=bname))[:50]
    return render(request, 'app/brand_detail.html', {'brand':brand})


def myfavorite(request):
    _candidates = list(Brand.objects.all())[:40]
    random.shuffle(_candidates)
    n = int(len(_candidates)/2)
    left = _candidates[:n]
    right = _candidates[n:]
    candidates = {'left':left, 'right':right}
    return render(request, 'app/myfavorite.html', {'candidates':candidates})


def level_test(request):
    return render(request, 'app/level_test.html')


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
    myfavorite = profile.myfavorite
    idty_all = _identity(weights=profile.weights())
    myidentity = profile.identify(idty_all)
    myawareness = dict(profile.awareness())
    myposts = Post.objects.filter(user__email=request.user.email).order_by('-created_at')
    return render(request, 'app/me.html', {'myfavorite':myfavorite, 'myidentity':myidentity, 'myawareness':myawareness, 'myposts':myposts})



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
    return os.path.join(settings.MEDIA_URL, str(brand.image))


def _indexer(brands):
    return sorted(list({brand.name[0] for brand in brands.all()}))


# def _search_helper(brands):
#     return [{'title':brand.fullname_en, 'description':brand.fullname_kr, 'categories':brand.keywords, 'image':_imgurl(brand)} for brand in brands.all()]


def search_helper(request):
    helper = [
        {'title':brand.fullname_en, 'description':brand.fullname_kr, 'categories':brand.keywords, 'image':_imgurl(brand), 'bname':brand.name}
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


class UpdateMyfavoriteView(View):
    def get(self, request):
        try:
            bname = request.GET.get('bname', None)
            if bname is not None:
                brand = Brand.objects.get(name=bname)
                profile = Profile.objects.get(user__email=request.user.email)
                profile.myfavorite = brand
                profile.save()
                return JsonResponse({'success':True})

        except:
            return JsonResponse({'success':False})


class ActionsView(View):
    def get(self, request):
        try:
            action = request.GET.get('action', None)
            add = request.GET.get('add', None)
            remove = request.GET.get('remove', None)
            profile = Profile.objects.get(user__email=request.user.email)
            profile.update_actions(action, add=add, remove=remove)
            return JsonResponse({'success':True})

        except:
            return JsonResponse({'success':False})


class UpdateLikesView(View):
    def get(self, request):
        try:
            type = request.GET.get('type', None)
            _like = request.GET.get('like', None)
            _dontlike = request.GET.get('dontlike', None)
            profile = Profile.objects.get(user__email=request.user.email)

            if type=='brand':
                like = Brand.objects.get(name=_like) if _like is not None else None
                dontlike = Brand.objects.get(name=_dontlike) if _dontlike is not None else None
                likes = profile.brand_likes

            elif type=='post':
                like = Post.objects.get(pk=_like) if _like is not None else None
                dontlike = Post.objects.get(pk=_dontlike) if _dontlike is not None else None
                likes = profile.post_likes

            if (like is not None) and (dontlike is None):
                likes.add(like)

            elif (like is None) and (dontlike is not None):
                likes.remove(dontlike)

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


def channels(request):
    channels_all = Channel.objects.all()
    _channels = channels_all.values('id', 'channel__name', 'channel__image', 'master__image').order_by('channel__name')
    [ch.pop('master__image',None) for ch in _channels if ch['master__image'] is None]
    _topch = list(channels_all.order_by('-nlikes'))[:5]
    return render(request, 'app/channels.html', {'channels':list(_channels), 'top_channels':_topch})


def channel(request, chname):
    _channel = Channel.objects.get(channel__name=chname)
    _channel_feeds = _channel.feed_set.all().prefetch_related('hashtags', 'channels__content').select_related('author').order_by('-timestamp')[:]

    _feeds = []
    for feed in _channel_feeds:
        _feed = {
            'id': feed.pk,
            'author_image': feed.author.image.name,
            'content': feed.content,
            # 'hashtags': feed.hashtags.all().values_list('hashtag', flat=True),
            'hashtags': [str(tag) for tag in feed.hashtags.all()],
            'image' : feed.image.name,
            'channels_image': [{'name':ch.content.name, 'image':ch.content.image.name} for ch in feed.channels.all()],
            'timestamp': feed.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        }

        _feeds.append(_feed)

    # template='app/page.html',
    # feeds_template='app/page_feeds.html'
    #
    # ctx = {
    #     'page': _page,
    #     'feeds_template': feeds_template,
    # }
    #
    # if request.is_ajax():
    #     template = feeds_template
    #
    # return render(request, template, ctx)

    return render(request, 'app/channel.html', {'channel':_channel, 'feeds':_feeds})


def discover(request):
    # 현재는 Social keywords 가 특정 브랜드로 들어가 있는데,
    # 향후, 트위터 real-time으로 불러오는 기능이 있어야함
    socialwords = _simwords('crocs', min=0.5, topn=100, amp=10)
    return render(request, 'app/discover.html', {'socialwords':socialwords})


def _hashtags_freq(words_list, topn):
    q = Q()
    for w in words_list:
        q = q | Q(feed__hashtags__hashtag__icontains=w)

    hashtags = Hashtag.objects.filter(q).values_list('hashtag', flat=True)
    freq = dict(Counter(hashtags).most_common(topn))
    [freq.pop(w, None) for w in words_list]
    return freq


def _feeds(words_list):
    q = Q()
    for w in words_list:
        q = q | Q(hashtags__hashtag__icontains=w)

    return Feed.objects.filter(q).exclude(image__exact='').distinct().order_by('-timestamp')


def journey(request, words):
    # feeds = Feed.objects.filter(hashtags__hashtag__icontains=hashtag)
    # feeds = Hashtag.objects.get(hashtag=hashtag).feed_set.all()
    # list_hashtags = feeds.values('hashtags__hashtag')

    _words = [w.strip() for w in words.split(',')]
    hashtags_freq = _hashtags_freq(_words, 100)
    feeds = _feeds(_words)

    ctx = {
        'hashtags_freq': hashtags_freq,
        'feeds': list(feeds.values('id','image')),
    }

    return render(request, 'app/journey.html', ctx)



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
