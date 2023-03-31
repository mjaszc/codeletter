from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase, Client
from django.contrib import auth
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core import mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from blog.tokens import account_activation_token
from blog.views.verification_view import send_verification_email, register_user


class VerifyEmailTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword",
            is_active=False,
        )
        self.token = account_activation_token.make_token(self.user)

    def test_verify_email_success(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        response = self.client.get(reverse("blog:verify_email", args=[uid, self.token]))
        self.assertRedirects(
            response, reverse("blog:login_user"), fetch_redirect_response=False
        )
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)

    def test_verify_email_invalid_link(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        response = self.client.get(
            reverse("blog:verify_email", args=[uid, "invalid-token"])
        )
        self.assertRedirects(response, reverse("blog:homepage"))
        self.assertIn(response.content, b"Activation link is invalid or expired.")
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)

    def test_verify_email_invalid_uid(self):
        uid = urlsafe_base64_encode(force_bytes(1234))
        response = self.client.get(reverse("blog:verify_email", args=[uid, self.token]))
        self.assertRedirects(response, reverse("blog:homepage"))
        self.assertIn(response.content, b"Activation link is invalid or expired.")
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)


class SendVerificationEmailTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword",
            is_active=False,
        )

    def test_send_verification_email_success(self):
        request = RequestFactory().get(reverse("blog:homepage"))
        setattr(request, "session", "session")
        messages = FallbackStorage(request)
        setattr(request, "_messages", messages)
        email_address = self.user.email
        send_verification_email(request, self.user, email_address)

        storage = messages
        stored_messages = list(storage)
        self.assertEqual(len(stored_messages), 1)
        expected_message = f"Success! Dear {self.user.username}, we have sent an activation link to {email_address}."
        self.assertEqual(str(stored_messages[0]), expected_message)


class RegisterUserTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_register_user_success(self):
        # Create a request object
        request = self.factory.post(
            reverse("blog:register_user"),
            {
                "username": "testuser",
                "first_name": "test",
                "last_name": "user",
                "email": "test@example.com",
                "password1": "testpassword",
                "password2": "testpassword",
            },
        )

        # Add session and messages attributes to the request
        request.session = {}
        setattr(request, "_messages", FallbackStorage(request))

        # Call the register_user view
        response = register_user(request)

        # Check the response
        self.assertEqual(response.status_code, 302)

        # Check that the user was created
        self.assertTrue(
            get_user_model().objects.filter(email="test@example.com").exists()
        )

        # Check that the message was added to the request
        storage = request._messages
        stored_messages = []
        for message in storage:
            stored_messages.append(message)

        self.assertEqual(len(stored_messages), 1)
        self.assertEqual(
            str(stored_messages[0]),
            "Success! Dear testuser, we have sent an activation link to test@example.com.",
        )

    def test_register_user_email_exists(self):
        # Create a user with the email address that will be used in the form
        get_user_model().objects.create_user(
            username="existinguser",
            email="test@example.com",
            password="existingpassword",
            is_active=True,
        )

        # Create a request object
        request = self.factory.post(
            reverse("blog:register_user"),
            {
                "username": "testuser",
                "first_name": "test",
                "last_name": "user",
                "email": "test@example.com",
                "password1": "testpassword",
                "password2": "testpassword",
            },
        )

        # Add session and messages attributes to the request
        request.session = {}
        setattr(request, "_messages", FallbackStorage(request))

        response = register_user(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "A user with that email already exists.")

        # Check that the user was not created
        self.assertFalse(get_user_model().objects.filter(username="testuser").exists())

        # Check that the message was added to the request
        storage = request._messages
        stored_messages = []
        for message in storage:
            stored_messages.append(message)

        self.assertEqual(len(stored_messages), 1)
        self.assertEqual(
            str(stored_messages[0]), "A user with that email already exists."
        )


class LoginTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username="testuser", email="testuser@example.com", password="testpassword"
        )

    def test_login_user_view_success(self):
        data = {
            "username": "testuser",
            "password": "testpassword",
        }

        response = self.client.post(reverse("blog:login_user"), data)

        self.client.login(username="testuser", password="testpassword")

        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated)

        self.assertEqual(response.status_code, 302)

    def test_login_user_view_failure(self):
        response = self.client.post(
            reverse("blog:login_user"),
            {"username": "nonexistentuser", "password": "wrongpass"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Incorrect username or password.")

    def test_log_out_user(self):
        response = self.client.post(
            reverse("blog:logout_user"),
            {"username": "testuser", "password": "testpassword"},
        )
        self.assertEqual(response.status_code, 302)
