
#  Aggregates

---

> ⚠ If the filter is applied and you encounter the error `query is incompatible with pg_search` when using an expression or lookup, try using the legacy ParadeDB function by passing the value as a dictionary or by using LookupParameter with legacy=True.


---

> - All the aggregations is inside the `paradedb.aggregates` module

---

## Count

```python
Count(field: str = "id")
```

> * see [ParadeDB Count ](https://docs.paradedb.com/documentation/aggregates/metrics/count).
> * see [Tantivy for more](https://docs.rs/tantivy/latest/tantivy/aggregation/metric/struct.CountAggregation.html)

**Example**

```python
from paradedb.aggregates import Count
from articles.models import Article

Article.objects.aggregate(count=Count("id", filter=models.Q(id__all=True)))
```

---

## Term

```python
Term(
    field: str,
    order: typing.Optional[TermAggregateOrder | dict[str,str]] = None,
    size: int = 0,
    segment_size: int = 0,
    min_doc_count: int = 0,
    missing: float | int | None = None,
    show_term_doc_count_error: bool = False,
    aggs: dict | None = None,
)
```

> * see [ParadeDB Terms Aggregation](https://docs.paradedb.com/documentation/aggregates/bucket/terms).
> * see [Tantivy for more](https://docs.rs/tantivy/latest/tantivy/aggregation/bucket/struct.TermsAggregation.html)

**Example**

```python
from paradedb.expressions import All
from paradedb.aggregates import Term, TermAggregateOrder, Count
from paradedb.expressions import All

# using count or _key
Article.objects.aggregate(
        count=Term(
            "rank",
            order={"_count": "desc"},  # _key
            filter = models.Q(id__all=True)
        )
    )


# using SubAggregation
Article.objects.filter(All(match_op=True)).aggregate(
        count=Term(
            "rank",
            order={"max_count": "desc"},
            aggs={
                "max_count": Count("id").build_json(as_dict=True),
            },
        )
    )
```

### TermAggregateOrder

```python
TermAggregateOrder(
    target: Literal["_count", "_key"] | str,
    order: Literal["asc", "desc"] = "asc",
)
```

**Example**

```python
TermAggregateOrder("_key", "asc")
```

---

## HistogramBound

```python
HistogramBound(min: int, max: int)
```

> * Used by DateHistogram and Histogram <br>

**Example**

```python
HistogramBound(0, 100)
```

---

## DateHistogram

```python
DateHistogram(
    field: str,
    fixed_interval: str = None,
    offset: str | None = None,
    min_doc_count: int | None = None,
    hard_bounds: HistogramBound | tuple[float, float] | None = None,
    extended_bounds: HistogramBound | tuple[float, float] | None = None,
    keyed: bool = True,
)
```

> * see [ParadeDB Date Histogram Aggregation](https://docs.paradedb.com/documentation/aggregates/bucket/datehistogram). <br>
> * see [Tantivy doc for more](https://docs.rs/tantivy/latest/tantivy/aggregation/bucket/struct.DateHistogramAggregationReq.html)

**Example**

```python
from paradedb.aggregates import DateHistogram

Article.objects.aggregate(
        date_histogram=DateHistogram(
            "created",
            "30d",
            filter=models.Q(id__all=True)
        )
    )
```

---

## Histogram

```python
Histogram(
    field: str,
    interval: str,
    offset: str | None = None,
    min_doc_count: int | None = None,
    hard_bounds: HistogramBound | tuple[float, float] | None = None,
    extended_bounds: HistogramBound | tuple[float, float] | None = None,
    keyed: bool = True,
    is_normalized_to_ns: bool = False,
)
```

> * see [ParadeDB Histogram](https://docs.paradedb.com/documentation/aggregates/bucket/histogram)
> * see [Tantivy for more](https://docs.rs/tantivy/latest/tantivy/aggregation/bucket/struct.HistogramAggregation.html)

**Example**

```python
from paradedb.aggregates import Histogram

Article.objects.aggregate(
    result=Histogram(field="created", interval="10d", filter=models.Q(id__all=True))
)
```

---

## Range

```python
Range(
    field: str,
    ranges: list[RangeAggegationRange],
    keyed: bool = True,
)
```

> * see [ParadeDB Range Aggregation](https://docs.paradedb.com/documentation/aggregates/bucket/range).
> * see [Tantivy for more](https://docs.rs/tantivy/latest/tantivy/aggregation/bucket/struct.RangeAggregation.html)


**Example**

```python
from paradedb.aggregates import Range, RangeAggegationRange

Article.objects.filter(All(match_op=True)).aggregate(
        range_histogram=Range(
            "created",
            ranges=[
                RangeAggegationRange(
                    from_=timezone.datetime(2022, 1, 1), to=timezone.datetime(2022, 1, 2)
                ),
                RangeAggegationRange(from_=date(2022, 1, 2), to=date(2022, 1, 3)),
            ],
        )
    )
```

### RangeAggegationRange

```python
RangeAggegationRange(
    from_: float | int | date | datetime,
    to: float | int | date | datetime,
    key: str | None = None,
)
```

---

## Avg

```python
Avg(
    field: str,
    missing: float | int | None = None,
)
```

> * see [ParadeDB Average Aggregation](https://docs.paradedb.com/documentation/aggregates/metrics/average).
> * see [Tantivy for more](https://docs.rs/tantivy/latest/tantivy/aggregation/metric/struct.AverageAggregation.html)


**Example**

```python
from paradedb.aggregates import Avg
Article.objects.filter(All(match_op=True)).aggregate(
        avg_rank=aggregates.Avg("rank")
    )
```

---

## Cardinality

```python
Cardinality(
    field: str,
    missing: float | int | str | None = None,
)
```


> * see [ParadeDB Cardinality Aggregation](https://docs.paradedb.com/documentation/aggregates/metrics/cardinality).
> * see [Tantivy for more](https://docs.rs/tantivy/latest/tantivy/aggregation/metric/struct.CardinalityAggregationReq.html)


**Example**

```python
from paradedb.aggregates import Cardinality

Article.objects.filter(All(match_op=True)).aggregate(
        cardinality=Cardinality("rank", filter=models.Q(rank__gte=1) & models.Q(rank__lte=4))
    )
```

---

## Min

```python
Min(
    field: str,
    missing: float | int | None = None,
)
```



> * see [ParadeDB Min Aggregation](https://docs.paradedb.com/documentation/aggregates/metrics/minmax).
> * see [Tantivy for more](https://docs.rs/tantivy/latest/tantivy/aggregation/metric/struct.MinAggregation.html)

**Example**

```python
from paradedb.aggregates import Min
Article.objects.filter(rank__gte=1).aggregate(m=Min("rank", filter=models.Q(id__all=True)))
```

---

## Max

```python
Max(
    field: str,
    missing: float | int | None = None,
)
```


> * see [ParadeDB Max Aggregation](https://docs.paradedb.com/documentation/aggregates/metrics/minmax).
> * see [Tantivy for more](https://docs.rs/tantivy/latest/tantivy/aggregation/metric/struct.MaxAggregation.html)

**Example**

```python
from paradedb.aggregates import Max

Article.objects.aggregate(m=Max("rank", filter=models.Q(id__all=True)))
```

---

## Percentile

```python
Percentile(
    field: str,
    percents: list[float | int] | None = None,
    missing: float | int | None = None,
    keyed: bool = True,
)
```


> * see [ParadeDB Percentile Aggregation](https://docs.paradedb.com/documentation/aggregates/metrics/percentiles).
> * see [Tantivy for more](https://docs.rs/tantivy/latest/tantivy/aggregation/metric/struct.PercentilesAggregationReq.html)


**Example**

```python
from paradedb.aggregates import Percentile

Article.objects.aggregate(
        percentile=Percentile("rank", [10], filter=models.Q(id__all=True))
    )
```

---

## Stats

```python
Stats(
    field: str,
    missing: float | int | None = None,
)
```


> * see [ParadeDB Stats Aggregation](https://docs.paradedb.com/documentation/aggregates/metrics/stats).
> * see [Tantivy for more](https://docs.rs/tantivy/latest/tantivy/aggregation/metric/struct.StatsAggregation.html)

**Example**

```python
from paradedb.aggregates import Stats

Article.objects.aggregate(stats=Stats("rank", filter=models.Q(id__all=True)))
```

---

## Sum

```python
Sum(
    field: str,
    missing: float | int | None = None,
)
```


> * see [ParadeDB Sum Aggregation](https://docs.paradedb.com/documentation/aggregates/metrics/sum).
> * see [Tantivy for more](https://docs.rs/tantivy/latest/tantivy/aggregation/metric/struct.SumAggregation.html)

**Example**

```python
from paradedb.aggregates import Sum

Article.objects.aggregate(total_score=Sum("rank", filter=models.Q(id__all=True)))
```

---

## TopHit

```python
TopHit(
    sort: list[TopHitSort] | list[dict[str, str]],
    size: int,
    from_: int | None = None,
    docvalue_fields=None,
)
```


> * see [ParadeDB TopHit Aggregation](https://docs.paradedb.com/documentation/aggregates/metrics/tophits).
> * see [Tantivy fro more](https://docs.rs/tantivy/latest/tantivy/aggregation/metric/struct.TopHitsAggregationReq.html)

**Example**

```python
from paradedb.aggregates import TopHit, TopHitSort

Article.objects.aggregate(
        top=TopHit(
            size=100,
            sort=[TopHitSort(field="created", order="desc")],
            docvalue_fields=["rank", "created", "id"],
            filter=models.Q(id__all=True),
        )
    )
```

### TopHitSort

```python
TopHitSort(
    field: str,
    order: Literal["asc", "desc"] = "asc",
)
```

---

## Facet

```python
Facet(aggregate: Aggregate)
```


> * see [ParadeDB Facet Aggregation](https://docs.paradedb.com/documentation/aggregates/facets).

**Example**

```python
from paradedb.aggregates import Facet, Term

Article.objects.annotate(
    facet=Facet(Term("category"))
)
```

---
