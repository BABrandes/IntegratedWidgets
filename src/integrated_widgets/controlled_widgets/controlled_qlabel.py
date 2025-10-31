from __future__ import annotations

from typing import Optional, Any
from logging import Logger
from PySide6.QtWidgets import QLabel, QWidget
from PySide6.QtCore import Signal
from integrated_widgets.controllers.core.base_controller import BaseController
from .base_controlled_widget import BaseControlledWidget

def _is_internal_update(controller: BaseController[Any, Any]) -> bool:
    # Check if the owner has the internal update flag set
    return bool(getattr(controller, "_internal_widget_update", False))



class ControlledQLabel(BaseControlledWidget, QLabel):
    """

    Signaling behavior:
    ------------------
    "userInputFinishedSignal" is emitted for the QLabel "textChanged" signal.
    """

    text_changed = Signal(str)

    def __init__(self, controller: BaseController[Any, Any], parent_of_widget: Optional[QWidget] = None, logger: Optional[Logger] = None) -> None:
        BaseControlledWidget.__init__(self, controller, logger)
        QLabel.__init__(self, parent_of_widget)

        # Note: Labels are display-only and don't generate user input signals
        # The text_changed signal is only for internal tracking/notification, not user input

    def setText(self, text: str) -> None:  # type: ignore[override]
        if not _is_internal_update(self._controller):
            raise RuntimeError("Direct modification of value_label is not allowed")
        super().setText(text)
        self.text_changed.emit(text)

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

