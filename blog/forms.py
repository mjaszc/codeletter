from django import forms
from .models import Post
from django.contrib.auth.models import AbstractUser


class AddPostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("title", "content")


class UserSettingsForm(forms.ModelForm):
    class Meta:
        model = AbstractUser
        fields = ("username", "email", "first_name", "last_name")
