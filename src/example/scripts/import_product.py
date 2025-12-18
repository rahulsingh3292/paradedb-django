import json
from datetime import datetime

from ecommerce.models import Product

from django.db import transaction


def import_products_from_json(file_path: str):
    """
    Import product JSON objects from a file into the Product table using bulk_create.
    """

    # --------------------
    # Load JSON
    # --------------------
    with open(file_path, "r") as f:
        data = json.load(f)

    # Allow both single object & list
    if isinstance(data, dict):
        data = [data]

    products = []

    for item in data:
        crawled_at_val = item.get("crawled_at")
        if crawled_at_val:
            try:
                crawled_at = datetime.strptime(crawled_at_val, "%d/%m/%Y, %H:%M:%S")
            except ValueError:
                crawled_at = None
        else:
            crawled_at = None

        discount = [
            d for d in item.get("discount", "").split("%") if d.strip().isdigit()
        ]
        if discount:
            item["discount"] = float(discount[0])

        selling_price = (
            item.get("selling_price", "").replace("₹", "").replace(",", "").strip()
        )
        if selling_price.isdigit():
            item["selling_price"] = int(selling_price)

        actual_price = (
            item.get("actual_price", "").replace("₹", "").replace(",", "").strip()
        )
        if actual_price.isdigit():
            item["actual_price"] = int(actual_price)
        else:
            item["actual_price"] = item.get("selling_price", 0) or 0

        product_details = []
        for detail in item.get("product_details", []):
            for key, value in detail.items():
                product_details.append({"key": key, "value": value})

        product = Product(
            id=item["_id"],
            title=item.get("title", "No Title"),
            brand=item.get("brand", "Unknown"),
            category=item.get("category", "Unknown"),
            sub_category=item.get("sub_category", "Unknown"),
            description=item.get("description", ""),
            actual_price=item.get("actual_price", 0) or 1,
            selling_price=item.get("selling_price", 0) or 1,
            discount=float(item.get("discount")) if item.get("discount") else 0,
            average_rating=(
                float(item.get("average_rating")) if item.get("average_rating") else 0
            ),
            out_of_stock=bool(item.get("out_of_stock", False)),
            url=item.get("url"),
            images=item.get("images", []),
            product_details=product_details,
            created=crawled_at,
        )

        products.append(product)

    # --------------------
    # Bulk insert
    # --------------------
    if products:
        with transaction.atomic():
            Product.objects.bulk_create(products, batch_size=500)

    return f"Imported {len(products)} products successfully."


def run():
    import_products_from_json(
        "/home/anupsingh3292/Desktop/personal/paradedb/flipkart_fashion_products_dataset.json"
    )
