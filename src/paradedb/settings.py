from django.conf import settings


PARADEDB_LOOKUP_SKIP_RHS_PREP: list | None = getattr(
    settings, "PARADEDB_LOOKUP_SKIP_RHS_PREP", None
)
assert isinstance(
    PARADEDB_LOOKUP_SKIP_RHS_PREP, (list, type(None))
), "PARADEDB_LOOKUP_SKIP_RHS_PREP must be a list or None"

PARADEDB_RAISE_ON_MODEL_NOT_FOUND: bool = getattr(
    settings, "PARADEDB_RAISE_ON_MODEL_NOT_FOUND", False
)
assert isinstance(
    PARADEDB_RAISE_ON_MODEL_NOT_FOUND, bool
), "PARADEDB_RAISE_ON_MODEL_NOT_FOUND must be a bool"


PARADEBD_USE_V2: bool = getattr(settings, "PARADEBD_USE_V2", False)
assert isinstance(PARADEBD_USE_V2, bool), "PARADEBD_USE_V2 must be a bool"

PARADEDB_USE_LEGACY: list[str] = getattr(
    settings, "PARADEDB_USE_LEGACY", ["term", "match"]
)
assert isinstance(PARADEDB_USE_LEGACY, list), "PARADEDB_USE_LEGACY must be a list"
