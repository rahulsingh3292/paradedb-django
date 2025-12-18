from django.db import models


__all__ = ["ValueCast"]


class ValueCast(models.Func):
    function = ""
    template = "%(expressions)s::%(cast)s"

    def __init__(self, value: str, cast: str, *args, **kwargs):
        super().__init__(
            models.Value(value),
            cast=cast,
            output_field=kwargs.pop("output_field", models.TextField()),
            *args,
            **kwargs,
        )
