from django.apps import AppConfig


class ParadeDBConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "paradedb"
    verbose_name = "Parade DB"

    def ready(self):
        from paradedb.lookups import ModelResolverFromTable
        from paradedb.monkey_patch import patch_django_lookup

        patch_django_lookup()
        ModelResolverFromTable.preload()
