from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from blog.tokens import account_activation_token
from django.core import mail
from blog.views.verification_view import send_verification_email
from django.test import RequestFactory
from django.contrib.messages.storage.fallback import FallbackStorage


class VerifyEmailTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword",
            is_active=False,
        )

        # Create a token for the user
        self.token = account_activation_token.make_token(self.user)

    def test_verify_email_success(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = account_activation_token.make_token(self.user)
        response = self.client.get(reverse("blog:verify_email", args=[uid, token]))
        self.assertRedirects(
            response, reverse("blog:login_user"), fetch_redirect_response=False
        )

        # Assert user is activated
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)

    def test_verify_email_invalid_link(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        response = self.client.get(
            reverse("blog:verify_email", args=[uid, "invalid-token"])
        )
        self.assertRedirects(response, reverse("blog:homepage"))
        self.assertIn(response.content, b"Activation link is invalid or expired.")

        # Assert user is not activated
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)

    def test_verify_email_invalid_uid(self):
        uid = urlsafe_base64_encode(force_bytes(1234))
        response = self.client.get(reverse("blog:verify_email", args=[uid, self.token]))
        self.assertRedirects(response, reverse("blog:homepage"))
        self.assertIn(response.content, b"Activation link is invalid or expired.")

        # Assert user is not activated
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

        # Check that the email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [email_address])
        self.assertIn("Activate your account", mail.outbox[0].subject)

        # Check that the message was added to the request
        storage = messages
        stored_messages = []
        for message in storage:
            stored_messages.append(message)

        self.assertEqual(len(stored_messages), 1)
        self.assertEqual(
            str(stored_messages[0]),
            f"Success! Dear {self.user.username}, we have sent an activation link to {email_address}.",
        )
