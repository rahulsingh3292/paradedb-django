from django.apps import apps
from django.db import models
from django.db.models import (
    CharField,
    ForeignKey,
    Lookup,
    ManyToManyField,
    OneToOneField,
)
from django.db.models.fields import Field

from paradedb import settings
from paradedb.cast import ValueCast
from paradedb.utils import KeyField

from .expressions import (
    All,
    Bm25Score,
    Boolean,
    Boost,
    ConstScore,
    DisjunctionMax,
    Empty,
    Exists,
    FuzzyTerm,
    Match,
    MoreLikeThis,
    Parse,
    ParseWithField,
    Phrase,
    PhrasePrefix,
    Proximity,
    Range,
    RangeTerm,
    Regex,
    Search,
    Snippet,
    Term,
    TermSet,
)


__all__ = [
    "ModelResolverFromTable",
    "LookupParameter",
    "ExpressionLookup",
    "AllLookup",
    "EmptyLookup",
    "SearchLookup",
    "MatchLookup",
    "ExistsLookup",
    "RangeLookup",
    "RangeTermLookup",
    "RegexLookup",
    "TermLookup",
    "TermSetLookup",
    "FuzzyTermLookup",
    "PhraseLookup",
    "PhrasePrefixLookup",
    "ConstScoreLookup",
    "Bm25ScoreLookup",
    "BoostLookup",
    "DisjunctionMaxLookup",
    "BooleanLookup",
    "MoreLikeThisLookup",
    "ParseWithFieldLookup",
    "ParseLookup",
    "SnippetLookup",
    "RelatedTableTransform",
    "MatchV2Lookup",
    "MatchConjunctionLookup",
    "PhraseV2Lookup",
    "TermV2Lookup",
    "ProximityLookup",
]


def register_lookup_for_all_fields(lookup_cls):
    for f in [ForeignKey, ManyToManyField, OneToOneField, Field, CharField]:
        f.register_lookup(lookup_cls)
    return lookup_cls


class ModelNotFoundError(Exception):
    pass


class ModelResolverFromTable:
    _model_cache = {}

    @classmethod
    def resolve_model(cls, table: str):
        if table in cls._model_cache:
            return cls._model_cache[table]

        raise ModelNotFoundError(f"Could not resolve model for table ({table})")

    @classmethod
    def preload(cls):
        for app in apps.get_app_configs():
            for model in app.get_models():
                cls._model_cache[model._meta.db_table] = model


class LookupParameter:
    """
    Wraps RHS parameters for ParadeDB lookups.
    Used for forwarding *args and **kwargs into expression constructors.
    """

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __repr__(self):
        return f"LookupParameter(args={self.args}, kwargs={self.kwargs})"


class ExpressionLookup(Lookup):
    """
    Base class for all ParadeDB lookups.
    Converts RHS into LookupParameter so the expression receives *args, **kwargs.
    """

    expr_class = None  # must be overridden in subclasses
    include_column_with_table_name = False
    exclude_field_in_expression = False
    exclude_args = False
    extra_param_kwargs = None

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)

        try:
            rhs, rhs_params = self.process_rhs(compiler, connection)
        except Exception:
            rhs, rhs_params = None, ()

        alias_map = compiler.query.alias_map

        try:
            alias, field = lhs.replace('"', "").split(".")
            table = alias
            if alias in alias_map:
                table = alias_map[alias].table_name
            model = ModelResolverFromTable.resolve_model(table)
            if self.include_column_with_table_name:
                field = f"{alias}.{field}"
        except Exception as e:
            if (
                isinstance(e, ModelNotFoundError)
                and settings.PARADEDB_RAISE_ON_MODEL_NOT_FOUND
            ):
                raise e

            model = compiler.query.model
            table = model._meta.db_table
            alias = table
            field = lhs

        value = getattr(self, "rhs_original", rhs or rhs_params)

        if isinstance(value, ValueCast):
            params = LookupParameter(value)

        elif isinstance(value, LookupParameter):
            params = value

        elif isinstance(value, (list, tuple)):
            params = LookupParameter(*value)

        elif isinstance(value, dict):
            params = LookupParameter(**value)

        else:
            params = LookupParameter(value)

        if self.extra_param_kwargs:
            assert isinstance(
                self.extra_param_kwargs, dict
            ), "extra_param_kwargs must be a dict"
            params.kwargs.update(self.extra_param_kwargs or {})

        if "key_field" not in params.kwargs:
            if hasattr(model, "paradedb_key_field"):
                primary_key_field = getattr(model, "paradedb_key_field")
            else:
                primary_key_field = model._meta.pk.name or "id"

            params.kwargs["key_field"] = KeyField(
                table=alias, primary_key_field=primary_key_field
            )

        if self.exclude_field_in_expression:
            expr = self.expr_class(
                *(params.args if not self.exclude_args else []), **params.kwargs
            )
        else:
            expr = self.expr_class(
                field, *(params.args if not self.exclude_args else []), **params.kwargs
            )

        if hasattr(expr, "match_op"):
            expr.match_op = params.kwargs.pop("match_op", True)

        if hasattr(self, "post_process_expression"):
            processed = self.post_process_expression(expr, field)
            if processed and isinstance(processed, expr):
                expr = processed

        return expr.as_sql(compiler, connection)

    def get_prep_lookup(self):
        if self.lookup_name in (settings.PARADEDB_LOOKUP_SKIP_RHS_PREP or []):
            return self.rhs
        return super().get_prep_lookup()


@register_lookup_for_all_fields
class AllLookup(ExpressionLookup):
    lookup_name = "all"
    expr_class = All
    exclude_field_in_expression = True
    exclude_args = True

    def get_prep_lookup(self):
        return self.rhs


@register_lookup_for_all_fields
class EmptyLookup(ExpressionLookup):
    lookup_name = "empty"
    expr_class = Empty
    exclude_field_in_expression = True
    exclude_args = True

    def get_prep_lookup(self):
        return self.rhs


@register_lookup_for_all_fields
class SearchLookup(ExpressionLookup):
    lookup_name = "pdb_search"
    expr_class = Search
    include_column_with_table_name = True
    extra_param_kwargs = {"op": "@@@"}

    def get_prep_lookup(self):
        return self.rhs


@register_lookup_for_all_fields
class MatchLookup(ExpressionLookup):
    lookup_name = "match"
    expr_class = Match


@register_lookup_for_all_fields
class ExistsLookup(ExpressionLookup):
    lookup_name = "pdb_exists"
    expr_class = Exists
    exclude_args = True

    def get_prep_lookup(self):
        return self.rhs


@register_lookup_for_all_fields
class RangeLookup(ExpressionLookup):
    lookup_name = "pdb_range"
    expr_class = Range

    def get_prep_lookup(self):
        return self.rhs


@register_lookup_for_all_fields
class RangeTermLookup(ExpressionLookup):
    lookup_name = "range_term"
    expr_class = RangeTerm

    def get_prep_lookup(self):
        return self.rhs


@register_lookup_for_all_fields
class RegexLookup(ExpressionLookup):
    lookup_name = "pdb_regex"
    expr_class = Regex


@register_lookup_for_all_fields
class TermLookup(ExpressionLookup):
    lookup_name = "term"
    expr_class = Term


@register_lookup_for_all_fields
class TermSetLookup(ExpressionLookup):
    lookup_name = "term_set"
    expr_class = TermSet
    exclude_field_in_expression = True

    def get_prep_lookup(self):
        return self.rhs


@register_lookup_for_all_fields
class FuzzyTermLookup(ExpressionLookup):
    lookup_name = "fuzzy_term"
    expr_class = FuzzyTerm


@register_lookup_for_all_fields
class PhraseLookup(ExpressionLookup):
    lookup_name = "phrase"
    expr_class = Phrase


@register_lookup_for_all_fields
class PhrasePrefixLookup(ExpressionLookup):
    lookup_name = "phrase_prefix"
    expr_class = PhrasePrefix


@register_lookup_for_all_fields
class ConstScoreLookup(ExpressionLookup):
    lookup_name = "const_score"
    expr_class = ConstScore
    exclude_field_in_expression = True

    def get_prep_lookup(self):
        return self.rhs


@register_lookup_for_all_fields
class BoostLookup(ExpressionLookup):
    lookup_name = "boost"
    expr_class = Boost
    exclude_field_in_expression = True

    def get_prep_lookup(self):
        return self.rhs


@register_lookup_for_all_fields
class Bm25ScoreLookup(ExpressionLookup):
    lookup_name = "bm25_score"
    expr_class = Bm25Score
    exclude_field_in_expression = True

    def get_prep_lookup(self):
        return self.rhs


@register_lookup_for_all_fields
class DisjunctionMaxLookup(ExpressionLookup):
    lookup_name = "disjunction_max"
    expr_class = DisjunctionMax
    exclude_field_in_expression = True

    def get_prep_lookup(self):
        return self.rhs


@register_lookup_for_all_fields
class BooleanLookup(ExpressionLookup):
    lookup_name = "boolean"
    expr_class = Boolean
    exclude_field_in_expression = True

    def get_prep_lookup(self):
        return self.rhs


@register_lookup_for_all_fields
class MoreLikeThisLookup(ExpressionLookup):
    lookup_name = "more_like_this"
    expr_class = MoreLikeThis
    exclude_field_in_expression = True

    def get_prep_lookup(self):
        return self.rhs


@register_lookup_for_all_fields
class ParseWithFieldLookup(ExpressionLookup):
    lookup_name = "parse_with_field"
    expr_class = ParseWithField

    def get_prep_lookup(self):
        return self.rhs


@register_lookup_for_all_fields
class ParseLookup(ExpressionLookup):
    lookup_name = "parse"
    expr_class = Parse

    def get_prep_lookup(self):
        return self.rhs


@register_lookup_for_all_fields
class SnippetLookup(ExpressionLookup):
    lookup_name = "snippet"
    expr_class = Snippet

    def get_prep_lookup(self):
        return self.rhs


@register_lookup_for_all_fields
class RelatedTableTransform(models.Transform):
    lookup_name = "related"

    def as_sql(self, compiler, connection):
        lhs_sql, lhs_params = compiler.compile(self.lhs)
        rel_field = self.lhs.field
        rel_model = rel_field.related_model
        rel_table = rel_model._meta.db_table
        rel_pk = getattr(rel_model, "paradedb_key_field", rel_model._meta.pk.column)
        sql = f"{rel_table}.{rel_pk}"
        return sql, lhs_params


# V2 lookup
@register_lookup_for_all_fields
class MatchV2Lookup(SearchLookup):
    lookup_name = "match_v2"
    extra_param_kwargs = {"op": "|||"}


@register_lookup_for_all_fields
class MatchConjunctionLookup(SearchLookup):
    lookup_name = "match_v2_conjunction"
    extra_param_kwargs = {"op": "&&&"}


@register_lookup_for_all_fields
class PhraseV2Lookup(SearchLookup):
    lookup_name = "phrase_v2"
    extra_param_kwargs = {"op": "###"}


@register_lookup_for_all_fields
class TermV2Lookup(SearchLookup):
    lookup_name = "term_v2"
    extra_param_kwargs = {"op": "==="}


@register_lookup_for_all_fields
class ProximityLookup(ExpressionLookup):
    lookup_name = "proximity"
    expr_class = Proximity
    exclude_field_in_expression = True

    def get_prep_lookup(self):
        return self.rhs

    def post_process_expression(self, expression, field):
        assert field is not None, "field cannot be None"
        expression.pfield = field
