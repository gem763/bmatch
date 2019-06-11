from django import forms
from .models import Post, CommentPost, CommentBrand

class PostForm(forms.ModelForm):
    # content = forms.CharField(max_length=500, widget=forms.Textarea(attrs={'style':'background:yellow;'}))

    class Meta:
        model = Post
        fields = ('image', 'content', 'hashtags', )


class CommentPostForm(forms.ModelForm):
    class Meta:
        model = CommentPost
        fields = ('content', )
