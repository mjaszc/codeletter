from django.urls import path

from .views import content_view, user_view, verification_view, homepage_view


app_name = "blog"
urlpatterns = [
    # HOMEPAGE URLS
    path("", homepage_view.homepage, name="homepage"),
    path("category/", homepage_view.categories_list, name="categories_list"),
    path(
        "category/<str:cat>/", homepage_view.category_details, name="category_details"
    ),
    #
    # VERIFICATION URLS
    path("register/", verification_view.register_user, name="register_user"),
    path(
        "verify/<uidb64>/<token>", verification_view.verify_email, name="verify_email"
    ),
    path("login/", verification_view.login_user, name="login_user"),
    path("logout/", verification_view.logout_user, name="logout_user"),
    #
    #
    # USER URLS
    path("settings/", user_view.settings_user, name="settings_user"),
    path(
        "notifications/",
        user_view.notifications,
        name="notifications",
    ),
    path("profile-settings/", user_view.profile_settings_user, name="profile_settings"),
    path("dashboard/", user_view.profile_dashboard, name="profile_dashboard"),
    path("change-password/", user_view.change_password, name="change_password"),
    path("recover", user_view.recover_password_request, name="recover_password"),
    path(
        "recover/<uidb64>/<token>",
        user_view.recover_password_confirm,
        name="recover_password_confirm",
    ),
    #
    # CONTENT URLS
    path("create-post/", content_view.create_post, name="create_post"),
    path("<slug:slug>/edit-post/", content_view.edit_post, name="edit_post"),
    path("<slug:slug>/delete-post/", content_view.delete_post, name="delete_post"),
    path("<int:id>/edit-comment", content_view.edit_comment, name="edit_comment"),
    path("<int:id>/delete-comment", content_view.delete_comment, name="delete_comment"),
    path("<slug:slug>/", content_view.post_details, name="post_details"),
    #
]
