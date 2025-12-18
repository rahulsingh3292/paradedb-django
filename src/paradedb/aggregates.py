import datetime
import json
import typing

from django.db import models
from django.db.models.aggregates import Aggregate
from django.db.models.expressions import Expression
from django.utils import timezone


__all__ = [
    "BaseAggregate",
    "Count",
    "TermAggregateOrder",
    "Term",
    "HistogramBound",
    "Histogram",
    "DateHistogram",
    "RangeAggegationRange",
    "Range",
    "Avg",
    "Cardinality",
    "Sum",
    "Max",
    "Min",
    "Stats",
    "Percentile",
    "TopHitSort",
    "TopHit",
    "Facet",
]


class BaseAggregate(Aggregate):
    function = "pdb.agg"
    template = "%(function)s(%(expressions)s)"
    output_field = models.JSONField()


class Count(BaseAggregate):
    def __init__(self, field: str = "id", *args, **kwargs):
        self.pfield = field
        super().__init__(models.Value(self.build_json()), *args, **kwargs)

    def build_json(self, as_dict=False):
        param_json = {"value_count": {"field": str(self.pfield)}}
        if as_dict:
            return param_json

        return json.dumps(param_json)


class TermAggregateOrder:
    def __init__(
        self,
        target: (
            typing.Literal["_count", "_key"] | str
        ),  # "_count", "_key", or metric name like "average_rank"
        order: typing.Literal["asc", "desc"] = "asc",
    ):
        if order not in ["asc", "desc"]:
            raise ValueError("order must be 'asc' or 'desc'")
        self.target = target
        self.order = order

    def to_json(self):
        return {self.target: self.order}

    @classmethod
    def from_dict(cls, d):
        for key, value in d.items():
            return TermAggregateOrder(key, value)
        raise ValueError("Invalid dict")


class Term(BaseAggregate):
    def __init__(
        self,
        field: str,
        order: typing.Optional[TermAggregateOrder | dict[str, str]] = None,
        size: int = 0,
        segment_size: int = 0,
        min_doc_count: int = 0,
        missing: typing.Optional[float | int] = None,
        show_term_doc_count_error: bool = False,
        aggs: typing.Optional[dict] = None,
        *args,
        **extra,
    ):
        if order is not None and not isinstance(order, (TermAggregateOrder, dict)):
            raise ValueError("order must be TermAggregateOrder or dict")

        self.pfield = field

        self.order = order
        if isinstance(order, dict):
            self.order = TermAggregateOrder.from_dict(order)

        self.size = size
        self.segment_size = segment_size
        self.min_doc_count = min_doc_count
        self.missing = missing
        self.show_term_doc_count_error = show_term_doc_count_error
        self.aggs = aggs

        super().__init__(models.Value(self.build_json()), *args, **extra)

    def build_json(self, as_dict=False):
        terms = {"field": self.pfield}

        if self.order is not None:
            terms["order"] = self.order.to_json()

        if self.size > 0:
            terms["size"] = self.size
        if self.segment_size > 0:
            terms["segment_size"] = self.segment_size
        if self.min_doc_count > 0:
            terms["min_doc_count"] = self.min_doc_count
        if self.missing is not None:
            terms["missing"] = self.missing
        if self.show_term_doc_count_error:
            terms["show_term_doc_count_error"] = self.show_term_doc_count_error

        res = {"terms": terms}

        if self.aggs is not None:
            res["aggs"] = self.aggs

        if as_dict:
            return res

        return json.dumps(res)


class HistogramBound:
    def __init__(self, min: int, max: int):
        self.min = min
        self.max = max

    def as_json(self):
        return {"min": self.min, "max": self.max}

    @classmethod
    def from_tuple(cls, tup):
        assert len(tup) == 2, "Expected tuple of length 2"
        return cls(tup[0], tup[1])


class DateHistogram(BaseAggregate):
    def __init__(
        self,
        field: str,
        fixed_interval: str = None,
        offset: typing.Optional[str] = None,
        min_doc_count: typing.Optional[int] = None,
        hard_bounds: typing.Optional[
            HistogramBound | typing.Tuple[float, float]
        ] = None,
        extended_bounds: typing.Optional[
            HistogramBound | typing.Tuple[float, float]
        ] = None,
        keyed: bool = True,
        *args,
        **extra,
    ):
        if min_doc_count is not None and extended_bounds is not None:
            raise ValueError(
                "Cannot set both min_doc_count and extended_bounds together."
            )

        if extended_bounds and not hard_bounds:
            raise ValueError("Cannot set extended_bounds without hard_bounds.")

        self.pfield = field
        self.fixed_interval = fixed_interval
        self.offset = offset
        self.min_doc_count = min_doc_count

        self.hard_bounds = hard_bounds
        if isinstance(hard_bounds, (list, tuple)):
            self.hard_bounds = HistogramBound.from_tuple(hard_bounds)

        self.extended_bounds = extended_bounds
        if isinstance(extended_bounds, (list, tuple)):
            self.extended_bounds = HistogramBound.from_tuple(extended_bounds)

        self.keyed = keyed

        super().__init__(models.Value(self.build_json()), *args, **extra)

    def build_json(self, as_dict=False):
        param_json = {
            "date_histogram": {
                "field": self.pfield,
                "fixed_interval": self.fixed_interval,
            }
        }

        if self.offset is not None:
            param_json["date_histogram"]["offset"] = self.offset

        if self.min_doc_count is not None:
            param_json["date_histogram"]["min_doc_count"] = self.min_doc_count

        if self.hard_bounds is not None:
            param_json["date_histogram"]["hard_bounds"] = self.hard_bounds.as_json()

        if self.extended_bounds is not None:
            param_json["date_histogram"]["hard_bounds"][
                "extended_bounds"
            ] = self.extended_bounds.as_json()

        if self.keyed is not None:
            param_json["date_histogram"]["keyed"] = self.keyed

        if as_dict:
            return param_json

        return json.dumps(param_json)


class Histogram(BaseAggregate):
    def __init__(
        self,
        field: str,
        interval: str,
        offset: typing.Optional[str] = None,
        min_doc_count: typing.Optional[int] = None,
        hard_bounds: typing.Optional[
            HistogramBound | typing.Tuple[float, float]
        ] = None,
        extended_bounds: typing.Optional[
            HistogramBound | typing.Tuple[float, float]
        ] = None,
        keyed: bool = True,
        is_normalized_to_ns: bool = False,
        *args,
        **extra,
    ):
        if min_doc_count is not None and extended_bounds is not None:
            raise ValueError(
                "Cannot set both min_doc_count and extended_bounds together."
            )

        if extended_bounds and not hard_bounds:
            raise ValueError("Cannot set extended_bounds without hard_bounds.")

        self.pfield = field
        self.interval = interval
        self.offset = offset
        self.min_doc_count = min_doc_count

        self.hard_bounds = hard_bounds
        if isinstance(hard_bounds, (list, tuple)):
            self.hard_bounds = HistogramBound.from_tuple(hard_bounds)

        self.extended_bounds = extended_bounds
        if isinstance(extended_bounds, (list, tuple)):
            self.extended_bounds = HistogramBound.from_tuple(extended_bounds)

        self.keyed = keyed
        self.is_normalized_to_ns = is_normalized_to_ns

        super().__init__(models.Value(self.build_json()), *args, **extra)

    def build_json(self, as_dict=False):
        param_json = {"histogram": {"field": self.pfield, "interval": self.interval}}

        if self.offset is not None:
            param_json["histogram"]["offset"] = self.offset

        if self.min_doc_count is not None:
            param_json["histogram"]["min_doc_count"] = self.min_doc_count

        if self.hard_bounds is not None:
            param_json["histogram"]["hard_bounds"] = self.hard_bounds.as_json()

        if self.extended_bounds is not None:
            param_json["histogram"]["hard_bounds"][
                "extended_bounds"
            ] = self.extended_bounds.as_json()

        if self.keyed is not None:
            param_json["histogram"]["keyed"] = self.keyed

        if self.is_normalized_to_ns is not None:
            param_json["histogram"]["is_normalized_to_ns"] = self.is_normalized_to_ns

        if as_dict:
            return param_json

        return json.dumps(param_json)


class RangeAggegationRange:
    def __init__(
        self,
        from_: float | int | datetime.date | datetime.datetime,
        to: float | int | datetime.date | datetime.datetime,
        key: str = None,
    ):
        self.from_ = from_
        self.to = to
        self.key = key

    def as_json(self):
        range_json = {
            "from": self._resolve_from_and_to(self.from_),
            "to": self._resolve_from_and_to(self.to),
        }

        if self.key is not None:
            range_json["key"] = self.key

        return range_json

    def _resolve_from_and_to(self, value):
        if isinstance(value, (datetime.datetime, timezone.datetime)):
            return value.timestamp()
        if isinstance(value, datetime.date):
            return timezone.datetime(value.year, value.month, value.day).timestamp()
        return value


class Range(BaseAggregate):
    def __init__(
        self,
        field: str,
        ranges: typing.List[RangeAggegationRange],
        keyed: bool = True,
        *args,
        **extra,
    ):
        self.pfield = field
        self.ranges = ranges
        self.keyed = keyed
        super().__init__(models.Value(self.build_json()), *args, **extra)

    def build_json(self, as_dict=False):
        param_json = {
            "range": {
                "field": self.pfield,
                "ranges": [r.as_json() for r in self.ranges],
            }
        }
        if self.keyed is not None:
            param_json["range"]["keyed"] = self.keyed

        if as_dict:
            return param_json

        return json.dumps(param_json)


class Avg(BaseAggregate):
    def __init__(
        self,
        field: str,
        missing: typing.Optional[float | int | float] = None,
        *args,
        **extra,
    ):
        self.pfield = field
        self.missing = missing
        super().__init__(models.Value(self.build_json()), *args, **extra)

    def build_json(self, as_dict=False):
        param_json = {"avg": {"field": self.pfield}}
        if self.missing is not None:
            param_json["avg"]["missing"] = self.missing

        if as_dict:
            return param_json

        return json.dumps(param_json)


class Cardinality(BaseAggregate):
    def __init__(
        self,
        field: str,
        missing: typing.Optional[float | int | float | str] = None,
        *args,
        **extra,
    ):
        self.pfield = field
        self.missing = missing
        super().__init__(models.Value(self.build_json()), *args, **extra)

    def build_json(self, as_dict=False):
        param_json = {"cardinality": {"field": self.pfield}}
        if self.missing is not None:
            param_json["cardinality"]["missing"] = self.missing

        if as_dict:
            return param_json

        return json.dumps(param_json)


class Min(BaseAggregate):
    def __init__(
        self,
        field: str,
        missing: typing.Optional[float | int | float] = None,
        *args,
        **extra,
    ):
        self.pfield = field
        self.missing = missing
        super().__init__(models.Value(self.build_json()), *args, **extra)

    def build_json(self, as_dict=False):
        param_json = {"min": {"field": self.pfield}}
        if self.missing is not None:
            param_json["min"]["missing"] = self.missing

        if as_dict:
            return param_json

        return json.dumps(param_json)


class Max(BaseAggregate):
    def __init__(
        self,
        field: str,
        missing: typing.Optional[float | int | float] = None,
        *args,
        **extra,
    ):
        self.pfield = field
        self.missing = missing
        super().__init__(models.Value(self.build_json()), *args, **extra)

    def build_json(self, as_dict=False):
        param_json = {"max": {"field": self.pfield}}
        if self.missing is not None:
            param_json["max"]["missing"] = self.missing

        if as_dict:
            return param_json

        return json.dumps(param_json)


class Percentile(BaseAggregate):
    def __init__(
        self,
        field: str,
        percents: typing.Optional[typing.List[float | int]] = None,
        missing: typing.Optional[float | int] = None,
        keyed=True,
        *args,
        **extra,
    ):
        if (percents is not None) and (
            not isinstance(percents, (list, tuple))
            or not all(isinstance(x, (int, float)) for x in percents)
        ):
            raise ValueError("percents must be a list of floats or ints")

        self.pfield = field
        self.percents = percents
        self.keyed = keyed
        self.missing = missing
        super().__init__(models.Value(self.build_json()), *args, **extra)

    def build_json(self, as_dict=False):
        param_json = {"percentiles": {"field": self.pfield}}
        if self.percents is not None:
            param_json["percentiles"]["percents"] = self.percents

        if self.keyed is not None:
            param_json["percentiles"]["keyed"] = self.keyed

        if self.missing is not None:
            param_json["percentiles"]["missing"] = self.missing

        if as_dict:
            return param_json

        return json.dumps(param_json)


class Stats(BaseAggregate):
    def __init__(
        self, field: str, missing: typing.Optional[float | int] = None, *args, **extra
    ):
        self.pfield = field
        self.missing = missing
        super().__init__(models.Value(self.build_json()), *args, **extra)

    def build_json(self, as_dict=False):
        param_json = {"stats": {"field": self.pfield}}
        if self.missing is not None:
            param_json["stats"]["missing"] = self.missing

        if as_dict:
            return param_json

        return json.dumps(param_json)


class Sum(BaseAggregate):
    def __init__(
        self, field: str, missing: typing.Optional[float | int] = None, *args, **extra
    ):
        self.pfield = field
        self.missing = missing
        super().__init__(models.Value(self.build_json()), *args, **extra)

    def build_json(self, as_dict=False):
        param_json = {"sum": {"field": self.pfield}}
        if self.missing is not None:
            param_json["sum"]["missing"] = self.missing

        if as_dict:
            return param_json

        return json.dumps(param_json)


class TopHitSort:
    def __init__(self, field: str, order: typing.Literal["asc", "desc"] = "asc"):
        if order not in ["asc", "desc"]:
            raise ValueError("order must be 'asc' or 'desc'")

        self.field = field
        self.order = order

    def to_json(self):
        return {self.field: self.order}

    @classmethod
    def from_array_json(cls, array_json):
        objs = []
        for item in array_json:
            if not isinstance(item, dict):
                raise ValueError("Expected array of objects")

            for key, value in item.items():
                objs.append(cls(key, value))

        return objs


class TopHit(BaseAggregate):
    def __init__(
        self,
        sort: typing.List[TopHitSort] | typing.List[dict[str, str]],
        size: int,
        from_: typing.Optional[int] = None,
        docvalue_fields=None,
        *args,
        **extra,
    ):
        if not isinstance(sort, (list, tuple)):
            raise ValueError(
                "sort must be a list or tuple and all elements must be TopHitSort or"
                " dict"
            )

        if isinstance(sort, (list, tuple)) and isinstance(sort[0], dict):
            self.sort = TopHitSort.from_array_json(sort)
        else:
            self.sort = sort

        self.size = size

        if from_ is not None and not isinstance(from_, int):
            raise ValueError("from_ must be an int")

        self.from_ = from_
        self.docvalue_fields = docvalue_fields
        super().__init__(models.Value(self.build_json()), *args, **extra)

    def build_json(self, as_dict=False):
        param_json = {
            "top_hits": {"sort": [s.to_json() for s in self.sort], "size": self.size}
        }
        if self.from_ is not None:
            param_json["top_hits"]["from"] = self.from_

        if self.docvalue_fields is not None:
            param_json["top_hits"]["docvalue_fields"] = self.docvalue_fields

        if as_dict:
            return param_json

        return json.dumps(param_json)


class Facet(Expression):
    def __init__(
        self,
        aggregate: Aggregate,
        visiblity_check: typing.Optional[str] = None,
        *args,
        **extra,
    ):
        self.aggregate = aggregate
        self.visiblity_check = visiblity_check
        super().__init__(*args, output_field=models.JSONField(), **extra)

    def as_sql(self, compiler, connection, **extra_context):
        sql = "{} OVER () ".format(
            connection.ops.compose_sql(*self.aggregate.as_sql(compiler, connection))
        )
        return sql, []
