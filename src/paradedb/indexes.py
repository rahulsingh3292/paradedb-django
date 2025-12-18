import json
import typing

from django.db import models
from django.db.models import Expression, F
from django.utils.deconstruct import deconstructible

from .tokenizers import Tokenizer


__all__ = [
    "IndexField",
    "TextFieldIndexConfig",
    "JSONFieldIndexConfig",
    "NumericFieldIndexConfig",
    "BooleanFieldIndexConfig",
    "DateTimeFieldIndexConfig",
    "IndexFieldConfig",
    "Bm25Index",
]


@deconstructible
class TextFieldIndexConfig:
    def __init__(
        self,
        field: str,
        fast: bool = True,
        tokenizer: typing.Optional[Tokenizer] = None,
        normalizer: typing.Literal["raw", "lowercase"] = "raw",
        record: typing.Literal["position", "freq", "basic"] = "position",
        indexed: bool = True,
        fieldnorms: bool = True,
        column: typing.Optional[str] = None,
    ):
        if record and record not in ["position", "freq", "basic"]:
            raise ValueError(
                f"Invalid record type: {record}. Must be one of ['position', 'freq',"
                " 'basic']"
            )
        if normalizer and normalizer not in ["raw", "lowercase"]:
            raise ValueError(
                f"Invalid normalizer: {normalizer}. Must be one of ['raw', 'lowercase']"
            )
        self.field = field
        self.fast = fast
        self.tokenizer = tokenizer
        self.normalizer = normalizer
        self.record = record
        self.indexed = indexed
        self.fieldnorms = fieldnorms
        self.column = column

    @property
    def json(self) -> dict[str, typing.Any]:
        field_config = {
            "fast": self.fast,
            "indexed": self.indexed,
            "fieldnorms": self.fieldnorms,
            "record": self.record,
        }
        if self.tokenizer:
            field_config["tokenizer"] = self.tokenizer.json
        if self.normalizer:
            field_config["normalizer"] = self.normalizer
        if self.column:
            field_config["column"] = self.column
        return field_config


@deconstructible
class JSONFieldIndexConfig(TextFieldIndexConfig):
    def __init__(
        self,
        field: str,
        fast: bool = True,
        tokenizer: typing.Optional[Tokenizer] = None,
        normalizer: typing.Optional[typing.Literal["raw", "lowercase"]] = None,
        record: typing.Literal["position", "freq", "basic"] = "position",
        indexed: bool = True,
        fieldnorms: bool = True,
        column: typing.Optional[str] = None,
        expand_dots: bool = True,
    ):
        super().__init__(
            field,
            fast,
            tokenizer,
            normalizer,
            record,
            indexed,
            fieldnorms,
            column=column,
        )
        self.expand_dots = expand_dots

    @property
    def json(self):
        config = super().json
        config["expand_dots"] = self.expand_dots
        return config


@deconstructible
class NumericFieldIndexConfig:
    def __init__(
        self,
        field: str,
        fast: bool = True,
        indexed: bool = True,
        column: typing.Optional[str] = None,
    ):
        self.field = field
        self.fast = fast
        self.indexed = indexed
        self.column = column

    @property
    def json(self):
        config = {"fast": self.fast, "indexed": self.indexed}
        if self.column:
            config["column"] = self.column
        return config


@deconstructible
class BooleanFieldIndexConfig:
    def __init__(
        self,
        field: str,
        fast: bool = True,
        indexed: bool = True,
        column: typing.Optional[str] = None,
    ):
        self.field = field
        self.fast = fast
        self.indexed = indexed
        self.column = column

    @property
    def json(self):
        config = {"fast": self.fast, "indexed": self.indexed}
        if self.column:
            config["column"] = self.column
        return config


@deconstructible
class DateTimeFieldIndexConfig:
    def __init__(
        self,
        field: str,
        fast: bool = True,
        indexed: bool = True,
        column: typing.Optional[str] = None,
    ):
        self.field = field
        self.fast = fast
        self.indexed = indexed
        self.column = column

    @property
    def json(self):
        config = {"fast": self.fast, "indexed": self.indexed}
        if self.column:
            config["column"] = self.column
        return config


@deconstructible
class IndexFieldConfig:
    def __init__(
        self,
        text_fields: typing.Optional[typing.List[TextFieldIndexConfig]] = None,
        json_fields: typing.Optional[typing.List[JSONFieldIndexConfig]] = None,
        numeric_fields: typing.Optional[typing.List[NumericFieldIndexConfig]] = None,
        boolean_fields: typing.Optional[typing.List[BooleanFieldIndexConfig]] = None,
        datetime_fields: typing.Optional[typing.List[DateTimeFieldIndexConfig]] = None,
    ):
        self.text_fields = text_fields or []
        self.json_fields = json_fields or []
        self.numeric_fields = numeric_fields or []
        self.boolean_fields = boolean_fields or []
        self.datetime_fields = datetime_fields or []


@deconstructible
class IndexField(Expression):
    def __init__(
        self,
        field: str | models.F,
        tokenizer_cast: typing.Optional[str] = None,
        field_resolver: typing.Optional[typing.Callable] = None,
        *args,
        **kwargs,
    ):
        self.index_field = field
        self.tokenizer_cast = tokenizer_cast
        self.field_resolver = field_resolver
        super().__init__(*args, **kwargs)

    def as_sql(self, compiler, connection):
        if isinstance(self.index_field, F) and not self.field_resolver:
            resolved = self.index_field.resolve_expression(compiler.query)
            self.index_field = resolved.target.column.__str__()

        elif (
            hasattr(self.index_field, "resolve_expression") and not self.field_resolver
        ):
            resolved = self.index_field.resolve_expression(compiler.query)
            self.index_field = resolved.as_sql(compiler, connection)[0]

        elif self.field_resolver:
            self.index_field = self.field_resolver(
                self.index_field, compiler, connection
            )

        if self.tokenizer_cast:
            if self.tokenizer_cast.startswith("::"):
                self.tokenizer_cast = self.tokenizer_cast[2:]

            sql = f"({self.index_field}::{self.tokenizer_cast})"
        else:
            sql = f"({self.index_field})"

        return sql, []

    def __repr__(self):
        return f"IndexField({self.index_field}, {self.tokenizer_cast})"


class Bm25Index(models.Index):
    suffix = "bm25"

    def __init__(
        self,
        *expressions,
        fields=(),
        name: str = None,
        db_tablespace=None,
        opclasses=(),
        condition=None,
        include=None,
        fields_config: typing.Optional[IndexFieldConfig] = None,
        key_field: str = "id",
        with_extra: typing.Optional[typing.Dict[str, typing.Any]] = None,
        **kwargs,
    ):
        assert bool(name), "Index name is required"
        self.fields_config = fields_config
        self.key_field = key_field
        self.with_extra = with_extra
        super().__init__(
            *expressions,
            fields=fields,
            name=name,
            db_tablespace=db_tablespace,
            opclasses=opclasses,
            condition=condition,
            include=include,
            **kwargs,
        )

    def create_sql(self, model, schema_editor, using="", **kwargs):
        from django.db.models.sql import Query

        include = [
            model._meta.get_field(field_name).column for field_name in self.include
        ]
        condition = self._get_condition_sql(model, schema_editor)
        if self.expressions:
            index_expressions = []
            for expression in self.expressions:
                index_expression = models.indexes.IndexExpression(expression)
                index_expression.set_wrapper_classes(schema_editor.connection)
                index_expressions.append(index_expression)
            expressions = models.ExpressionList(*index_expressions).resolve_expression(
                Query(model, alias_cols=False),
            )
            fields = None
            col_suffixes = None
        else:
            fields = [
                model._meta.get_field(field_name)
                for field_name, _ in self.fields_orders
            ]
            if schema_editor.connection.features.supports_index_column_ordering:
                col_suffixes = [order[1] for order in self.fields_orders]
            else:
                col_suffixes = [""] * len(self.fields_orders)
            expressions = None

        statement = schema_editor._create_index_sql(
            model,
            fields=fields,
            name=self.name,
            using=using or " USING {}".format(self.suffix),
            db_tablespace=self.db_tablespace,
            col_suffixes=col_suffixes,
            opclasses=self.opclasses,
            condition=condition,
            include=include,
            expressions=expressions,
            **kwargs,
        )
        with_parts = [
            "key_field={}".format(
                self.key_field
                or getattr(model, "paradedb_key_field", model._meta.pk.name)
            ),
        ]
        for field, value in (self.with_extra or {}).items():
            with_parts.append("{}={}".format(field, value))

        if self.fields_config:

            def _to_json_string(configs: typing.List[TextFieldIndexConfig]):
                return json.dumps({c.field: c.json for c in configs})

            if self.fields_config.text_fields:
                with_parts.append(
                    "text_fields='{}'".format(
                        _to_json_string(self.fields_config.text_fields)
                    )
                )
            if self.fields_config.json_fields:
                with_parts.append(
                    "json_fields='{}'".format(
                        _to_json_string(self.fields_config.json_fields)
                    )
                )
            if self.fields_config.numeric_fields:
                with_parts.append(
                    "numeric_fields='{}'".format(
                        _to_json_string(self.fields_config.numeric_fields)
                    )
                )
            if self.fields_config.boolean_fields:
                with_parts.append(
                    "boolean_fields='{}'".format(
                        _to_json_string(self.fields_config.boolean_fields)
                    )
                )
            if self.fields_config.datetime_fields:
                with_parts.append(
                    "datetime_fields='{}'".format(
                        _to_json_string(self.fields_config.datetime_fields)
                    )
                )

        statement.parts["extra"] = " WITH ({})".format(", ".join(with_parts))
        return statement

    def deconstruct(self):
        path, expressions, kwargs = super().deconstruct()
        kwargs["fields_config"] = self.fields_config
        kwargs["key_field"] = self.key_field
        kwargs["with_extra"] = self.with_extra
        return path, expressions, kwargs
