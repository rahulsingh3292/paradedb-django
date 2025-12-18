# Getting Started

This quick guide shows how to define a Django model with a **BM25 index** and perform a simple ParadeDB search.

---

##  Model Definition

Create a simple model.
Attach a **BM25 index** using ParadeDB.

```python
from django.db import models
from paradedb.indexes import Bm25Index

class Article(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    rank = models.IntegerField(default=0)
    published = models.BooleanField(default=True)
    price_range = IntegerRangeField(null=True, blank=True, default=None)
    date_range = DateRangeField(null=True, blank=True, default=None)
    created = models.DateTimeField(auto_now_add=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    tags = ArrayField(models.TextField(max_length=255), default=list, blank=True)

    paradedb_key_field = "id"

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
                "metadata",
                name="article_bm25_idx",
                fields_config=IndexFieldConfig(json_fields=[JSONFieldIndexConfig("metadata", fast=True)]),
            ),
        ]
```

> 🧩 The [`Bm25Index`](./indexes.md#bm25index) makes your model searchable with full-text search using paradedb.

---

##  Example Query

Use ParadeDB’s expression system to perform a full text search on your model:

```python
from paradedb.expressions import Search
from .models import Article

# Search for articles matching "django search"
results = Article.objects.filter(Search("title", "django search"))

for article in results:
    print(article.title)
```

> * The `Search` expression automatically uses the ParadeDB BM25 index to rank results by relevance.
> * To verify that the BM25 index is being applied, run `results.explain()` to inspect the underlying query plan.

---

## Using normal django search with fts
```python

results = Article.objects.filter(Search("title", "value") & models.Q(rank=2))

```


✅ That’s it — your model is now ParadeDB-powered and ready for full-text search in Django.
For more Advance features check [Expressions](./expressions.md)
