from __future__ import annotations

from PySide6.QtWidgets import QSlider, QWidget


class GuardedSlider(QSlider):
    def __init__(self, owner: QWidget, orientation=None) -> None:  # orientation optional for convenience
        if orientation is None:
            super().__init__(owner)
        else:
            super().__init__(orientation, owner)
        self._owner = owner
    # Programmatic setValue allowed; controller manages commit


