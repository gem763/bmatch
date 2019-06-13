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


# @register.filter
# def liked(user, brand):
#     profile = Profile.objects.get(user__email=user.email)
#     return (brand.name in profile.get_likes2())

@register.filter
def likes_this(user, what):
    profile = Profile.objects.get(user__email=user.email)
    type = what.__class__.__name__.lower()
    likes = profile.get_likes(type)
    return (what in likes)


@register.filter
def post_likes_howmany(what):
    pass
    # print(what.post_likes_set.all())
