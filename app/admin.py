from django.contrib import admin
from app.models import Brand, Profile, Option, Post, Hashtag, Feed, CommentBrand, CommentPost, CustomEmailUser#, Page
from custom_user.admin import EmailUserAdmin
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


# class ProfileAdmin(EmailUserAdmin):
#     pass

class FeedAdmin(admin.ModelAdmin):
    # raw_id_fields = ('hashtags', 'membership', 'author', )
    raw_id_fields = ('hashtags', 'author', )
    readonly_fields = ('timestamp',)


admin.site.register(Brand)
admin.site.register(Profile)
admin.site.register(Option)
admin.site.register(Post)
admin.site.register(CommentBrand)
admin.site.register(CommentPost)
admin.site.register(Hashtag)
# admin.site.register(Page)
admin.site.register(Feed, FeedAdmin)

admin.site.register(CustomEmailUser)
