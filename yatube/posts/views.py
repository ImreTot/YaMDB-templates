from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post, User
from .utilities import post_paginator

POST_AMOUNT = 10


@cache_page(20, key_prefix='index_page')
def index(request):
    post_list = Post.objects.select_related()
    page_obj = post_paginator(post_list, request)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.group_posts.order_by('-pub_date')
    page_obj = post_paginator(post_list, request)
    context = {
        'page_obj': page_obj,
        'group': group,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    user_to_follow = User.objects.get(username=username)
    author_id = user_to_follow.id
    following = Follow.objects.filter(
        user_id=request.user.id,
        author_id=author_id
    ).exists()
    profile_data = author.posts.all()
    posts_count = profile_data.count()
    page_obj = post_paginator(profile_data, request)
    context = {
        'page_obj': page_obj,
        'posts_count': posts_count,
        'author': author,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    current_post = get_object_or_404(
        Post.objects.select_related('author', 'group'),
        id=post_id
    )
    author = current_post.author
    posts_count = author.posts.count()
    comments = Comment.objects.filter(post_id=post_id)
    form = CommentForm(request.POST or None)
    context = {
        'current_post': current_post,
        'posts_count': posts_count,
        'comments': comments,
        'form': form,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=request.user)
    form = PostForm()
    return render(
        request,
        'posts/post_create.html',
        {'form': form, 'is_edit': False}
    )


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id)
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    context = {
        'post': post,
        'form': form,
        'is_edit': True,
    }
    return render(
        request,
        'posts/post_create.html',
        context
    )


@login_required
def add_comment(request, post_id):
    post = Post.objects.get(id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    following_list = Follow.objects.filter(user_id=request.user)
    following_author_ids = following_list.values_list('author_id', flat=True)
    post_list = Post.objects.filter(
        author_id__in=following_author_ids).distinct()
    page_obj = post_paginator(post_list, request)
    context = {'page_obj': page_obj}
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    user_to_follow = User.objects.get(username=username)
    author_id = user_to_follow.id
    if author_id != request.user.id:
        Follow.objects.get_or_create(user=request.user, author_id=author_id)
    return redirect('posts:follow_index')


@login_required
def profile_unfollow(request, username):
    user_to_unfollow = User.objects.get(username=username)
    author_id = user_to_unfollow.id
    follow = Follow.objects.filter(user=request.user, author_id=author_id)
    if follow:
        follow.delete()
    return redirect('posts:follow_index')
