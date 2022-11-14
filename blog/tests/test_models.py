from django.test import TestCase
from blog.models import Post


class TestModels(TestCase):
    def test_post_title(self):
        title = Post.objects.create(title="Test title")
        self.assertEqual(str(title), "Test title")
