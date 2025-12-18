from functools import cache

from django.db import connection


__all__ = ["get_version"]


@cache
def get_version():
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM paradedb.version_info();")
        res = cursor.fetchone()[0]
    return res
