# Inroduction

BM25 indexes in ParadeDB provide full-text search with relevance scoring. Creating a BM25 index is similar to creating a default Django index — you specify the fields to index, and you can use expressions or individual fields along with conditional expressions. Additional BM25-specific parameters, such as boosting, stopwords, and field normalization, can also be configured.

---

> - import from  `paradedb.indexes` module

---

## IndexField

`IndexField` represents a model field inside a ParadeDB BM25 index with an optional **PostgreSQL cast** used for ParadeDB tokenizers.

```python
IndexField(field: str | models.F, tokenizer_cast: typing.Optional[str] = None, field_resolver: typing.Optional[typing.Callable] = None)
```

### tokenizer_cast

`tokenizer_cast` is appended directly to the SQL column reference and is expected to be a **postgres paradedb cast**, for example:

* `pdb.literal`
* `pdb.ngram(1,2)`  and other


### field_resolver

`field_resolver` resolved the field name with our without expression.

---

**Example**

```python
from django.db import models
from paradedb.indexes import Bm25Index, IndexField

class Article(models.Model):
    title = models.CharField(max_length=255)
    body = models.TextField()
    metadata = models.JsonField(default=dict)

    class Meta:
        indexes = [
            Bm25Index(
                IndexField("body", tokenizer_cast="pdb.ngram(1,2)"),
                IndexField("(metadata->>'word_count')", tokenizer_cast="pdb.ngram(1,2)"),
                IndexField(Lower('title'), tokenizer_cast="pdb.ngram(1,2)"),
                name="article_bm25",
            )
        ]
```


---

## Bm25Index

```python
Bm25Index(
    *expressions,
    fields=(),
    name: str,
    db_tablespace=None,
    opclasses=(),
    condition=None,
    include=None,
    fields_config: typing.Optional[IndexFieldConfig] = None,
    key_field: str = "id",
    with_extra: with_extra: typing.Optional[typing.Dict[str, typing.Any]] = None
)
```
> `fields_config` additional field configuration for bm25 index. [see the index field configuration](#indexfieldconfig)<br>
> To learn more about Index parameters, see the [Django Index](https://docs.djangoproject.com/en/5.2/ref/models/indexes/) <br>

---

## IndexFieldConfig

```python
IndexFieldConfig(
    text_fields: typing.Optional[typing.List[TextFieldIndexConfig]] = None,
    json_fields: typing.Optional[typing.List[JSONFieldIndexConfig]] = None,
    numeric_fields: typing.Optional[typing.List[NumericFieldIndexConfig]] = None,
    boolean_fields: typing.Optional[typing.List[BooleanFieldIndexConfig]] = None,
    datetime_fields: typing.Optional[typing.List[DateTimeFieldIndexConfig]] = None,
)
```
> see [`TextFieldIndexConfig` field configuration](#textfieldindexconfig) <br>
> see [`JSONFieldIndexConfig` field configuration](#jsonfieldindexconfig) <br>
> see [`NumericFieldIndexConfig` field configuration](#numericfieldindexconfig) <br>
> see [`BooleanFieldIndexConfig` field configuration](#booleanfieldindexconfig) <br>
> see [`DateTimeFieldIndexConfig` field configuration](#datetimefieldindexconfig) <br>

To learn more, see the [ParadeDB field configuration](https://docs.paradedb.com/legacy/indexing/field-options).

---

## TextFieldIndexConfig

```python
TextFieldIndexConfig(
    field: str,
    fast: bool = True,
    tokenizer: typing.Optional[Tokenizer] = None,
    normalizer: typing.Literal["raw", "lowercase"] = "raw",
    record: typing.Literal["position", "freq", "basic"] = "position",
    indexed: bool = True,
    fieldnorms: bool = True,
    column: typing.Optional[str] = None,
)
```

Configure a text field for indexing. <br>
If `column` is provided, `field` will be treated as an alias.  <br>
To learn more, see the [ParadeDB TextFieldIndexConfig](https://docs.paradedb.com/legacy/indexing/field-options#text-fields).

**Example**
```python
from paradedb.indexes import Bm25Index, IndexFieldConfig, TextFieldIndexConfig

Bm25Index(
    fields=["id", "title", "description"],
    name="idx_name",
    fields_config= IndexFieldConfig(
    text_fields=[
        TextFieldIndexConfig(
            field="title",
            fast=True,
            normalizer="lowercase",
            record="position"
        ),
        TextFieldIndexConfig(
            field="description",
            fast=True,
            normalizer="lowercase",
        )
    ]
))
```
---

## JSONFieldIndexConfig

```python
JSONFieldIndexConfig(
    field: str,
    fast: bool = True,
    tokenizer: typing.Optional[Tokenizer] = None,
    normalizer: typing.Optional[typing.Literal["raw","lowercase"]] = None,
    record: typing.Literal["position", "freq", "basic"] = "position",
    indexed: bool = True,
    fieldnorms: bool = True,
    column: typing.Optional[str] = None,
    expand_dots: bool = True,
)
```

Configure a json field for indexing.
To learn more, see the [ParadeDB JSONFieldIndexConfig](https://docs.paradedb.com/legacy/indexing/field-options#json-fields).

**Example**
```python
from paradedb.indexes import Bm25Index, IndexFieldConfig, JSONFieldIndexConfig

Bm25Index(
    fields=["id", "metadata"],
    name="idx_name",
    fields_config=IndexFieldConfig(
    json_fields=[
        JSONFieldIndexConfig(
            field="metadata",
            fast=True,
            expand_dots=True
        )
    ]
)
)
```

---


## NumericFieldIndexConfig

```python
NumericFieldIndexConfig(
    field: str,
    fast: bool = True,
    indexed: bool = True,
    column: typing.Optional[str] = None,
)
```

Configure a numeric field for indexing.
To learn more, see the [ParadeDB NumericFieldIndexConfig](https://docs.paradedb.com/legacy/indexing/field-options#numeric-fields).

**Example**
```python
from paradedb.indexes import Bm25Index, IndexFieldConfig, NumericFieldIndexConfig

Bm25Index(
    fields=["id", "rank"],
    name="idx_name",
    fields_config=IndexFieldConfig(
    numeric_fields=[
        NumericFieldIndexConfig(field="rank", fast=True),
    ]
)
)
```

---


## BooleanFieldIndexConfig

```python
BooleanFieldIndexConfig(
    field: str,
    fast: bool = True,
    indexed: bool = True,
    column: typing.Optional[str] = None,
)
```
Configure a boolean field for indexing.
To learn more, see the [ParadeDB BooleanFieldIndexConfig](https://docs.paradedb.com/legacy/indexing/field-options#boolean-fields).

**Example**
```python
from paradedb.indexes import Bm25Index, IndexFieldConfig, BooleanFieldIndexConfig

Bm25Index(
    fields=["id", "published"],
    name="idx_name",
    fields_config=IndexFieldConfig(
    numeric_fields=[
        BooleanFieldIndexConfig(field="published", fast=True),
    ]
))
```

---
## DateTimeFieldIndexConfig

```python
DateTimeFieldIndexConfig(
    field: str,
    fast: bool = True,
    indexed: bool = True,
    column: typing.Optional[str] = None,
)
```
Configure a date or datetime field for indexing.
To learn more, see the [ParadeDB DateTimeFieldIndexConfig](https://docs.paradedb.com/legacy/indexing/field-options#datetime-fields).

**Example**
```python
from paradedb.indexes import Bm25Index, IndexFieldConfig, DateTimeFieldIndexConfig

Bm25Index(
    fields=["id", "created"],
    name="idx_name",
    fields_config=IndexFieldConfig(
    numeric_fields=[
        DateTimeFieldIndexConfig(field="created", fast=True),
    ]
))
```

---



## Using Tokenizers with BM25 Index

```python
from paradedb.indexes import Bm25Index, IndexFieldConfig, TextFieldIndexConfig, JSONFieldIndexConfig
from paradedb.tokenizers import WhitespaceTokenizer, NGramTokenizer

Bm25Index(
    fields=["id", "title", "description", "metadata"],
    name="article_bm25_tokenizer_idx",
    fields_config=IndexFieldConfig(
        text_fields=[
            TextFieldIndexConfig(
                field="title",
                fast=True,
                tokenizer=WhitespaceTokenizer(),
                normalizer="lowercase",
                record="position"
            ),
            TextFieldIndexConfig(
                field="description",
                fast=True,
                tokenizer=NGramTokenizer(min_gram=2, max_gram=3),
                normalizer="lowercase",
                record="position"
            )
        ],
        json_fields=[
            JSONFieldIndexConfig(
                field="metadata",
                tokenizer=WhitespaceTokenizer(),
                expand_dots=True
            )
        ]
    )
)
```
> To see more details about each tokenizer, check the class documentation above.
> To see all tokenizers and options, see [Tokenizers](./tokenizers.md).

---
