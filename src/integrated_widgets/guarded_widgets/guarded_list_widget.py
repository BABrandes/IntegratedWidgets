from __future__ import annotations

from typing import Optional, Iterable

from PySide6.QtWidgets import QListWidget, QWidget, QListWidgetItem
from integrated_widgets.widget_controllers.base_widget_controller import BaseWidgetController


def _is_internal_update(owner: object) -> bool:
    return bool(getattr(owner, "_internal_widget_update", False))


class GuardedListWidget(QListWidget):
    """QListWidget that guards programmatic mutations to avoid UI↔model loops.

    Methods that mutate the item model require the controller's internal update
    context (owner._internal_widget_update=True). End-user interactions remain
    unrestricted.
    """

    def __init__(self, owner: BaseWidgetController) -> None:
        super().__init__(owner._owner_widget)
        self._owner = owner

    def clear(self) -> None:  # type: ignore[override]
        if not _is_internal_update(self._owner):
            raise RuntimeError(
                "Direct programmatic modification of list widget is not allowed; perform changes within the controller's internal update context"
            )
        super().clear()

    def addItem(self, item: QListWidgetItem | str) -> None:  # type: ignore[override]
        if not _is_internal_update(self._owner):
            raise RuntimeError(
                "Direct programmatic modification of list widget is not allowed; perform changes within the controller's internal update context"
            )
        super().addItem(item)

    def addItems(self, labels: Iterable[str]) -> None:  # type: ignore[override]
        if not _is_internal_update(self._owner):
            raise RuntimeError(
                "Direct programmatic modification of list widget is not allowed; perform changes within the controller's internal update context"
            )
        super().addItems(labels)

    def insertItem(self, row: int, item: QListWidgetItem | str) -> None:  # type: ignore[override]
        if not _is_internal_update(self._owner):
            raise RuntimeError(
                "Direct programmatic modification of list widget is not allowed; perform changes within the controller's internal update context"
            )
        super().insertItem(row, item)

    def takeItem(self, row: int) -> QListWidgetItem | None:  # type: ignore[override]
        if not _is_internal_update(self._owner):
            raise RuntimeError(
                "Direct programmatic modification of list widget is not allowed; perform changes within the controller's internal update context"
            )
        return super().takeItem(row)

    def removeItemWidget(self, item: QListWidgetItem) -> None:  # type: ignore[override]
        if not _is_internal_update(self._owner):
            raise RuntimeError(
                "Direct programmatic modification of list widget is not allowed; perform changes within the controller's internal update context"
            )
        super().removeItemWidget(item)

    def sortItems(self, *args, **kwargs) -> None:  # type: ignore[override]
        if not _is_internal_update(self._owner):
            raise RuntimeError(
                "Direct programmatic modification of list widget is not allowed; perform changes within the controller's internal update context"
            )
        super().sortItems(*args, **kwargs)


