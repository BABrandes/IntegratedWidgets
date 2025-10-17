from __future__ import annotations

from typing import Optional, Any
from logging import Logger
from PySide6.QtWidgets import QLabel, QWidget
from PySide6.QtCore import Signal
from integrated_widgets.util.base_controller import BaseController
from .base_controlled_widget import BaseControlledWidget

def _is_internal_update(controller: BaseController[Any, Any, Any]) -> bool:
    # Check if the owner has the internal update flag set
    return bool(getattr(controller, "_internal_widget_update", False))



class ControlledQLabel(BaseControlledWidget, QLabel):

    text_changed = Signal(str)

    def __init__(self, controller: BaseController[Any, Any, Any], parent_of_widget: Optional[QWidget] = None, logger: Optional[Logger] = None) -> None:
        BaseControlledWidget.__init__(self, controller, logger)
        QLabel.__init__(self, parent_of_widget)

    def setText(self, text: str) -> None:  # type: ignore[override]
        if not _is_internal_update(self._controller):
            raise RuntimeError("Direct modification of value_label is not allowed")
        super().setText(text)
        self.text_changed.emit(text)


