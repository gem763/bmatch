from django import forms
from .models import Post, CommentPost, CommentBrand

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('image', 'content', 'hashtags', )


class CommentPostForm(forms.ModelForm):
    class Meta:
        model = CommentPost
        fields = ('content', )
