# Introduction

Django ParadeDB provides custom lookups that forward their RHS (right-hand-side) values into ParadeDB Expressions.
You can pass RHS values in **four ways**:  (`tuple`, `list` , `dict`, `LookupParameter`).

Arguments are forwarded **exactly in the same order** required by the Expression (see [Expressions](./expressions.md)).

---

> ⚠ **Note**
>
> * For expressions or functions that do not require a field, use `id` or any other field.
>   The left-hand side (LHS) will be ignored in this case.
>
> * When filtering on **ForeignKey**, **OneToOne**, or **ManyToMany** fields using
>   `related__id__pdb_lookup=...`, and it is **not** a reverse relation, you **must** use
>   `<related_field>__related__<field_name>` to correctly resolve the target table.
> * If value for the lookup fails, use [PARADEDB_LOOKUP_SKIP_RHS_PREP](./settings.md#paradedb_lookup_skip_rhs_prep).

---

---

## __match
**Expression:** [Match](./expressions.md#match)

**Example:**

```python
Article.objects.filter(title__match="deep learning")
```

---


## __pdb_search

**Expression:** [Search](./expressions.md#search)

**Example:**

```python
Aricle.objects.filter(title__pdb_search="django")
```

---

## __term

**Expression:** [Term](./expressions.md#term)

**Example:**

```python
Article.objects.filter(title__term="fantasy")
```

---

## __term_set

**Expression:** [TermSet](./expressions.md#termset)

**Example:**

```python
Article.objects.filter(
    id__term_set=LookupParameter(
                terms=[
                    Term(field="rank", value=1),
                    Term(field="rank", value=200),
                ])
)
```

---

## __pdb_range

**Expression:** [Range](./expressions.md#range)

**Example:**

```python
Article.objects.filter(
    created__pdb_range=("daterange", timezone.datetime(2021, 1, 1), timezone.datetime(2022, 1, 1), "[]")
)
```

---

## __range_term

**Expression:** [RangeTerm](./expressions.md#rangeterm)

**Example:**

```python
Article.objects.filter(
    date_range__range_term=("'[2025-09-02,2025-09-10]'", "daterange", "Intersects"),
    price_range__range_term=("'[0,100]'", "int4range", "Intersects"),
)
```

---

## __phrase

**Expression:** [Phrase](./expressions.md#phrase)

**Example:**

```python
Aricle.objects.filter(title__phrase=LookupParameter(pharses=["quick", "brown", "fox"], slop=3))
```

---

## __phrase_prefix

**Expression:** [PhrasePrefix](./expressions.md#phraseprefix)

**Example:**

```python
Article.objects.filter( title__phrase_prefix=LookupParameter(["deep", "learn"]))
```

---

## __fuzzy_term

**Expression:** [FuzzyTerm](./expressions.md#fuzzyterm)

**Example:**

```python
Article.objects.filter(title__fuzzy_term=("fuzzy", 2, True))
```

---

## __boolean

**Expression:** [Boolean](./expressions.md#boolean)

**Example:**

```python
Article.objects.filter(
    id__boolean=dict(
                should=[Term(field="title", value="running"), Term(field="title", value="shoes")],
            )
)
```

---

## __more_like_this

**Expression:** [MoreLikeThis](./expressions.md#morelikethis)

**Example:**

```python
Article.objects.filter(id__more_like_this=LookupParameter(123, fields=["title", "description"]))

Article.objects.filter(id__more_like_this=LookupParameter(document={'title': "django"}))
```


---

## __pdb_regex

**Expression:** [Regex](./expressions.md#regex)

**Example:**

```python
Article.objects.filter(title__pdb_regex="^Deep.*")
```

---

## __const_score

**Expression:** [ConstScore](./expressions.md#constscore)

**Example:**

```python
Article.objects.filter(id__const_score=(1.0, Match(field="title", value="shoes")))
```

---

## __disjunction_max

**Expression:** [DisjunctionMax](./expressions.md#disjunctionmax)

**Example:**

```python
Article.objects.filter(
    id__disjunction_max=LookupParameter(
                [Term(field="title", value="django")],
                tie_breaker=1,
            )
)
```

---

## __parse_with_field

**Expression:** [ParseWithField](./expressions.md#parsewithfield)

**Example:**

```python
Article.objects.filter(title__parse_with_field="title:deep learning")
```

---

## __parse

**Expression:** [Parse](./expressions.md#parse)

**Example:**

```python
Article.objects.filter(
    id__parse=LookupParameter(
                "title:well AND description:well", lenient=True, conjunction_mode=True
            )
)
```

---

## __match_v2

**Expression:** [Search](./expressions.md#search)

**Example:**

```python
Article.objects.filter(title__match_v2='django')

# using value with custom tokenizer
from paradedb.cast import ValueCast

Article.objects.filter(title__match_v2=ValueCast('django', 'pdb.ngram(1,2)'))
```

---

## __match_v2_conjunction

**Expression:** [Search](./expressions.md#search)

**Example:**

```python
Article.objects.filter(title__match_v2_conjunction='django')

# using value with custom tokenizer
from paradedb.cast import ValueCast

Article.objects.filter(title__match_v2_conjunction=ValueCast('django', 'pdb.ngram(1,2)'))
```

---

## __term_v2

**Expression:** [Search](./expressions.md#search)

**Example:**

```python
Article.objects.filter(title__term_v2='django')

# using value with custom tokenizer
from paradedb.cast import ValueCast

Article.objects.filter(title__term_v2=ValueCast('django', 'pdb.ngram(1,2)'))
```

---

## __phrase_v2

**Expression:** [Search](./expressions.md#search)

**Example:**

```python
Article.objects.filter(title__phrase_v2='django')

# using value with custom tokenizer
from paradedb.cast import ValueCast

Article.objects.filter(title__phrase_v2=ValueCast('django', 'pdb.ngram(1,2)'))
```

---

## __proximity

**Expression:** [Proximity](./expressions.md#proximity)

**Example:**

```python
Article.objects.filter(title__proximity=[["python", "##" 1, "##>",  "django"]])
```

---
