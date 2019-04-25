from django.contrib import admin
from app.models import Brand, Profile, Option, Post
# from custom_user.admin import EmailUserAdmin
# from .models import MyUser

# Register your models here.

# class MyUserAdmin(EmailUserAdmin):
#     """
#     You can customize the interface of your model here.
#     """
#     # model = MyUser
#     # list_display = ['email','is_staff', 'date_of_birth']
#     pass
#
# admin.site.register(MyUser, MyUserAdmin)
# Register your models here.

admin.site.register(Brand)
admin.site.register(Profile)
admin.site.register(Option)
admin.site.register(Post)
