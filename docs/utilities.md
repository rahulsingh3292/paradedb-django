> - All the utilities is inside the `paradedb.utils` module

#

## KeyField

`KeyField` is a utility class to represent a key field of a Django model or a database table, and generate SQL references. it can be used with [Expressions](./expressions.md)

### Parameters

- `table` (`Type[models.Model] | models.Model | str`):
  The model class, model instance, or table name.
  - If `str`, `primary_key_field` must also be provided.

- `primary_key_field` (`Optional[str]`):
  Name of the primary key field if the table is provided as a string. Optional if using a model.

### Methods

#### `__str__()`
Returns the SQL representation of the key field by calling `get_sql()`.

#### `get_sql()`
Generates the SQL expression for the key field:
```python
"{table}.{key_field}"
```

#### `get_lhs_sql()`

Returns a left-hand side SQL placeholder for the key field:

```python
"{table}.{key_field} @@@ "
```

#### `get_table()`

Returns the table name:

* If `table` is a Django model or instance, returns `table._meta.db_table`.
* If `table` is a string, returns the string itself.

#### `resolve_sql_from_table_column_string(table_column_string: str) -> KeyField`

Class method that creates a `KeyField` from a string in `table.column` format.

* `table_column_string` (`str`): Expected format `"table.column"`.

### Example
```python
Article.objects.filter(Match('title', 'value', key_field=KeyField(Article), match_op=True))
```

---

## TableField

`TableField` represents a specific field in a table or model key field and generates SQL references.

### Parameters

* `field` (`str`): The name of the field. Required.
* `table` (`typing.Optional[typing.Type[models.Model] | models.Model | str] `): Name of the table. Optional if `key_field` is provided.
* `key_field` (`typing.Optional[KeyField]`): A `KeyField` instance representing the table's key. Required if `table` is not provided.

### Methods

#### `get_sql()`

Generates the SQL expression for the table field:

```python
"{table}.{field}"
```

* `table` is either provided directly or derived from `key_field`.

###  Example
```python
Article.objects.select_related("user").filter(
        Search(TableField("username", key_field=KeyField(TableUser)), "python")
    )
```

---
