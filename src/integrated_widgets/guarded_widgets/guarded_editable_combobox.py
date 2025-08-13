from __future__ import annotations

"""Guarded editable combo box.

This widget extends the guarded semantics to an editable QComboBox. Item list
mutations (clear/add/insert/remove) are only allowed during an internal update
cycle that is controlled by the owner object by setting the attribute
``_internal_widget_update = True``. End-users can freely type into the embedded
line edit. Programmatic text changes should also go through an internal update.
"""

from typing import Optional

from PySide6.QtWidgets import QComboBox, QWidget


def _is_internal_update(owner: object) -> bool:
    return bool(getattr(owner, "_internal_widget_update", False))


class GuardedEditableComboBox(QComboBox):
    """Editable combo box that guards programmatic mutations.

    - setEditable(True)
    - Guards item list changes like GuardedComboBox
    - Allows user typing; programmatic text changes should be wrapped in an
      internal update by the owner
    """

    def __init__(self, owner: Optional[QWidget] = None) -> None:
        super().__init__(owner)
        self._owner = owner
        self.setEditable(True)

    # Guard mutations of the item model
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

    def setEditText(self, text: str) -> None:  # type: ignore[override]
        # Permit programmatic edit text changes only inside internal update
        # End-user edits go via the embedded QLineEdit directly
        if not _is_internal_update(self._owner):
            raise RuntimeError("Programmatic setEditText requires the controller's internal update context")
        super().setEditText(text)


