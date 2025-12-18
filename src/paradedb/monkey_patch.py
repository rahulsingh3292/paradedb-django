def patch_django_lookup():
    from django.db.models.lookups import Lookup

    original_init = Lookup.__init__

    def init(self, lhs, rhs, *args, **kwargs):
        self.rhs_original = rhs
        original_init(self, lhs, rhs, *args, **kwargs)

    Lookup.__init__ = init
    Lookup._parade_patched = True
