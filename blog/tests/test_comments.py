from django.test import Client, TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.template.defaultfilters import slugify

from blog.models import Comment, Post, Category


class AddCommentViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.category = Category.objects.create(name="Test Category")
        self.post = Post.objects.create(
            title="Test Post",
            content="Test content",
            user=self.user,
            category=self.category,
            slug="test-post",
        )
        self.url = reverse("blog:post_details", args=[self.post.slug])

    def test_adding_comment(self):
        self.client.login(username="testuser", password="testpassword")
        response = self.client.post(self.url, {"body": "Test comment content"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Comment.objects.count(), 1)
        comment = Comment.objects.first()
        self.assertEqual(comment.body, "Test comment content")
        self.assertEqual(comment.post, self.post)
        self.assertEqual(comment.user, self.user)
        self.assertIsNone(comment.parent)


class EditCommentViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.category = Category.objects.create(name="Test Category")
        self.post = Post.objects.create(
            title="Test Post",
            content="Test content",
            user=self.user,
            category=self.category,
        )
        self.comment = Comment.objects.create(
            post=self.post, user=self.user, body="Test comment content"
        )
        self.url = reverse("blog:edit_comment", kwargs={"id": self.comment.id})

    def test_edit_comment_view_uses_correct_template(self):
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "blog/comment/edit_comment.html")

    def test_edit_comment_view_redirects_to_post_detail_view_on_success(self):
        self.client.login(username="testuser", password="testpassword")
        response = self.client.post(
            self.url, {"body": "Updated test comment content"}, follow=True
        )
        post_slug = slugify(self.post.title)
        self.assertRedirects(
            response,
            reverse("blog:post_details", args=[post_slug]),
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )


class DeleteCommentViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.category = Category.objects.create(name="Test Category")
        self.post = Post.objects.create(
            title="Test Post",
            content="Test content",
            user=self.user,
            category=self.category,
        )
        self.comment = Comment.objects.create(
            post=self.post, user=self.user, body="Test comment content"
        )
        self.url = reverse("blog:delete_comment", kwargs={"id": self.comment.id})

    def test_delete_comment_view_uses_correct_template(self):
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "blog/comment/delete_comment.html")

    def test_delete_comment_view_redirects_to_post_detail_view_on_success(self):
        self.client.login(username="testuser", password="testpassword")
        response = self.client.post(self.url, follow=True)
        post_slug = slugify(self.post.title)
        self.assertRedirects(
            response,
            reverse("blog:post_details", args=[post_slug]),
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )

    def test_delete_comment_view_does_not_delete_comment_on_get_request(self):
        self.client.login(username="testuser", password="testpassword")
        self.client.get(self.url)
        self.assertTrue(Comment.objects.filter(id=self.comment.id).exists())

    def test_delete_comment_view_requires_authentication(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Comment.objects.filter(id=self.comment.id).exists())
