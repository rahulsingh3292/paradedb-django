from datetime import datetime

from django.core.paginator import Paginator
from django.db import models
from django.shortcuts import render

from paradedb import aggregates
from paradedb.cast import ValueCast
from paradedb.lookups import LookupParameter

from .models import Product


def product_list_view(request):
    products = Product.objects.filter(id__all=True)

    # ------------------- FILTERS --------------------

    # Category filter
    category = request.GET.get("category")
    if category:
        products = products.filter(category=category)

    # Brand filter
    brand = request.GET.get("brand")
    if brand:
        products = products.filter(brand__in=brand.split(","))

    # Price range
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")

    def clean_price(price):
        if price:
            return int(price.replace(",", "").replace("₹", ""))
        return None

    if min_price:
        products = products.filter(selling_price__gte=clean_price(min_price))
    if max_price:
        products = products.filter(selling_price__lte=clean_price(max_price))

    # Rating
    min_rating = request.GET.get("min_rating")
    if min_rating:
        products = products.filter(average_rating__gte=min_rating)

    # Date range
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    if start_date or end_date:
        date_filter = [
            "daterange",
            start_date if start_date else None,
            end_date if end_date else None,
            "()",
        ]
        if start_date:
            date_filter[1] = datetime.strptime(start_date, "%Y-%m-%d")
        if end_date:
            date_filter[2] = datetime.strptime(end_date, "%Y-%m-%d")

        products = products.filter(
            created__pdb_range=LookupParameter(*date_filter, legacy=True)
        )

    for attr in request.GET.get("attr", "").split(","):
        if not attr:
            continue
        products = products.filter(product_details__contains=[{"key": attr}])

    search = request.GET.get("search")
    if search:
        products = products.filter(
            models.Q(title__match_v2=ValueCast(search, "pdb.ngram(1,2)"))
            | models.Q(description__pdb_search=search)
        )

    sort_by = request.GET.get("sort")
    if sort_by:
        if sort_by == "new":
            products = products.order_by("-created")
        elif sort_by == "old":
            products = products.order_by("created")
        elif sort_by == "price_asc":
            products = products.order_by("selling_price")
        elif sort_by == "price_desc":
            products = products.order_by("-selling_price")
        elif sort_by == "rating_desc":
            products = products.order_by("-average_rating")
        elif sort_by == "rating_asc":
            products = products.order_by("average_rating")

    counts = products.filter(id__all=True).aggregate(
        catgeory_counts=aggregates.Term("category", size=1000),
        brands=aggregates.Term("brand", size=1000),
        attributes=aggregates.Term("product_details.key", size=10000),
    )

    paginator = Paginator(products, 25)  # 25 items per page
    page = request.GET.get("page")
    products_page = paginator.get_page(page)

    context = {
        "products": products_page,
        "categories": counts["catgeory_counts"]["buckets"],
        "brands": counts["brands"]["buckets"],
        "attributes": counts["attributes"]["buckets"],
        "count": products.count(),
    }

    return render(
        request,
        "product_list.html",
        context,
    )
