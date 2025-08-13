from __future__ import annotations

from typing import Optional

from PySide6.QtWidgets import QComboBox, QWidget


def _is_internal_update(owner: object) -> bool:
    return bool(getattr(owner, "_internal_widget_update", False))


class GuardedComboBox(QComboBox):
    def __init__(self, owner: Optional[QWidget] = None) -> None:
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


