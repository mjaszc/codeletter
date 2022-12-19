from django import forms
from .models import Post, Comment, ProfileSettings
from django.contrib.auth.forms import (
    PasswordChangeForm,
    SetPasswordForm,
    PasswordResetForm,
)
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser, User
from django.contrib.auth.forms import UserCreationForm


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=25)
    last_name = forms.CharField(max_length=25)

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


class UserSettingsForm(forms.ModelForm):
    class Meta:
        model = AbstractUser
        fields = ("username", "email", "first_name", "last_name")


class ProfileSettingsForm(forms.ModelForm):
    class Meta:
        model = ProfileSettings
        fields = (
            "profile_image",
            "bio",
            "location",
            "twitter_url",
            "website_url",
            "instagram_url",
            "linked_in_url",
        )


class AddCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("body",)


class SetNewPasswordForm(SetPasswordForm):
    class Meta:
        model = get_user_model()
        fields = (
            "new_password1",
            "new_password2",
        )
