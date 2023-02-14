from django.contrib.auth.models import User
from django.urls import reverse
from django.test import Client, TestCase
from django.template.defaultfilters import slugify

from blog.models import Post, Category


class CreatePostTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="password")
        self.client.login(username="testuser", password="password")
        self.category = Category.objects.create(name="Test Category")

    def test_create_post_view_uses_correct_template(self):
        self.client.login(username="testuser", password="password")
        response = self.client.get(reverse("blog:create_post"))
        self.assertTemplateUsed(response, "blog/create_post.html")

    def test_create_post_view_redirect_to_homepage_after_creating_post(self):
        data = {
            "title": "Test Post",
            "content": "This is a test post",
            "category": self.category.id,
        }

        response = self.client.post(reverse("blog:create_post"), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/")
        self.assertEqual(Post.objects.count(), 1)
        post = Post.objects.first()
        self.assertEqual(post.title, "Test Post")
        self.assertEqual(post.content, "This is a test post")
        self.assertEqual(post.user, self.user)


class DeletePostTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="password")
        self.client.login(username="testuser", password="password")
        self.category = Category.objects.create(name="Test Category")
        self.post = Post.objects.create(
            title="Test post",
            content="This is a test post",
            user=self.user,
            category=self.category,
        )

    def test_delete_post_view_uses_correct_template(self):
        response = self.client.get(
            reverse("blog:delete_post", kwargs={"slug": self.post.slug})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/delete_post.html")

    def test_delete_post_view_redirect_to_homepage_after_delete(self):
        response = self.client.post(
            reverse("blog:delete_post", kwargs={"slug": self.post.slug})
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/")
        self.assertEqual(Post.objects.count(), 0)


class EditPostTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="password")
        self.category = Category.objects.create(name="Test Category")
        self.client.login(username="testuser", password="password")
        self.edit_category = Category.objects.create(name="Edited Category")
        self.post = Post.objects.create(
            title="Test Post",
            content="This is a test post",
            category=self.category,
            user=self.user,
        )

    def test_edit_post_view_uses_correct_template(self):
        slug = slugify(self.post.title)
        response = self.client.get(reverse("blog:edit_post", args=[slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/create_post.html")

    def test_edit_post_view_redirect_to_post_details_after_editing(self):
        data = {
            "title": "Edited Test Post",
            "content": "This is an edited test post",
            "category": self.edit_category.id,
        }

        post_slug = slugify(self.post.title)
        response = self.client.post(reverse("blog:edit_post", args=[post_slug]), data)

        post = Post.objects.get(title=data["title"])
        new_post_slug = slugify(post.title)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            reverse("blog:post_details", args=[new_post_slug]),
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )
        self.assertEqual(post.title, "Edited Test Post")
        self.assertEqual(post.content, "This is an edited test post")
        self.assertEqual(post.user, self.user)
