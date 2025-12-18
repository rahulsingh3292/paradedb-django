from django.contrib.postgres.operations import CreateExtension


__all__ = ["ParadeDbExtension"]


class ParadeDbExtension(CreateExtension):
    def __init__(self):
        self.name = "pg_search"
