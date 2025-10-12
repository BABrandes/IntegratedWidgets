from __future__ import annotations

# Standard library imports
from typing import Any, Optional, Generic, TypeVar, Literal, Callable
from logging import Logger
from PySide6.QtWidgets import QWidget, QFrame, QVBoxLayout, QGroupBox

# BAB imports
from observables import HookLike, ObservableSingleValueLike, InitialSyncMode

# Local imports
from ..util.base_single_hook_controller import BaseSingleHookController
from ..controlled_widgets.controlled_label import ControlledLabel
from ..util.resources import log_msg

T = TypeVar("T")

class DisplayValueController(BaseSingleHookController[T, "DisplayValueController"], Generic[T]):
    """Controller for displaying a value with a read-only label."""

    def __init__(
        self,
        value_or_hook_or_observable: T | HookLike[T] | ObservableSingleValueLike[T],
        formatter: Optional[Callable[[T], str]] = None,
        parent_of_widgets: Optional[QWidget] = None,
        logger: Optional[Logger] = None) -> None:

        self._formatter = formatter
        
        BaseSingleHookController.__init__(
            self,
            value_or_hook_or_observable=value_or_hook_or_observable,
            parent_of_widgets=parent_of_widgets,
            logger=logger
        )

    ###########################################################################
    # Widget methods
    ###########################################################################

    def _initialize_widgets(self) -> None:
        """Initialize the display label widget."""
        self._label = ControlledLabel(self, parent_of_widget=self.parent_of_widgets)

    def _invalidate_widgets_impl(self) -> None:
        """Update the label from component values."""

        log_msg(self, "_invalidate_widgets_impl", self._logger, f"Updating label with value: {self.value}")

        if self._formatter is None:
            text = str(self.value)
        else:
            text = self._formatter(self.value)

        self._label.setText(text)

    ###########################################################################
    # Public API
    ###########################################################################

    @property
    def value(self) -> T:
        """Get the current value."""
        return self.get_value_of_hook("value") # type: ignore

    @value.setter
    def value(self, value: T) -> None:
        """Set the current value."""
        self.submit_values({"value": value})

    def change_value(self, value: T) -> None:
        """Set the current value."""
        self.submit_values({"value": value})

    @property
    def formatter(self) -> Optional[Callable[[T], str]]:
        """Get the formatter function."""
        return self._formatter

    @formatter.setter
    def formatter(self, formatter: Callable[[T], str]) -> None:
        """Set the formatter function."""
        self._formatter = formatter
        self.invalidate_widgets()

    def change_formatter(self, formatter: Callable[[T], str]) -> None:
        """Set the formatter function."""
        self._formatter = formatter
        self.invalidate_widgets()

    ###########################################################################
    # Public API
    ###########################################################################

    @property
    def widget_label(self) -> ControlledLabel:
        """Get the display label widget."""
        return self._label

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