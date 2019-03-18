from django import template
# from django.core.files.storage import default_storage
from app.models import Brand
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
