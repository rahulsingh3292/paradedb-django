from django.apps import AppConfig


class EcommerceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ecommerce"

    def ready(self):
        from paradedb.monkey_patch import patch_django_lookup

        patch_django_lookup()
