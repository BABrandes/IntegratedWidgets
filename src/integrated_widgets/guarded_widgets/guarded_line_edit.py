from __future__ import annotations

from typing import Optional

from PySide6.QtWidgets import QLineEdit, QWidget

class GuardedLineEdit(QLineEdit):
    def __init__(self, owner: Optional[QWidget] = None) -> None:
        super().__init__(owner)
        self._owner = owner
    # Programmatic setText allowed; controller commits via editingFinished


