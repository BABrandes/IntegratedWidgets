from __future__ import annotations
from typing import Optional, Any
from logging import Logger

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLineEdit, QWidget

from ._enable_watcher import EnabledWatcher
from integrated_widgets.controllers.core.base_controller import BaseController
from .base_controlled_widget import BaseControlledWidget

class ControlledLineEdit(BaseControlledWidget, QLineEdit):
    """QLineEdit that exposes an enabledChanged(bool) signal via an internal watcher."""
    enabledChanged = Signal(bool)

    def __init__(
        self,
        controller: BaseController[Any, Any],
        parent_of_widget: Optional[QWidget] = None,
        logger: Optional[Logger] = None,
    ) -> None:
        BaseControlledWidget.__init__(self, controller, logger)
        QLineEdit.__init__(self, parent_of_widget)

        # Watch *this* line edit's enabled state
        self._enabled_watcher = EnabledWatcher(self, parent=self)
        self._enabled_watcher.enabledChanged.connect(self.enabledChanged)