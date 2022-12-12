from django import forms
from .models import Post, Comment, ProfileSettings
from django.contrib.auth.models import AbstractUser


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
