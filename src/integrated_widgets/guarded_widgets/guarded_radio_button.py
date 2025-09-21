from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QRadioButton, QWidget

from ._enable_watcher import EnabledWatcher

class GuardedRadioButton(QRadioButton):
    enabledChanged = Signal(bool)

    def __init__(self, owner: Optional[QWidget] = None, text: str = "") -> None:
        super().__init__(text, owner)
        self._owner = owner

        self._enabled_watcher = EnabledWatcher(self, parent=self)
        self._enabled_watcher.enabledChanged.connect(self.enabledChanged)


