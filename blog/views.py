from django.contrib import messages
from django.contrib.auth import (
    authenticate,
    get_user_model,
    login,
    logout,
    update_session_auth_hash,
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.mail import EmailMessage
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.defaultfilters import slugify
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from .forms import (
    AddCommentForm,
    AddPostForm,
    PasswordResetForm,
    ProfileSettingsForm,
    SetNewPasswordForm,
    UserRegisterForm,
    UserSettingsForm,
)
from .models import Category, Comment, Notification, Post, ProfileSettings
from .tokens import account_activation_token


def homepage(request):
    q = request.POST.get("q", "")

    post_list = (
        Post.objects.filter(Q(title__icontains=q) | Q(content__icontains=q))
        .prefetch_related()
        .order_by("-pub_date")
    )

    # number of posts per page
    paginator = Paginator(post_list, 2)

    page_obj = paginator.get_page(request.GET.get("page"))

    context = {"page_obj": page_obj}
    return render(request, "blog/homepage.html", context)


def categories_list(request):
    categories = Category.objects.select_related().order_by("id")[:20]

    return render(request, "blog/categories_list.html", {"categories": categories})


def category_details(request, cat):
    category = cache.get(cat)
    if not category:
        category = Category.objects.get(name=cat)
        cache.set(cat, category)
        posts = Post.objects.filter(category=category)
    if not posts:
        return HttpResponse("Category does not exist.")

    context = {"category": category, "posts": posts}
    return render(request, "blog/category_details.html", context)


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


# Account verification process
def verify_email(request, uidb64, token):
    User = get_user_model()
    # Decode the uid and assign it to the user's primary key
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        messages.error(request, "Activation link is invalid or expired.")
        return redirect("/")

    # Check if the token is valid and if the user exists and activate the account
    if account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(
            request,
            "Thank you for your email confirmation. You can now log in to your account.",
        )
        return redirect("/login")
    else:
        messages.error(request, "Activation link is invalid or expired.")
        return redirect("/")


# Function is called when user submits the register form with selected parameters
def send_verification_email(request, user, email_address):
    message_subject = "Activate your account"
    message_content = render_to_string(
        "blog/message_verify_account.html",
        {
            "user": user.username,
            "domain": get_current_site(request).domain,
            "uid": urlsafe_base64_encode(force_bytes(user.pk)).decode(),
            "token": account_activation_token.make_token(user),
            "protocol": "https" if request.is_secure() else "http",
        },
    )
    # Specify parameters for sending a verification email
    email = EmailMessage(message_subject, message_content, to=[email_address])
    success = email.send()

    if success:
        messages.success(
            request,
            f"Success! Dear {user.username}, we have sent an activation link to {email_address}.",
        )
    else:
        messages.error(
            request, f"There was a problem sending an email to {email_address}."
        )


def register(request):
    form = UserRegisterForm()

    if request.method == "POST":
        form = UserRegisterForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data.get("email")

            if not User.objects.filter(email=email).exists():
                user = form.save(commit=False)
                user.username = user.username.lower()
                user.is_active = False
                user.save()
                send_verification_email(request, user, email)
                return redirect("/")
            else:
                messages.error(request, "A user with that email already exists.")

    context = {"form": form}
    return render(request, "blog/register_user.html", context)


def login_user(request):
    if request.method == "POST":
        username = request.POST.get("username", "").lower()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("/")
        else:
            messages.error(request, "Incorrect username or password.")

    return render(request, "blog/login_user.html")


@login_required
def settings_user(request):
    user = request.user
    if request.method == "POST":
        form = UserSettingsForm(request.POST, instance=user)

        if form.is_valid():
            form.save()
            return redirect("/")
        else:
            form = UserSettingsForm(instance=user)

    context = {"form": form}
    return render(request, "blog/settings_user.html", context)


@login_required
def profile_settings_user(request):
    user_profile = ProfileSettings.objects.get_or_create(user=request.user)[0]
    form = ProfileSettingsForm(instance=user_profile)

    if request.method == "POST":
        form = ProfileSettingsForm(request.POST, request.FILES, instance=user_profile)

        if form.is_valid():
            form.save()
            return redirect("/")

    context = {"form": form}
    return render(request, "blog/settings_profile.html", context)


def logout_user(request):
    logout(request)
    return redirect("/")


@login_required
def recover_password_request(request):
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            user_email = form.cleaned_data.get("email")
            user = get_user_model().objects.filter(email=user_email).first()
            if user:
                subject = "Password Reset Request"
                content = render_to_string(
                    "blog/message_recover_password.html",
                    {
                        "user": user,
                        "domain": get_current_site(request).domain,
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "token": account_activation_token.make_token(user),
                        "protocol": "https" if request.is_secure() else "http",
                    },
                )
                email = EmailMessage(subject, content, to=[user.email])
                if email.send():
                    messages.success(
                        request,
                        "Password reset instructions sent. Please check your email.",
                    )
                else:
                    messages.error(
                        request,
                        "Something went wrong, it might be a server error.",
                    )
            else:
                messages.error(
                    request,
                    "No account exists with the given email address.",
                )

        return redirect("/")

    form = PasswordResetForm()
    context = {"form": form}
    return render(request, "blog/recover_password.html", context)


def recover_password_confirm(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and account_activation_token.check_token(user, token):
        if request.method == "POST":
            form = SetNewPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(
                    request,
                    "Password reset successfully. You can now log in.",
                )
                return redirect("/")
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)

        form = SetNewPasswordForm(user)
        context = {"form": form}
        return render(request, "blog/recover_password_confirm.html", context)
    else:
        messages.error(request, "Link is expired.")

    messages.error(request, "Something went wrong")
    return redirect("/")


@login_required
def change_password(request):
    form = PasswordChangeForm(request.user)
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Your password has been changed")
            return redirect("/")
        else:
            messages.error(request, form.errors.values())

    return render(request, "blog/change_password.html", {"form": form})


def notifications(request):
    notifications = Notification.objects.filter(receiver_user=request.user)

    # checking all unread notifications as a read after leaving notifications section
    if not request.GET.get("notifications"):
        Notification.objects.filter(receiver_user=request.user).update(is_seen=True)

    context = {"notifications": notifications}
    return render(request, "blog/notifications.html", context)


@login_required
def profile_dashboard(request):
    current_user = request.user

    # Count the posts written by the logged in user
    posts = Post.objects.filter(user=current_user)
    posts_count = posts.count()

    # Count added comments written by users under
    # the posts that were created by currently logged in user
    comments = (
        Comment.objects.filter(post__in=posts)
        .exclude(user=current_user)
        .filter(approve=True)
    )
    comments_count = comments.count()

    # Count all of the likes under the posts that were created by currently logged in user
    likes_count = 0
    for post in posts:
        likes_count += post.like.count()

    # Display most liked posts
    posts = Post.objects.filter(user=current_user)
    most_liked_posts = (
        posts.annotate(like_count=Count("like"))
        .order_by("-like_count")
        .prefetch_related("like")[:3]
    )

    # Count added comments written by other users on
    # the posts created by the currently logged in user
    comments = Comment.objects.filter(post__in=posts).exclude(user=current_user)
    comments_count = comments.count()

    # Display most commented posts
    posts = Post.objects.filter(user=current_user)

    most_commented_posts = (
        posts.annotate(comment_count=Count("comments"))
        .exclude(comments__user=current_user)
        .order_by("-comment_count")
        .prefetch_related("comments")[:3]
    )

    # Display most viewed posts
    most_viewed_posts = posts.annotate(view_count=Count("views")).order_by(
        "-view_count"
    )[:3]

    return render(
        request,
        "blog/profile_dashboard.html",
        {
            "posts_count": posts_count,
            "comments_count": comments_count,
            "likes_count": likes_count,
            "most_liked_posts": most_liked_posts,
            "most_commented_posts": most_commented_posts,
            "most_viewed_posts": most_viewed_posts,
        },
    )
