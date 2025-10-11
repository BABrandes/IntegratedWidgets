from __future__ import annotations

from integrated_widgets.util.base_controller import BaseController

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QCheckBox, QWidget
from typing import Optional
from logging import Logger

from ._enable_watcher import EnabledWatcher
from .base_controlled_widget import BaseControlledWidget


class ControlledCheckBox(BaseControlledWidget, QCheckBox):
    enabledChanged = Signal(bool)

    def __init__(self, controller: BaseController, text: str = "", parent_of_widget: Optional[QWidget] = None, logger: Optional[Logger] = None) -> None:
        BaseControlledWidget.__init__(self, controller, logger)
        QCheckBox.__init__(self, text, parent_of_widget)

        self._enabled_watcher = EnabledWatcher(self, parent=self)
        self._enabled_watcher.enabledChanged.connect(self.enabledChanged)


