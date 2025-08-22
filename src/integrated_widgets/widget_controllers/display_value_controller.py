from __future__ import annotations

from typing import Any, Optional, Generic, TypeVar, Literal
from logging import Logger
from PySide6.QtWidgets import QWidget, QFrame, QVBoxLayout, QGroupBox

from integrated_widgets.widget_controllers.base_controller import BaseObservableController
from integrated_widgets.guarded_widgets.guarded_label import GuardedLabel
from observables import HookLike, ObservableSingleValueLike, InitialSyncMode, ObservableSingleValue

T = TypeVar("T")

class DisplayValueController(BaseObservableController, ObservableSingleValueLike[T], Generic[T]):
    """Controller for displaying a value with a read-only label."""

    def __init__(self, value: T | HookLike[T] | ObservableSingleValueLike[T], parent: Optional[QWidget] = None, logger: Optional[Logger] = None) -> None:
        
        # Handle different types of value input
        if isinstance(value, HookLike):
            # It's a hook - get initial value
            initial_value: Any = value.value
            value_hook: Optional[HookLike[T]] = value

        elif isinstance(value, ObservableSingleValueLike):
            # It's an ObservableSingleValue - get initial value
            initial_value: Any = value.single_value
            value_hook: Optional[HookLike[T]] = value.single_value_hook

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

    def initialize_widgets(self) -> None:
        """Initialize the display label widget."""
        self._label = GuardedLabel(self)

    def _fill_widgets_from_component_values(self, component_values: dict[Literal["value"], Any]) -> None:
        """Update the label from component values."""

        if not self.is_blocking_signals:
            raise RuntimeError("This method should be called while the signals are blocked.")
        
        with self._internal_update():
            self._label.setText(str(component_values["value"]))

    ###########################################################################
    # Public API
    ###########################################################################

    @property
    def single_value_hook(self) -> HookLike[T]:
        """Get the hook for the single value."""
        return self.get_hook("value")

    @property
    def widget_label(self) -> GuardedLabel:
        """Get the display label widget."""
        return self._label

    @property
    def single_value(self) -> T:
        """Get the current display value."""
        return self.get_value("value")
    
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