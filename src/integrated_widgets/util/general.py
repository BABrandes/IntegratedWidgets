from __future__ import annotations
from types import TracebackType

from united_system import RealUnitedScalar

"""General small helpers and defaults."""

# Default formatter for RealUnitedScalar value display
def format_real_united_scalar(value: RealUnitedScalar) -> str:
    return f"{value.value():.3f} {value.unit}"
DEFAULT_FLOAT_FORMAT_VALUE = format_real_united_scalar

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
            def __exit__(self, exc_type: type[BaseException] | None, exc: BaseException | None, tb: TracebackType | None) -> None:
                setattr(self._owner, "_internal_widget_update", False)
        return _Ctx(self._owner)