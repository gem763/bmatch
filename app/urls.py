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
    path('discover/', v.discover, name='discover'),
    # path('library/', v.library, name='library'),
    # path('searched/', v.BrandListView.as_view()),
    # path('db_update/<category>/', v.db_update),
    path('rating/', v.RatingView.as_view(), name='rating'),
    path('myfavorite/', v.myfavorite, name='myfavorite'),
    path('brands/<bname>/', v.brand_detail, name='brand_detail'),
    path('brands/<bname>/identity/', v.identity, name='identity'),
    # path('brand/<brand_name>/interest/trend/', interest_trend, name='interest_trend'),
    path('brands/<brand_name>/gtrend/', v.gtrend, name='gtrend'),
    path('search_helper/', v.search_helper, name='search_helper'),
    # path('bnames/', v.bnames, name='bnames'),
    #path('brands/<bname>/identities/', identities, name='identities'),

    path('journey/<str:words>/', v.journey, name='journey'),
    path('pages/', v.pages, name='pages'),
    path('page/<str:pname>/', v.page, name='page'),
    # path('feed_blocks/<str:keywords>/', v.feed_blocks, name='feed_blocks'),
    # path('feed_block/<int:feed_id>/', v.feed_block, name='feed_block'),

    path('me/', v.me, name='me'),

    path('profiling/', v.profiling, name='profiling'),
    path('save_worldcup/', v.SaveWorldcupView.as_view(), name='save_worldcup'),
    # path('save_like/', v.SaveLikeView.as_view(), name='save_like'),

    path('level_test/', v.level_test, name='level_test'),
    path('update_likes/', v.UpdateLikesView.as_view(), name='update_likes'),
    path('update_myfavorite/', v.UpdateMyfavoriteView.as_view(), name='update_myfavorite'),
    path('actions/', v.ActionsView.as_view(), name='actions'),

    path('posts/', v.posts, name='posts'),
    # path('posts/sub/', v.posts_sub, name='posts_sub'),
    path('posts/newpost/', v.newpost, name='newpost'),
    path('posts/<int:pk>/', v.post_detail, name='post_detail'),
    path('posts/<int:pk>/edit/', v.editpost, name='editpost'),
    path('posts/<int:pk>/delete/', v.deletepost, name='deletepost'),
    path('posts/<int:pk>/commenting/', v.commenting_post, name='commenting_post'),
    path('commentpost_actions/', v.CommentPostActionsView.as_view(), name='commentpost_actions'),

    path('blocks/', v.blocks, name='blocks'),
    # path('search/<qry>/', v.search, name='search'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
