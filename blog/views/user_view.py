from django.contrib import messages
from django.contrib.auth import (
    get_user_model,
    update_session_auth_hash,
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.db.models import Count
from django.shortcuts import redirect, render, get_object_or_404
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from blog.forms import (
    UserPasswordResetForm,
    ProfileSettingsForm,
    SetNewPasswordForm,
    UserSettingsForm,
)
from blog.models import Comment, Notification, Post, ProfileSettings
from blog.tokens import account_activation_token
from django.urls import reverse
from django.contrib.auth.models import User


@login_required
def user_settings(request):
    user = request.user
    form = UserSettingsForm(instance=user)
    if request.method == "POST":
        form = UserSettingsForm(request.POST, instance=user)

        if form.is_valid():
            form.save()
            url = reverse("blog:homepage")
            return redirect(url)

    context = {"form": form}
    return render(request, "blog/user_profile/settings_user.html", context)


@login_required
def profile_settings(request):
    user_profile = ProfileSettings.objects.get_or_create(user=request.user)[0]
    form = ProfileSettingsForm(instance=user_profile)

    if request.method == "POST":
        form = ProfileSettingsForm(
            request.POST, request.FILES, instance=user_profile)

        if form.is_valid():
            form.save()
            url = reverse("blog:homepage")
            return redirect(url)

    context = {"form": form}
    return render(request, "blog/user_profile/settings_profile.html", context)


def recover_password_request(request):
    if request.method == "POST":
        form = UserPasswordResetForm(request.POST)
        if form.is_valid():
            user_email = form.cleaned_data.get("email")
            user = get_user_model().objects.filter(email=user_email).first()
            if user:
                subject = "Password Reset Request"
                content = render_to_string(
                    "blog/email_message/message_recover_password.html",
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

        url = reverse("blog:homepage")
        return redirect(url)

    form = UserPasswordResetForm()
    context = {"form": form}
    return render(request, "blog/password/recover_password.html", context)


def recover_password_confirm(request, uidb64, token):
    User = get_user_model()

    home_url = reverse("blog:homepage")

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
                return redirect(home_url)
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)

        form = SetNewPasswordForm(user)
        context = {"form": form}
        return render(request, "blog/password/recover_password_confirm.html", context)
    else:
        messages.error(request, "Link is expired.")

    return redirect(home_url)


@login_required
def change_password(request):
    form = PasswordChangeForm(request.user)
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Your password has been changed")
            url = reverse("blog:homepage")
            return redirect(url)
        else:
            messages.error(request, form.errors.values())

    return render(request, "blog/password/change_password.html", {"form": form})


def get_notifications(request):
    unread_notifications = Notification.objects.filter(
        receiver_user=request.user, is_seen=False)
    read_notifications = Notification.objects.filter(
        receiver_user=request.user, is_seen=True)
    notifications = list(unread_notifications) + list(read_notifications)

    context = {"notifications": notifications}
    return render(request, "blog/user_profile/notifications.html", context)


def mark_notification_as_read(request, notification_id):
    notification = get_object_or_404(
        Notification, notification_id=notification_id)

    # Check if the notification is for the current user and the post exists
    if notification.receiver_user == request.user and notification.post_name:
        # Update the status of the notification to is_read=True
        notification.is_seen = True
        notification.save()
        return redirect("blog:notifications")
    else:
        return messages.error(
            request,
            "Notification does not exist or you are not authorized to access it.",
        )


def profile_dashboard(request, username):
    viewed_user = get_object_or_404(User, username=username)

    user_profile = ProfileSettings.objects.get_or_create(user=viewed_user)[0]

    posts = Post.objects.filter(user=viewed_user)
    posts_count = posts.count()

    comments = Comment.objects.filter(post__in=posts)
    comments_count = comments.count()

    likes_count = 0
    for post in posts:
        likes_count += post.like.count()

    most_liked_posts = (
        posts.annotate(like_count=Count("like"))
        .order_by("-like_count")
        .prefetch_related("like")[:3]
    )

    most_commented_posts = (
        posts.annotate(comment_count=Count("comments"))
        .order_by("-comment_count")
        .prefetch_related("comments")[:3]
    )

    most_viewed_posts = posts.annotate(view_count=Count("views")).order_by(
        "-view_count"
    )[:3]

    return render(
        request,
        "blog/user_profile/profile_dashboard.html",
        {
            "user_profile": user_profile,
            "posts_count": posts_count,
            "comments_count": comments_count,
            "likes_count": likes_count,
            "most_liked_posts": most_liked_posts,
            "most_commented_posts": most_commented_posts,
            "most_viewed_posts": most_viewed_posts,
        },
    )
