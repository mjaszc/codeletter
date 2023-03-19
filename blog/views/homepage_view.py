from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.cache import cache
from blog.models import Post, Category
from django.urls import reverse
from django.http import QueryDict
from urllib.parse import urlencode


def homepage(request):
    # Retrieve the value of the 'q' parameter from the request's GET dictionary
    q = request.GET.get("q", "")

    # If the request method is POST, retrieve the value of the 'q' parameter
    # from the request's POST dictionary and redirect to a new URL that includes
    # the 'q' parameter as a query parameter in the URL
    if request.method == "POST":
        q = request.POST.get("q", "")
        query_params = {"q": q}
        query_string = urlencode(query_params)
        url = reverse("blog:homepage") + "?" + query_string
        return redirect(url)

    # Perform a search query using the 'q' parameter and retrieve a list of matching posts
    post_list = (
        Post.objects.filter(
            Q(title__icontains=q)
            | Q(content__icontains=q)
            | Q(category__name__icontains=q)
        )
        .prefetch_related()
        .order_by("-pub_date")
    )

    # Create a paginator object using the post_list and the number of items to display per page
    paginator = Paginator(post_list, 3)

    # Retrieve the current page of search results to display to the user
    page_num = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_num)

    # Create a context dictionary to pass to the template
    context = {
        "page_obj": page_obj,
        "q": q,
    }

    # If the 'q' parameter is not empty, add it as a query parameter to the pagination links
    if q:
        query_params = {"q": q}
        query_dict = QueryDict(mutable=True)
        query_dict.update(query_params)
        context["page_obj"].querystring = query_dict.urlencode()

    # Render the template with the context
    return render(request, "blog/homepage/homepage.html", context)


def categories_list(request):
    categories = Category.objects.select_related().order_by("id")[:20]

    return render(
        request, "blog/category/categories_list.html", {"categories": categories}
    )


def category_details(request, cat):
    category = cache.get(cat)
    if not category:
        try:
            category = Category.objects.get(name=cat)
        except Category.DoesNotExist:
            return HttpResponse("Category does not exist.")
        cache.set(cat, category)
    posts = Post.objects.filter(category=category)
    context = {"category": category, "posts": posts}
    return render(request, "blog/category/category_details.html", context)
