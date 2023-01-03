from django.urls import path
from . import views


app_name = "blog"
urlpatterns = [
    path("", views.homepage, name="homepage"),
    path("create-post/", views.create_post, name="create_post"),
    path("category/", views.categories_list, name="categories_list"),
    path("category/<str:cat>/", views.category_details, name="category_details"),
    path("register/", views.register_user, name="register_user"),
    path("verify/<uidb64>/<token>", views.verify_email, name="verify_email"),
    path("login/", views.login_user, name="login_user"),
    path("recover", views.recover_password_request, name="recover_password"),
    path(
        "recover/<uidb64>/<token>",
        views.recover_password_confirm,
        name="recover_password_confirm",
    ),
    path("logout/", views.logout_user, name="logout_user"),
    path("settings/", views.settings_user, name="settings_user"),
    path("profile-settings/", views.profile_settings_user, name="profile_settings"),
    path("notifications/", views.notifications, name="notifications"),
    path("change-password/", views.change_password, name="change_password"),
    path("<slug:slug>/", views.post_details, name="post_details"),
    path("<slug:slug>/edit-post/", views.edit_post, name="edit_post"),
    path("<slug:slug>/delete-post/", views.delete_post, name="delete_post"),
]
