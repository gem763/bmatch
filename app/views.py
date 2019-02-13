from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.generic.list import ListView
from django.db.models import Q
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
from django.contrib.staticfiles.storage import staticfiles_storage
from sklearn import preprocessing

# Create your views here.

def intro(request):
    return render(request, 'intro.html')

def discover(request):
    # if request.user.is_authenticated:
    #     messages.info(request, "Welcome")

    return render(request, 'discover.html')

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

def brands(request):
    brands = Brand.objects.filter(pk__range=(0,50)) #all()
    return render(request, 'brands.html', {'brands':brands})

def brand_detail2(request, name):
    brand = Brand.objects.get(name=name)
    return render(request, 'brand_detail.html', {'brand':brand})

def brand_detail(request, bname):
    brand = Brand.objects.get(name=bname)
    return render(request, 'brand_detail.html', {'brand':brand})


def me(request):
    return render(request, 'me.html')

def sharing(request):
    return render(request, 'sharing.html')

def analysis(request):
    return render(request, 'analysis.html')


class BrandListView(AjaxListView):
    context_object_name = 'brand_list'
    template_name = 'brand_list.html'
    page_template = 'brand_list_page.html'

    def get_queryset(self):
        qs = Brand.objects.exclude(logo_url='')
        search = self.request.GET.get('search')

        if search:
            q_objects = Q()
            for kwd in search.split(' '):
                if kwd!='': q_objects.add(Q(name__icontains=kwd), Q.OR)
            qs = qs.filter(q_objects)

        return qs


def identities(request, bname):
    df = pd.read_pickle('id_dict.pkl')
    min_max_scaler = preprocessing.MinMaxScaler(feature_range=(0.1, 1))
    X_train_minmax = min_max_scaler.fit_transform(df)
    df[:] = X_train_minmax

    _df = df[[bname]].reset_index().rename(columns={'index':'key', bname:'value'})
    #df.value[:] = X_train_minmax

    _df.value = (_df.value*100).astype(int)
    idty = _df.to_dict('record')
    return JsonResponse({'idty':idty})


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

    # print(pd.read_pickle('id_dict.pkl'))
    #test = queries['top'].copy()
    #test.columns = ["abc", 'kkk']
    #print(query_top_data)

    #print(pd.read_pickle('id_dict.pkl')[[brand_name]].reset_index().rename(columns={'index':'key', brand_name:'value'}).to_dict('record'))

    return JsonResponse({
        'trend_data':trend_data,
        'query_top_data':query_top_data,
        'query_rising_data':query_rising_data
    })
