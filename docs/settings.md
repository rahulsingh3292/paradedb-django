#

## PARADEDB_LOOKUP_SKIP_RHS_PREP

`PARADEDB_LOOKUP_SKIP_RHS_PREP` is an optional setting that lists lookup names that should skip RHS (right-hand side) preparation.
It must be either a list or None. default `None`

```python
PARADEDB_LOOKUP_SKIP_RHS_PREP = ["match"]
```

## PARADEDB_RAISE_ON_MODEL_NOT_FOUND
`PARADEDB_RAISE_ON_MODEL_NOT_FOUND` : if set to `true` and when resolving lookup expression for a queryset fails then, it raises `ModelNotFoundError`. default `True`.

```python
PARADEDB_RAISE_ON_MODEL_NOT_FOUND = True
```

## PARADEDB_USE_LEGACY
`PARADEDB_USE_LEGACY`: force to use `paradedb` schema legacy functions.


```python
PARADEDB_USE_LEGACY = ['match']
```

## PARADEBD_USE_V2
`PARADEBD_USE_V2` : when set to `true` then `pdb` schema functions will be used.
