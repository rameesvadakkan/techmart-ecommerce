from django.shortcuts import render, get_object_or_404, redirect
from .models import Category, Product
from .models import ProductRating
from .forms import RatingForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg
from django.core.paginator import Paginator


def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()

    # BASE QUERY
    products = Product.objects.filter(available=True)

    # -------- CATEGORY FILTER --------
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    # -------- PRICE FILTER --------
    min_price = request.GET.get("min")
    max_price = request.GET.get("max")

    if min_price:
        products = products.filter(price__gte=min_price)

    if max_price:
        products = products.filter(price__lte=max_price)

    # -------- SORTING --------
    sort_by = request.GET.get("sort")

    if sort_by == "low":
        products = products.order_by("price")
    elif sort_by == "high":
        products = products.order_by("-price")
    elif sort_by == "new":
        products = products.order_by("-id")
    elif sort_by == "rating":
        products = products.annotate(
            avg_rating=Avg("ratings__rating")
        ).order_by("-avg_rating")

    # -------- PAGINATION (LAST) --------
    paginator = Paginator(products, 6)  # 6 items per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "products/product_list.html", {
        "category": category,
        "categories": categories,
        "products": page_obj,
        "page_obj": page_obj,
    })

    
def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, available=True)
    return render(request, 'products/product_detail.html', {'product': product})

@login_required
def add_rating(request, slug):
    product = get_object_or_404(Product, slug=slug)

    try:
        existing = ProductRating.objects.get(product=product, user=request.user)
    except ProductRating.DoesNotExist:
        existing = None

    if request.method == "POST":
        form = RatingForm(request.POST, instance=existing)
        if form.is_valid():
            rating_obj = form.save(commit=False)
            rating_obj.product = product
            rating_obj.user = request.user
            rating_obj.save()
            messages.success(request, "Rating submitted!")
            return redirect('product_detail', slug=slug)
    else:
        form = RatingForm(instance=existing)

    return render(request, "products/add_rating.html", {"form": form, "product": product})

def search(request):
    query = request.GET.get('q', '')

    results = Product.objects.filter(
        Q(name__icontains=query) |
        Q(description__icontains=query) |
        Q(category__name__icontains=query)
    )

    context = {
        'query': query,
        'results': results,
    }

    return render(request, 'products/search.html', context)