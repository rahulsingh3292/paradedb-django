import re
import typing

from django.db import models
from django.db.models.expressions import Col


class KeyField:
    def __init__(
        self,
        table: typing.Type[models.Model] | models.Model | str,
        primary_key_field: typing.Optional[str] = None,
    ):
        if not isinstance(table, (models.Model, type(models.Model), str)):
            raise ValueError("table must be a model or a string")

        if isinstance(table, str) and not primary_key_field:
            raise ValueError("primary_key_field must be provided if table is a string")

        self.table = table
        self.primary_key_field = primary_key_field

    def __str__(self):
        return self.get_sql()

    def get_sql(self) -> str:
        table = self.get_table()
        if hasattr(self.table, "paradedb_key_field"):
            key_field = self.table.paradedb_key_field
        else:
            key_field = (
                self.table._meta.pk.name
                if self.primary_key_field is None
                else self.primary_key_field
            )
        return f"{table}.{key_field}"

    def get_lhs_sql(self) -> str:
        return "{} @@@ ".format(self.get_sql())

    def get_table(self) -> str:
        if isinstance(self.table, (models.Model, type(models.Model))) or hasattr(
            self.table, "_meta"
        ):
            return self.table._meta.db_table
        else:
            return self.table

    @classmethod
    def resolve_sql_from_table_column_string(
        cls, table_column_string: str
    ) -> "KeyField":
        """Expected table.column format"""

        table_column_string = table_column_string.replace('"', "")
        assert (
            table_column_string.split(".").__len__() == 2
        ), "Expected table.column format"
        return cls(
            table=table_column_string.split(".")[0],
            key_field=table_column_string.split(".")[1],
        )


class TableField:
    def __init__(
        self,
        field: str,
        table: typing.Optional[typing.Type[models.Model] | models.Model | str] = None,
        key_field: typing.Optional[KeyField | str] = None,
    ):
        assert isinstance(field, str), "field must be a string"
        if not table and not key_field:
            raise ValueError("Either table or key_field must be provided")
        if key_field and not isinstance(key_field, KeyField):
            raise ValueError("key_field must be a KeyField")

        self.table = table
        self.field = field
        self.key_field = key_field

    def get_sql(self) -> str:
        if isinstance(self.table, (models.Model, type(models.Model))):
            table = self.table._meta.db_table
        else:
            table = self.table or self.key_field.get_table()
        return f"{table}.{self.field}"

    def get_table_primary_key_field(self):
        if isinstance(self.key_field, KeyField):
            return self.key_field.primary_key_field

        if isinstance(self.table, (models.Model, type(models.Model))):
            return getattr(self.table, "paradedb_key_field", self.table._meta.pk.name)

    def __str__(self):
        return self.get_sql()


def resolve_f_model_and_field(f_expr, query, connection=None):
    if not isinstance(f_expr, models.F):
        raise TypeError("Expected a models.F() expression")

    resolved = f_expr.resolve_expression(query)

    if not isinstance(resolved, Col):
        raise ValueError("Could not resolve F() expression into a column")

    field = resolved.target
    return field.model, field.name, resolved.alias


def postgres_array(iterable: typing.Iterable) -> str:
    def format_value(v):
        if v is None:
            return "NULL"
        # Strings need escaping and quotes
        if isinstance(v, str):
            s = v.replace("\\", "\\\\").replace("'", "''")
            return f"'{s}'"
        return str(v)

    items = ", ".join(format_value(v) for v in iterable)
    return f"ARRAY[{items}]"


def escape_query(value: str) -> str:
    if not isinstance(value, str):
        return value

    # Define all special characters that need escaping
    special_chars = r'+^`:{}"\[\]()<>\~!\\*\s,'
    # Escape each special character by prefixing with a backslash
    pattern = f"([{special_chars}])"
    escaped_value = re.sub(pattern, r"\\\1", value)

    return escaped_value
