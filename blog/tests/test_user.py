from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.contrib.auth.models import User
from blog.views.user_view import recover_password_request
from django.core import mail
from django.contrib.auth import get_user_model
from django.contrib.messages.storage.fallback import FallbackStorage
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from blog.tokens import account_activation_token
from django.contrib.messages import get_messages
from django.contrib.auth.hashers import make_password, check_password
from blog.models import Post, Comment, Category
from blog.models import ProfileSettings


class UserSettingsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpassword",
            first_name="Test",
            last_name="User",
        )
        self.client.login(username="testuser", password="testpassword")

    def test_user_settings_view_uses_correct_template(self):
        response = self.client.get(reverse("blog:settings_user"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/settings_user.html")

    def test_change_email(self):
        response = self.client.post(
            reverse("blog:settings_user"),
            {
                "email": "newemail@example.com",
                "username": "testuser",
                "first_name": "Test",
                "last_name": "User",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "newemail@example.com")

    def test_change_first_name(self):
        response = self.client.post(
            reverse("blog:settings_user"),
            {
                "first_name": "New",
                "email": "newemail@example.com",
                "username": "testuser",
                "last_name": "User",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "New")

    def test_change_last_name(self):
        response = self.client.post(
            reverse("blog:settings_user"),
            {
                "last_name": "New",
                "email": "newemail@example.com",
                "username": "testuser",
                "first_name": "Test",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.last_name, "New")

    def test_change_username(self):
        response = self.client.post(
            reverse("blog:settings_user"),
            {
                "email": "testuser@example.com",
                "username": "Newuser",
                "first_name": "Test",
                "last_name": "User",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "Newuser")

    def test_change_everything(self):
        response = self.client.post(
            reverse("blog:settings_user"),
            {
                "email": "newemail@example.com",
                "first_name": "New",
                "last_name": "User",
                "username": "Newuser",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "newemail@example.com")
        self.assertEqual(self.user.first_name, "New")
        self.assertEqual(self.user.last_name, "User")
        self.assertEqual(self.user.username, "Newuser")


class ProfileSettingsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.login(username="testuser", password="testpass")
        self.url = reverse("blog:profile_settings")

    def test_profile_settings_view_uses_correct_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "blog/settings_profile.html")

    def test_profile_settings_view_post(self):
        form_data = {
            "bio": "Test bio",
            "location": "Test location",
            "twitter_url": "https://twitter.com/testuser",
            "website_url": "https://www.testuser.com",
            "linkedin_url": "https://www.linkedin.com/in/testuser",
        }

        # Post the form data
        response = self.client.post(self.url, form_data, follow=True)

        # Check that the form is valid and the user profile is updated
        user_profile = ProfileSettings.objects.get(user=self.user)
        self.assertTrue(response.status_code, 302)
        self.assertEqual(user_profile.bio, "Test bio")
        self.assertEqual(user_profile.location, "Test location")
        self.assertEqual(user_profile.twitter_url, "https://twitter.com/testuser")
        self.assertEqual(user_profile.website_url, "https://www.testuser.com")
        self.assertEqual(
            user_profile.linkedin_url, "https://www.linkedin.com/in/testuser"
        )


class RecoverPasswordRequestTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_recover_password_view_uses_correct_template(self):
        response = self.client.get(reverse("blog:recover_password"))
        self.assertTemplateUsed(response, "blog/recover_password.html")

    def test_recover_password_request_valid_email(self):
        user = get_user_model().objects.create_user(
            username="testuser", email="test@example.com", password="testpassword"
        )

        request = self.factory.post(
            reverse("blog:recover_password"),
            {"email": user.email},
        )

        # Add session and messages attributes to the request
        request.session = {}
        setattr(request, "_messages", FallbackStorage(request))

        response = recover_password_request(request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("blog:homepage"))

        # Check that the password reset email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Password Reset Request")

    def test_recover_password_request_invalid_email(self):
        request = self.factory.post(
            reverse("blog:recover_password"),
            {"email": "invalid@example.com"},
        )

        # Add session and messages attributes to the request
        request.session = {}
        setattr(request, "_messages", FallbackStorage(request))

        response = recover_password_request(request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("blog:homepage"))

        # Check that no password reset email was sent
        self.assertEqual(len(mail.outbox), 0)

        # Check that the error message was added to the request
        storage = request._messages
        stored_messages = []
        for message in storage:
            stored_messages.append(message)

        self.assertEqual(len(stored_messages), 1)
        self.assertEqual(
            str(stored_messages[0]),
            "No account exists with the given email address.",
        )


class RecoverPasswordConfirmTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create(
            username="testuser",
            email="testuser@example.com",
            password=make_password("testpass"),
        )
        self.token = account_activation_token.make_token(self.user)
        self.uid = urlsafe_base64_encode(force_bytes(self.user.pk))

    def test_invalid_uidb64(self):
        url = reverse(
            "blog:recover_password_confirm",
            kwargs={"uidb64": "invalid_uidb64", "token": self.token},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("blog:homepage"))

    def test_invalid_token(self):
        url = reverse(
            "blog:recover_password_confirm",
            kwargs={"uidb64": self.uid, "token": "invalid_token"},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("blog:homepage"))

    def test_recover_password_confirm_with_valid_data(self):
        url = reverse(
            "blog:recover_password_confirm",
            kwargs={"uidb64": self.uid, "token": self.token},
        )
        data = {
            "new_password1": "new_password",
            "new_password2": "new_password",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("blog:homepage"))
        self.assertTrue(
            get_user_model().objects.get(pk=self.user.pk).check_password("new_password")
        )

        # check if success message is displayed
        storage = get_messages(response.wsgi_request)
        messages = [str(message) for message in storage]
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            messages[0], "Password reset successfully. You can now log in."
        )

    def test_recover_password_confirm_with_invalid_data(self):
        url = reverse(
            "blog:recover_password_confirm",
            kwargs={"uidb64": self.uid, "token": self.token},
        )
        data = {
            "new_password1": "new_password",
            "new_password2": "not_matching_password",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/recover_password_confirm.html")
        self.assertContains(response, "The two password fields didn’t match.")


class ChangePasswordTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="testuser@test.com", password="testpass"
        )
        self.url = reverse("blog:change_password")
        self.client = Client()

    def test_get_change_password_page(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/change_password.html")
        self.assertIsNotNone(response.context["form"])
        self.client.logout()

    def test_change_password_successfully(self):
        self.client.login(username="testuser", password="testpass")
        data = {
            "old_password": "testpass",
            "new_password1": "new_password",
            "new_password2": "new_password",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("blog:homepage"))
        self.user.refresh_from_db()
        self.assertTrue(check_password("new_password", self.user.password))
        self.client.logout()


class ProfileDashboardTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.user1 = User.objects.create_user(username="testuser1", password="testpass")
        self.client.login(username="testuser", password="testpass")
        self.category = Category.objects.create(name="Test Category")
        self.post1 = Post.objects.create(
            title="Test post 1",
            content="Test content 1",
            user=self.user,
            category=self.category,
            views=2,
        )
        self.post2 = Post.objects.create(
            title="Test post 2",
            content="Test content 2",
            user=self.user,
            category=self.category,
            views=1,
        )
        self.post3 = Post.objects.create(
            title="Test post 3",
            content="Test content 3",
            user=self.user,
            category=self.category,
            views=3,
        )

        self.comment1 = Comment.objects.create(
            body="Test comment 1", user=self.user1, post=self.post1, approve=True
        )
        self.comment2 = Comment.objects.create(
            body="Test comment 2", user=self.user1, post=self.post1, approve=True
        )
        self.comment3 = Comment.objects.create(
            body="Test comment 3", user=self.user, post=self.post2, approve=False
        )
        self.comment4 = Comment.objects.create(
            body="Test comment 4", user=self.user, post=self.post2, approve=False
        )
        self.comment5 = Comment.objects.create(
            body="Test comment 5", user=self.user, post=self.post2, approve=False
        )
        self.comment6 = Comment.objects.create(
            body="Test comment 6", user=self.user, post=self.post3, approve=False
        )

        self.post1.like.set([self.user1])
        self.post2.like.set([self.user])
        self.post2.like.set([self.user1])

        user_profile = ProfileSettings.objects.get_or_create(user=self.user)[0]
        user_profile.save()

    def test_profile_dashboard_view(self):
        response = self.client.get(reverse("blog:profile_dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test post 1")
        self.assertContains(response, "Test post 2")
        self.assertContains(response, "Test post 3")
        self.assertContains(response, "Posts written")
        self.assertContains(response, "Comments count")
        self.assertContains(response, "Likes count")

    def test_profile_dashboard_view_most_liked_posts(self):
        response = self.client.get(reverse("blog:profile_dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context["most_liked_posts"],
            ["<Post: Test post 2>", "<Post: Test post 1>", "<Post: Test post 3>"],
            ordered=False,
        )

    def test_profile_dashboard_view_most_viewed_posts(self):
        response = self.client.get(reverse("blog:profile_dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context["most_viewed_posts"],
            ["<Post: Test post 3>", "<Post: Test post 1>", "<Post: Test post 2>"],
            ordered=False,
        )
