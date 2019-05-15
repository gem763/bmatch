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
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views as v


urlpatterns = [
    # path('users/', include('users.urls')),
    path('accounts/', include('allauth.urls')),
    # path('users/', include('django.contrib.auth.urls')),

    # path('login/', login, name='login'),
    # path('logout/', logout, name='logout'),
    # path('auth/', include('social_django.urls', namespace='social')),


    path('', v.home, name='home'),
    path('discover/', v.DiscoverView.as_view(), name='discover'),
    path('library/', v.DiscoverView.as_view(template_name='app/discover_20190514.html'), name='library'),
    # path('discover/', discover),
    #path('searched/', searched),
    path('searched/', v.BrandListView.as_view()),
    #path('rating/', rating),
    path('db_update/<category>/', v.db_update),
    # path('rating/', v.rating),
    path('rating/', v.RatingView.as_view(), name='rating'),
    path('brands/<bname>/', v.brand_detail, name='brand_detail'),
    path('brands/<bname>/identity/', v.identity, name='identity'),
    # path('brand/<brand_name>/interest/trend/', interest_trend, name='interest_trend'),
    path('brands/<brand_name>/gtrend/', v.gtrend, name='gtrend'),
    path('search_helper/', v.search_helper, name='search_helper'),
    # path('bnames/', v.bnames, name='bnames'),
    #path('brands/<bname>/identities/', identities, name='identities'),

    path('analysis/', v.analysis),
    path('me/', v.me, name='me'),
    path('sharing/', v.sharing, name='sharing'),

    path('profiling/', v.profiling, name='profiling'),
    path('save_worldcup/', v.SaveWorldcupView.as_view(), name='save_worldcup'),
    path('save_like/', v.SaveLikeView.as_view(), name='save_like'),

    path('posts/', v.posts, name='posts'),
    path('posts/all/', v.posts_all, name='posts_all'),
    path('posts/posting/', v.posting, name='posting'),
    path('posts/detail/<pk>/', v.post_detail, name='post_detail'),
    path('posts/detail/<pk>/commenting/', v.commenting_post, name='commenting_post'),
    path('commentpost_actions/', v.CommentPostActionsView.as_view(), name='commentpost_actions'),

    # path('search/<qry>/', v.search, name='search'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
