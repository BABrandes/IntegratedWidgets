from __future__ import annotations

from typing import Callable, Optional, overload, Any, Mapping, Literal
from logging import Logger
from PySide6.QtWidgets import QWidget, QFrame, QVBoxLayout, QGroupBox

from ..widget_controllers.base_controller import BaseWidgetController
from ..guarded_widgets.guarded_line_edit import GuardedLineEdit
from ..util.resources import log_bool, log_msg

from observables import ObservableSingleValueLike, HookLike, InitialSyncMode


class IntegerEntryController(BaseWidgetController[Literal["value"], Any], ObservableSingleValueLike[int]):
    """Controller for an integer entry widget with validation support."""

    @classmethod
    def _mandatory_component_value_keys(cls) -> set[str]:
        """Get the mandatory component value keys for this controller."""
        return {"value"}

    @overload
    def __init__(
        self,
        value: int,
        *,
        validator: Optional[Callable[[int], bool]] = None,
        parent: Optional[QWidget] = None,
        logger: Optional[Logger] = None,
    ) -> None: ...

    @overload
    def __init__(
        self,
        value: ObservableSingleValueLike[int] | HookLike[int],
        *,
        validator: Optional[Callable[[int], bool]] = None,
        parent: Optional[QWidget] = None,
        logger: Optional[Logger] = None,
    ) -> None: ...

    def __init__(
        self,
        value,
        *,
        validator: Optional[Callable[[int], bool]] = None,
        parent: Optional[QWidget] = None,
        logger: Optional[Logger] = None,
    ) -> None:
        
        self._validator = validator
        
        # Handle different types of value input
        if isinstance(value, HookLike):
            # It's a hook - get initial value
            initial_value: int = value.value
            value_hook: Optional[HookLike[int]] = value

        elif isinstance(value, ObservableSingleValueLike):
            # It's an ObservableSingleValue - get initial value
            initial_value: int = value.single_value
            value_hook: Optional[HookLike[int]] = value.single_value_hook

        else:
            # It's a direct value
            initial_value = int(value)
            value_hook = None
        
        def verification_method(x: Mapping[Literal["value"], Any]) -> tuple[bool, str]:
            # Verify the value is an integer
            current_value = x.get("value", initial_value)
            if not isinstance(current_value, int):
                return False, f"Value must be an integer, got {type(current_value)}"
            if self._validator is not None and not self._validator(current_value):
                return False, f"Value {current_value} failed validation"
            return True, "Verification method passed"

        super().__init__(
            {"value": initial_value},
            verification_method=verification_method,
            parent=parent,
            logger=logger
        )

        if value_hook is not None:
            self.attach(value_hook, to_key="value", initial_sync_mode=InitialSyncMode.PULL_FROM_TARGET)

    @property
    def can_be_disabled(self) -> bool:
        """Whether the controller can be disabled."""
        return True

    ###########################################################################
    # Widget methods
    ###########################################################################

    def _initialize_widgets(self) -> None:
        """Initialize the line edit widget."""
        self._line_edit = GuardedLineEdit(self, logger=self._logger)
        
        # Connect UI -> model
        self._line_edit.editingFinished.connect(self._on_line_edit_editing_finished)

    def _disable_widgets(self) -> None:
        """
        Disable all widgets.
        """
        self._line_edit.setText("")
        self._line_edit.setEnabled(False)

    def _enable_widgets(self, initial_component_values: dict[Literal["value"], Any]) -> None:
        """
        Enable all widgets.
        """
        self._line_edit.setEnabled(True)

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
            self.apply_component_values_to_widgets()
            return
        
        if self._validator is not None and not self._validator(new_value):
            log_bool(self, "on_line_edit_editing_finished", self._logger, False, "Invalid input, reverting to current value")
            self.apply_component_values_to_widgets()
            return
        
        # Update component values
        self._update_component_values_and_widgets({"value": new_value})

    def _fill_widgets_from_component_values(self, component_values: dict[Literal["value"], Any]) -> None:
        """Update the line edit from component values."""

        self._line_edit.setText(str(component_values["value"]))

    ###########################################################################
    # Public API
    ###########################################################################

    @property
    def single_value_hook(self) -> HookLike[int]:
        """Get the hook for the single value."""
        return self.get_hook("value")

    @property
    def widget_line_edit(self) -> GuardedLineEdit:
        """Get the line edit widget."""
        return self._line_edit

    @property
    def single_value(self) -> int:
        """Get the current integer value."""
        return self.get_value("value")
    
    @single_value.setter
    def single_value(self, value: int) -> None:
        """Set the current integer value."""
        self._update_component_values_and_widgets({"value": value})

    def change_single_value(self, value: int) -> None:
        """Change the current integer value."""
        self._update_component_values_and_widgets({"value": value})

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