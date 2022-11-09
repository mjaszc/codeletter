from django.urls import path
from . import views


app_name = "blog"
urlpatterns = [
    path("", views.homepage, name="homepage"),
    path("<slug:slug>/", views.post_details, name="post_details"),
]
