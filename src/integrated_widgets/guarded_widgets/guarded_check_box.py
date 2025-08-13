from __future__ import annotations

from PySide6.QtWidgets import QCheckBox, QWidget


class GuardedCheckBox(QCheckBox):
    def __init__(self, owner: QWidget, text: str = "") -> None:
        super().__init__(text, owner)
        self._owner = owner
    # Programmatic setChecked allowed; controller commits via signals


