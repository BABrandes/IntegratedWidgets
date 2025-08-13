from __future__ import annotations

from typing import Optional

from PySide6.QtWidgets import QLabel, QWidget


def _is_internal_update(owner: object) -> bool:
    return bool(getattr(owner, "_internal_widget_update", False))


class GuardedLabel(QLabel):
    def __init__(self, owner: Optional[QWidget] = None) -> None:
        super().__init__(owner)
        self._owner = owner

    def setText(self, text: str) -> None:  # type: ignore[override]
        if not _is_internal_update(self._owner):
            raise RuntimeError("Direct modification of value_label is not allowed")
        super().setText(text)


