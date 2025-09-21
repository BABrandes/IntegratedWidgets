from __future__ import annotations

# Standard library imports
from typing import Optional
from logging import Logger
from PySide6.QtWidgets import QWidget, QFrame, QVBoxLayout, QGroupBox

# BAB imports
from observables import HookLike, ObservableSingleValueLike, OwnedHook

# Local imports
from ..util.base_single_hook_controller import BaseSingleHookController
from ..guarded_widgets.guarded_check_box import GuardedCheckBox
from ..util.resources import log_msg

class CheckBoxController(BaseSingleHookController[bool]):
    """Controller for a checkbox widget with boolean value binding."""

    def __init__(self, value_or_hook_or_observable: bool | HookLike[bool] | ObservableSingleValueLike[bool], *, text: str = "", parent: Optional[QWidget] = None, logger: Optional[Logger] = None) -> None:
        
        # Store text for the checkbox before calling super().__init__()
        self._text = text
 
        BaseSingleHookController.__init__(
            self,
            value_or_hook_or_observable=value_or_hook_or_observable,
            verification_method=None,
            parent=parent,
            logger=logger
        )

        def submit_widget_enabled() -> tuple[bool, str]:
            value: bool = self._check_box.isEnabled()
            self._check_box.setEnabled(value)
            return True, "Widget enabled"
        self._widget_enabled_hook = OwnedHook[bool](
            self, self._check_box.isEnabled(),
            lambda _: submit_widget_enabled(),
            logger=logger
        )
        self._check_box.enabledChanged.connect(self._widget_enabled_hook.submit_single_value)

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
        self._submit_values_on_widget_changed(bool(state))

    def _invalidate_widgets_impl(self) -> None:
        """Update the checkbox from component values."""

        self._check_box.setChecked(self.value)

    ###########################################################################
    # Public API
    ###########################################################################

    @property
    def widget_check_box(self) -> GuardedCheckBox:
        """Get the checkbox widget."""
        return self._check_box

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
        
        # Checkbox
        checkbox_group = QGroupBox("Checkbox")
        checkbox_layout = QVBoxLayout()
        checkbox_layout.addWidget(self.widget_check_box)
        checkbox_group.setLayout(checkbox_layout)
        layout.addWidget(checkbox_group)

        return frame