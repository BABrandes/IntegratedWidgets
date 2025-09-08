from __future__ import annotations

from logging import Logger
from typing import Optional

from PySide6.QtWidgets import QComboBox, QWidget

from integrated_widgets.widget_controllers.base_widget_controller import BaseWidgetController
from integrated_widgets.util.resources import log_msg


def _is_internal_update(owner: object) -> bool:
    return bool(getattr(owner, "_internal_widget_update", False))


class GuardedComboBox(QComboBox):
    def __init__(self, owner: BaseWidgetController, logger: Optional[Logger] = None) -> None:
        super().__init__(owner._owner_widget)
        self._owner = owner
        self._logger = logger

    def clear(self) -> None:  # type: ignore[override]
        if not _is_internal_update(self._owner):
            log_msg(self, "clear", self._logger, "Direct programmatic modification of combo box is not allowed; perform changes within the controller's internal update context")
            raise RuntimeError("Direct programmatic modification of combo box is not allowed; perform changes within the controller's internal update context")
        super().clear()

    def addItem(self, *args, **kwargs) -> None:  # type: ignore[override]
        if not _is_internal_update(self._owner):
            log_msg(self, "addItem", self._logger, "Direct programmatic modification of combo box is not allowed; perform changes within the controller's internal update context")
            raise RuntimeError("Direct programmatic modification of combo box is not allowed; perform changes within the controller's internal update context")
        super().addItem(*args, **kwargs)

    def insertItem(self, *args, **kwargs) -> None:  # type: ignore[override]
        if not _is_internal_update(self._owner):
            log_msg(self, "insertItem", self._logger, "Direct programmatic modification of combo box is not allowed; perform changes within the controller's internal update context")
            raise RuntimeError("Direct programmatic modification of combo box is not allowed; perform changes within the controller's internal update context")
        super().insertItem(*args, **kwargs)

    def removeItem(self, *args, **kwargs) -> None:  # type: ignore[override]
        if not _is_internal_update(self._owner):
            log_msg(self, "removeItem", self._logger, "Direct programmatic modification of combo box is not allowed; perform changes within the controller's internal update context")
            raise RuntimeError("Direct programmatic modification of combo box is not allowed; perform changes within the controller's internal update context")
        super().removeItem(*args, **kwargs)


