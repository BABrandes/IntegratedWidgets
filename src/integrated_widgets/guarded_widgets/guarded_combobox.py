from __future__ import annotations

from typing import Optional

from PySide6.QtWidgets import QComboBox, QWidget

from integrated_widgets.widget_controllers.base_controller import BaseObservableController


def _is_internal_update(owner: object) -> bool:
    return bool(getattr(owner, "_internal_widget_update", False))


class GuardedComboBox(QComboBox):
    def __init__(self, owner: BaseObservableController) -> None:
        super().__init__(owner._owner_widget)
        self._owner = owner

    def clear(self) -> None:  # type: ignore[override]
        if not _is_internal_update(self._owner):
            raise RuntimeError("Direct programmatic modification of combo box is not allowed; perform changes within the controller's internal update context")
        super().clear()

    def addItem(self, *args, **kwargs) -> None:  # type: ignore[override]
        if not _is_internal_update(self._owner):
            raise RuntimeError("Direct programmatic modification of combo box is not allowed; perform changes within the controller's internal update context")
        super().addItem(*args, **kwargs)

    def insertItem(self, *args, **kwargs) -> None:  # type: ignore[override]
        if not _is_internal_update(self._owner):
            raise RuntimeError("Direct programmatic modification of combo box is not allowed; perform changes within the controller's internal update context")
        super().insertItem(*args, **kwargs)

    def removeItem(self, *args, **kwargs) -> None:  # type: ignore[override]
        if not _is_internal_update(self._owner):
            raise RuntimeError("Direct programmatic modification of combo box is not allowed; perform changes within the controller's internal update context")
        super().removeItem(*args, **kwargs)


