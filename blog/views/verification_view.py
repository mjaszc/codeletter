from django.contrib import messages
from django.contrib.auth import (
    authenticate,
    get_user_model,
    login,
    logout,
)
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.utils.http import urlsafe_base64_decode
from ..forms import (
    UserRegisterForm,
)
from blog.tokens import account_activation_token
from django.urls import reverse
from blog.tasks import send_verification_email_task


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
        return redirect(reverse("blog:login_user"))
    else:
        messages.error(request, "Activation link is invalid or expired.")
        return redirect("/")


# Function is called when user submits the register form with selected parameters
def send_verification_email(request, user, email_address):
    domain = get_current_site(request).domain
    protocol = "https" if request.is_secure() else "http"

    send_verification_email_task.delay(user.id, email_address, domain, protocol)

    messages.success(
        request,
        f"Success! Dear {user.username}, we have sent an activation link to {email_address}.",
    )


def register_user(request):
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
                return redirect(reverse("blog:homepage"))
            else:
                messages.error(request, "A user with that email already exists.")

    context = {"form": form}
    return render(request, "blog/homepage/register_user.html", context)


def login_user(request):
    if request.method == "POST":
        username = request.POST.get("username", "").lower()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect(reverse("blog:homepage"))
        else:
            messages.error(request, "Incorrect username or password.")

    return render(request, "blog/homepage/login_user.html")


def logout_user(request):
    logout(request)
    return redirect("/")
