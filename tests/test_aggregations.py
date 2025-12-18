from ecommerce.models import Article

from django.db import models
from django.test import TestCase
from django.utils import timezone

from paradedb.aggregates import (
    Avg,
    Cardinality,
    Count,
    DateHistogram,
    Facet,
    Histogram,
    Max,
    Min,
    Percentile,
    Range,
    RangeAggegationRange,
    Stats,
    Sum,
    Term,
    TopHit,
    TopHitSort,
)
from paradedb.expressions import All, Match
from paradedb.sql import get_version


if get_version() >= "0.20":

    class TestAggregations(TestCase):

        def test_count(self):
            Article.objects.aggregate(
                count=Count(
                    "id",
                    filter=models.Q(id__pdb_exists=[]),
                )
            )

        def test_term_aggregation(self):
            Article.objects.filter(All(match_op=True)).aggregate(
                count=Term(
                    "rank",
                    order={"max_count": "desc"},
                    aggs={
                        "max_count": Count("id").build_json(as_dict=True),
                    },
                )
            )

        def test_annotated_count(self):
            (
                Article.objects.filter(All(match_op=True))
                .values("rank")
                .annotate(
                    count=Count(
                        "id",
                        filter=models.Q(rank__gt=1),
                    )
                )
                .values("rank", "count")
                .order_by("-rank")
            )

        def test_date_histogram(self):
            min_date = Article.objects.aggregate(m=models.Min("created"))[
                "m"
            ] or timezone.datetime(2021, 1, 1)

            max_date = Article.objects.aggregate(m=models.Max("created"))[
                "m"
            ] or timezone.datetime(2022, 1, 1)

            hard_bounds = (
                int(min_date.timestamp() * 1000.0),
                int(max_date.timestamp() * 1000.0),
            )

            Article.objects.filter(All(match_op=True)).aggregate(
                date_histogram=DateHistogram(
                    "created",
                    "30d",
                    max_doc_count=100,
                    hard_bounds=hard_bounds,
                    extended_bounds=hard_bounds,
                    keyed=True,
                )
            )

        def test_rank_histogram(self):
            Article.objects.filter(All(match_op=True)).aggregate(
                rank_histogram=Histogram(
                    "rank",
                    "1",
                    extended_bounds=(1, 5),
                    hard_bounds=(1, 5),
                )
            )

        def test_range_aggregation(self):
            from datetime import date

            Article.objects.filter(All(match_op=True)).aggregate(
                range_histogram=Range(
                    "created",
                    ranges=[
                        RangeAggegationRange(
                            from_=timezone.datetime(2022, 1, 1),
                            to=timezone.datetime(2022, 1, 2),
                            key="1",
                        ),
                        RangeAggegationRange(
                            from_=date(2022, 1, 2),
                            to=date(2022, 1, 3),
                            key="2",
                        ),
                    ],
                )
            )

        def test_avg_rank_with_missing(self):
            Article.objects.filter(All(match_op=True)).aggregate(
                avg_rank=Avg(
                    "rank",
                    missing=1.0,
                )
            )

        def test_min_rank(self):
            Article.objects.filter(rank__gte=1).aggregate(
                m=Min(
                    "rank",
                    filter=models.Q(id__all=True),
                )
            )

        def test_max_rank(self):
            Article.objects.filter(All(match_op=True)).filter(rank__lte=4).aggregate(
                m=Max("rank")
            )

        def test_sum_rank(self):
            Article.objects.filter(All(match_op=True)).aggregate(m=Sum("rank"))

        def test_avg_rank(self):
            Article.objects.filter(All(match_op=True)).aggregate(m=Avg("rank"))

        def test_stats(self):
            Article.objects.filter(All(match_op=True)).aggregate(stats=Stats("rank"))

        def test_percentile(self):
            Article.objects.filter(All(match_op=True)).aggregate(
                percentile=Percentile("rank", [0.1])
            )

        def test_cardinality(self):
            Article.objects.filter().aggregate(
                cardinality=Cardinality(
                    "rank",
                    filter=(
                        models.Q(rank__gte=1)
                        & models.Q(rank__lte=4)
                        & models.Q(id__all=True)
                    ),
                )
            )

        def test_top_hits(self):
            Article.objects.filter().aggregate(
                top=TopHit(
                    size=100,
                    sort=[
                        TopHitSort(
                            field="created",
                            order="desc",
                        )
                    ],
                    docvalue_fields=["rank", "created", "id"],
                    filter=Match("title", "quick", match_op=True),
                )
            )

        def test_facet(self):
            qs = (
                Article.objects.filter()
                .annotate(facet=Facet(Count("rank")))
                .order_by("-rank")
            )
            bool(qs[:1])
