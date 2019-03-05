"""main URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import include
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from app.views import intro, discover, searched, brand_detail, analysis, me, BrandListView, db_update, gtrend, sharing, brands, identities, wc


urlpatterns = [
    path('admin/', admin.site.urls),

    # path('users/', include('users.urls')),
    path('accounts/', include('allauth.urls')),
    # path('users/', include('django.contrib.auth.urls')),

    # path('login/', login, name='login'),
    # path('logout/', logout, name='logout'),
    # path('auth/', include('social_django.urls', namespace='social')),


    path('', discover, name='home'),
    path('discover/', discover),
    #path('searched/', searched),
    path('searched/', BrandListView.as_view()),
    #path('rating/', rating),
    path('db_update/<category>/', db_update),
    path('rating/', BrandListView.as_view()),
    path('brands/', brands),
    path('brands/<bname>/', brand_detail),
    # path('brand/<brand_name>/interest/trend/', interest_trend, name='interest_trend'),
    path('brands/<brand_name>/gtrend/', gtrend, name='gtrend'),
    path('brands/<bname>/identities/', identities, name='identities'),

    path('analysis/', analysis),
    path('me/', me),
    path('sharing/', sharing),

    path('wc/<bname>/', wc),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
