from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QSlider, QWidget


class GuardedRangeSlider(QWidget):
    """Simple two-handle range using two QSliders; controller manages layout.

    For sophisticated range sliders, integrate a dedicated widget later.
    """

    def __init__(self, owner: QWidget, orientation: Qt.Orientation = Qt.Horizontal) -> None:
        super().__init__(owner)
        self._owner = owner
        self.min_slider = QSlider(orientation, self)
        self.max_slider = QSlider(orientation, self)
        self.min_slider.setRange(0, 100)
        self.max_slider.setRange(0, 100)
        self.min_slider.setValue(0)
        self.max_slider.setValue(100)


