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

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox, QWidget

from integrated_widgets.util.base_controller import BaseController
from integrated_widgets.util.resources import log_msg
from .base_controlled_widget import BaseControlledWidget

def _is_internal_update(controller: BaseController[Any, Any, Any]) -> bool:
    return bool(getattr(controller, "_internal_widget_update", False))

class ControlledEditableComboBox(BaseControlledWidget, QComboBox):
    """Editable combo box that guards programmatic mutations and filters spurious signals.

    This widget provides a QComboBox with an editable line edit that:
    - Guards programmatic mutations (clear/add/insert/remove) to prevent accidental changes
    - Allows user typing and editing in the embedded line edit
    - Emits a custom userEditingFinished signal only for genuine user edits
    - Filters out spurious signals during programmatic updates and widget invalidation
    
    Signal Emission Behavior:
    - The userEditingFinished signal is emitted when:
      * User finishes editing (loses focus or presses Enter)
      * Signals are not blocked (is_blocking_signals == False)
      * Not during internal widget updates (_internal_widget_update == False)
      * User actually typed something (buffered text is not empty)
    
    - The signal is NOT emitted when:
      * During programmatic widget updates (widget invalidation)
      * During controller initialization
      * When signals are explicitly blocked by the controller
      * When user hasn't typed anything (empty buffer)
    
    This prevents spurious submissions of stale or empty text during widget synchronization.
    
    Attributes
    ----------
    userEditingFinished : Signal(str)
        Custom signal emitted when the user finishes editing.
        Carries the text that the user typed (never empty).
    """

    # Emitted when the user finishes editing in the embedded line edit.
    # Only emitted for genuine user edits, not during programmatic updates.
    # The signal carries the actual text the user typed (never empty or stale).
    editingFinished: Signal = Signal(str)

    def __init__(self, controller: BaseController[Any, Any, Any], parent_of_widget: Optional[QWidget] = None, logger: Optional[Logger] = None) -> None:
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
        super().addItem(*args, **kwargs) # type: ignore

    def insertItem(self, *args, **kwargs) -> None:  # type: ignore[override]
        if not _is_internal_update(self._controller):
            log_msg(self, "insertItem", self._logger, "Direct programmatic modification of combo box is not allowed; perform changes within the controller's internal update context")
            raise RuntimeError("Direct programmatic modification of combo box is not allowed; perform changes within the controller's internal update context")
        super().insertItem(*args, **kwargs) # type: ignore

    def removeItem(self, *args, **kwargs) -> None:  # type: ignore[override]
        if not _is_internal_update(self._controller):
            log_msg(self, "removeItem", self._logger, "Direct programmatic modification of combo box is not allowed; perform changes within the controller's internal update context")
            raise RuntimeError("Direct programmatic modification of combo box is not allowed; perform changes within the controller's internal update context")
        super().removeItem(*args, **kwargs) # type: ignore

    def setEditText(self, text: str) -> None:  # type: ignore[override]
        # Permit programmatic edit text changes only inside internal update
        # End-user edits go via the embedded QLineEdit directly
        if not _is_internal_update(self._controller):
            log_msg(self, "setEditText", self._logger, "Direct programmatic modification of combo box is not allowed; perform changes within the controller's internal update context")
            raise RuntimeError("Direct programmatic modification of combo box is not allowed; perform changes within the controller's internal update context")
        super().setEditText(text)

    def _buffer_user_input(self, text: str) -> None:
        """Buffer user input text as they type.
        
        This method is connected to textChanged and stores the user's input.
        It ignores programmatic text changes during internal widget updates,
        ensuring we only capture genuine user typing.
        
        Args:
            text: The current text in the line edit.
        """
        # Ignore programmatic updates during internal widget updates
        if _is_internal_update(self._controller):
            return
        log_msg(self, "_buffer_user_input", self._logger, f"text: {text}")
        self._last_user_text = text

    def _on_editor_editing_finished(self) -> None:
        """Handle when editing finishes (focus lost).
        
        This emits userEditingFinished only for genuine user edits, filtering out:
        - Signals during internal widget updates (programmatic changes)
        - Signals when the controller is blocking signals
        - Empty text (user didn't actually type anything)
        
        This prevents spurious Unit("") submissions during widget invalidation.
        """
        # Ignore if this is triggered during internal widget updates or when signals are blocked
        if _is_internal_update(self._controller) or self._controller.is_blocking_signals:
            return
        # Only emit if there's actual buffered user text (not empty)
        if self._last_user_text:
            log_msg(self, "_on_editor_editing_finished", self._logger, f"text: {self._last_user_text}")
            self.editingFinished.emit(self._last_user_text)
        self._last_user_text = ""

    def _on_editor_return_pressed(self) -> None:
        """Handle when user presses Return/Enter key.
        
        This emits userEditingFinished immediately, filtering out:
        - Signals during internal widget updates
        - Signals when the controller is blocking signals
        
        The buffer is kept until editingFinished fires (which clears it).
        """
        # Ignore if this is triggered during internal widget updates or when signals are blocked
        if _is_internal_update(self._controller) or self._controller.is_blocking_signals:
            return
        # Emit immediately on Return before any programmatic resets occur
        log_msg(self, "_on_editor_return_pressed", self._logger, f"text: {self._last_user_text}")
        self.editingFinished.emit(self._last_user_text)
        # Keep buffer until editingFinished fires, then it will clear