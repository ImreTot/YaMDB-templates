from django import forms
from django.forms import Textarea

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        widgets = {
            'text': Textarea(attrs={'cols': 80, 'rows': 20}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text', )
        widgets = {
            'text': Textarea(),
        }
