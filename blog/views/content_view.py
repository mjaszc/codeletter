from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.template.defaultfilters import slugify
from ..forms import (
    AddCommentForm,
    AddPostForm,
)
from ..models import Post, Comment, Notification


def post_details(request, slug):
    post = get_object_or_404(Post, slug=slug)
    comments = post.comments.filter(approve=True, parent__isnull=True)
    comment_form = AddCommentForm()
    liked = False

    if request.user.is_authenticated:
        user = request.user
        if post.like.filter(id=user.id).exists():
            liked = True

    if request.method == "POST":
        comment_form = AddCommentForm(request.POST)
        if comment_form.is_valid():
            parent_id = request.POST.get("parent_id", None)
            parent_obj = None
            if parent_id:
                parent_obj = Comment.objects.get(id=parent_id)

            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.user = user
            new_comment.parent = parent_obj
            new_comment.save()
            comment_form = AddCommentForm()
        else:
            if request.user.is_authenticated:
                if post.like.filter(id=user.id).exists():
                    post.like.remove(user.id)
                    liked = False
                    Notification.objects.filter(
                        provider_user=user, notification_type=Notification.LIKE
                    ).delete()
                else:
                    post.like.add(user.id)
                    liked = True
                    Notification.objects.create(
                        receiver_user=post.user,
                        provider_user=user,
                        notification_type=Notification.LIKE,
                        post_name=post,
                    )
            comment_form = AddCommentForm()

    post.views += 1
    post.save()

    context = {
        "post": post,
        "comments": comments,
        "comment_form": comment_form,
        "liked": liked,
    }
    return render(request, "blog/post_details.html", context)


@login_required
def edit_comment(request, id):
    comment = get_object_or_404(Comment, pk=id)
    form = AddCommentForm(instance=comment)

    if request.method == "POST":
        form = AddCommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            post_slug = slugify(comment.post.title)
            return redirect(f"/{post_slug}")

    context = {"form": form}
    return render(request, "blog/edit_comment.html", context)


@login_required
def delete_comment(request, id):
    comment = get_object_or_404(Comment, pk=id)

    if request.method == "POST":
        comment.delete()
        post_slug = slugify(comment.post.title)
        return redirect(f"/{post_slug}")

    context = {"comment": comment}

    return render(request, "blog/delete_comment.html", context)


@login_required
def create_post(request):
    if request.method == "POST":
        form = AddPostForm(request.POST, request.FILES)
        if form.is_valid():
            created_post = form.save(commit=False)
            created_post.user = request.user
            created_post.save()
            return redirect("/")
        else:
            form = AddPostForm()

    context = {"form": form}
    return render(request, "blog/create_post.html", context)


@login_required
def delete_post(request, slug):
    post = get_object_or_404(Post, slug=slug)

    if request.method == "POST":
        post.delete()
        return redirect("/")

    context = {"post": post}

    return render(request, "blog/delete_post.html", context)


@login_required
def edit_post(request, slug):
    post = get_object_or_404(Post, slug=slug)
    form = AddPostForm(instance=post)

    if request.method == "POST":
        form = AddPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect(post.get_absolute_url())

    context = {"form": form}
    return render(request, "blog/create_post.html", context)
