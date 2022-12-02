from django.test import TestCase
from blog.models import Post, Category


class TestModels(TestCase):
    def test_post_title(self):
        category = Category.objects.create()
        title = Post.objects.create(
            title="Test title",
            content="Hello this is post title",
            image="image.svg",
            category=category,
        )
        self.assertEqual(str(title), "Test title")
