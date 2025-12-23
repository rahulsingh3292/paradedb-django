from __future__ import annotations

import datetime
import json
import typing

from django.db import models
from django.db.models.expressions import Expression

from paradedb import settings
from paradedb.cast import ValueCast
from paradedb.sql import get_version
from paradedb.tokenizers import Tokenizer
from paradedb.utils import (
    KeyField,
    TableField,
    escape_query,
    postgres_array,
    resolve_f_model_and_field,
)


__all__ = [
    "All",
    "Empty",
    "Proximity",
    "Search",
    "Match",
    "Exists",
    "Range",
    "RangeTerm",
    "Regex",
    "Term",
    "TermSet",
    "FuzzyTerm",
    "Phrase",
    "PhrasePrefix",
    "ConstScore",
    "Bm25Score",
    "Boost",
    "DisjunctionMax",
    "Boolean",
    "Snippet",
    "MoreLikeThis",
    "Parse",
    "ParseWithField",
    "ProximityArray",
    "ProximityRegex",
    "JsonOp",
]


ParadeDbFunctionExpression: typing.TypeAlias = Expression


def _get_schema(legacy=False, func=None):
    if legacy:
        return "paradedb"

    if func and func in settings.PARADEDB_USE_LEGACY:
        return "paradedb"

    if settings.PARADEBD_USE_V2:
        return "pdb"

    version = get_version()

    if version >= "0.20":
        return "pdb"

    return "paradedb"


def _normalize_bool(value: bool) -> str:
    return "true" if value else "false"


def _resolve_field_name(
    compiler, field: str | models.F | TableField, key_field: KeyField = None
):
    if isinstance(field, TableField):
        return field.get_sql()
    if isinstance(field, models.F):
        model, field, alias = resolve_f_model_and_field(field, compiler.query)
        return f"{alias}.{field}"
    else:
        return field if not key_field else f"{key_field.get_table()}.{field}"


def _resolve_and_set_key_field(
    pfield: str | models.F | TableField,
    instance,
    connection,
    compiler,
    field_name="pfield",
    key_field_name="key_field",
):
    if isinstance(pfield, models.F):
        model, field, alias = resolve_f_model_and_field(pfield, compiler.query)
        if field_name is not None:
            setattr(instance, field_name, field)
        setattr(
            instance,
            key_field_name,
            KeyField(
                table=alias,
                primary_key_field=getattr(
                    model, "paradedb_key_field", model._meta.pk.name
                ),
            ),
        )

    if isinstance(pfield, TableField):
        if field_name is not None:
            setattr(instance, field_name, pfield.field)
        table, field = pfield.get_sql().split(".")
        primary_key_field = pfield.get_table_primary_key_field() or field
        setattr(
            instance,
            key_field_name,
            KeyField(table=table, primary_key_field=primary_key_field),
        )


def _resolve_value(value, connection, compiler):
    if isinstance(value, list):
        return postgres_array(value)
    if isinstance(value, models.Value):
        return connection.ops.compose_sql(*value.as_sql(compiler, connection))
    if isinstance(value, models.F):
        model, field, alias = resolve_f_model_and_field(value, compiler.query)
        return f"{alias}.{field}"
    return value


def _make_schema_sql(func, args, schema="paradedb", lhs=None, op="@@@", key_field=None):
    if lhs:
        sql = f"{lhs} {op} {schema}.{func}({','.join(args)})"
    else:
        sql = f"{schema}.{func}({','.join(args)})"
        if key_field:
            sql = f"{key_field} {op} {sql}"
    return sql


class All(Expression):
    def __init__(
        self,
        key_field: str | KeyField | models.F | TableField = "id",
        match_op: bool = False,
        *args,
        **kwargs,
    ):
        self.key_field = key_field
        self.match_op = match_op
        self.legacy = kwargs.pop("legacy", False)
        super().__init__(
            *args,
            output_field=kwargs.pop("output_field", models.BooleanField()),
            **kwargs,
        )

    def as_sql(self, compiler, connection):
        _resolve_and_set_key_field(
            self.key_field, self, connection, compiler, field_name=None
        )
        sql = "pdb.all()" if not self.legacy else "paradedb.all()"
        if self.match_op:
            sql = f"{self.key_field} @@@ {sql}"
        return sql, []

    def __repr__(self):
        return "All"


class Empty(Expression):
    def __init__(
        self,
        key_field: KeyField | str | models.F | TableField = "id",
        match_op: bool = False,
        *args,
        **kwargs,
    ):
        self.key_field = key_field
        self.match_op = match_op
        super().__init__(
            *args,
            output_field=kwargs.pop("output_field", models.BooleanField()),
            **kwargs,
        )

    def as_sql(self, compiler, connection):
        _resolve_and_set_key_field(
            self.key_field, self, connection, compiler, field_name=None
        )

        sql = "pdb.empty()"
        if self.match_op:
            sql = f"{self.key_field} @@@ {sql}"
        return sql, []

    def __repr__(self):
        return "Empty"


class Search(Expression):
    def __init__(
        self,
        field: str | models.F | TableField,
        value: str | ValueCast | ParadeDbFunctionExpression,
        escaped: bool = False,
        op: typing.Literal["@@@", "|||", "===", "###", "&&&"] = "@@@",
        *args,
        **kwargs,
    ):
        if op not in ["@@@", "|||", "===", "###", "&&&"]:
            raise ValueError("op must be one of '@@@", "|||", "===", "###", "&&&'")

        self.pfield = field
        self.value = value if not escaped else escape_query(value)
        self.op = op
        self.escaped = escaped
        self.key_field = kwargs.pop("key_field", None)
        self.legacy = kwargs.pop("legacy", False)

        super().__init__(
            *args,
            output_field=kwargs.pop("output_field", models.BooleanField()),
            **kwargs,
        )

    def as_sql(self, compiler, connection):
        sql = """{} {} """.format(_resolve_field_name(compiler, self.pfield), self.op)

        if isinstance(self.value, (Expression, models.Func, ValueCast)):
            value_sql = connection.ops.compose_sql(
                *self.value.as_sql(compiler, connection)
            )
            sql += value_sql
            return sql, []

        if isinstance(self.value, list):
            sql += " {}".format(postgres_array(self.value))
            return sql, []

        sql += " %s"

        return sql, [self.value]

    def __repr__(self):
        return f"SimpleSearch({self.pfield}, {self.value})"


class Match(Expression):
    def __init__(
        self,
        field: str | models.F | TableField,
        value: str,
        distance: int = 0,
        conjunction_mode: bool = False,
        tokenizer: typing.Optional[
            Tokenizer
            | typing.Optional[
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
        key_field: KeyField | str = "id",
        transposition_cost_one: str = True,
        prefix: bool = False,
        escaped: bool = False,
        match_op: bool = False,
        *args,
        **kwargs,
    ):
        if (
            tokenizer is not None
            and not isinstance(tokenizer, Tokenizer)
            and tokenizer
            not in [
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
        ):
            raise ValueError(
                f"Invalid tokenizer: {tokenizer}. Must be one of ['whitespace',"
                " 'keyword', 'ngram', 'regex', 'icu', 'jieba', 'chinese_lindera',"
                " 'chinese_compatible', 'source_code', 'raw']"
            )

        self.pfield = field
        self.value = value
        self.distance = distance
        self.conjunction_mode = conjunction_mode
        self.tokenizer = tokenizer
        self.key_field = key_field
        self.prefix = prefix
        self.transposition_cost_one = transposition_cost_one
        self.escaped = escaped
        self.match_op = match_op
        self.ignore_lhs = kwargs.pop("ignore_lhs", False)
        self.legacy = kwargs.pop("legacy", False)

        super().__init__(
            *args,
            output_field=kwargs.pop("output_field", models.BooleanField()),
            **kwargs,
        )

    def as_sql(self, compiler, connection):
        _resolve_and_set_key_field(self.pfield, self, connection, compiler)

        params = [
            self.value if not self.escaped else escape_query(self.value),
            self.normalize_bool(self.conjunction_mode),
            self.normalize_bool(self.transposition_cost_one),
            self.normalize_bool(self.prefix),
            self.distance,
        ]

        args = [
            " %s",
            " conjunction_mode:=%s",
            " transposition_cost_one:=%s",
            " prefix:=%s",
            "distance:=%s",
        ]

        schema = _get_schema(self.legacy, func="match")
        if include_field := schema == "paradedb":
            args.insert(0, "%s")
            params.insert(0, self.pfield)

        if self.tokenizer is not None:
            if isinstance(self.tokenizer, Tokenizer):
                raise ValueError("Tokenizer instance is not supported right now")
            else:
                args.append("tokenizer:=paradedb.tokenizer(%s)")
                params.append(self.tokenizer)

        return (
            _make_schema_sql(
                func="match",
                args=args,
                schema=schema,
                lhs=self.pfield if not self.ignore_lhs and not include_field else None,
                key_field=self.key_field if self.match_op else None,
            ),
            params,
        )

    def normalize_bool(self, value):
        return "true" if value else "false"

    def __repr__(self):
        return (
            f"Match(field={self.field}, value={self.value}, distance={self.distance},"
            f" conjunction_mode={self.conjunction_mode}, tokenizer={self.tokenizer},"
            f" key_field={self.key_field})"
        )


class Exists(Expression):
    def __init__(
        self,
        field: str | models.F | TableField = None,
        key_field: KeyField | str = "id",
        match_op: bool = False,
        *args,
        **kwargs,
    ):
        self.pfield = field
        self.key_field = key_field
        self.match_op = match_op
        self.ignore_lhs = kwargs.pop("ignore_lhs", False)
        self.legacy = kwargs.pop("legacy", False)

        super().__init__(
            *args,
            output_field=kwargs.pop("output_field", models.BooleanField()),
            **kwargs,
        )

    def as_sql(self, compiler, connection):
        _resolve_and_set_key_field(self.pfield, self, connection, compiler)

        params = [self.pfield] if self.pfield else []
        sql = """paradedb.exists(%s)""" if self.pfield else """pdb.exists()"""
        if self.match_op:
            sql = f"{self.key_field} @@@ {sql}"
        return sql, params

    def __repr__(self):
        return f"Exists(field={self.field}, key_field={self.key_field})"


class Range(Expression):
    class RangeType:
        INT4RANGE = "int4range"
        INT8RANGE = "int8range"
        DATERANGE = "daterange"
        TSRANGE = "tsrange"
        TSTZRANGE = "tstzrange"

        all = [INT4RANGE, INT8RANGE, DATERANGE, TSRANGE, TSTZRANGE]

    class RangeBound:
        INCLUSIVE_LOWER_EXCLUSIVE_UPPER = "[)"
        EXCLUSIVE_LOWER_INCLUSIVE_UPPER = "(]"
        INCLUSIVE_BOTH = "[]"
        EXCLUSIVE_BOTH = "()"

        all = [
            INCLUSIVE_LOWER_EXCLUSIVE_UPPER,
            EXCLUSIVE_LOWER_INCLUSIVE_UPPER,
            INCLUSIVE_BOTH,
            EXCLUSIVE_BOTH,
        ]

    def __init__(
        self,
        field: str | models.F | TableField,
        range_type: typing.Literal[
            "int4range", "int8range", "daterange", "tsrange", "tstzrange"
        ],
        start: int | str | datetime.datetime | datetime.date,
        end: typing.Optional[int | str | datetime.datetime | datetime.date] = None,
        bounds: typing.Literal[
            "[)", "(]", "[]", "()"
        ] = RangeBound.INCLUSIVE_LOWER_EXCLUSIVE_UPPER,
        key_field: KeyField | str = "id",
        match_op: bool = False,
        *args,
        **kwargs,
    ):
        self.pfield = field
        self.range_type = self._validate_range_type(range_type)
        self.start = start
        self.end = end
        self.bounds = self._validate_bound(bounds)
        self.key_field = key_field
        self.match_op = match_op
        self.ignore_lhs = kwargs.pop("ignore_lhs", False)
        self.legacy = kwargs.pop("legacy", False)
        super().__init__(
            *args,
            output_field=kwargs.pop("output_field", models.BooleanField()),
            **kwargs,
        )

    def as_sql(self, compiler, connection):
        _resolve_and_set_key_field(self.pfield, self, connection, compiler)

        params = []
        args = [
            "range:= {}".format(
                self.make_range(self.range_type, self.start, self.end, self.bounds)
            )
        ]

        schema = _get_schema(self.legacy, func="range")

        if include_field := schema == "paradedb":
            params.insert(0, self.pfield)
            args.insert(0, "%s")

        return (
            _make_schema_sql(
                func="range",
                args=args,
                schema=schema,
                lhs=self.pfield if not self.ignore_lhs and not include_field else None,
                key_field=self.key_field if self.match_op else None,
            ),
            params,
        )

    def make_range(self, range_type, start, end, bounds):
        return f"{range_type}({self._format(start)}, {self._format(end)}, '{bounds}')"

    @classmethod
    def _format(self, value):
        if value is None:
            return "NULL"
        elif isinstance(value, datetime.datetime):
            return f"'{value.strftime('%Y-%m-%d %H:%M:%S')}'"
        elif isinstance(value, datetime.date):
            return f"'{value.strftime('%Y-%m-%d')}'"
        elif isinstance(value, str):
            return f"'{value}'"
        else:
            return str(value)

    def _validate_range_type(self, range_type):
        if range_type not in Range.RangeType.all:
            raise ValueError(
                f"Invalid range type: {range_type}. Must be one of"
                f" {Range.RangeType.all}"
            )
        return range_type

    def _validate_bound(self, bounds):
        if bounds not in Range.RangeBound.all:
            raise ValueError(
                f"Invalid bounds: {bounds}. Must be one of {Range.RangeBound.all}"
            )
        return bounds

    def __repr__(self):
        return (
            f"Range(field={self.field}, range_type={self.range_type},"
            f" start={self.start}, end={self.end}, bounds={self.bounds},"
            f" key_field={self.key_field})"
        )


class RangeTerm(Expression):
    class Relation:
        Intersects = "Intersects"
        Within = "Within"
        Contains = "Contains"

        all = [Intersects, Within, Contains]

    class Cast:
        tsrange = "tsrange"
        int4range = "int4range"
        int8range = "int8range"
        daterange = "daterange"
        tstzrange = "tstzrange"
        char = "char"
        bigint = "bigint"
        date = "date"
        double_precision = "double precision"
        integer = "integer"
        numeric = "numeric"
        real = "real"
        smallint = "smallint"
        timestamp_with_time_zone = "timestamp with time zone"
        timestamp_without_time_zone = "timestamp without time zone"
        char = '"char"'
        numrange = "numrange"

        all = [
            tsrange,
            int4range,
            int8range,
            daterange,
            char,
            bigint,
            date,
            double_precision,
            integer,
            numeric,
            real,
            smallint,
            timestamp_with_time_zone,
            timestamp_without_time_zone,
            tstzrange,
            numrange,
        ]

    def __init__(
        self,
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
        relation: typing.Optional[
            typing.Literal["Intersects", "Within", "Contains"]
        ] = None,
        key_field: KeyField | str = "id",
        match_op: str = False,
        *args,
        **kwargs,
    ):
        if relation is not None and relation not in RangeTerm.Relation.all:
            raise ValueError(
                f"Invalid relation: {relation}. Must be one of {RangeTerm.Relation.all}"
            )

        if cast not in RangeTerm.Cast.all:
            raise ValueError(
                f"Invalid cast: {cast}. Must be one of {RangeTerm.Cast.all}"
            )

        self.pfield = field
        self.term_range = term_or_range
        self.cast = cast
        self.relation = relation
        self.key_field = key_field
        self.match_op = match_op
        self.ignore_lhs = kwargs.pop("ignore_lhs", False)
        self.legacy = kwargs.pop("legacy", False)
        super().__init__(
            *args,
            output_field=kwargs.pop("output_field", models.BooleanField()),
            **kwargs,
        )

    def as_sql(self, compiler, connection):
        _resolve_and_set_key_field(self.pfield, self, connection, compiler)

        schema = _get_schema(self.legacy, func="range_term")
        params = []
        args = ["{}::{}".format(self.term_range, self.cast)]

        if include_field := schema == "paradedb":
            params.insert(0, self.pfield)
            args.insert(0, "%s")

        if self.relation is not None:
            args.append(f"'{self.relation}'")

        return (
            _make_schema_sql(
                func="range_term",
                args=args,
                schema=schema,
                lhs=self.pfield if not self.ignore_lhs and not include_field else None,
                key_field=self.key_field if self.match_op else None,
            ),
            params,
        )

    def __repr__(self):
        return (
            f"RangeTerm(field={self.field}, value={self.term}, cast={self.cast},"
            f" key_field={self.key_field})"
        )


class Regex(Expression):
    def __init__(
        self,
        field: str | models.F | TableField,
        value: str,
        key_field: KeyField | str = "id",
        match_op: bool = False,
        *args,
        **kwargs,
    ):
        self.pfield = field
        self.value = value
        self.key_field = key_field
        self.match_op = match_op
        self.ignore_lhs = kwargs.pop("ignore_lhs", False)
        self.legacy = kwargs.pop("legacy", False)
        super().__init__(
            *args,
            output_field=kwargs.pop("output_field", models.BooleanField()),
            **kwargs,
        )

    def as_sql(self, compiler, connection):
        _resolve_and_set_key_field(self.pfield, self, connection, compiler)

        schema = _get_schema(self.legacy, func="regex")
        params = [self.value]
        args = ["%s"]

        if include_field := schema == "paradedb":
            args.insert(0, "%s")
            params.insert(0, self.pfield)

        return (
            _make_schema_sql(
                func="regex",
                args=args,
                schema=schema,
                lhs=self.pfield if not self.ignore_lhs and not include_field else None,
                key_field=self.key_field if self.match_op else None,
            ),
            params,
        )

    def __repr__(self):
        return (
            f"Regex(field={self.field}, value={self.value}, key_field={self.key_field})"
        )


class Term(Expression):
    def __init__(
        self,
        field: str | models.F | TableField,
        value: str,
        enum_cast_field: typing.Optional[str] = None,
        key_field: KeyField | str = "id",
        match_op: bool = False,
        *args,
        **kwargs,
    ):
        self.pfield = field
        self.value = value
        self.enum_cast_field = enum_cast_field
        self.key_field = key_field
        self.match_op = match_op
        self.ignore_lhs = kwargs.pop("ignore_lhs", False)
        self.legacy = kwargs.pop("legacy", False)
        super().__init__(
            *args,
            output_field=kwargs.pop("output_field", models.BooleanField()),
            **kwargs,
        )

    def as_sql(self, compiler, connection):
        _resolve_and_set_key_field(self.pfield, self, connection, compiler)

        schema = _get_schema(self.legacy, func="term")
        args = []
        params = []

        if include_field := schema == "paradedb":
            params.append(self.pfield)
            args.append("%s")

        if self.enum_cast_field:
            args.append("%s::{}".format(self.enum_cast_field))
        else:
            args.append("%s")

        params.append(self.value)

        return (
            _make_schema_sql(
                func="term",
                args=args,
                schema=schema,
                lhs=self.pfield if not self.ignore_lhs and not include_field else None,
                key_field=self.key_field if self.match_op else None,
            ),
            params,
        )

    def __repr__(self):
        return (
            f"Term(field={self.field}, value={self.value},"
            f" enum_cast_field={self.enum_cast_field},key_field={self.key_field})"
        )


class TermSet(Expression):
    def __init__(
        self,
        terms: typing.List[Term],
        key_field: KeyField | str = "id",
        match_op: bool = False,
        *args,
        **kwargs,
    ):
        self.terms = terms
        self.key_field = key_field
        self.match_op = match_op
        super().__init__(
            *args,
            output_field=kwargs.pop("output_field", models.BooleanField()),
            **kwargs,
        )

    def as_sql(self, compiler, connection):
        terms_sql = []
        for term in self.terms:
            term.ignore_lhs = True
            term.legacy = True
            terms_sql.append(
                connection.ops.compose_sql(*term.as_sql(compiler, connection))
            )
        sql = """paradedb.term_set(terms := ARRAY[{}])""".format(", ".join(terms_sql))
        if self.match_op:
            sql = f"{self.key_field} @@@ {sql}"
        return sql, []

    def __repr__(self):
        return (
            f"TermSet(field={self.field}, terms={self.terms},"
            f" key_field={self.key_field})"
        )


class FuzzyTerm(Expression):
    def __init__(
        self,
        field: str | models.F | TableField,
        value: str,
        distance: int = 2,
        transposition_cost_one: bool = True,
        prefix: bool = False,
        key_field: KeyField | str = "id",
        match_op: bool = False,
        *args,
        **kwargs,
    ):
        self.pfield = field
        self.value = value
        self.distance = distance
        self.transposition_cost_one = transposition_cost_one
        self.prefix = prefix
        self.key_field = key_field
        self.match_op = match_op
        self.ignore_lhs = kwargs.pop("ignore_lhs", False)
        self.legacy = kwargs.pop("legacy", False)
        super().__init__(
            *args,
            output_field=kwargs.pop("output_field", models.BooleanField()),
            **kwargs,
        )

    def as_sql(self, compiler, connection):
        _resolve_and_set_key_field(self.pfield, self, connection, compiler)

        params = [
            self.value,
            _normalize_bool(self.transposition_cost_one),
            _normalize_bool(self.prefix),
            self.distance,
        ]
        args = ["%s", "transposition_cost_one:=%s", "prefix:=%s", "distance:=%s"]
        schema = _get_schema(self.legacy, func="fuzzy_term")

        if include_field := schema == "paradedb":
            args.insert(0, "%s")
            params.insert(0, self.pfield)

        return (
            _make_schema_sql(
                func="fuzzy_term",
                args=args,
                schema=schema,
                lhs=self.pfield if not self.ignore_lhs and not include_field else None,
                key_field=self.key_field if self.match_op else None,
            ),
            params,
        )

    def __repr__(self):
        return (
            f"FuzzyTerm(field={self.field}, value={self.value},"
            f" distance={self.distance}, key_field={self.key_field})"
        )


class Phrase(Expression):
    def __init__(
        self,
        field: str | models.F | TableField,
        pharses: typing.List[str],
        slop: int = 0,
        key_field: KeyField | str = "id",
        match_op: bool = False,
        *args,
        **kwargs,
    ):

        assert len(pharses) > 1, "Phrase must have more than one phrase"

        self.pfield = field
        self.pharses = pharses

        try:
            self.slop = int(slop)
        except (TypeError, ValueError):
            raise ValueError("slop must be an integer")

        self.key_field = key_field
        self.match_op = match_op
        self.ignore_lhs = kwargs.pop("ignore_lhs", False)
        self.legacy = kwargs.pop("legacy", False)
        super().__init__(
            *args,
            output_field=kwargs.pop("output_field", models.BooleanField()),
            **kwargs,
        )

    def as_sql(self, compiler, connection):
        _resolve_and_set_key_field(self.pfield, self, connection, compiler)

        schema = _get_schema(self.legacy, func="phrase")
        args = ["{}".format(postgres_array(self.pharses)), "%s"]
        params = [self.slop]
        if include_field := schema == "paradedb":
            args.insert(0, "%s")
            params.insert(0, self.pfield)

        return (
            _make_schema_sql(
                func="phrase",
                args=args,
                schema=schema,
                lhs=self.pfield if not self.ignore_lhs and not include_field else None,
                key_field=self.key_field if self.match_op else None,
            ),
            params,
        )

    def __repr__(self):
        return (
            f"Phrase(field={self.field}, pharses={self.pharses}, slop={self.slop},"
            f" key_field={self.key_field})"
        )


class PhrasePrefix(Expression):
    def __init__(
        self,
        field: str | models.F | TableField,
        pharses: typing.List[str],
        max_expansion: int = 0,
        key_field: KeyField | str = "id",
        match_op: bool = False,
        *args,
        **kwargs,
    ):
        assert len(pharses) > 1, "Phrase must have more than one phrase"
        self.pfield = field
        self.pharses = pharses
        self.max_expansion = max_expansion
        self.key_field = key_field
        self.match_op = match_op
        self.ignore_lhs = kwargs.pop("ignore_lhs", False)
        self.legacy = kwargs.pop("legacy", False)
        super().__init__(
            *args,
            output_field=kwargs.pop("output_field", models.BooleanField()),
            **kwargs,
        )

    def as_sql(self, compiler, connection):
        _resolve_and_set_key_field(self.pfield, self, connection, compiler)

        schema = _get_schema(self.legacy, func="phrase_prefix")
        params = []
        args = ["{}".format(postgres_array(self.pharses))]

        if self.max_expansion != 0:
            args.append("max_expansion:=%s")
            params.append(self.max_expansion)

        if include_field := schema == "paradedb":
            args.insert(0, "%s")
            params.insert(0, self.pfield)

        return (
            _make_schema_sql(
                func="phrase_prefix",
                args=args,
                schema=schema,
                lhs=self.pfield if not self.ignore_lhs and not include_field else None,
                key_field=self.key_field if self.match_op else None,
            ),
            params,
        )

    def __repr__(self):
        return (
            f"PhrasePrefix(field={self.field}, pharses={self.pharses},"
            f" max_expansion={self.max_expansion}, key_field={self.key_field})"
        )


class ConstScore(Expression):
    def __init__(
        self,
        score: float | int,
        query: ParadeDbFunctionExpression,
        key_field: KeyField | str = "id",
        match_op: bool = False,
        *args,
        **kwargs,
    ):
        self.score = score
        self.query = query
        self.key_field = key_field
        self.match_op = match_op
        super().__init__(
            *args,
            output_field=kwargs.pop("output_field", models.BooleanField()),
            **kwargs,
        )

    def as_sql(self, compiler, connection):
        self.query.legacy = True
        sql = """paradedb.const_score(%s::real, {})""".format(
            connection.ops.compose_sql(*self.query.as_sql(compiler, connection))
        )
        if self.match_op:
            sql = f"{self.key_field} @@@ {sql}"
        return sql, [self.score]

    def __repr__(self):
        return f"ConstScore({self.score}, {self.query})"


class Bm25Score(Expression):
    def __init__(
        self, key_field: KeyField | str | models.F | TableField = "id", *args, **kwargs
    ):
        self.key_field = key_field
        super().__init__(
            *args,
            output_field=kwargs.pop("output_field", models.FloatField()),
            **kwargs,
        )

    def as_sql(self, compiler, connection):
        _resolve_and_set_key_field(self.key_field, self, connection, compiler)

        sql = f"pdb.score({self.key_field})"
        return sql, []

    def __repr__(self):
        return "Bm25Score({})"


class Boost(Expression):
    def __init__(
        self,
        factor: float | int,
        query: ParadeDbFunctionExpression,
        key_field: KeyField | str = "id",
        match_op: bool = False,
        *args,
        **kwargs,
    ):
        self.factor = factor
        self.query = query
        self.key_field = key_field
        self.match_op = match_op
        super().__init__(
            *args,
            output_field=kwargs.pop("output_field", models.FloatField()),
            **kwargs,
        )

    def as_sql(self, compiler, connection):
        sql = """paradedb.boost(%s, {})""".format(
            connection.ops.compose_sql(*self.query.as_sql(compiler, connection))
        )
        if self.match_op:
            sql = f"{self.key_field} @@@ {sql}"
        return sql, [self.factor]

    def __repr__(self):
        return f"Boost({self.factor}, {self.query})"


class DisjunctionMax(Expression):
    def __init__(
        self,
        disjuncts: typing.List[ParadeDbFunctionExpression],
        tie_breaker: int = 0,
        key_field: KeyField | str = "id",
        match_op: bool = False,
        *args,
        **kwargs,
    ):
        assert isinstance(tie_breaker, int), "tie_breaker must be an integer"

        self.disjuncts = disjuncts
        self.tie_breaker = tie_breaker
        self.key_field = key_field
        self.match_op = match_op
        super().__init__(
            *args,
            output_field=kwargs.pop("output_field", models.BooleanField()),
            **kwargs,
        )

    def as_sql(self, compiler, connection):
        inner_queries = [
            connection.ops.compose_sql(*q.as_sql(compiler, connection))
            for q in self.disjuncts
        ]
        query_sql = ", ".join(inner_queries)
        sql = (
            f"paradedb.disjunction_max(ARRAY[{query_sql}],"
            f" tie_breaker:={self.tie_breaker})"
        )
        if self.match_op:
            sql = f"{self.key_field} @@@ {sql}"

        return sql, []

    def __repr__(self):
        return f"DisjunctionMax({self.disjuncts}, tie_breaker={self.tie_breaker})"


class Boolean(Expression):
    def __init__(
        self,
        must: typing.Optional[typing.List[ParadeDbFunctionExpression]] = None,
        must_not: typing.Optional[typing.List[ParadeDbFunctionExpression]] = None,
        should: typing.Optional[typing.List[ParadeDbFunctionExpression]] = None,
        key_field: KeyField | str = "id",
        match_op: bool = False,
        *args,
        **kwargs,
    ):
        if not must and not must_not and not should:
            raise ValueError(
                "Boolean must have at least one of must, must_not or should"
            )
        if must:
            assert isinstance(must, (list, tuple)), "must must be a list or tuple"
        if must_not:
            assert isinstance(
                must_not, (list, tuple)
            ), "must_not must be a list or tuple"
        if should:
            assert isinstance(should, (list, tuple)), "should must be a list or tuple"

        self.must = must
        self.must_not = must_not
        self.should = should
        self.key_field = key_field
        self.match_op = match_op
        super().__init__(
            *args,
            output_field=kwargs.pop("output_field", models.BooleanField()),
            **kwargs,
        )

    def as_sql(self, compiler, connection):
        must_inner_sqls = []
        must_not_inner_sqls = []
        should_inner_sqls = []

        for q in self.must or []:
            q.ignore_lhs = True
            q.legacy = True
            must_inner_sqls.append(
                connection.ops.compose_sql(*q.as_sql(compiler, connection))
            )

        for q in self.must_not or []:
            q.ignore_lhs = True
            q.legacy = True
            must_not_inner_sqls.append(
                connection.ops.compose_sql(*q.as_sql(compiler, connection))
            )

        for q in self.should or []:
            q.ignore_lhs = True
            q.legacy = True
            should_inner_sqls.append(
                connection.ops.compose_sql(*q.as_sql(compiler, connection))
            )

        param_sqls_array = []
        if must_inner_sqls:
            must_sql = ", ".join(must_inner_sqls)
            param_sqls_array.append(f"must := ARRAY[{must_sql}]")
        if must_not_inner_sqls:
            must_not_sql = ", ".join(must_not_inner_sqls)
            param_sqls_array.append(f"must_not := ARRAY[{must_not_sql}]")
        if should_inner_sqls:
            should_sql = ", ".join(should_inner_sqls)
            param_sqls_array.append(f"should := ARRAY[{should_sql}]")

        sql = f"paradedb.boolean({', '.join(param_sqls_array)})"
        if self.match_op:
            sql = f"{self.key_field} @@@ {sql}"
        return sql, []

    def __repr__(self):
        return (
            f"Boolean(must={self.must}, must_not={self.must_not}, should={self.should})"
        )


class Snippet(Expression):
    def __init__(
        self,
        field: str | models.F | TableField,
        limit: typing.Optional[int] = None,
        offset: typing.Optional[int] = None,
        start_tag: typing.Optional[str] = None,
        end_tag: typing.Optional[str] = None,
        max_num_chars: typing.Optional[int] = None,
        key_field: KeyField | str = "id",
        match_op: bool = False,
        *args,
        **kwargs,
    ):
        self.pfield = field
        self.limit = limit
        self.offset = offset
        self.start_tag = start_tag
        self.end_tag = end_tag
        self.max_num_chars = max_num_chars
        self.key_field = key_field
        self.match_op = match_op
        super().__init__(
            *args, output_field=kwargs.pop("output_field", models.TextField()), **kwargs
        )

    def as_sql(self, compiler, connection):
        _resolve_and_set_key_field(self.pfield, self, connection, compiler)

        sql = f"pdb.snippet({self.pfield} "
        params = []

        if self.limit is not None:
            sql += ', "limit":=%s'
            params.append(self.limit)

        if self.offset is not None:
            sql += ', "offset":=%s'
            params.append(self.offset)

        if self.start_tag is not None:
            sql += ", start_tag:=%s"
            params.append(self.start_tag)

        if self.end_tag is not None:
            sql += ", end_tag:=%s"
            params.append(self.end_tag)

        if self.max_num_chars is not None:
            sql += ", max_num_chars:=%s"
            params.append(self.max_num_chars)

        sql += ")"

        if self.match_op:
            sql = f"{self.key_field} @@@ {sql}"
        return sql, params

    def __repr__(self):
        return (
            f"Snippet(field={self.pfield}, limit={self.limit}, offset={self.offset},"
            f" start_tag={self.start_tag}, end_tag={self.end_tag},"
            f" max_num_chars={self.max_num_chars})"
        )


class MoreLikeThis(Expression):
    def __init__(
        self,
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
        *args,
        **kwargs,
    ):
        if document:
            assert isinstance(document, dict), "document must be a dict"
        self.document_id = document_id
        self.document = document
        self.fields = fields
        self.min_doc_frequency = min_doc_frequency
        self.max_doc_frequency = max_doc_frequency
        self.min_term_frequency = min_term_frequency
        self.max_query_terms = max_query_terms
        self.min_word_length = min_word_length
        self.max_word_length = max_word_length
        self.boost_factor = boost_factor
        self.stop_words = stop_words
        self.key_field = key_field
        self.match_op = match_op
        super().__init__(
            *args,
            output_field=kwargs.pop("output_field", models.BooleanField()),
            **kwargs,
        )

    def as_sql(self, compiler, connection):
        params = []
        sql = """pdb.more_like_this("""
        if self.document_id:
            sql += "key_value :=%s"
            params.append(self.document_id)
            if self.fields:
                sql += ", fields := {}".format(postgres_array(self.fields))

        if self.document and not self.document_id:
            sql += "document :=%s"
            params.append(json.dumps(self.document))

        if self.min_doc_frequency:
            sql += ", min_doc_frequency :=%s"
            params.append(self.min_doc_frequency)
        if self.max_doc_frequency:
            sql += ", max_doc_frequency :=%s"
            params.append(self.max_doc_frequency)
        if self.min_term_frequency:
            sql += ", min_term_frequency :=%s"
            params.append(self.min_term_frequency)
        if self.max_query_terms:
            sql += ", max_query_terms :=%s"
            params.append(self.max_query_terms)
        if self.min_word_length:
            sql += ", min_word_length :=%s"
            params.append(self.min_word_length)
        if self.max_word_length:
            sql += ", max_word_length :=%s"
            params.append(self.max_word_length)
        if self.boost_factor:
            sql += ", boost_factor :=%s"
            params.append(self.boost_factor)
        if self.stop_words:
            sql += ", stopwords:= {}".format(postgres_array(self.stop_words))

        sql += ")"
        if self.match_op:
            sql = f"{self.key_field} @@@ {sql}"
        return sql, params

    def __repr__(self):
        return (
            f"MoreLikethis(document_id={self.document_id}, document={self.document},"
            f" fields={self.fields}, min_doc_frequency={self.min_doc_frequency},"
            f" max_doc_frequency={self.max_doc_frequency},"
            f" min_term_frequency={self.min_term_frequency},"
            f" max_query_terms={self.max_query_terms},"
            f" min_word_length={self.min_word_length},"
            f" max_word_length={self.max_word_length},"
            f" boost_factor={self.boost_factor}, stop_words={self.stop_words})"
        )


class Parse(Expression):
    def __init__(
        self,
        query: str,
        lenient: bool = False,
        conjunction_mode: bool = False,
        key_field: KeyField | str = "id",
        match_op: str = False,
        *args,
        **kwargs,
    ):
        self.query = query
        self.lenient = lenient
        self.conjunction_mode = conjunction_mode
        self.key_field = key_field
        self.match_op = match_op
        self.legacy = kwargs.pop("legacy", False)
        super().__init__(
            *args,
            output_field=kwargs.pop("output_field", models.BooleanField()),
            **kwargs,
        )

    def as_sql(self, compiler, connection):
        schema = _get_schema(self.legacy, func="parse")
        sql = f"{schema}.parse(%s, lenient:=%s, conjunction_mode:=%s)"
        if self.match_op:
            sql = f"{self.key_field} @@@ {sql}"
        return sql, [
            self.query,
            _normalize_bool(self.lenient),
            _normalize_bool(self.conjunction_mode),
        ]

    def __repr__(self):
        return (
            f"Parse({self.query}, lenient={self.lenient},"
            f" conjunction_mode={self.conjunction_mode})"
        )


class ParseWithField(Expression):
    def __init__(
        self,
        field: str | models.F | TableField,
        value: str,
        lenient: bool = False,
        conjunction_mode: bool = False,
        key_field: KeyField | str = "id",
        match_op: bool = False,
        *args,
        **kwargs,
    ):
        self.pfield = field
        self.value = value
        self.lenient = lenient
        self.conjunction_mode = conjunction_mode
        self.key_field = key_field
        self.match_op = match_op
        super().__init__(
            *args,
            output_field=kwargs.pop("output_field", models.BooleanField()),
            **kwargs,
        )

    def as_sql(self, compiler, connection):
        _resolve_and_set_key_field(self.pfield, self, connection, compiler)

        sql = "paradedb.parse_with_field(%s, %s, lenient:=%s, conjunction_mode:=%s)"
        if self.match_op:
            sql = f"{self.key_field} @@@ {sql}"
        return sql, [
            self.pfield,
            self.value,
            _normalize_bool(self.lenient),
            _normalize_bool(self.conjunction_mode),
        ]

    def __repr__(self):
        return (
            f"ParseWithField({self.pfield}, {self.value}, lenient={self.lenient},"
            f" conjunction_mode={self.conjunction_mode})"
        )


class ProximityRegex(Expression):
    def __init__(
        self,
        regex: str,
        max_expansions: typing.Optional[int] = None,
        wrap: bool = True,
        *args,
        **kwargs,
    ):
        if max_expansions and max_expansions < 0:
            raise ValueError("max_expansions must be greater than 0")

        self.regex = regex
        self.max_expansions = max_expansions
        self.wrap = wrap
        self.key_field = kwargs.pop("key_field", None)

        super().__init__(
            *args,
            output_field=kwargs.pop("output_field", models.BooleanField()),
            **kwargs,
        )

    def as_sql(self, compiler, connection):
        params = [self.regex]
        sql = "pdb.prox_regex(%s"

        if self.max_expansions:
            sql += ", %s"
            params.append(self.max_expansions)

        sql += ")"

        if self.wrap:
            sql = f"({sql})"

        return sql, params

    def __repr__(self):
        return f"ProximityRegex({self.regex}, max_expansions={self.max_expansions})"


class ProximityArray(Expression):
    def __init__(
        self,
        values: typing.List[str | int | ProximityRegex],
        wrap: bool = True,
        *args,
        **kwargs,
    ):
        assert isinstance(values, (list, tuple)), "values must be a list or tuple"
        self.values = values
        self.wrap = wrap
        self.key_field = kwargs.pop("key_field", None)
        super().__init__(
            *args,
            output_field=kwargs.pop("output_field", models.BooleanField()),
            **kwargs,
        )

    def as_sql(self, compiler, connection):
        params = []
        sql_build = []
        for value in self.values:
            if isinstance(value, ProximityRegex):
                query = connection.ops.compose_sql(*value.as_sql(compiler, connection))
                sql_build.append(query)
            else:
                sql_build.append("%s")
                params.append(value)

        sql = "pdb.prox_array({})".format(", ".join(sql_build))

        if self.wrap:
            sql = f"({sql})"

        return sql, params

    def __repr__(self):
        return f"ProximityArray({self.values})"


class Proximity(Expression):
    ops = ["##", "##>"]

    def __init__(
        self,
        values: typing.List[
            str | int | ProximityRegex | ProximityArray | typing.Literal["##", "##>"]
        ],
        field: typing.Optional[str | models.F | TableField] = None,
        *args,
        **kwargs,
    ):

        if len(values) < 3:
            raise ValueError("Expected at least 3 values. got '{}'".format(len(values)))

        self.values = values
        self.pfield = field
        self.key_field = kwargs.pop("key_field", None)
        super().__init__(
            *args,
            output_field=kwargs.pop("output_field", models.BooleanField()),
            **kwargs,
        )

    def as_sql(self, compiler, connection, **extra_context):
        sql_build = []
        params = []

        check = "value"

        for idx, v in enumerate(self.values):
            check_op = idx % 2 == 1
            if check_op:
                if v not in self.ops:
                    raise ValueError(
                        "Expected op one of {} at psoition {}. got '{}'".format(
                            self.ops, idx + 1, v
                        )
                    )

                sql_build.append(v)
                continue

            if check == "value":
                if isinstance(v, (ProximityRegex, ProximityArray)):
                    if hasattr(v, "wrap"):
                        v.wrap = False

                    sql = connection.ops.compose_sql(*v.as_sql(compiler, connection))
                    sql_build.append(sql)
                else:
                    sql_build.append("%s")
                    params.append(v)

            if check == "distance":
                if not isinstance(v, int) and not (isinstance(v, str) and v.isdigit()):
                    raise ValueError(
                        "Expected int at position {}. got '{}'".format(idx + 1, v)
                    )

                sql_build.append("%s")
                params.append(int(v))

            check = "distance" if check == "value" else "value"

        sql = "({})".format(" ".join(sql_build))

        if self.pfield:
            sql = f"{_resolve_field_name(compiler, self.pfield)} @@@ {sql}"

        return sql, params

    def __repr__(self):
        return f"Proximity(values={self.values}, field={self.pfield})"


class JsonOp(Expression):
    def __init__(
        self, field: str, *keys: str, value: str | int | models.Value, **kwargs
    ):
        self.pfield = field
        self.keys = keys
        self.value = value
        super().__init__(
            output_field=kwargs.pop("output_field", models.BooleanField()),
            **kwargs,
        )

    def as_sql(self, compiler, connection):
        _resolve_and_set_key_field(self.pfield, self, connection, compiler)

        access_key = f"{self.pfield}{self.build_key(self.keys)}"
        return f"{access_key} @@@ %s", [
            _resolve_value(self.value, connection, compiler)
        ]

    @classmethod
    def build_key(self, keys):
        native_python_dict_access_ke_string = []
        for key in keys:
            native_python_dict_access_ke_string.append("['{}']".format(key))
        return "".join(native_python_dict_access_ke_string)
