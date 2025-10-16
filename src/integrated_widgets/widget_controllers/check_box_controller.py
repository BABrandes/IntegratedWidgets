from __future__ import annotations

# Standard library imports
from typing import Optional
from logging import Logger
from PySide6.QtWidgets import QWidget, QFrame, QVBoxLayout, QGroupBox

# BAB imports
from observables import ObservableSingleValueLike, HookLike
from observables.core import OwnedHook

# Local imports
from ..util.base_single_hook_controller import BaseSingleHookController
from ..controlled_widgets.controlled_check_box import ControlledCheckBox
from ..util.resources import log_msg

class CheckBoxController(BaseSingleHookController[bool, "CheckBoxController"]):
    """
    A controller for a checkbox widget with boolean value binding.
    
    This controller provides a simple checkbox interface for boolean values. It can
    synchronize with observable values and hooks, making it suitable for reactive
    applications where the checkbox state needs to be shared across components.
    
    The controller maintains a single boolean value that can be toggled by user
    interaction or programmatic changes. It also provides a hook to monitor when
    the checkbox widget is enabled or disabled.
    
    Parameters
    ----------
    value_or_hook_or_observable : bool | HookLike[bool] | ObservableSingleValueLike[bool]
        The initial checkbox state or an observable/hook to sync with. Can be:
        - A direct boolean value (True or False)
        - A HookLike object for bidirectional synchronization
        - An ObservableSingleValueLike for synchronization with reactive data
    text : str, optional
        The label text to display next to the checkbox. Defaults to "" (no label).
    parent_of_widgets : Optional[QWidget], optional
        The parent widget for the created UI widgets. Defaults to None.
    logger : Optional[Logger], optional
        Logger instance for debugging. Defaults to None.
    
    Attributes
    ----------
    value : bool
        Property to get/set the current checkbox state (inherited from base class).
    widget_check_box : ControlledCheckBox
        The checkbox widget managed by this controller.
    widget_enabled_hook : OwnedHook[bool]
        Hook that emits True/False when the checkbox widget is enabled/disabled.
    
    Examples
    --------
    Basic usage with a static value:
    
    >>> controller = CheckBoxController(True, text="Enable feature")
    >>> print(controller.value)
    True
    >>> controller.value = False  # Programmatically uncheck
    
    With observables for reactive programming:
    
    >>> from observables import ObservableSingleValue
    >>> observable = ObservableSingleValue(False)
    >>> controller = CheckBoxController(observable, text="Auto-save")
    >>> # Changes to controller.value automatically sync with observable
    
    Accessing the widget:
    
    >>> checkbox = controller.widget_check_box
    >>> layout.addWidget(checkbox)
    
    Monitoring enabled state:
    
    >>> def on_enabled_changed(enabled: bool):
    ...     print(f"Checkbox {'enabled' if enabled else 'disabled'}")
    >>> controller.widget_enabled_hook.add_callback(on_enabled_changed)
    
    Notes
    -----
    - The checkbox state changes immediately when the user clicks it
    - The widget can be programmatically enabled/disabled using standard Qt methods
    - The enabled state is tracked via widget_enabled_hook for reactive applications
    """

    def __init__(
        self,
        value_or_hook_or_observable: bool | HookLike[bool] | ObservableSingleValueLike[bool],
        *,
        text: str = "",
        logger: Optional[Logger] = None,
    ) -> None:
        
        # Store text for the checkbox before calling super().__init__()
        self._text = text
 
        BaseSingleHookController.__init__(
            self,
            value_or_hook_or_observable=value_or_hook_or_observable,
            verification_method=None,
            logger=logger
        )

        self._widget_enabled_hook = OwnedHook[bool](
            self, 
            self._check_box.isEnabled(),
            logger=logger
        )
        self._check_box.enabledChanged.connect(self._widget_enabled_hook.submit_value)

    ###########################################################################
    # Widget methods
    ###########################################################################

    def _initialize_widgets(self) -> None:
        """
        Initialize the checkbox widget.
        
        This method is called internally during initialization. It creates the checkbox
        widget and connects its state change signal to the controller's internal handler.
        It also sets up a hook to monitor the widget's enabled/disabled state.
        
        Notes
        -----
        This method should not be called directly by users of the controller.
        """
        self._check_box = ControlledCheckBox(self, self._text, logger=self._logger)
        self._check_box.stateChanged.connect(lambda state: self._on_checkbox_state_changed(state))

    def _on_checkbox_state_changed(self, state: int) -> None:
        """
        Handle when the user changes the checkbox state.
        
        This internal callback is triggered whenever the checkbox is clicked or its
        state changes programmatically. It converts the Qt state integer to a boolean
        and submits the new value through the controller's validation system.
        
        Parameters
        ----------
        state : int
            The Qt checkbox state (0 for unchecked, 2 for checked).
        
        Notes
        -----
        This method should not be called directly by users of the controller.
        """
        if self.is_blocking_signals:
            return
        log_msg(self, "on_checkbox_state_changed", self._logger, f"New value: {bool(state)}")
        self._submit_values_debounced(bool(state))

    def _invalidate_widgets_impl(self) -> None:
        """
        Update the checkbox from component values.
        
        This internal method synchronizes the UI widget with the current state of
        the controller's value. It sets the checkbox's checked state to match the
        current boolean value.
        
        The method is called automatically whenever the controller's state changes,
        whether from user interaction, programmatic changes, or synchronized observables.
        
        Notes
        -----
        This method should not be called directly. Use `invalidate_widgets()` instead
        if you need to manually trigger a widget update.
        """

        self._check_box.setChecked(self.value)

    ###########################################################################
    # Public API
    ###########################################################################

    @property
    def widget_check_box(self) -> ControlledCheckBox:
        """
        Get the checkbox widget.
        
        This is the primary widget for user interaction. It displays the checkbox
        with the configured label text and can be added to any Qt layout.
        
        Returns
        -------
        ControlledCheckBox
            The checkbox widget managed by this controller.
        
        Examples
        --------
        >>> checkbox = controller.widget_check_box
        >>> layout.addWidget(checkbox)
        """
        return self._check_box

    @property
    def widget_enabled_hook(self) -> OwnedHook[bool]:
        """
        Get the widget enabled hook.
        
        This hook emits True when the checkbox widget is enabled and False when
        it's disabled. This is useful for reactive applications that need to respond
        to changes in widget enabled state.
        
        Returns
        -------
        OwnedHook[bool]
            Hook that tracks the checkbox widget's enabled state.
        
        Examples
        --------
        >>> def on_enabled_changed(is_enabled: bool):
        ...     print(f"Checkbox is now {'enabled' if is_enabled else 'disabled'}")
        >>> controller.widget_enabled_hook.add_callback(on_enabled_changed)
        >>> controller.widget_check_box.setEnabled(False)  # Triggers callback
        """
        return self._widget_enabled_hook

    ###########################################################################
    # Debugging
    ###########################################################################

    def all_widgets_as_frame(self) -> QFrame:
        """
        Return all widgets organized in a QFrame for easy layout.
        
        This is a convenience method for adding the controller's widgets to a UI.
        It creates a vertical layout containing the checkbox widget inside a group box.
        
        Returns
        -------
        QFrame
            A frame containing the controller's widgets in a vertical layout.
        
        Examples
        --------
        >>> frame = controller.all_widgets_as_frame()
        >>> main_layout.addWidget(frame)
        """
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