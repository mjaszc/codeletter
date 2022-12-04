from django.shortcuts import render, redirect, get_object_or_404
from .models import Post, Category
from django.core.cache import cache
from django.http import HttpResponse
from .forms import AddPostForm, AddCommentForm
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from .forms import UserSettingsForm
from django.db.models import Q


def homepage(request):
    q = request.POST.get("q") if request.POST.get("q") is not None else ""

    lookup = (
        Q(title__icontains=q) | Q(content__icontains=q) | Q(category__name__icontains=q)
    )
    posts = Post.objects.filter(lookup)

    context = {"posts": posts}
    return render(request, "blog/homepage.html", context)


def categories_list(request):
    categories = Category.objects.all()

    context = {"categories": categories}

    return render(request, "blog/categories_list.html", context)


def category_details(request, cat):
    category = Category.objects.filter(name=cat)
    posts = Post.objects.filter(category__name=cat)

    if cache.get(cat):
        categ = cache.get(cat)
        print("hit the cache")
    else:
        categ = Category.objects.get(name=cat)
        cache.set(cat, categ)
        print("hit the db")

    if category.exists():
        category = category
        posts = posts
    else:
        return HttpResponse("Something went wrong.")

    context = {"category": category, "posts": posts}
    return render(request, "blog/category_details.html", context)


def post_details(request, slug):
    post = Post.objects.filter(slug=slug)
    get_post = get_object_or_404(Post, slug=slug)

    if post.exists():
        post = post[0]
    else:
        return HttpResponse("Page not found")

    comments = post.comments.filter(approve=True)
    user = request.user
    new_comment = None
    comment_form = AddCommentForm()
    liked = None

    # when user enters the details section
    # this function checks if user already liked the post
    if request.user.is_authenticated:
        user = request.user

        if get_post.like.filter(id=user.id).exists():
            liked = True

    if request.method == "POST":
        comment_form = AddCommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            # when submitted, crucial info that helps trace the comment is saved
            new_comment.post = get_post
            new_comment.user = user
            new_comment.save()
            comment_form = AddCommentForm()
        else:
            if request.user.is_authenticated:
                # when user clicks the like button
                if get_post.like.filter(id=user.id).exists():
                    get_post.like.remove(user.id)
                    liked = False
                else:
                    get_post.like.add(user.id)
                    liked = True
            comment_form = AddCommentForm()

    context = {
        "post": post,
        "comments": comments,
        "new_commment": new_comment,
        "comment_form": comment_form,
        "liked": liked,
    }
    return render(request, "blog/post_details.html", context)


def create_post(request):
    form = AddPostForm()

    if request.method == "POST":
        form = AddPostForm(request.POST, request.FILES)
        if form.is_valid():
            created_post = form.save(commit=False)
            created_post.user = request.user
            created_post.save()
            return redirect("/")

    context = {"form": form}
    return render(request, "blog/create_post.html", context)


def delete_post(request, slug):
    post = Post.objects.filter(slug=slug)[0]

    if request.method == "POST":
        post.delete()
        return redirect("/")
    context = {"post": post}

    return render(request, "blog/delete_post.html", context)


def edit_post(request, slug):
    post = Post.objects.filter(slug=slug)[0]
    form = AddPostForm(instance=post)

    if request.method == "POST":
        form = AddPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect("/")

    context = {"form": form}
    return render(request, "blog/create_post.html", context)


def register_user(request):
    form = UserCreationForm()
    context = {"form": form}

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect("/")
        else:
            return HttpResponse("Something went wrong, please try again")

    return render(request, "blog/register_user.html", context)


def login_user(request):
    if request.method == "POST":
        username = request.POST["username"].lower()
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("/")
        else:
            return HttpResponse("Something went wrong.")

    else:
        return render(request, "blog/login_user.html")


def settings_user(request):
    if request.method == "POST":
        form = UserSettingsForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("/")
    else:
        form = UserSettingsForm(instance=request.user)
        context = {"form": form}
        return render(request, "blog/settings_user.html", context)


def logout_user(request):
    logout(request)
    return redirect("/")


def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect("/")
        else:
            return HttpResponse("Something went wrong, try again.")
    else:
        form = PasswordChangeForm(request.user)

    context = {"form": form}
    return render(request, "blog/change_password.html", context)
