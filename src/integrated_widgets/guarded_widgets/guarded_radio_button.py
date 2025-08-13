from __future__ import annotations

from typing import Optional

from PySide6.QtWidgets import QRadioButton, QWidget

class GuardedRadioButton(QRadioButton):
    def __init__(self, owner: Optional[QWidget] = None, text: str = "") -> None:
        super().__init__(text, owner)
        self._owner = owner
    # No extra guards needed; selection is user-driven


