from blog.models import Post, User, Category
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm

client = Client()


class TestForms(TestCase):
    def setup(self):
        self.user = User.objects.create_user(
            username="usertest500", password="yhwkWuQQ_94_yTTop."
        )

        login = self.client.login(username="usertest500", password="yhwkWuQQ_94_yTTop.")

        Post.objects.create(
            title="Test post",
            content="This is test post",
            slug="test-post",
            image="image.svg",
            category=Category.objects.create(),
        )

        self.assertTrue(login)

    def test_comment_form(self):
        TestForms.setup(self)

        post = Post.objects.get(slug="test-post")

        data = {"body": "This is test comment"}

        response = self.client.post(
            reverse("blog:post_details", args=(post.slug,)), data
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name="blog/post_details.html")

    def test_add_post_form(self):
        TestForms.setup(self)

        category = Category.objects.create()

        data = {
            "title": "Testing post",
            "content": "This is post content",
            "image": "image.jpg",
            "slug": "testing-post",
            "category_id": category,
        }

        response = self.client.post(reverse("blog:create_post"), data)
        self.assertEqual(response.status_code, 302)

    def test_edit_post_url(self):
        TestForms.setup(self)

        post = Post.objects.get(slug="test-post")

        response = self.client.get(
            reverse("blog:edit_post", kwargs={"slug": post.slug})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name="blog/create_post.html")

    def test_edit_post_form(self):
        TestForms.setup(self)

        post = Post.objects.get(slug="test-post")

        data = {
            "title": "Edited post",
            "content": "This is edited post",
            "slug": "edited-post",
        }

        response = self.client.post(
            reverse("blog:edit_post", kwargs={"slug": post.slug}), data
        )
        self.assertEqual(response.status_code, 302)

    def test_delete_post_url(self):
        TestForms.setup(self)

        post = Post.objects.get(slug="test-post")

        data = {
            "title": "Test post",
            "content": "This is test post",
            "slug": "test-post",
        }

        response = self.client.get(
            reverse("blog:delete_post", kwargs={"slug": post.slug}), data
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name="blog/delete_post.html")

    def test_delete_post_from_profile(self):
        TestForms.setup(self)

        post = Post.objects.get(slug="test-post")

        data = {
            "title": "Test post",
            "content": "This is test post",
            "slug": "test-post",
        }

        response = self.client.post(
            reverse("blog:delete_post", kwargs={"slug": post.slug}), data
        )
        self.assertEqual(response.status_code, 302)

    def test_user_sign_up_success(self):
        data = {
            "username": "testuser50124",
            "password1": 'Oo4[RpEI3k4Bf8Oo"bUl%_w0',
            "password2": 'Oo4[RpEI3k4Bf8Oo"bUl%_w0',
        }
        response = self.client.post(reverse("blog:register_user"), data)

        self.assertEqual(response.status_code, 302)

        users = get_user_model().objects.all()
        self.assertEqual(users.count(), 1)

    def test_user_sign_up_failed(self):
        data = {
            "username": "testuser1",
            "password1": "password123",
            "password2": "password321",
        }

        response = self.client.post(reverse("blog:register_user"), data)
        self.assertEqual(response.status_code, 200)

    def test_user_settings_url(self):
        self.user = User.objects.create_user(
            username="testuser12_qOo15", password="yh%_WuQQ_94_yTTop."
        )

        login = self.client.login(
            username="testuser12_qOo15", password="yh%_WuQQ_94_yTTop."
        )

        self.assertTrue(login)

        response = self.client.get(reverse("blog:settings_user"))
        self.assertEqual(response.status_code, 200)

    def test_user_settings_form(self):
        TestForms.setup(self)

        data = {
            "username": "user_is_testing_555",
            "email": "hello_admin@example.com",
            "first_name": "john",
            "last_name": "doe",
        }

        response = self.client.post(reverse("blog:settings_user"), data)
        self.assertEqual(response.status_code, 302)

    def test_change_password_url(self):
        TestForms.setup(self)

        response = self.client.get(reverse("blog:change_password"))
        self.assertEqual(response.status_code, 200)

    def test_change_password_form(self):
        self.user = User.objects.create_user(
            username="testuser12_qOo15", password="yh%_WuQQ_94_yTTop."
        )

        login = self.client.login(
            username="testuser12_qOo15", password="yh%_WuQQ_94_yTTop."
        )

        self.assertTrue(login)

        user = User.objects.get(username="testuser12_qOo15")
        data = {
            "old_password": "yh%_WuQQ_94_yTTop.",
            "new_password1": 'Oo4[RpEI3k4Bf8Oo"bUl%_w0',
            "new_password2": 'Oo4[RpEI3k4Bf8Oo"bUl%_w0',
        }

        form = PasswordChangeForm(user, data)
        self.assertTrue(form.is_valid())
        form.save(commit=False)

        response = self.client.post(reverse("blog:change_password"), data)
        self.assertEqual(response.status_code, 302)
