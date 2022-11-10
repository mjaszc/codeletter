from django.urls import path
from . import views


app_name = "blog"
urlpatterns = [
    path("", views.homepage, name="homepage"),
    path("create-post/", views.create_post, name="create_post"),
    path("register/", views.register_user, name="register_user"),
    path("<slug:slug>/", views.post_details, name="post_details"),
    path("edit-post/<slug:slug>/", views.edit_post, name="edit_post"),
    path("delete-post/<slug:slug>/", views.delete_post, name="delete_post"),
]
