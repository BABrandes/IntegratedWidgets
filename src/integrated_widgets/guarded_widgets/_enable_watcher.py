from __future__ import annotations

from typing import Optional
from PySide6.QtCore import QObject, Signal, QEvent
from PySide6.QtWidgets import QWidget


class EnabledWatcher(QObject):
    """
    Attach to any QWidget to get a signal whenever its enabled/disabled state changes.
    """

    enabledChanged = Signal(bool)

    def __init__(self, target: QWidget, parent: Optional[QObject] = None) -> None:
        super().__init__(parent or target)
        self._target = target
        target.installEventFilter(self)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if watched is self._target and event.type() == QEvent.Type.EnabledChange:
            self.enabledChanged.emit(self._target.isEnabled())
        return super().eventFilter(watched, event)