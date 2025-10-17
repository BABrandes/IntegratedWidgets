from __future__ import annotations

from typing import Optional, Any
from logging import Logger

from PySide6.QtWidgets import QComboBox, QWidget

from integrated_widgets.util.base_controller import BaseController
from integrated_widgets.util.resources import log_msg
from .base_controlled_widget import BaseControlledWidget

def _is_internal_update(controller: BaseController[Any, Any, Any]) -> bool:
    return bool(getattr(controller, "_internal_widget_update", False))

class ControlledComboBox(BaseControlledWidget, QComboBox):
    def __init__(self, controller: BaseController[Any, Any, Any], parent_of_widget: Optional[QWidget] = None, logger: Optional[Logger] = None) -> None:
        BaseControlledWidget.__init__(self, controller, logger) # type: ignore
        QComboBox.__init__(self, parent_of_widget)

    def clear(self) -> None:  # type: ignore[override]
        if not _is_internal_update(self._controller): # type: ignore
            log_msg(self, "clear", self._logger, "Direct programmatic modification of combo box is not allowed; perform changes within the controller's internal update context")
            raise RuntimeError("Direct programmatic modification of combo box is not allowed; perform changes within the controller's internal update context")
        super().clear()

    def addItem(self, *args, **kwargs) -> None:  # type: ignore[override]
        if not _is_internal_update(self._controller): # type: ignore
            log_msg(self, "addItem", self._logger, "Direct programmatic modification of combo box is not allowed; perform changes within the controller's internal update context")
            raise RuntimeError("Direct programmatic modification of combo box is not allowed; perform changes within the controller's internal update context")
        super().addItem(*args, **kwargs) # type: ignore

    def insertItem(self, *args, **kwargs) -> None:  # type: ignore[override]
        if not _is_internal_update(self._controller): # type: ignore
            log_msg(self, "insertItem", self._logger, "Direct programmatic modification of combo box is not allowed; perform changes within the controller's internal update context")
            raise RuntimeError("Direct programmatic modification of combo box is not allowed; perform changes within the controller's internal update context")
        super().insertItem(*args, **kwargs) # type: ignore

    def removeItem(self, *args, **kwargs) -> None:  # type: ignore[override]
        if not _is_internal_update(self._controller): # type: ignore # type: ignore
            log_msg(self, "removeItem", self._logger, "Direct programmatic modification of combo box is not allowed; perform changes within the controller's internal update context")
            raise RuntimeError("Direct programmatic modification of combo box is not allowed; perform changes within the controller's internal update context")
        super().removeItem(*args, **kwargs) # type: ignore


