from __future__ import annotations

# Standard library imports
from typing import Any, Optional, Literal
from logging import Logger
from PySide6.QtWidgets import QWidget, QFrame, QVBoxLayout, QGroupBox

# BAB imports
from observables import HookLike, ObservableSingleValueLike, InitialSyncMode

# Local imports
from ..widget_controllers.base_widget_controller import BaseWidgetController
from ..guarded_widgets.guarded_check_box import GuardedCheckBox
from ..util.resources import log_msg

class CheckBoxController(BaseWidgetController[Literal["value"], Any, bool, Any], ObservableSingleValueLike[bool]):
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
            initial_value = value.value
            value_hook = value.value_hook

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
            self.connect(value_hook, to_key="value", initial_sync_mode=InitialSyncMode.USE_TARGET_VALUE)

    ###########################################################################
    # Widget methods
    ###########################################################################

    def _initialize_widgets(self) -> None:
        """Initialize the checkbox widget."""
        self._check_box = GuardedCheckBox(self, self._text)
        self._check_box.stateChanged.connect(lambda state: self._on_checkbox_state_changed(state))

    def _on_checkbox_state_changed(self, state: int) -> None:
        """
        Handle when the user changes the checkbox state.
        """
        if self.is_blocking_signals:
            return
        log_msg(self, "on_checkbox_state_changed", self._logger, f"New value: {bool(state)}")
        self._submit_values_on_widget_changed({"value": bool(state)})

    def _invalidate_widgets_impl(self) -> None:
        """Update the checkbox from component values."""

        self._check_box.setChecked(self.get_hook_value("value"))

    ###########################################################################
    # Public API
    ###########################################################################

    @property
    def value_hook(self) -> HookLike[bool]:
        """Get the hook for the single value."""
        return self.get_hook("value")

    @property
    def widget_check_box(self) -> GuardedCheckBox:
        """Get the checkbox widget."""
        return self._check_box

    @property
    def value(self) -> bool:
        """Get the current checkbox value."""
        return self.get_hook_value("value")
    
    @value.setter
    def value(self, value: bool) -> None:
        """Set the current checkbox value."""
        self.submit_single_value("value", value)

    def change_value(self, new_value: bool) -> None:
        """Change the current checkbox value."""
        self.submit_single_value("value", new_value)

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