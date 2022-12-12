from django.shortcuts import render, redirect, get_object_or_404
from .models import Post, Category, ProfileSettings
from django.core.cache import cache
from django.http import HttpResponse
from .forms import AddPostForm, AddCommentForm, ProfileSettingsForm
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.core.paginator import Paginator
from .forms import UserSettingsForm
from django.db.models import Q


def homepage(request):
    q = request.POST.get("q") if request.POST.get("q") is not None else ""

    lookup = Q(title__icontains=q) | Q(content__icontains=q)
    posts = Post.objects.filter(lookup)

    post_list = Post.objects.prefetch_related().order_by("-pub_date")
    # number of posts per page
    paginator = Paginator(post_list, 2)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {"posts": posts, "page_obj": page_obj}
    return render(request, "blog/homepage.html", context)


def categories_list(request):
    categories = Category.objects.select_related().order_by("id")[:20]

    context = {"categories": categories}

    return render(request, "blog/categories_list.html", context)


def category_details(request, cat):
    category = Category.objects.filter(name=cat)
    posts = Post.objects.filter(category__name=cat)

    if cache.get(cat):
        categ = cache.get(cat)
    else:
        categ = Category.objects.get(name=cat)
        cache.set(cat, categ)

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
    post = Post.objects.filter(slug=slug)

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
    form = UserSettingsForm(instance=request.user)

    if request.method == "POST":
        form = UserSettingsForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("/")

    context = {"form": form}
    return render(request, "blog/settings_user.html", context)


def profile_settings_user(request):
    user = ProfileSettings.objects.filter(user=request.user).first()

    # if user enters for the first time to the Profile Settings
    # this function is automatically creates form for to fill
    if not user:
        user = ProfileSettings.objects.create(user=request.user)

    form = ProfileSettingsForm(instance=user)

    if request.method == "POST":
        form = ProfileSettingsForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect("/")

    context = {"form": form}
    return render(request, "blog/settings_profile.html", context)


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
