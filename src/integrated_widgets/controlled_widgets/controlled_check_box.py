from __future__ import annotations

from integrated_widgets.controllers.core.base_controller import BaseController

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QCheckBox, QWidget
from typing import Optional, Any
from logging import Logger

from ._enable_watcher import EnabledWatcher
from .base_controlled_widget import BaseControlledWidget


class ControlledCheckBox(BaseControlledWidget, QCheckBox):
    """

    Signaling behavior:
    ------------------
    "userInputFinishedSignal" is emitted for the QCheckBox "stateChanged" signal.
    """

    enabledChanged = Signal(bool)

    def __init__(self, controller: BaseController[Any, Any], text: str = "", parent_of_widget: Optional[QWidget] = None, logger: Optional[Logger] = None) -> None:
        BaseControlledWidget.__init__(self, controller, logger) # type: ignore
        QCheckBox.__init__(self, text, parent_of_widget)

        self._enabled_watcher = EnabledWatcher(self, parent=self)
        self._enabled_watcher.enabledChanged.connect(self.enabledChanged)

        self.stateChanged.connect(self._on_user_input_finished)

    def __str__(self) -> str:
        checked = self.isChecked()
        text = self.text()
        if len(text) > 15:
            text = text[:12] + "..."
        return f"{self.__class__.__name__}(checked={checked}, text={text!r})"

    def __repr__(self) -> str:
        checked = self.isChecked()
        text = self.text()
        if len(text) > 15:
            text = text[:12] + "..."
        return f"{self.__class__.__name__}(checked={checked}, text={text!r}, id={hex(id(self))})"

