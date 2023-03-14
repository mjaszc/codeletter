from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render
from django.http import HttpResponse
from django.core.cache import cache
from ..models import Post, Category


def homepage(request):
    q = request.POST.get("q", "")

    post_list = (
        Post.objects.filter(Q(title__icontains=q) | Q(content__icontains=q))
        .prefetch_related()
        .order_by("-pub_date")
    )

    # number of posts per page
    paginator = Paginator(post_list, 2)

    page_obj = paginator.get_page(request.GET.get("page"))

    context = {"page_obj": page_obj}
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
