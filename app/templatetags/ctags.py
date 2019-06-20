from django import template
# from django.core.files.storage import default_storage
from app.models import Brand, Profile
register = template.Library()

@register.filter#(name='file_exists')
def file_exists(filepath):
    if default_storage.exists(filepath):
        print(default_storage)
        return filepath

    else:
        return None


@register.filter
def of_name(namepair):
    # print(type(namepair))
    return Brand.objects.filter(name__in=namepair)


@register.filter
def of_name2(bname):
    return Brand.objects.get(name=bname)

# @register.filter
# def likes_this(user, what):
#     profile = Profile.objects.get(user__email=user.email)
#     type = what.__class__.__name__.lower()
#     likes = profile.get_likes(type)
#     return (what in likes)


@register.filter
def like_this(user, obj):
    profile = Profile.objects.get(user__email=user.email)
    return profile.like_this(obj)

@register.filter
def bookmark_this(user, obj):
    profile = Profile.objects.get(user__email=user.email)
    return profile.bookmark_this(obj)

@register.filter
def post_likes_howmany(what):
    pass
    # print(what.post_likes_set.all())
