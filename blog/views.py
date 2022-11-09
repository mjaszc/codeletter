from django.shortcuts import render
from .models import Post
from django.http import HttpResponse
from django.shortcuts import get_object_or_404


def homepage(request):
    posts = Post.objects.all()
    context = {"posts": posts}
    return render(request, "blog/homepage.html", context)


def post_details(request, slug):
    post = Post.objects.filter(slug=slug)

    if post.exists():
        post = post[0]
    else:
        return HttpResponse("Page not found")

    context = {"post": post}
    return render(request, "blog/post_details.html", context)
