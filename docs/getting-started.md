# 🚀 Getting Started with ParadeDB in Django

This guide shows how to:

* Define a Django model with a **BM25 index**
* Perform **full-text search**
* Query **JSON and Array fields**
* Use **custom ParadeDB operators with Json SubScripting** (`match`, `term`, `phrase`, `match_conjunction`)
* Combine ParadeDB search with Django ORM filters
* Aggregation

---

##  Quick Example

Create a Django model and attach a **BM25 index** using ParadeDB:

```python
from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.fields.ranges import (
    IntegerRangeField,
    DateRangeField,
)
from paradedb.indexes import Bm25Index, IndexFieldConfig, JSONFieldIndexConfig

class Article(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    created = models.DateTimeField(auto_now_add=True, blank=True)
    rank = models.IntegerField(default=0)
    published = models.BooleanField(default=True)

    price_range = IntegerRangeField(null=True, blank=True, default=None)
    date_range = DateRangeField(null=True, blank=True, default=None)

    metadata = models.JSONField(default=dict, blank=True)
    tags = ArrayField(
        models.TextField(max_length=255),
        default=list,
        blank=True,
    )

    # ParadeDB primary key (optional)
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
                fields_config=IndexFieldConfig(
                    json_fields=[
                        JSONFieldIndexConfig(
                            "metadata",
                            fast=True,
                        )
                    ]
                ),
            ),
        ]
```

> The `Bm25Index` enables **fast, relevance-ranked full-text search**.

---

## Basic Full-Text Search

```python
from paradedb.expressions import Search
from .models import Article

results = Article.objects.filter(
    Search("title", "django search")
)

for article in results:
    print(article.title)
```

* Inspect query planner to verify:

```python
results.explain()
```

---

## JSON SubScript Field Search

Assume stored JSON:

```json
{
  "category": "backend",
  "framework": "django",
  "reading_time": 2
}
```

---

### Using Django Lookup (`__json_op`)

### Lookup Pattern

```
field__json_key__operator__json_op=value
```

| Part        | Meaning                 |
| ----------- | ----------------------- |
| `metadata`  | JSONField               |
| `framework` | JSON key                |
| `match`, `phrase`, `term`, `match_conjunction`  | ParadeDB operator |
| `json_op`   | Enables JSON expression |
| `"django"`  | search value            |

---

### Term

```python
results = Article.objects.filter(
    metadata__framework__term__json_op="django"
)
```

---

### Using Expression API (`JsonOp`)

```python
from paradedb.expressions import JsonOp
```

---

### MATCH

```python
results = Article.objects.filter(
    JsonOp("metadata", "framework", "match", value="dj")
)
```

---

## Combine with Django Filters

```python
from django.db import models

results = Article.objects.filter(
    JsonOp("metadata", "framwork", "match", value="django") &
    models.Q(rank=2) &
    models.Q(published=True)
)
```

---

## Using V2 API with normal fields and Json, Array fields Querying

operator lookups - `match_v2`, `phrase_v2`, `match_conjunction`, `term_v2`

```python
from django.db import models
from paradedb.cast import ValueCast

# query using normal fields
results = Article.objects.filter(models.Q(title__term_v2='djangp'))

# query using v2 value using cast with tokenizer
results = Article.objects.filter(models.Q(title__term_v2=ValueCast('django', 'pdb.ngram(2,2)')))

# query jsonfield
results = Article.objects.filter(models.Q(metadata__framework__term_v2='django')) # value can be passed as valuecast also

# query array field
results = Article.objects.filter(tags__term_v2='django')

```

---


## Mixing ParadeDB Search + ORM

```python
results = Article.objects.filter(
    Search("title", "django") &
    models.Q(rank__gte=5) &
    models.Q(published=True)
)

```

---

## Aggregation

```python
from paradedb.aggregates import Count, Avg

article_aggregated_count = Article.objects.aggregate(count=Count('id', filter=models.Q(id__all=True)))
print(article_aggregated_count)

avg_read_time_data = Article.objects.aggregate(avg_reeading_time=Avg('metadata.reading_time', filter=models.Q(id__all=True)))
print(avg_read_time_data)

```

---

# 🎉 You're All Set!

Your Django app is now:

✅ ParadeDB powered
✅ BM25 indexed
✅ JSON searchable

---

## 📚 Learn More

* [Expressions](./expressions.md)
* [Indexes](./index.md)
* [Aggregations](./aggregations.md)
* [Lookups](./lookups.md)

---
