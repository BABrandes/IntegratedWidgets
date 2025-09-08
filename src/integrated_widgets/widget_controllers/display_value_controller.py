from __future__ import annotations

# Standard library imports
from typing import Any, Optional, Generic, TypeVar, Literal
from logging import Logger
from PySide6.QtWidgets import QWidget, QFrame, QVBoxLayout, QGroupBox

# BAB imports
from observables import HookLike, ObservableSingleValueLike, InitialSyncMode

# Local imports
from ..widget_controllers.base_widget_controller_with_disable import BaseWidgetControllerWithDisable
from ..guarded_widgets.guarded_label import GuardedLabel
from ..util.resources import log_msg

T = TypeVar("T")

class DisplayValueController(BaseWidgetControllerWithDisable[Literal["value"], Any], ObservableSingleValueLike[T], Generic[T]):
    """Controller for displaying a value with a read-only label."""

    def __init__(self, value: T | HookLike[T] | ObservableSingleValueLike[T], parent: Optional[QWidget] = None, logger: Optional[Logger] = None) -> None:
        
        # Handle different types of value input
        if isinstance(value, HookLike):
            # It's a hook - get initial value
            initial_value: T = value.value
            value_hook: Optional[HookLike[T]] = value

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
        """Initialize the display label widget."""
        self._label = GuardedLabel(self)

    def _disable_widgets(self) -> None:
        """
        Disable all widgets.
        """
        self._label.setText("")
        self._label.setEnabled(False)

    def _enable_widgets(self, initial_component_values: dict[Literal["value"], Any]) -> None:
        """
        Enable all widgets.
        """
        self._label.setEnabled(True)

    def _invalidate_widgets_impl(self) -> None:
        """Update the label from component values."""

        component_values: dict[Literal["value"], Any] = self.component_values_dict

        log_msg(self, "_invalidate_widgets_impl", self._logger, f"Updating label with value: {component_values['value']}")

        self._label.setText(str(component_values["value"]))

    ###########################################################################
    # Public API
    ###########################################################################

    @property
    def value_hook(self) -> HookLike[T]:
        """Get the hook for the value."""
        return self.get_component_hook("value")

    @property
    def widget_label(self) -> GuardedLabel:
        """Get the display label widget."""
        return self._label

    @property
    def value(self) -> T:
        """Get the current display value."""
        return self.get_value("value")
    
    @value.setter
    def value(self, value: T) -> None:
        """Set the current display value."""
        self._set_incomplete_primary_component_values({"value": value})

    def change_value(self, new_value: T) -> None:
        """Change the current display value."""
        self._set_incomplete_primary_component_values({"value": new_value})

    ###########################################################################
    # Debugging
    ###########################################################################

    def all_widgets_as_frame(self) -> QFrame:
        """Return all widgets as a QFrame."""
        frame = QFrame()
        layout = QVBoxLayout()
        frame.setLayout(layout)
        
        # Value Label
        value_group = QGroupBox("Value")
        value_layout = QVBoxLayout()
        value_layout.addWidget(self.widget_label)
        value_group.setLayout(value_layout)
        layout.addWidget(value_group)

        return frame