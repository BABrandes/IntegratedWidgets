"""Example widget displaying a United scalar bound to an observable.

The widget never creates a QApplication; it assumes the host has done so.
"""

from __future__ import annotations

from typing import Generic, Optional, Protocol, TypeVar

from PySide6.QtCore import QObject, Qt, Slot
from PySide6.QtWidgets import QLabel


# Minimal structural types to avoid hard dependency on specific runtime shapes
T = TypeVar("T")


class SupportsUnited(Protocol):
    """Structural protocol for a united scalar value.

    We avoid importing heavy types here. The protocol matches typical attributes
    used for display. If the concrete type provides ``magnitude`` and ``unit`` or
    ``units``, the widget will render accordingly. Fallback to ``str(value)``.
    """

    # Common attribute names in unit systems
    magnitude: float
    # some libs use ``unit`` others ``units``
    unit: object  # pragma: no cover - structural only
    units: object  # pragma: no cover - structural only


class ObservableLike(Generic[T], Protocol):
    """Structural protocol for an observable object.

    Expected to provide a ``subscribe(callable)`` method and a ``value`` attr.
    """

    value: T

    def subscribe(self, callback: object) -> object:  # return disposable/handle
        ...


class UnitValueDisplay(QLabel):
    """QLabel showing a united scalar's magnitude and unit from an observable."""

    def __init__(self, observable: ObservableLike[SupportsUnited], parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self._observable: ObservableLike[SupportsUnited] = observable
        # Subscribe to updates; store handle if provided
        self._subscription = self._observable.subscribe(self._on_value_changed)
        # Initialize with current value if available
        try:
            current = self._observable.value
            self._on_value_changed(current)
        except Exception:
            # If observable has no current value yet, leave empty
            self.setText("")

    @Slot(object)
    def _on_value_changed(self, value: SupportsUnited) -> None:
        text = self._format_value(value)
        self.setText(text)

    @staticmethod
    def _format_value(value: SupportsUnited) -> str:
        # Try common attribute combinations
        try:
            magnitude = getattr(value, "magnitude")
            unit = getattr(value, "unit", None) or getattr(value, "units", None)
            if unit is not None:
                return f"{magnitude} {unit}"
        except Exception:
            pass
        # Fallback
        return str(value)


