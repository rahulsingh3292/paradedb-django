# Introduction

Expressions in **ParadeDB Django** define how search, filtering, and ranking logic is constructed in Django ORM queries.
They translate your filters into ParadeDB-compatible queries for full-text or structured search.

---

> ⚠ **Note on Parameters**
>
> - `key_field` (`str | KeyField)`, default `id`. see [KeyField](./utilities.md#keyfield)):
>   The primary field used as the key for the operation. <br>

>   when using the `KeyField` on related table (fk,o2o,m2m), make sure the join is applied using select_related or using reverse related query.

> - `match_op` (`bool`, default `False`):
>    When `True`, the expression `<key_field_or_lhs> @@@ actual_function()` will be applied.
>    When `False` (or not provided), only the function will be used to generate the SQL, and no key field match operation is applied.


> - when `expression.field` is a `models.F` or `TableField` then, in this case `key_field` paramter is not required it will be automatically resolved and will set to the corresponding table model(table).
>  make sure the join is applied when using a foreign field `ex(models.F(user__id))`.

>  - `output_field` can be passed in the expression in case of custom field type. by default no need to pass output field.
>  - `legacy: bool`  when `True` then `paradedb` schema functions will be used instead `pdb`. no need to pass unless you want to use legacy function. see legacy [settings](./settings.md#paradedb_use_legacy)


---

> - All the Expressions is inside the `paradedb.expressions` module

---

## All

```python
All( key_field: KeyField | str | models.F | TableField = "id", match_op: bool = False)
```

To learn more, see the [ParadeDB All](https://docs.paradedb.com/legacy/advanced/compound/all)

---

## Empty

```python
Empty(key_field: KeyField | str | models.F | TableField = "id", match_op: bool = False)
```

To learn more, see the [ParadeDB Empty](https://docs.paradedb.com/legacy/advanced/compound/empty).


**Example**

---
## Search

```python
Search(
    field: str | models.F | TableField,
    value: str | ValueCast| ParadeDbFunctionExpression,
    escaped: bool = False,
    op: typing.Literal["@@@", "|||", "===", "###", "&&&"] = "@@@"
)
```

> * See [TableField](./utilities.md#tablefield) <br>
> * `@@@` is default normal paradedb operator and evaluates complex query expressions like proximity searches, regex patterns, and parsed queries
> * `|||` performs disjunctive matching, finding documents that contain any of the query term.
> * `###` enforces both term presence and positional requirements, perfect for phrase matching
> * `&&&` requires all terms to be present (conjunction)
> * `===` performs exact token matching, ideal for categorical fields or identifier lookups
> * `|||, ===, &&&, ###, paradedb.cast.ValueCast` only supoorted in paradedb v2 api.


To learn more, see the [ParadeDB Search Overview](https://docs.paradedb.com/legacy/full-text/overview).

**Example**
```python
 Article.objects.filter(Search(field="title", value="well", escaped=False))

 # using F.. when using on related field make sure join is applied using select_related
 Article.objects.filter(Search(models.F("title"), "python"))

 # using table field
 Article.objects.filter(Search(TableField('title', key_field=KeyField(Article)), "python"))

 # using search value with tokenizer. -- supported in v2 only
 from paradedb.cast import ValueCast
 Article.objects.filter(Search('title', ValueCast('django', 'pdb.ngram(1,2)')))

```

---

## Match

```python
Match(
    field: str | models.F | TableField,
    value: str,
    distance: int = 0,
    conjunction_mode: bool = False,
    tokenizer: typing.Optional[
            Tokenizer | typing.Optional[
                typing.Literal[
                    "whitespace",
                    "keyword",
                    "ngram",
                    "regex",
                    "icu",
                    "jieba",
                    "chinese_lindera",
                    "chinese_compatible",
                    "source_code",
                    "raw",
                ]
            ]
        ] = None,
    transposition_cost_one: str = True,
    prefix: bool = False,
    escaped: bool = False,
    key_field: KeyField | str = "id",
    match_op: bool = False
)
```
> `tokenizer`: currently string tokenizers are supported. Tokenizer instance implementation will be available soon. <br>

To learn more, see the [ParadeDB Match](https://docs.paradedb.com/legacy/advanced/full-text/match).

**Example**
```python
Article.objects.filter(
        Match(
            field="title",
            value="python",
            distance=1,
            conjunction_mode=False,
            prefix=True,
            tokenizer="whitespace",
            match_op=True,
        )
    )
```

---

## Exists

```python
Exists(field: str | models.F | TableField, key_field: KeyField | str = "id", match_op: bool = False)
```

To learn more, see the [ParadeDB Exists](https://docs.paradedb.com/legacy/advanced/term/exists).

**Example**
```python
Article.objects.filter(Exists(field="rank", match_op=True))
```

---

## Range

```python
Range(
    field: str | models.F | TableField,
    range_type: typing.Literal["int4range", "int8range", "daterange", "tsrange", "tstzrange"],
    start: int | str | datetime.datetime | datetime.date,
    end: typing.Optional[int | str | datetime.datetime | datetime.date] = None,
    bounds: typing.Literal["[)", "(]", "[]", "()"] = Range.RangeBound.INCLUSIVE_LOWER_EXCLUSIVE_UPPER,
    key_field: KeyField | str = "id",
    match_op: bool = False,
)
```

### RangeType
```python
RangeType.INT4RANGE  # "int4range"
RangeType.INT8RANGE  # "int8range"
RangeType.DATERANGE  # "daterange"
RangeType.TSRANGE    # "tsrange"
RangeType.TSTZRANGE  # "tstzrange"
```

### RangeBound
```python
RangeBound.INCLUSIVE_LOWER_EXCLUSIVE_UPPER  # "[)"
RangeBound.EXCLUSIVE_LOWER_INCLUSIVE_UPPER  # "(]"
RangeBound.INCLUSIVE_BOTH                    # "[]"
RangeBound.EXCLUSIVE_BOTH                    # "()"
```

To learn more, see the [ParadeDB Range](https://docs.paradedb.com/legacy/advanced/term/range).

**Example**

```python

# Range Date

Article.objects.filter(
        Range(
            field="created",
            range_type="daterange",
            start=date(2025, 9, 2),
            end=date(2025, 9, 10),
            bounds="[)",
            match_op=True,
        )
    )
# Range Integer

Article.objects.filter(
        Range(
            field="rank",
            range_type="int4range",  # Range.RangeType.INT4RANGE
            start=1,
            end=3,
            bounds="()",
            match_op=True,
        )
    )

# Unbounded Range

Article.objects.filter(
        Range(
            field="rank",
            range_type="int4range",  # Range.RangeType.INT4RANGE
            start=1,
            match_op=True,
        )
    )
```

---

## RangeTerm

```python
RangeTerm(
    field: str | models.F | TableField,
    term_or_range: str | int | float,
        cast: typing.Literal[
            "tsrange",
            "int4range",
            "int8range",
            "daterange",
            "tstzrange",
            "bigint",
            "date",
            "double precision",
            "integer",
            "numeric",
            "real",
            "smallint",
            '"char"',
            "timestamp with time zone",
            "timestamp without time zone",
            "numrange",
        ],
    relation: typing.Optional[typing.Literal["Intersects", "Within", "Contains"]] = None,
    key_field: KeyField | str = "id",
    match_op: bool = False,
)
```

To learn more, see the [ParadeDB RangeTerm](https://docs.paradedb.com/legacy/advanced/term/range-term).

**Example**
```python

# Range Term With Date Range Fields
Article.objects.filter(
        RangeTerm(
            field="date_range",
            term_or_range="'[2025-09-02,2025-09-10]'",
            cast=Range.RangeType.DATERANGE,
            relation=RangeTerm.Relation.Intersects,
            match_op=True,
        )
    )
# Range with Integer Range Fields
 Article.objects.filter(
        RangeTerm(
            field="price_range",
            term_or_range=1,
            cast=RangeTerm.Cast.integer,
            match_op=True,
        )
    )

```

---

## Regex

```python
Regex(
    field: str | models.F | TableField,
    value: str,
    key_field: KeyField | str = "id",
    match_op: bool = False,
)
```

To learn more, see the [ParadeDB Regex](https://docs.paradedb.com/legacy/advanced/term/regex).

**Example**
```python

Article.objects.filter(
        Regex(
            field="title",
            value='^well$',
            match_op=True,
        )
    )

```

---

## Term

```python
Term(
    field: str | models.F | TableField,
    value: str,
    enum_cast_field: typing.Optional[str] = None, # PostgreSQL cast type, e.g., 'int', 'date', 'timestamp'
    key_field: KeyField | str = "id",
    match_op: bool = False,
)
```

To learn more, see the [ParadeDB Term](https://docs.paradedb.com/legacy/advanced/term/term).

**Example**
```python

 Article.objects.filter(Term(field="rank", value=100, match_op=True))

```

---

## TermSet

```python
TermSet(
    terms: typing.List[Term],
    key_field: KeyField | str = "id",
    match_op: bool = False,
)
```

To learn more, see the [ParadeDB TermSet](https://docs.paradedb.com/legacy/advanced/term/term-set).

**Example**
```python
 Article.objects.filter(
        TermSet(
            terms=[
                Term(field="rank", value=1),
                Term(field="rank", value=200),
            ],
            match_op=True
        )
    )
```

---

## FuzzyTerm

```python
FuzzyTerm(
    field: str | models.F | TableField,
    value: str,
    distance: int = 2,
    transposition_cost_one: bool = True,
    prefix: bool = False,
    key_field: KeyField | str = "id",
    match_op: bool = False,
)
```

To learn more, see the [ParadeDB FuzzyTerm](https://docs.paradedb.com/legacy/advanced/term/fuzzy-term).

**Example**
```python
Article.objects.filter(
            FuzzyTerm(
                field="title",
                value="well",
                distance=2,
                prefix=False,
                transposition_cost_one=True,
                match_op=True
            )
        )
```

---

## Phrase

```python
Phrase(
    field: str | models.F | TableField,
    pharses: typing.List[str] # must be atleast 2,
    slop: int = 0,
    key_field: KeyField | str = "id",
    match_op: bool = False,
)
```

To learn more, see the [ParadeDB Phrase](https://docs.paradedb.com/legacy/advanced/phrase/phrase).

**Example**
```python

Article.objects.filter(
        Phrase(field="description", pharses=["quick", "brown", "fox"], slop=3, match_op=True)
    )

```

---

## PhrasePrefix

```python
PhrasePrefix(
    field: str | models.F | TableField,
    pharses: typing.List[str], # must be atleast 2,
    max_expansion: int = 0,
    key_field: KeyField | str = "id",
    match_op: bool = False
)
```

To learn more, see the [ParadeDB PhrasePrefix](https://docs.paradedb.com/legacy/advanced/phrase/phrase-prefix).

**Example**
```python

Article.objects.filter(
        PhrasePrefix(field="title", pharses=["deep", "learn"], max_expansion=5, match_op=True)
    )

```

---

## ConstScore

```python
ConstScore(
    score: float | int,
    query: ParadeDbFunctionExpression,
    key_field: KeyField | str = "id",
    match_op: bool = False
)
```

To learn more, see the [ParadeDB ConstScore](https://docs.paradedb.com/legacy/advanced/compound/const).

**Example**
```python

  Article.objects.filter(
        Boolean(
            should=[Term("title", value="running"), ConstScore(1.0, Match(field="title", value="shoes"))],
            match_op=True,
        )
    )

```

---

## Bm25Score

```python
Bm25Score(key_field: KeyField | str | models.F | TableField  = "id")
```

To learn more, see the [ParadeDB BM25 Scoring](https://docs.paradedb.com/legacy/full-text/scoring).

**Example**
```python

Article.objects.annotate(score=Bm25Score()).filter(score__gt=0).order_by("-score")

```

---

## Boost

```python
Boost(
    factor: float | int,
    query: ParadeDbFunctionExpression,
    key_field: KeyField | str = "id",
    match_op: bool = False,
)
```

To learn more, see the [ParadeDB Boost](https://docs.paradedb.com/legacy/advanced/compound/boost).

**Example**
```python
 Article.objects.filter(
        Boolean(
            should=[Term("title", value="running"), Boost(1.0, Match(field="title", value="shoes"))],
            match_op=True,
        )
    )
```

---

## DisjunctionMax

```python
DisjunctionMax(
    disjuncts: typing.List[ParadeDbFunctionExpression],
    tie_breaker: int = 0,
    key_field: KeyField | str = "id",
    match_op: bool = False
)
```

To learn more, see the [ParadeDB DisjunctionMax](https://docs.paradedb.com/legacy/advanced/compound/disjunction-max).

**Example**
```python
Article.objects.filter(
        DisjunctionMax(
            disjuncts=[Term(field="title", value="running"), Term(field="title", value="shoes")],
            tie_breaker=1,
            match_op=True,
        )
    )

```

---


## Boolean

```python
Boolean(
    must: typing.Optional[typing.List[ParadeDbFunctionExpression]] = None,
    must_not: typing.Optional[typing.List[ParadeDbFunctionExpression]] = None,
    should: typing.Optional[typing.List[ParadeDbFunctionExpression]] = None,
    key_field: KeyField | str = "id",
    match_op: bool = False
)
```

To learn more, see the [ParadeDB Boolean](https://docs.paradedb.com/legacy/advanced/compound/boolean).

**Example**
```python
Article.objects.filter(
        Boolean(
            must=[Match(field="title", value="python")],
            must_not=[Match("description", value="python", tokenizer="raw")],
            should=[Term("title", value="python"), ConstScore(1.0, Term("title", value="python"))],
            match_op=True,
        )
    )
```

---

## Snippet

```python
Snippet(
    field: str | models.F | TableField,
    limit: typing.Optional[int] = None,
    offset: typing.Optional[int] = None,
    start_tag: typing.Optional[str] = None,
    end_tag: typing.Optional[str] = None,
    max_num_chars: typing.Optional[int] = None
)
```

To learn more, see the [ParadeDB Snippet and Highlighting](https://docs.paradedb.com/legacy/full-text/highlighting).

**Example**
```python
 Article.objects.annotate(
        snippet_title=Snippet(field="description", start_tag="<b>", end_tag="</b>", max_num_chars=100),
        snippet_description=Snippet(field="description", start_tag="<b>", end_tag="</b>", max_num_chars=100),
    ).filter(
        Boolean(must=[Match(field="title", value="hello")], match_op=True)
        | Match(field="description", value="well", match_op=True)
    )

```

---

## MoreLikeThis

```python
MoreLikeThis(
    document_id: typing.Optional[str | int] = None,
    document: typing.Optional[dict] = None,
    fields: typing.Optional[typing.List[str]] = None,
    min_doc_frequency: typing.Optional[int] = None,
    max_doc_frequency: typing.Optional[int] = None,
    min_term_frequency: typing.Optional[int] = None,
    max_query_terms: typing.Optional[int] = None,
    min_word_length: typing.Optional[int] = None,
    max_word_length: typing.Optional[int] = None,
    boost_factor: typing.Optional[int | float] = None,
    stop_words: typing.Optional[typing.List[str]] = None,
    key_field: KeyField | str = "id",
    match_op: bool = False,
)
```
> ⚠ **Note:**
> - `document_id` and `document` **cannot be used together**.
>   When `document` is provided, the `document_id` field will be excluded, and vice versa.
> - `document_id` and `fields` **can be used together**, while `document` must be used alone.

To learn more, see the [ParadeDB MoreLikeThis](https://docs.paradedb.com/legacy/advanced/specialized/more-like-this).

**Example**
```python

# with document id and field
Article.objects.filter(
        MoreLikeThis(
            document_id=1,
            fields=["title", "description"],
            min_term_frequency=1,
            max_query_terms=20,
            match_op=True
        )
    )

# with document field
Article.objects.filter(
        MoreLikeThis(
            document={"title": "well", "description": "world"},
            min_term_frequency=1,
            max_query_terms=20,
            match_op=True
        )
    )
```

---

## Parse

```python
Parse(
    query: str,
    lenient: bool = False,
    conjunction_mode: bool = False,
    key_field: KeyField | str = "id",
    match_op: bool = False,
)
```

To learn more, see the [ParadeDB Parse](https://docs.paradedb.com/).

**Example**
```python
Article.objects.filter(
        Parse(
            query="title:well AND description:well",
            lenient=True,
            conjunction_mode=True,
            key_field="id",
            match_op=True,
        )
    )

```

---

## ParseWithField

```python
ParseWithField(
    field: str | models.F | TableField,
    value: str,
    lenient: bool = False,
    conjunction_mode: bool = False,
    key_field: KeyField | str = "id",
    match_op: bool = False,
)
```

To learn more, see the [ParadeDB ParseWithField](https://docs.paradedb.com/).

**Example**
```python
Article.objects.filter(
        ParseWithField(
            field="title",
            value="well",
            lenient=True,
            conjunction_mode=True,
            match_op=True,
        )
        & ParseWithField(field="description", value="hello", conjunction_mode=True, match_op=True)
    )
```

---


## Proximity

```python
Proximity(
        values: typing.List[str | int | ProximityRegex | ProximityArray | typing.Literal["##", "##>"]],
        field: typing.Optional[str | models.F | TableField] = None,
)
```

> * `values` expected length must be >= 3. passing wrong sequence value will raise `ValueError`.

To learn more, see the [ParadeDB Proximity](https://docs.paradedb.com/documentation/full-text/proximity).

**Example**
```python
from paradedb.expressions import Proximity, ProximityRegex, ProximityArray

Article.objects.filter(
        Proximity(
            ["python", "##" 1, "##>", "django"],
            field="title"
        )
    )

# using proximity regex and proximity array
Article.objects.filter(
        Proximity(
             (
                "django",
                "##",
                "1",
                "##>",
                ProximityRegex("m.*"),
                "##",
                100,
                "##>",
                ProximityArray(["wow", ProximityRegex("wow.*", 10)]),
            ),
            field='title'
        )
    )
```

## JsonOp
* supported in version - 0.20.5

```python
JsonOp(field: str, *keys: str, value: str | int | models.Value)
```

Documentation link: -

**Example**
```python
from paradedb.expressions import JsonOp

Article.objects.filter(JsonOp("metadata", "read_count", value=models.Value(1)))
Article.objects.filter(JsonOp("metadata", "tags", "name", value='django'))
```
