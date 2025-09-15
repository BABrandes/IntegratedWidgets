from __future__ import annotations

# Standard library imports
from typing import Any, Optional, Generic, TypeVar, Literal
from logging import Logger
from PySide6.QtWidgets import QWidget, QFrame, QVBoxLayout, QGroupBox

# BAB imports
from observables import HookLike, ObservableSingleValueLike, InitialSyncMode

# Local imports
from ..widget_controllers.base_widget_controller import BaseWidgetController
from ..guarded_widgets.guarded_label import GuardedLabel
from ..util.resources import log_msg

T = TypeVar("T")

class DisplayValueController(BaseWidgetController[Literal["value"], Any, T, Any], ObservableSingleValueLike[T], Generic[T]):
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

    def _invalidate_widgets_impl(self) -> None:
        """Update the label from component values."""

        component_values: dict[Literal["value"], Any] = self.hook_value_dict    

        log_msg(self, "_invalidate_widgets_impl", self._logger, f"Updating label with value: {component_values['value']}")

        self._label.setText(str(component_values["value"]))

    ###########################################################################
    # Public API
    ###########################################################################

    @property
    def value(self) -> T:
        """Get the current display value."""
        return self.get_hook_value("value")

    @property
    def value_hook(self) -> HookLike[T]:
        """Get the hook for the value."""
        return self.get_hook("value")

    @property
    def widget_label(self) -> GuardedLabel:
        """Get the display label widget."""
        return self._label
    
    @value.setter
    def value(self, value: T) -> None:
        """Set the current display value."""
        self.submit_single_value("value", value)

    def change_value(self, new_value: T) -> None:
        """Change the current display value."""
        self.submit_single_value("value", new_value)

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