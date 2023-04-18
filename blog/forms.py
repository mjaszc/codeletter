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
            attrs={"class": "rounded-md",
                   "placeholder": "Enter your first name"}
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
            attrs={"class": "rounded-md",
                   "placeholder": "Confirm your password"}
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
            "image": forms.FileInput(
                attrs={
                    "class": "bg-white border ",
                }
            ),
        }


class UserSettingsForm(forms.ModelForm):
    first_name = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "rounded-md",
                   "placeholder": "Enter your first name"}
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

    class Meta:
        model = User
        fields = ("email", "first_name", "last_name")


class ProfileSettingsForm(forms.ModelForm):
    image = forms.FileField(
        widget=forms.FileInput(
            attrs={
                "class": "bg-white border mt-2",
            }
        ),
        required=False,
    )

    bio = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "rounded-md mt-2",
                "placeholder": "Enter your profile description",
            }
        ),
        required=False,
    )

    location = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "rounded-md mt-2",
                   "placeholder": "Enter your location"}
        ),
        required=False,
    )

    twitter_url = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "rounded-md mt-2",
                   "placeholder": "Enter your Twitter URL"}
        ),
        required=False,
    )

    website_url = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "rounded-md mt-2",
                   "placeholder": "Enter your Website URL"}
        ),
        required=False,
    )

    linkedin_url = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "rounded-md mt-2",
                   "placeholder": "Enter your LinkedIn URL"}
        ),
        required=False,
    )

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
                    "class": "w-full h-32 text-lg rounded-md p-4 resize-y overflow-auto md:w-3/4 lg:h-48",
                    "placeholder": "Write a comment...",
                }
            )
        }


class SetNewPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "rounded-md", "placeholder": "Type your password...", })
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "rounded-md", "placeholder": "Confirm your password", })
    )

    class Meta:
        model = get_user_model()
        fields = (
            "new_password1",
            "new_password2",
        )


class UserPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={"class": "rounded-md", "placeholder": "user@example.com"}
        )
    )
