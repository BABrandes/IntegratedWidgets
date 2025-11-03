from __future__ import annotations

from typing import Optional, Any
from logging import Logger

from PySide6.QtWidgets import QComboBox, QWidget
from PySide6.QtCore import Qt

from integrated_widgets.controllers.core.base_controller import BaseController
from integrated_widgets.auxiliaries.resources import log_msg, combo_box_find_data
from .base_controlled_widget import BaseControlledWidget

def _is_internal_update(controller: BaseController[Any, Any]) -> bool:
    return bool(getattr(controller, "_internal_widget_update", False))

class ControlledComboBox(BaseControlledWidget, QComboBox):
    """

    Signaling behavior:
    ------------------
    "userInputFinishedSignal" is emitted for the QComboBox "currentIndexChanged" signal.
    """

    def __init__(self, controller: BaseController[Any, Any], parent_of_widget: Optional[QWidget] = None, logger: Optional[Logger] = None) -> None:
        BaseControlledWidget.__init__(self, controller, logger) # type: ignore
        QComboBox.__init__(self, parent_of_widget)

        self.currentIndexChanged.connect(self._on_user_input_finished)

    def clear(self) -> None:  # type: ignore[override]
        if not _is_internal_update(self._controller): # type: ignore
            log_msg(self, "clear", self._logger, "Direct programmatic modification of combo box is not allowed; perform changes within the controller's internal update context")
            raise RuntimeError("Direct programmatic modification of combo box is not allowed; perform changes within the controller's internal update context")
        QComboBox.clear(self)

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

    def __str__(self) -> str:
        current = self.currentText()
        count = self.count()
        if len(current) > 15:
            current = current[:12] + "..."
        return f"{self.__class__.__name__}(current={current!r}, items={count})"

    def __repr__(self) -> str:
        current = self.currentText()
        count = self.count()
        if len(current) > 15:
            current = current[:12] + "..."
        return f"{self.__class__.__name__}(current={current!r}, items={count}, id={hex(id(self))})"

    # Fixing the broken finddata method
    def findData(self, data: Any, /, role: int = Qt.ItemDataRole.UserRole, flags: Qt.MatchFlag = Qt.MatchFlag.MatchExactly) -> int:
        if role == Qt.ItemDataRole.UserRole and flags == Qt.MatchFlag.MatchExactly: 
            return combo_box_find_data(self, data)
        else:
            raise RuntimeError("Use super().findData() to find data with custom roles or flags")
            

