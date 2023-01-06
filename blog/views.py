from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.sites.shortcuts import get_current_site
from django.contrib import messages
from .models import Post, Category, ProfileSettings, Notification
from django.contrib.auth.models import User
from django.core.cache import cache
from django.http import HttpResponse
from .forms import (
    AddPostForm,
    AddCommentForm,
    ProfileSettingsForm,
    UserRegisterForm,
    SetNewPasswordForm,
    PasswordResetForm,
)
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import (
    login,
    authenticate,
    logout,
    update_session_auth_hash,
    get_user_model,
)
from django.core.paginator import Paginator
from .forms import UserSettingsForm
from django.db.models import Q
from .tokens import account_activation_token
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage


from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from datetime import datetime


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
                    # deleting notification for user when user unlike the post
                    if Notification.objects.filter(
                        provider_user=request.user, notification_type=Notification.LIKE
                    ).exists():
                        Notification.objects.filter(
                            provider_user=request.user,
                            notification_type=Notification.LIKE,
                        ).delete()
                else:
                    get_post.like.add(user.id)
                    liked = True

                    # creating notification for user
                    notification = Notification.objects.create(
                        receiver_user=get_post.user,
                        provider_user=user,
                        notification_type=Notification.LIKE,
                        post_name=Post.objects.get(title=get_post.title),
                    )
                    notification.save()

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


# Account verification process
def verify_email(request, uidb64, token):
    User = get_user_model()
    try:
        # Decoding uid and assigning to user's primary key
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    # Checking if token is valid and if user exists and activating account
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        messages.success(
            request,
            "Thank you for your email confirmation. Now you can login your account.",
        )
        return redirect("/login")
    else:
        messages.error(request, "Activation link is invalid or expired.")

    return redirect("/")


# Function is called when user submits the register form with selected parameters
def send_verify_email(request, user, email_address):
    message_subject = "Activate your account"
    message_content = render_to_string(
        "blog/message_verify_account.html",
        {
            "user": user.username,
            "domain": get_current_site(request).domain,
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "token": account_activation_token.make_token(user),
            "protocol": "https" if request.is_secure() else "http",
        },
    )
    # Specifying parameters for sending an verification email
    email = EmailMessage(message_subject, message_content, to=[email_address])

    if email.send():
        messages.success(
            request,
            f"Success! Dear {user}, we send activation link to the {email_address}. To complete registration please follow the instruction\
        given in the email message. NOTE: Check the SPAM folder.",
        )
    else:
        messages.error(
            request, f"There's a problem with sending email to {email_address}."
        )


def register_user(request):
    form = UserRegisterForm()

    if request.method == "POST":
        form = UserRegisterForm(request.POST)

        if form.is_valid():
            if (
                User.objects.filter(email=form.cleaned_data.get("email")).exists()
                is False
            ):
                user = form.save(commit=False)
                user.username = user.username.lower()
                # Setting the inactive user in order to set status to active after account verification
                user.is_active = False
                user.save()
                send_verify_email(request, user, form.cleaned_data.get("email"))
                return redirect("/")
            else:
                messages.error(request, "User with that email already exists.")

    context = {"form": form}
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


def recover_password_request(request):
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            user_email = form.cleaned_data.get("email")
            get_user = get_user_model().objects.filter(email=user_email).first()
            if get_user:
                message_subject = "Password Reset Request"
                message_content = render_to_string(
                    "blog/message_recover_password.html",
                    {
                        "user": get_user,
                        "domain": get_current_site(request).domain,
                        "uid": urlsafe_base64_encode(force_bytes(get_user.pk)),
                        "token": account_activation_token.make_token(get_user),
                        "protocol": "https" if request.is_secure() else "http",
                    },
                )
                email = EmailMessage(
                    message_subject, message_content, to=[get_user.email]
                )
                if email.send():
                    messages.success(
                        request,
                        """
                        Password reset sent
                        We've emailed you instructions for setting your password, if an account exists with the email you entered. 
                        You should receive them shortly.If you don't receive an email, please make sure you've entered the address
                        you registered with, and check your spam folder.
                        """,
                    )
                else:
                    messages.error(
                        request,
                        "Something went wrong, it might be server error.",
                    )
            else:
                messages.error(
                    request,
                    "Problem with resetting password, email does not exist in our database.",
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
    except (TypeError, ValueError, OverflowError, user.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        if request.method == "POST":
            form = SetNewPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(
                    request,
                    "Your password has been set. You may go ahead and log in now.",
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


def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Your password has been changed")
            return redirect("/")
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)
    else:
        form = PasswordChangeForm(request.user)

    context = {"form": form}
    return render(request, "blog/change_password.html", context)


def notifications(request):
    notifications = Notification.objects.filter(receiver_user=request.user)

    context = {"notifications": notifications}
    return render(request, "blog/notifications.html", context)
