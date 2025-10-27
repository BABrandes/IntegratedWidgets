from __future__ import annotations

from typing import Optional, Any
from logging import Logger
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QRadioButton, QWidget

from ._enable_watcher import EnabledWatcher
from integrated_widgets.controllers.core.base_controller import BaseController
from .base_controlled_widget import BaseControlledWidget

class ControlledRadioButton(BaseControlledWidget, QRadioButton):
    enabledChanged = Signal(bool)

    def __init__(self, controller: BaseController[Any, Any], text: str = "", parent_of_widget: Optional[QWidget] = None, logger: Optional[Logger] = None) -> None:
        BaseControlledWidget.__init__(self, controller, logger)
        QRadioButton.__init__(self, text, parent_of_widget)

        self._enabled_watcher = EnabledWatcher(self, parent=self)
        self._enabled_watcher.enabledChanged.connect(self.enabledChanged)


