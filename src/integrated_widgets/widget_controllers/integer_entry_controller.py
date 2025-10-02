from __future__ import annotations

from typing import Callable, Optional
from logging import Logger
from PySide6.QtWidgets import QWidget, QFrame, QVBoxLayout, QGroupBox

from ..util.base_single_hook_controller import BaseSingleHookController
from ..guarded_widgets.guarded_line_edit import GuardedLineEdit
from ..util.resources import log_bool, log_msg

from observables import ObservableSingleValueLike, HookLike, OwnedHook


class IntegerEntryController(BaseSingleHookController[int, "IntegerEntryController"]):
    """Controller for an integer entry widget with validation support."""

    def __init__(
        self,
        value_or_hook_or_observable: int | HookLike[int] | ObservableSingleValueLike[int],
        *,
        validator: Optional[Callable[[int], bool]] = None,
        parent: Optional[QWidget] = None,
        logger: Optional[Logger] = None,
    ) -> None:
        
        self._validator = validator
        
        def verification_method(x: int) -> tuple[bool, str]:
            # Verify the value is an integer
            if not isinstance(x, int):
                return False, f"Value must be an integer, got {type(x)}"
            if self._validator is not None and not self._validator(x):
                return False, f"Value {x} failed validation"
            return True, "Verification method passed"

        BaseSingleHookController.__init__(
            self,
            value_or_hook_or_observable=value_or_hook_or_observable,
            verification_method=verification_method,
            parent=parent,
            logger=logger
        )

        self._widget_enabled_hook = OwnedHook[bool](
            self, self._line_edit.isEnabled(),
            logger=logger
        )
        self._line_edit.enabledChanged.connect(self._widget_enabled_hook.submit_value)

    ###########################################################################
    # Widget methods
    ###########################################################################

    def _initialize_widgets(self) -> None:
        """Initialize the line edit widget."""
        self._line_edit = GuardedLineEdit(self, logger=self._logger)
        
        # Connect UI -> model
        self._line_edit.editingFinished.connect(self._on_line_edit_editing_finished)

    def _on_line_edit_editing_finished(self) -> None:
        """
        Handle when the user finishes editing the line edit.
        """
        if self.is_blocking_signals:
            return
        
        # Get the new value from the line edit
        text: str = self._line_edit.text().strip()
        log_msg(self, "on_line_edit_editing_finished", self._logger, f"New value: {text}")
        
        try:
            new_value: int = int(text)
        except ValueError:
            # Invalid input, revert to current value
            self.invalidate_widgets()
            return
        
        if self._validator is not None and not self._validator(new_value):
            log_bool(self, "on_line_edit_editing_finished", self._logger, False, "Invalid input, reverting to current value")
            self.invalidate_widgets()
            return
        
        # Update component values
        self._submit_values_on_widget_changed(new_value)

    def _invalidate_widgets_impl(self) -> None:
        """Update the line edit from component values."""

        self._line_edit.setText(str(self.value))

    ###########################################################################
    # Public API
    ###########################################################################

    @property
    def widget_line_edit(self) -> GuardedLineEdit:
        """Get the line edit widget."""
        return self._line_edit

    @property
    def widget_enabled_hook(self) -> OwnedHook[bool]:
        """Get the widget enabled hook."""
        return self._widget_enabled_hook

    ###########################################################################
    # Debugging
    ###########################################################################

    def all_widgets_as_frame(self) -> QFrame:
        """Return all widgets as a QFrame."""
        frame = QFrame()
        layout = QVBoxLayout()
        frame.setLayout(layout)
        
        # Line Edit
        line_edit_group = QGroupBox("Integer Entry")
        line_edit_layout = QVBoxLayout()
        line_edit_layout.addWidget(self.widget_line_edit)
        line_edit_group.setLayout(line_edit_layout)
        layout.addWidget(line_edit_group)

        return frame