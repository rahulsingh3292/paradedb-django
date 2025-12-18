from django.conf import settings
from django.contrib.postgres.fields import ArrayField, DateRangeField, IntegerRangeField
from django.db import models

from paradedb.indexes import (
    Bm25Index,
    IndexField,
    IndexFieldConfig,
    JSONFieldIndexConfig,
)


class Product(models.Model):
    id = models.CharField(max_length=150, primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        default=None,
    )
    title = models.CharField(max_length=500)
    brand = models.CharField(max_length=100, blank=True, null=True)

    category = models.CharField(max_length=100)
    sub_category = models.CharField(max_length=100, blank=True, null=True)

    description = models.TextField(blank=True, default="")

    actual_price = models.IntegerField()
    selling_price = models.IntegerField()
    discount = models.DecimalField(
        max_digits=6, decimal_places=2, blank=True, default=0
    )
    average_rating = models.IntegerField(default=0, blank=True)

    out_of_stock = models.BooleanField(default=False, blank=True)

    url = models.URLField(max_length=500, blank=True, null=True)
    images = ArrayField(models.URLField(max_length=500), default=list, blank=True)

    product_details = models.JSONField(default=list)  # List of key-value dicts
    created = models.DateTimeField()

    class Meta:
        db_table = "product"
        indexes = [
            Bm25Index(
                "id",
                "title",
                IndexField("brand", "pdb.literal"),
                "description",
                IndexField("category", "pdb.literal"),
                IndexField("sub_category", "pdb.simple"),
                "selling_price",
                "average_rating",
                "out_of_stock",
                IndexField("product_details", "pdb.literal"),
                models.F("created"),
                models.F("user"),
                name="product_bm25_idx",
            ),
        ]

    def __str__(self):
        return f"{self.title}"


class UserProduct(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        default=None,
    )
    product = models.ForeignKey(
        "Product", on_delete=models.CASCADE, blank=True, null=True, default=None
    )

    class Meta:
        indexes = [
            Bm25Index("id", "user", "product", name="user_product_bm25_idx"),
        ]
        db_table = "user_product"


class Article(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True
    )
    created = models.DateTimeField(auto_now_add=True)
    rank = models.IntegerField(default=0)
    published = models.BooleanField(default=True)
    price_range = IntegerRangeField(null=True, blank=True, default=None)
    date_range = DateRangeField(null=True, blank=True, default=None)
    created = models.DateTimeField(auto_now_add=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    tags = ArrayField(models.TextField(max_length=255), default=list, blank=True)

    paradeb_key_field = "id"

    def __str__(self):
        return self.title

    class Meta:
        indexes = [
            Bm25Index(
                "id",
                "title",
                "description",
                "rank",
                "published",
                "price_range",
                "date_range",
                "created",
                "user",
                IndexField(models.F("tags"), tokenizer_cast="pdb.ngram(1,2)"),
                "metadata",
                name="article_bm25_idx",
                fields_config=IndexFieldConfig(
                    json_fields=[JSONFieldIndexConfig("metadata", fast=True)]
                ),
            ),
        ]
        db_table = "article"
