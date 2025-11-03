from __future__ import annotations

# Standard library imports
from typing import Optional, Callable
from logging import Logger

# BAB imports
from nexpy import Hook, XSingleValueProtocol
from nexpy.core import NexusManager
from nexpy import default as nexpy_default

# Local imports
from ..core.base_singleton_controller import BaseSingletonController
from ...controlled_widgets.controlled_check_box import ControlledCheckBox

class CheckBoxController(BaseSingletonController[bool]):
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
    value : bool | Hook[bool] | XSingleValueProtocol[bool, Hook[bool]]
        The initial checkbox state or an observable/hook to sync with. Can be:
        - A direct boolean value (True or False)
        - A Hook object for bidirectional synchronization
        - An XSingleValueProtocol for synchronization with reactive data
    text : str, optional
        The label text to display next to the checkbox. Defaults to "" (no label).
    debounce_ms : int|Callable[[], int], optional
        The debounce time in milliseconds for the checkbox state changes. Defaults to None (no debounce).
    logger : Optional[Logger], optional
        Logger instance for debugging. Defaults to None.
    nexus_manager : NexusManager, optional
        The nexus manager to use for the controller. Defaults to the default nexus manager.
    
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
    
    >>> from nexpy import XValue
    >>> observable = XValue(False)
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
        value: bool | Hook[bool] | XSingleValueProtocol[bool],
        *,
        text: str = "",
        debounce_ms: int|Callable[[], int],
        logger: Optional[Logger] = None,
        nexus_manager: NexusManager = nexpy_default.NEXUS_MANAGER,
    ) -> None:
        
        # Store text for the checkbox before calling super().__init__()
        self._text = text
 
        BaseSingletonController.__init__( # type: ignore
            self,
            value=value,
            verification_method=None,
            debounce_ms=debounce_ms,
            logger=logger,
            nexus_manager=nexus_manager
        )

    ###########################################################################
    # Widget methods
    ###########################################################################

    def _initialize_widgets_impl(self) -> None:
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
        self._check_box.userInputFinishedSignal.connect(self.evaluate)

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

    def _read_widget_single_value_impl(self) -> tuple[bool, bool]:
        """
        Read the value from the checkbox widget.
        
        This method reads the current checked state from the checkbox widget
        and returns it as a boolean.

        Returns:
            A tuple containing a boolean indicating if the value is valid and the value.
            If the value is invalid, the boolean will be False and the value will be the last valid value.
        """
        return True, self._check_box.isChecked()

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