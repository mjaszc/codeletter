from django import forms
from .models import Post, Comment, ProfileSettings
from django.contrib.auth.forms import (
    SetPasswordForm,
    PasswordChangeForm,
    PasswordResetForm,
)
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class UserRegisterForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "rounded-md bg-white border",
                "placeholder": "Enter your username",
            }
        )
    )
    first_name = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "rounded-md", "placeholder": "Enter your first name"}
        )
    )
    last_name = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "rounded-md", "placeholder": "Enter your last name"}
        )
    )
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={"class": "rounded-md", "placeholder": "user@example.com"}
        )
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "rounded-md", "placeholder": "Create a password"}
        )
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "rounded-md", "placeholder": "Confirm your password"}
        )
    )

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        )


class AddPostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("title", "content", "image", "category")
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "rounded-md block w-96",
                }
            ),
            "content": forms.Textarea(
                attrs={
                    "class": "rounded-md resize w-full",
                }
            ),
            "category": forms.Select(
                attrs={
                    "class": "rounded-md",
                }
            ),
        }


class UserSettingsForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name")


class ProfileSettingsForm(forms.ModelForm):
    class Meta:
        model = ProfileSettings
        fields = (
            "image",
            "bio",
            "location",
            "twitter_url",
            "website_url",
            "linkedin_url",
        )


class AddCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("body",)
        widgets = {
            "body": forms.Textarea(
                attrs={
                    "class": "w-full h-32 text-lg border border-gray-400 p-4 resize-none overflow-auto md:w-3/4 lg:h-48",
                    "placeholder": "Write a comment...",
                }
            )
        }


class SetNewPasswordForm(SetPasswordForm):
    class Meta:
        model = get_user_model()
        fields = (
            "new_password1",
            "new_password2",
        )
