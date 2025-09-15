from __future__ import annotations

# Standard library imports
from typing import Any, Optional, Generic, TypeVar, Literal
from logging import Logger
from PySide6.QtWidgets import QWidget, QFrame, QVBoxLayout, QGroupBox

# BAB imports
from observables import HookLike, ObservableSingleValueLike, InitialSyncMode

# Local imports
from ..util.base_single_hook_controller import BaseSingleHookController
from ..guarded_widgets.guarded_label import GuardedLabel
from ..util.resources import log_msg

T = TypeVar("T")

class DisplayValueController(BaseSingleHookController[T], Generic[T]):
    """Controller for displaying a value with a read-only label."""

    def __init__(self, value_or_hook_or_observable: T | HookLike[T] | ObservableSingleValueLike[T], parent: Optional[QWidget] = None, logger: Optional[Logger] = None) -> None:
        
        BaseSingleHookController.__init__(
            self,
            value_or_hook_or_observable=value_or_hook_or_observable,
            verification_method=None,
            parent=parent,
            logger=logger
        )

    ###########################################################################
    # Widget methods
    ###########################################################################

    def _initialize_widgets(self) -> None:
        """Initialize the display label widget."""
        self._label = GuardedLabel(self)

    def _invalidate_widgets_impl(self) -> None:
        """Update the label from component values."""

        log_msg(self, "_invalidate_widgets_impl", self._logger, f"Updating label with value: {self.value}")

        self._label.setText(str(self.value))

    ###########################################################################
    # Public API
    ###########################################################################

    @property
    def widget_label(self) -> GuardedLabel:
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