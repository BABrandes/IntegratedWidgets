from __future__ import annotations

# Standard library imports
from typing import Any, Optional, Literal
from logging import Logger
from PySide6.QtWidgets import QWidget, QFrame, QVBoxLayout, QGroupBox

# BAB imports
from observables import HookLike, ObservableSingleValueLike, InitialSyncMode, ObservableSingleValue

# Local imports
from ..widget_controllers.base_controller import BaseObservableController
from ..guarded_widgets.guarded_check_box import GuardedCheckBox
from ..util.resources import log_msg

class CheckBoxController(BaseObservableController[Literal["value"], Any], ObservableSingleValueLike[bool]):
    """Controller for a checkbox widget with boolean value binding."""

    def __init__(
            self,
            value: bool | HookLike[bool] | ObservableSingleValueLike[bool],
            *,
            text: str = "",
            parent: Optional[QWidget] = None,
            logger: Optional[Logger] = None,
    ) -> None:
        
        # Store text for the checkbox before calling super().__init__()
        self._text = text
        
        # Handle different types of value input
        if isinstance(value, HookLike):
            # It's a hook - get initial value
            initial_value: bool = value.value
            value_hook: Optional[HookLike[bool]] = value

        elif isinstance(value, ObservableSingleValueLike):
            # It's an ObservableSingleValue - get initial value
            initial_value: bool = value.single_value
            value_hook: Optional[HookLike[bool]] = value.single_value_hook

        else:
            # It's a direct value
            initial_value = value
            value_hook = None
        
        super().__init__(
            {"value": initial_value},
            parent=parent,
            logger=logger
        )

        if value_hook is not None:
            self.attach(value_hook, to_key="value", initial_sync_mode=InitialSyncMode.PULL_FROM_TARGET)

    ###########################################################################
    # Widget methods
    ###########################################################################

    def _initialize_widgets(self) -> None:
        """Initialize the checkbox widget."""
        self._check_box = GuardedCheckBox(self, self._text)
        self._check_box.stateChanged.connect(lambda state: self._on_checkbox_state_changed(state))

    def _disable_widgets(self) -> None:
        """
        Disable all widgets.
        """
        self._check_box.setChecked(False)
        self._check_box.setEnabled(False)

    def _enable_widgets(self, initial_component_values: dict[Literal["value"], Any]) -> None:
        """
        Enable all widgets.
        """
        self._check_box.setEnabled(True)

    def _on_checkbox_state_changed(self, state: int) -> None:
        """
        Handle when the user changes the checkbox state.
        """
        if self.is_blocking_signals:
            return
        log_msg(self, "on_checkbox_state_changed", self._logger, f"New value: {bool(state)}")
        self._set_component_values({"value": bool(state)}, notify_binding_system=True)

    def _fill_widgets_from_component_values(self, component_values: dict[Literal["value"], Any]) -> None:
        """Update the checkbox from component values."""

        self._check_box.setChecked(component_values["value"])

    ###########################################################################
    # Public API
    ###########################################################################

    @property
    def single_value_hook(self) -> HookLike[bool]:
        """Get the hook for the single value."""
        return self.get_hook("value")

    @property
    def widget_check_box(self) -> GuardedCheckBox:
        """Get the checkbox widget."""
        return self._check_box

    @property
    def single_value(self) -> bool:
        """Get the current checkbox value."""
        return self.get_value("value")
    
    @single_value.setter
    def single_value(self, value: bool) -> None:
        """Set the current checkbox value."""
        self._set_component_values({"value": value}, notify_binding_system=True)
        self.apply_component_values_to_widgets()

    def change_single_value(self, value: bool) -> None:
        """Change the current checkbox value."""
        self._set_component_values({"value": value}, notify_binding_system=True)
        self.apply_component_values_to_widgets()

    # Alias for backward compatibility with tests
    @property
    def distinct_single_value_reference(self) -> bool:
        """Get the current checkbox value (alias for single_value)."""
        return self.single_value
    
    @distinct_single_value_reference.setter
    def distinct_single_value_reference(self, value: bool) -> None:
        """Set the current checkbox value (alias for single_value)."""
        self.single_value = value

    @property
    def distinct_single_value_hook(self) -> HookLike[bool]:
        """Get the hook for the single value (alias for single_value_hook)."""
        return self.single_value_hook

    ###########################################################################
    # Debugging
    ###########################################################################

    def all_widgets_as_frame(self) -> QFrame:
        """Return all widgets as a QFrame."""
        frame = QFrame()
        layout = QVBoxLayout()
        frame.setLayout(layout)
        
        # Checkbox
        checkbox_group = QGroupBox("Checkbox")
        checkbox_layout = QVBoxLayout()
        checkbox_layout.addWidget(self.widget_check_box)
        checkbox_group.setLayout(checkbox_layout)
        layout.addWidget(checkbox_group)

        return frame