from datetime import date

from ecommerce.models import Article

from django.db import models
from django.test import TestCase

from paradedb.expressions import (
    All,
    Boolean,
    Boost,
    ConstScore,
    DisjunctionMax,
    Exists,
    FuzzyTerm,
    Match,
    MoreLikeThis,
    Parse,
    ParseWithField,
    Phrase,
    PhrasePrefix,
    Proximity,
    ProximityArray,
    ProximityRegex,
    Range,
    RangeTerm,
    Regex,
    Search,
    Term,
    TermSet,
)
from paradedb.lookups import LookupParameter
from paradedb.utils import TableField


class TestExpressions(TestCase):

    def test_search(self):
        qs = Article.objects.filter(Search(field="title", value="well", escaped=False))
        bool(qs[:1])

    def test_match(self):
        qs = Article.objects.filter(
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
        bool(qs[:1])

    def test_match_with_lookup(self):
        qs = Article.objects.filter(
            title__match=LookupParameter(
                value="python",
                distance=1,
                conjunction_mode=False,
                prefix=True,
                tokenizer="whitespace",
            )
        )
        bool(qs[:1])

    def test_exists(self):
        qs = Article.objects.filter(Exists(match_op=True))
        bool(qs[:1])

    def test_all(self):
        qs = Article.objects.filter(All(match_op=True))
        bool(qs[:1])

    def test_range_date(self):
        qs = Article.objects.select_related("user").filter(
            Range(
                field=models.F("user__date_joined"),
                range_type="daterange",
                start=date(2025, 9, 2),
                end=date(2025, 9, 10),
                bounds="[)",
                match_op=True,
            )
        )
        bool(qs[:1])

    def test_range_int(self):
        qs = Article.objects.filter(
            Range("rank", "int4range", 1, 3, "()", match_op=True)
        )
        bool(qs[:1])

    def test_range_end_with_null(self):
        qs = Article.objects.filter(Range("rank", "int4range", start=1, match_op=True))
        bool(qs[:1])

    def test_range_term_date(self):
        qs = Article.objects.filter(
            RangeTerm(
                field=models.F("date_range"),
                term_or_range="'[2025-09-02,2025-09-10]'",
                cast=Range.RangeType.DATERANGE,
                relation=RangeTerm.Relation.Intersects,
                match_op=True,
            )
        )
        bool(qs[:1])

    def test_range_term_numrange(self):
        qs = Article.objects.filter(
            RangeTerm(
                field=models.F("price_range"),
                term_or_range="'[1,3]'",
                cast=RangeTerm.Cast.numrange,
                relation=RangeTerm.Relation.Intersects,
                match_op=True,
            )
        )
        bool(qs[:1])

    def test_range_term_integer(self):
        qs = Article.objects.filter(
            RangeTerm("price_range", 1, cast=RangeTerm.Cast.integer, match_op=True)
        )
        bool(qs[:1])

    def test_regex(self):
        qs = Article.objects.filter(Regex("title", "^well$", match_op=True))
        bool(qs[:1])

    def test_term(self):
        qs = Article.objects.filter(Term("rank", 100, match_op=True))
        bool(qs[:1])

    def test_term_set(self):
        qs = Article.objects.filter(
            TermSet([Term("rank", 1), Term("rank", 200)], match_op=True)
        )
        bool(qs[:1])

    def test_fuzzy_term(self):
        qs = Article.objects.filter(
            FuzzyTerm("title", "well", 2, False, True, match_op=True)
        )
        bool(qs[:1])

    def test_phrase(self):
        qs = Article.objects.select_related("user").filter(
            Phrase(
                TableField("title", Article),
                ["quick", "brown", "fox"],
                3,
                match_op=True,
            )
        )
        bool(qs[:1])

    def test_phrase_prefix(self):
        qs = Article.objects.filter(
            PhrasePrefix("title", ["deep", "learn"], 5, match_op=True)
        )
        bool(qs[:1])

    def test_boolean(self):
        qs = Article.objects.filter(
            Boolean(
                must=[Match("title", "python")],
                must_not=[Match("description", "python", tokenizer="raw")],
                should=[
                    Term("title", "python"),
                    ConstScore(1.0, Term("title", "python")),
                ],
                match_op=True,
            )
        )
        bool(qs[:1])

    def test_boost(self):
        qs = Article.objects.filter(
            Boolean(
                should=[Term("title", "running"), Boost(1.0, Match("title", "shoes"))],
                match_op=True,
            )
        )
        bool(qs[:1])

    def test_disjunction_max(self):
        qs = Article.objects.filter(
            DisjunctionMax(
                [Term("title", "running"), Term("title", "shoes")],
                1,
                match_op=True,
            )
        )
        bool(qs[:1])

    def test_parse(self):
        qs = Article.objects.filter(
            Parse("title:well AND description:well", True, True, "id", match_op=True)
        )
        bool(qs[:1])

    def test_parse_with_field(self):
        qs = Article.objects.filter(
            ParseWithField("title", "well", True, True, match_op=True)
            & ParseWithField("description", "hello", True, match_op=True)
        )
        bool(qs[:1])

    def test_proximity(self):
        qs = Article.objects.filter(
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
                "title",
            )
        )
        bool(qs[:1])

    def test_more_like_this(self):
        qs = Article.objects.filter(
            MoreLikeThis(123, fields=["title", "description"], match_op=True)
        )
        bool(qs[:1])

    def test_more_like_this_id(self):
        qs = Article.objects.filter(MoreLikeThis(document={"id": 123}, match_op=True))
        bool(qs[:1])
