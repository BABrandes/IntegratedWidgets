from __future__ import annotations
from typing import Optional, Any
from logging import Logger

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLineEdit, QWidget

from ._enable_watcher import EnabledWatcher
from integrated_widgets.controllers.core.base_controller import BaseController
from .base_controlled_widget import BaseControlledWidget

class ControlledLineEdit(BaseControlledWidget, QLineEdit):
    """

    Signaling behavior:
    ------------------
    "userInputFinishedSignal" is emitted for the QLineEdit "editingFinished" signal.
    """

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

        self.editingFinished.connect(self._on_user_input_finished)
        self.returnPressed.connect(self._on_return_pressed)

    def _on_return_pressed(self) -> None:
        """Clear focus when Enter is pressed, which triggers editingFinished."""
        self.clearFocus()

    def __str__(self) -> str:
        text = self.text()
        if len(text) > 20:
            text = text[:17] + "..."
        return f"{self.__class__.__name__}(text={text!r})"

    def __repr__(self) -> str:
        text = self.text()
        if len(text) > 20:
            text = text[:17] + "..."
        return f"{self.__class__.__name__}(text={text!r}, id={hex(id(self))})"