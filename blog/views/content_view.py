from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.template.defaultfilters import slugify
from ..forms import (
    AddCommentForm,
    AddPostForm,
)
from ..models import Post, Comment, Notification, ProfileSettings
from django.urls import reverse
import markdown
from markdown.extensions.toc import TocExtension
from django.contrib.auth.models import User


def get_comments(post):
    return post.comments.filter(parent__isnull=True)


def get_comment_form():
    return AddCommentForm()


def get_viewed_user(post):
    return get_object_or_404(User, username=post.user)


def get_user_profile(viewed_user):
    return ProfileSettings.objects.get_or_create(user=viewed_user)[0]


def is_liked(post, user):
    return post.like.filter(id=user.id).exists()


def get_parent_comment(request):
    parent_id = request.POST.get("parent-comment-id")
    parent_obj = None

    if parent_id:
        parent_obj = Comment.objects.get(id=parent_id)

    return parent_obj


def add_comment(post, user, parent_obj, comment_form):
    new_comment = comment_form.save(commit=False)
    new_comment.post = post
    new_comment.user = user
    new_comment.parent = parent_obj
    new_comment.save()

    if user != post.user:
        Notification.objects.create(
            receiver_user=post.user,
            provider_user=user,
            notification_type=Notification.COMMENT,
            post_name=post,
        )


def handle_like(post, user, liked):
    if liked:
        post.like.remove(user.id)
        Notification.objects.filter(
            provider_user=user, notification_type=Notification.LIKE
        ).delete()
    else:
        post.like.add(user.id)
        Notification.objects.create(
            receiver_user=post.user,
            provider_user=user,
            notification_type=Notification.LIKE,
            post_name=post,
        )


def get_markdown_content(post):
    md = markdown.Markdown(extensions=[TocExtension()])
    post_content = md.convert(post.content)
    toc = md.toc if len(md.toc_tokens) > 0 else None
    return post_content, toc


def post_details(request, slug):
    post = get_object_or_404(Post, slug=slug)
    comments = get_comments(post)
    comment_form = get_comment_form()
    user = request.user

    viewed_user = get_viewed_user(post)
    user_profile = get_user_profile(viewed_user)

    liked = is_liked(post, user)

    if request.method == "POST":
        comment_form = AddCommentForm(request.POST)

        if comment_form.is_valid():
            parent_obj = get_parent_comment(request)
            add_comment(post, user, parent_obj, comment_form)
            comment_form = get_comment_form()
        else:
            handle_like(post, user, liked)
            comment_form = get_comment_form()

        return redirect(reverse("blog:post_details", kwargs={"slug": post.slug}))

    post_content, toc = get_markdown_content(post)

    context = {
        "post": post,
        "comments": comments,
        "comment_form": comment_form,
        "liked": liked,
        "post_content": post_content,
        "toc": toc,
        "user_profile": user_profile,
        "redirect_url": reverse("blog:post_details", kwargs={"slug": post.slug}),
    }

    return render(request, "blog/post/post_details.html", context)


@login_required
def edit_comment(request, id):
    comment = get_object_or_404(Comment, pk=id)
    form = AddCommentForm(instance=comment)

    if request.method == "POST":
        form = AddCommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            post_slug = slugify(comment.post.title)
            url = reverse("blog:post_details", args=[post_slug])
            return redirect(url)

    context = {"form": form}
    return render(request, "blog/comment/edit_comment.html", context)


@login_required
def delete_comment(request, id):
    comment = get_object_or_404(Comment, pk=id)

    if request.method == "POST":
        # Looking for the notification that refers to the deleted comment
        notification = Notification.objects.filter(
            provider_user=request.user,
            notification_type=Notification.COMMENT,
            post_name=comment.post,
        ).first()

        # Checking if selected notification exists, then remove
        if notification:
            notification.delete()

        comment.delete()

        post_slug = slugify(comment.post.title)
        url = reverse("blog:post_details", args=[post_slug])
        return redirect(url)

    context = {"comment": comment}

    return render(request, "blog/comment/delete_comment.html", context)


@login_required
def create_post(request):
    form = AddPostForm()
    if request.method == "POST":
        form = AddPostForm(request.POST, request.FILES)
        if form.is_valid():
            created_post = form.save(commit=False)
            created_post.user = request.user
            created_post.save()
            url = reverse("blog:homepage")
            return redirect(url)

    context = {"form": form}
    return render(request, "blog/post/create_post.html", context)


@login_required
def delete_post(request, slug):
    post = get_object_or_404(Post, slug=slug)

    if request.method == "POST":
        post.delete()
        url = reverse("blog:homepage")
        return redirect(url)

    context = {"post": post}

    return render(request, "blog/post/delete_post.html", context)


@login_required
def edit_post(request, slug):
    post = get_object_or_404(Post, slug=slug)
    form = AddPostForm(instance=post)

    if request.method == "POST":
        form = AddPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            post_slug = slugify(post.title)
            url = reverse("blog:post_details", args=[post_slug])
            return redirect(url)

    context = {"form": form}
    return render(request, "blog/post/create_post.html", context)
