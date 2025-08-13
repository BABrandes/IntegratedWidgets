"""Guarded Qt widgets used internally by composite widgets.

These classes forward most behavior to their Qt base classes but restrict
programmatic mutation unless the owning widget is performing an internal
update (flagged by `_internal_widget_update = True`).

This helps enforce the rule that only the composite widget should mutate
its child widgets' state, while still allowing user-driven interactions.
"""

from __future__ import annotations

from typing import Any

from PySide6.QtWidgets import QLabel, QComboBox, QLineEdit, QWidget


def _is_internal_update(owner: Any) -> bool:
    return bool(getattr(owner, "_internal_widget_update", False))


class GuardedLabel(QLabel):
    def __init__(self, owner: QWidget) -> None:
        super().__init__(owner)
        self._owner = owner

    def setText(self, text: str) -> None:  # type: ignore[override]
        if not _is_internal_update(self._owner):
            raise RuntimeError("Direct modification of value_label is not allowed")
        super().setText(text)


class GuardedComboBox(QComboBox):
    def __init__(self, owner: QWidget) -> None:
        super().__init__(owner)
        self._owner = owner

    def clear(self) -> None:  # type: ignore[override]
        if not _is_internal_update(self._owner):
            raise RuntimeError("Direct modification of unit_combo is not allowed")
        super().clear()

    def addItem(self, *args, **kwargs) -> None:  # type: ignore[override]
        if not _is_internal_update(self._owner):
            raise RuntimeError("Direct modification of unit_combo is not allowed")
        super().addItem(*args, **kwargs)

    def insertItem(self, *args, **kwargs) -> None:  # type: ignore[override]
        if not _is_internal_update(self._owner):
            raise RuntimeError("Direct modification of unit_combo is not allowed")
        super().insertItem(*args, **kwargs)

    def removeItem(self, *args, **kwargs) -> None:  # type: ignore[override]
        if not _is_internal_update(self._owner):
            raise RuntimeError("Direct modification of unit_combo is not allowed")
        super().removeItem(*args, **kwargs)


class GuardedLineEdit(QLineEdit):
    def __init__(self, owner: QWidget) -> None:
        super().__init__(owner)
        self._owner = owner

    # We intentionally allow programmatic setText to support workflows/tests.
    # The owning widget commits changes on editingFinished.


