from django.test import RequestFactory, TestCase, Client
from django.contrib.auth.models import User
from django.shortcuts import reverse
from django.core.cache import cache
from blog.views.homepage_view import category_details

from blog.models import Post, Category


class HomepageTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.category = Category.objects.create(name="Test Category")
        self.post1 = Post.objects.create(
            title="Test Post 1",
            content="This is a test post",
            user=self.user,
            category=self.category,
        )
        self.post2 = Post.objects.create(
            title="Test Post 2",
            content="This is another test post",
            user=self.user,
            category=self.category,
        )
        self.post3 = Post.objects.create(
            title="Test Post 3",
            content="Yet another test post",
            user=self.user,
            category=self.category,
        )

    def test_homepage_view(self):
        response = self.client.get(reverse("blog:homepage"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/homepage.html")

    def test_search_title(self):
        response = self.client.post(reverse("blog:homepage"), {"q": "Test Post 1"})
        self.assertEqual(len(response.context["page_obj"]), 1)
        self.assertEqual(response.context["page_obj"][0], self.post1)

    def test_search_no_results(self):
        response = self.client.post(reverse("blog:homepage"), {"q": "no results"})
        self.assertEqual(len(response.context["page_obj"]), 0)

    # Add tests for the pagination and search by tags


class CategoriesListViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        Category.objects.create(name="category 1")
        Category.objects.create(name="category 2")
        Category.objects.create(name="category 3")

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse("blog:categories_list"))
        self.assertTemplateUsed(response, "blog/categories_list.html")

    def test_view_displays_categories_in_id_order(self):
        response = self.client.get(reverse("blog:categories_list"))
        categories = response.context["categories"]
        self.assertEqual(categories[0].name, "category 1")
        self.assertEqual(categories[1].name, "category 2")
        self.assertEqual(categories[2].name, "category 3")


class CategoryDetailsViewTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="test_user", email="test@example.com", password="secret"
        )
        self.category = Category.objects.create(name="Test Category")
        self.post = Post.objects.create(
            title="Test post",
            content="Test content",
            user=self.user,
            category=self.category,
        )

    def test_category_details_view(self):
        request = self.factory.get(
            reverse("blog:category_details", args=[self.category.name])
        )
        request.user = self.user

        response = category_details(request, self.category.name)

        self.assertContains(response, self.category.name)
        self.assertContains(response, self.post.title)

    def test_category_details_view_with_cache(self):
        # Set the cache for the category
        cache.set(self.category.name, self.category)

        # Request to the view with cache
        request = self.factory.get(
            reverse("blog:category_details", args=[self.category.name])
        )
        request.user = self.user

        response = category_details(request, self.category.name)

        self.assertContains(response, self.category.name)
        self.assertContains(response, self.post.title)

    def test_category_details_view_not_found(self):
        # Request to the view with non-existing category
        request = self.factory.get(
            reverse("blog:category_details", args=["nonexisting"])
        )
        request.user = self.user

        response = category_details(request, "nonexisting")

        # Check if response returns HttpResponse with the message "Category does not exist."
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"Category does not exist.")
