from __future__ import annotations
from typing import Optional
from logging import Logger

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLineEdit, QWidget

from ._enable_watcher import EnabledWatcher
from integrated_widgets.util.base_controller import BaseController


class GuardedLineEdit(QLineEdit):
    """QLineEdit that exposes an enabledChanged(bool) signal via an internal watcher."""
    enabledChanged = Signal(bool)

    def __init__(
        self,
        owner: BaseController,
        logger: Optional[Logger] = None,
        parent: Optional[QWidget] = None,
    ) -> None:

        super().__init__(parent)

        self._owner = owner
        self._logger = logger

        # Watch *this* line edit's enabled state
        self._enabled_watcher = EnabledWatcher(self, parent=self)
        self._enabled_watcher.enabledChanged.connect(self.enabledChanged)