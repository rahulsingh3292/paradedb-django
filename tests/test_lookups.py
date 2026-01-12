from ecommerce.models import Article

from django.test import TestCase
from django.utils import timezone

from paradedb.cast import ValueCast
from paradedb.expressions import *
from paradedb.lookups import LookupParameter


class TestExpressions(TestCase):

    def test_lookup_match(self):
        qs = Article.objects.filter(
            user__username__match="username_match"
        ).select_related("user")
        bool(qs[:1])

    def test_lookup_pdb_search(self):
        qs = Article.objects.filter(
            user__username__pdb_search=LookupParameter("username search")
        ).select_related("user")
        bool(qs[:1])

    def test_lookup_match_with_param(self):
        qs = Article.objects.filter(
            user__email__match=LookupParameter(value="match email")
        ).select_related("user")
        bool(qs[:1])

    def test_lookup_regex(self):
        qs = Article.objects.filter(
            user__email__pdb_regex="^.*@.*\\..*$"
        ).select_related("user")
        bool(qs[:1])

    def test_lookup_range(self):
        qs = Article.objects.filter(
            created__pdb_range=(
                "daterange",
                timezone.datetime(2021, 1, 1),
                timezone.datetime(2022, 1, 1),
                "[]",
            )
        )
        bool(qs[:1])

    def test_lookup_range_term_date(self):
        qs = Article.objects.filter(
            date_range__range_term=(
                "'[2025-09-02,2025-09-10]'",
                "daterange",
                "Intersects",
            )
        )
        bool(qs[:1])

    def test_lookup_range_term_price(self):
        qs = Article.objects.filter(
            price_range__range_term=(
                "'[0,100]'",
                "int4range",
                "Intersects",
            )
        )
        bool(qs[:1])

    def test_lookup_term_title(self):
        qs = Article.objects.filter(title__term="term")
        bool(qs[:1])

    def test_lookup_term_related(self):
        qs = Article.objects.filter(user__email__term="term")
        bool(qs[:1])

    def test_lookup_fuzzy_term(self):
        qs = Article.objects.filter(title__fuzzy_term=("fuzzy", 2, True))
        bool(qs[:1])

    def test_lookup_phrase_prefix(self):
        qs = Article.objects.filter(
            title__phrase_prefix=LookupParameter(["deep", "learn"], "2")
        )
        bool(qs[:1])

    def test_lookup_boolean(self):
        qs = Article.objects.filter(
            user__related__boolean={"must": [Term("username", "v")]}
        ).select_related("user")
        bool(qs[:1])

    def test_lookup_more_like_this_id(self):
        qs = Article.objects.filter(
            id__more_like_this=LookupParameter(
                123,
                fields=["title", "description"],
                match_op=True,
            )
        )
        bool(qs[:1])

    def test_lookup_more_like_this_document(self):
        qs = Article.objects.filter(
            user__related__more_like_this=LookupParameter(
                document={"username": "u"},
                min_term_frequency=1,
                max_query_terms=20,
            )
        ).select_related("user")
        bool(qs[:1])

    def test_lookup_parse_with_field(self):
        qs = Article.objects.filter(
            id__parse_with_field=LookupParameter(
                "title:well AND description:well",
                lenient=True,
                conjunction_mode=True,
            )
        )
        bool(qs[:1])

    def test_lookup_const_score(self):
        qs = Article.objects.filter(
            id__const_score=LookupParameter(
                1.0,
                Match(field="title", value="shoes"),
            )
        )
        bool(qs[:1])

    def test_lookup_boost(self):
        qs = Article.objects.filter(
            id__boost=LookupParameter(
                1.0,
                Match(field="title", value="shoes"),
            )
        )
        bool(qs[:1])

    def test_lookup_disjunction_max(self):
        qs = Article.objects.filter(
            user__related__disjunction_max=LookupParameter(
                disjuncts=[
                    Term(field="username", value="running"),
                    Term(field="username", value="shoes"),
                ],
                tie_breaker=1,
            )
        ).select_related("user")
        bool(qs[:1])

    def test_lookup_term_set(self):
        qs = Article.objects.filter(
            id__term_set=LookupParameter(
                terms=[
                    Term(field="rank", value=1),
                    Term(field="rank", value=200),
                ]
            )
        )
        bool(qs[:1])

    def test_lookup_phrase(self):
        qs = Article.objects.filter(
            title__phrase=LookupParameter(
                pharses=["quick", "brown", "fox"],
                slop=3,
            )
        )
        bool(qs[:1])

    def test_lookup_empty(self):
        qs = Article.objects.filter(id__empty=True)
        bool(qs[:1])

    # -------------------------
    # V2 LOOKUPS
    # -------------------------

    def test_lookup_term_v2(self):
        qs = Article.objects.filter(title__term_v2="term")
        bool(qs[:1])

        qs_with_cast = Article.objects.filter(
            title__term_v2=ValueCast("term cast", "pdb.whitespace")
        )
        bool(qs_with_cast[:1])

        qs_with_json_simple = Article.objects.filter(metadata__field1__term_v2="term")
        bool(qs_with_json_simple[:1])

        qs_with_json_cast = Article.objects.filter(
            metadata__field1__term_v2=ValueCast("term cast", "pdb.whitespace")
        )
        bool(qs_with_json_cast[:1])

    def test_match_v2(self):
        qs = Article.objects.filter(title__match_v2="django")
        bool(qs[:1])

        qs_with_cast = Article.objects.filter(
            title__match_v2=ValueCast("django", "pdb.whitespace")
        )
        bool(qs_with_cast[:1])

        qs_with_json_simple = Article.objects.filter(
            metadata__field1__match_v2="django"
        )
        bool(qs_with_json_simple[:1])

        qs_with_json_cast = Article.objects.filter(
            metadata__field1__match_v2=ValueCast("django", "pdb.whitespace")
        )
        bool(qs_with_json_cast[:1])

    def test_phrase_v2(self):
        qs = Article.objects.filter(title__phrase_v2="django")
        bool(qs[:1])

        qs_with_cast = Article.objects.filter(
            title__phrase_v2=ValueCast("django", "pdb.whitespace")
        )
        bool(qs_with_cast[:1])

        qs_with_json_simple = Article.objects.filter(
            metadata__field1__phrase_v2="django"
        )
        bool(qs_with_json_simple[:1])

        qs_with_json_cast = Article.objects.filter(
            metadata__field1__phrase_v2=ValueCast("django", "pdb.whitespace")
        )
        bool(qs_with_json_cast[:1])

    def test_match_cojunction_v2(self):
        qs = Article.objects.filter(title__match_conjunction="django")
        bool(qs[:1])

        qs_with_cast = Article.objects.filter(
            title__match_conjunction=ValueCast("django", "pdb.whitespace")
        )
        bool(qs_with_cast[:1])

        qs_with_json_simple = Article.objects.filter(
            metadata__field1__match_conjunction="django"
        )
        bool(qs_with_json_simple[:1])

        qs_with_json_cast = Article.objects.filter(
            metadata__field1__field_2__match_conjunction=ValueCast(
                "django", "pdb.whitespace"
            )
        )
        bool(qs_with_json_cast[:1])

    # others
    def test_pdb(self):
        qs = Article.objects.filter(title__pdb="django")
        bool(qs[:1])

    def test_lookup_proximity_v2(self):
        qs = Article.objects.filter(
            title__proximity=[
                (
                    "django",
                    "##",
                    "1",
                    "##>",
                    ProximityRegex("m.*"),
                    "##>",
                    100,
                    "##",
                    ProximityArray(["wow", ProximityRegex("wow", 10, wrap=False)]),
                )
            ]
        )
        bool(qs[:1])

    def test_lookup_json_op(self):
        _1_path = Article.objects.filter(metadata__field1__json_op="django")
        bool(_1_path[:1])
        _2_path = Article.objects.filter(metadata__field1__field2__json_op="django")
        bool(_2_path[:1])

    def test_lookup_json_op_with_custom_operator(self):
        match = Article.objects.filter(metadata__field1__match__json_op="django")
        bool(match[:1])
        phrase = Article.objects.filter(metadata__field1__phrase__json_op="django")
        bool(phrase[:1])
        term = Article.objects.filter(metadata__field1__term__json_op="django")
        bool(term[:1])
        conjunction = Article.objects.filter(
            metadata__field1__f2__match_conjunction__json_op="django"
        )
        bool(conjunction[:1])

    def test_v2_on_array_field(self):
        array_with_term = Article.objects.filter(tags__term_v2="django")
        bool(array_with_term[:1])

        array_with_cast = Article.objects.filter(
            tags__term_v2=ValueCast("django", "pdb.whitespace")
        )
        bool(array_with_cast[:1])

        array_with_phrase = Article.objects.filter(tags__phrase_v2="django")
        bool(array_with_phrase[:1])

        array_with_cast = Article.objects.filter(
            tags__phrase_v2=ValueCast("django", "pdb.whitespace")
        )
        bool(array_with_cast[:1])

        array_with_match = Article.objects.filter(tags__match_v2="django")
        bool(array_with_match[:1])

        array_with_cast = Article.objects.filter(
            tags__match_v2=ValueCast("django", "pdb.whitespace")
        )
        bool(array_with_cast[:1])

        array_with_match_conjunction = Article.objects.filter(
            tags__match_conjunction="django"
        )
        bool(array_with_match_conjunction[:1])

        array_with_cast = Article.objects.filter(
            tags__match_conjunction=ValueCast("django", "pdb.whitespace")
        )
        bool(array_with_cast[:1])
