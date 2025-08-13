
"""General small helpers and defaults."""

# Default formatter for RealUnitedScalar value display
DEFAULT_FLOAT_FORMAT_VALUE = lambda value: f"{value.value():.3f} {value.unit}"


class InternalUpdateHelper:
    """Shared helper to mark an owner with an internal update flag.

    Controllers can mix this in, or widgets can instantiate and use it to set
    the attribute ``_internal_widget_update`` on the owner during programmatic
    UI updates. Guarded widgets check this flag to allow model mutations.
    """

    def __init__(self, owner: object) -> None:
        self._owner = owner

    def context(self):
        class _Ctx:
            def __init__(self, owner: object) -> None:
                self._owner = owner
            def __enter__(self) -> None:
                setattr(self._owner, "_internal_widget_update", True)
            def __exit__(self, exc_type, exc, tb) -> None:
                setattr(self._owner, "_internal_widget_update", False)
        return _Ctx(self._owner)