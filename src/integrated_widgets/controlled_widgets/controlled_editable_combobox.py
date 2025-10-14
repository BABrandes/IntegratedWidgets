from __future__ import annotations

"""Guarded editable combo box.

This widget extends the guarded semantics to an editable QComboBox. Item list
mutations (clear/add/insert/remove) are only allowed during an internal update
cycle that is controlled by the owner object by setting the attribute
``_internal_widget_update = True``. End-users can freely type into the embedded
line edit. Programmatic text changes should also go through an internal update.
"""

from typing import Optional, Any
from logging import Logger

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QComboBox, QWidget

from integrated_widgets.util.base_controller import BaseController
from integrated_widgets.util.resources import log_msg
from .base_controlled_widget import BaseControlledWidget

def _is_internal_update(controller: BaseController) -> bool:
    return bool(getattr(controller, "_internal_widget_update", False))

class ControlledEditableComboBox(BaseControlledWidget, QComboBox):
    """Editable combo box that guards programmatic mutations.

    - setEditable(True)
    - Guards item list changes like GuardedComboBox
    - Allows user typing; programmatic text changes should be wrapped in an
      internal update by the owner
    """

    # Emitted when the embedded line edit loses focus or the user presses Enter.
    # Carries the current text from the editor at the time of emission.
    userEditingFinished: Signal = Signal(str)

    def __init__(self, controller: BaseController, parent_of_widget: Optional[QWidget] = None, logger: Optional[Logger] = None) -> None:
        BaseControlledWidget.__init__(self, controller, logger)
        QComboBox.__init__(self, parent_of_widget)

        self.setEditable(True)
        self._last_user_text: str = ""
        # Connect the embedded editor's signals to a dedicated unguarded signal
        editor = self.lineEdit()
        if editor is not None:
            editor.textChanged.connect(self._buffer_user_input)
            editor.editingFinished.connect(self._on_editor_editing_finished)
            editor.returnPressed.connect(self._on_editor_return_pressed)

    # Guard mutations of the item model
    def clear(self) -> None:  # type: ignore[override]
        if not _is_internal_update(self._controller):
            log_msg(self, "clear", self._logger, "Direct programmatic modification of combo box is not allowed; perform changes within the controller's internal update context")
            raise RuntimeError("Direct programmatic modification of combo box is not allowed; perform changes within the controller's internal update context")
        super().clear()

    def addItem(self, *args, **kwargs) -> None:  # type: ignore[override]
        if not _is_internal_update(self._controller):
            log_msg(self, "addItem", self._logger, "Direct programmatic modification of combo box is not allowed; perform changes within the controller's internal update context")
            raise RuntimeError("Direct programmatic modification of combo box is not allowed; perform changes within the controller's internal update context")
        super().addItem(*args, **kwargs)

    def insertItem(self, *args, **kwargs) -> None:  # type: ignore[override]
        if not _is_internal_update(self._controller):
            log_msg(self, "insertItem", self._logger, "Direct programmatic modification of combo box is not allowed; perform changes within the controller's internal update context")
            raise RuntimeError("Direct programmatic modification of combo box is not allowed; perform changes within the controller's internal update context")
        super().insertItem(*args, **kwargs)

    def removeItem(self, *args, **kwargs) -> None:  # type: ignore[override]
        if not _is_internal_update(self._controller):
            log_msg(self, "removeItem", self._logger, "Direct programmatic modification of combo box is not allowed; perform changes within the controller's internal update context")
            raise RuntimeError("Direct programmatic modification of combo box is not allowed; perform changes within the controller's internal update context")
        super().removeItem(*args, **kwargs)

    def setEditText(self, text: str) -> None:  # type: ignore[override]
        # Permit programmatic edit text changes only inside internal update
        # End-user edits go via the embedded QLineEdit directly
        if not _is_internal_update(self._controller):
            log_msg(self, "setEditText", self._logger, "Direct programmatic modification of combo box is not allowed; perform changes within the controller's internal update context")
            raise RuntimeError("Direct programmatic modification of combo box is not allowed; perform changes within the controller's internal update context")
        super().setEditText(text)

    def _buffer_user_input(self, text: str) -> None:
        # Ignore programmatic updates during internal widget updates
        if _is_internal_update(self._controller):
            return
        log_msg(self, "_buffer_user_input", self._logger, f"text: {text}")
        self._last_user_text = text

    def _on_editor_editing_finished(self) -> None:
        log_msg(self, "_on_editor_editing_finished", self._logger, f"text: {self._last_user_text}")
        self.userEditingFinished.emit(self._last_user_text)
        self._last_user_text = ""

    def _on_editor_return_pressed(self) -> None:
        # Emit immediately on Return before any programmatic resets occur
        log_msg(self, "_on_editor_return_pressed", self._logger, f"text: {self._last_user_text}")
        self.userEditingFinished.emit(self._last_user_text)
        # Keep buffer until editingFinished fires, then it will clear