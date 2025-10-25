from __future__ import annotations

from typing import Optional, Iterable, Any
from logging import Logger
from PySide6.QtWidgets import QListWidget, QWidget, QListWidgetItem
from integrated_widgets.controllers.core.base_controller import BaseController
from .base_controlled_widget import BaseControlledWidget


def _is_internal_update(controller: BaseController[Any, Any, Any]) -> bool:
    return bool(getattr(controller, "_internal_widget_update", False))

class ControlledListWidget(BaseControlledWidget, QListWidget):
    """QListWidget that guards programmatic mutations to avoid UI↔model loops.

    Methods that mutate the item model require the controller's internal update
    context (owner._internal_widget_update=True). End-user interactions remain
    unrestricted.
    """

    def __init__(self, controller: BaseController[Any, Any, Any], parent_of_widget: Optional[QWidget] = None, logger: Optional[Logger] = None) -> None:
        BaseControlledWidget.__init__(self, controller, logger)
        QListWidget.__init__(self, parent_of_widget)

    def clear(self) -> None:  # type: ignore[override]
        if not _is_internal_update(self._controller):
            raise RuntimeError(
                "Direct programmatic modification of list widget is not allowed; perform changes within the controller's internal update context"
            )
        super().clear()

    def addItem(self, item: QListWidgetItem | str) -> None:  # type: ignore[override]
        if not _is_internal_update(self._controller):
            raise RuntimeError(
                "Direct programmatic modification of list widget is not allowed; perform changes within the controller's internal update context"
            )
        super().addItem(item)

    def addItems(self, labels: Iterable[str]) -> None:  # type: ignore[override]
        if not _is_internal_update(self._controller):
            raise RuntimeError(
                "Direct programmatic modification of list widget is not allowed; perform changes within the controller's internal update context"
            )
        super().addItems(list(labels))

    def insertItem(self, row: int, item: QListWidgetItem | str) -> None:  # type: ignore[override]
        if not _is_internal_update(self._controller):
            raise RuntimeError(
                "Direct programmatic modification of list widget is not allowed; perform changes within the controller's internal update context"
            )
        super().insertItem(row, item)

    def takeItem(self, row: int) -> QListWidgetItem | None:  # type: ignore[override]
        if not _is_internal_update(self._controller):
            raise RuntimeError(
                "Direct programmatic modification of list widget is not allowed; perform changes within the controller's internal update context"
            )
        return super().takeItem(row)

    def removeItemWidget(self, item: QListWidgetItem) -> None:  # type: ignore[override]
        if not _is_internal_update(self._controller):
            raise RuntimeError(
                "Direct programmatic modification of list widget is not allowed; perform changes within the controller's internal update context"
            )
        super().removeItemWidget(item)

    def sortItems(self, *args, **kwargs) -> None:  # type: ignore[override]
        if not _is_internal_update(self._controller):
            raise RuntimeError(
                "Direct programmatic modification of list widget is not allowed; perform changes within the controller's internal update context"
            )
        super().sortItems(*args, **kwargs) # type: ignore


