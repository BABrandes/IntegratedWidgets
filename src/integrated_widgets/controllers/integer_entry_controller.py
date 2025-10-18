from __future__ import annotations

from typing import Callable, Optional
from logging import Logger

from ..util.base_single_hook_controller import BaseSingleHookController
from ..controlled_widgets.controlled_line_edit import ControlledLineEdit
from ..util.resources import log_msg

from observables import ObservableSingleValueProtocol, Hook


class IntegerEntryController(BaseSingleHookController[int, "IntegerEntryController"]):
    """
    A controller for an integer entry widget with validation support.
    
    This controller provides a text field for entering integer values. It validates
    user input, rejecting non-integer values and optionally applying custom validation
    rules. Invalid entries are automatically reverted to the last valid value.
    
    The controller can synchronize with observable values and hooks, making it suitable
    for reactive applications where integer inputs need to be shared across components.
    
    Parameters
    ----------
    value_or_hook_or_observable : int | Hook[int] | ObservableSingleValueProtocol[int]
        The initial integer value or an observable/hook to sync with. Can be:
        - A direct integer value
        - A Hook object for bidirectional synchronization
        - An ObservableSingleValueProtocol for synchronization with reactive data
    validator : Optional[Callable[[int], bool]], optional
        Custom validation function that returns True if the value is valid, False
        otherwise. For example, use `lambda x: x > 0` to only allow positive integers.
        Defaults to None (no custom validation).
    parent_of_widgets : Optional[QWidget], optional
        The parent widget for the created UI widgets. Defaults to None.
    logger : Optional[Logger], optional
        Logger instance for debugging. Defaults to None.
    
    Attributes
    ----------
    value : int
        Property to get/set the current integer value (inherited from base class).
    widget_line_edit : ControlledLineEdit
        The line edit widget for entering integers.
    widget_enabled_hook : OwnedHook[bool]
        Hook that emits True/False when the widget is enabled/disabled.
    
    Examples
    --------
    Basic usage with a static value:
    
    >>> controller = IntegerEntryController(42)
    >>> print(controller.value)
    42
    >>> controller.value = 100
    
    With custom validation (only positive values):
    
    >>> controller = IntegerEntryController(
    ...     value=10,
    ...     validator=lambda x: x > 0
    ... )
    >>> # User can only enter positive integers
    
    With range validation:
    
    >>> controller = IntegerEntryController(
    ...     value=50,
    ...     validator=lambda x: 0 <= x <= 100
    ... )
    >>> # User can only enter values between 0 and 100
    
    With observables for reactive programming:
    
    >>> from observables import ObservableSingleValue
    >>> observable = ObservableSingleValue(25)
    >>> controller = IntegerEntryController(observable)
    >>> # Changes sync automatically with observable
    
    Accessing the widget:
    
    >>> line_edit = controller.widget_line_edit
    >>> layout.addWidget(line_edit)
    
    Notes
    -----
    - Invalid entries (non-integers or failing validation) are rejected and the
      field reverts to the last valid value
    - The value updates when the user finishes editing (presses Enter or loses focus)
    - Leading/trailing whitespace is automatically stripped
    - The widget can be programmatically enabled/disabled using standard Qt methods
    """

    def __init__(
        self,
        value_or_hook_or_observable: int | Hook[int] | ObservableSingleValueProtocol[int],
        *,
        validator: Optional[Callable[[int], bool]] = None,
        debounce_ms: Optional[int] = None,
        logger: Optional[Logger] = None,
    ) -> None:
        
        self._validator = validator
        
        def verification_method(x: int) -> tuple[bool, str]:
            # Verify the value is an integer
            if not isinstance(x, int): # type: ignore
                return False, f"Value must be an integer, got {type(x)}"
            if self._validator is not None and not self._validator(x):
                return False, f"Value {x} failed validation"
            return True, "Verification method passed"

        BaseSingleHookController.__init__( # type: ignore
            self,
            value_or_hook_or_observable=value_or_hook_or_observable,
            verification_method=verification_method,
            debounce_ms=debounce_ms,
            logger=logger
        )
        
    ###########################################################################
    # Widget methods
    ###########################################################################

    def _initialize_widgets_impl(self) -> None:
        """
        Initialize the line edit widget.
        
        This method is called internally during initialization. It creates the line edit
        widget and connects its editingFinished signal to the controller's handler.
        It also sets up a hook to monitor the widget's enabled/disabled state.
        
        Notes
        -----
        This method should not be called directly by users of the controller.
        """
        self._line_edit = ControlledLineEdit(self, logger=self._logger)
        
        # Connect UI -> model
        self._line_edit.editingFinished.connect(self._on_line_edit_editing_finished)

    def _on_line_edit_editing_finished(self) -> None:
        """
        Handle when the user finishes editing the line edit.
        
        This internal callback is triggered when the user presses Enter or the widget
        loses focus. It:
        1. Parses the text as an integer
        2. Applies custom validation if provided
        3. Updates the value if valid, or reverts to the current value if invalid
        
        Notes
        -----
        This method should not be called directly by users of the controller.
        """
        if self.is_blocking_signals:
            return
        
        # Get the new value from the line edit
        text: str = self._line_edit.text().strip()
        log_msg(self, "on_line_edit_editing_finished", self._logger, f"New value: {text}")
        
        try:
            new_value: int = int(text)
        except ValueError:
            # Invalid input, revert to current value
            self.invalidate_widgets()
            return
        
        if self._validator is not None and not self._validator(new_value):
            log_msg(self, "on_line_edit_editing_finished", self._logger, "Invalid input, reverting to current value")
            self.invalidate_widgets()
            return
        
        # Update component values
        self.submit(new_value)

    def _invalidate_widgets_impl(self) -> None:
        """
        Update the line edit from component values.
        
        This internal method synchronizes the UI widget with the current value.
        It converts the integer value to a string for display in the line edit.
        
        The method is called automatically whenever the controller's value changes,
        whether from user interaction, programmatic changes, or synchronized observables.
        
        Notes
        -----
        This method should not be called directly. Use `invalidate_widgets()` instead
        if you need to manually trigger a widget update.
        """

        self._line_edit.setText(str(self.value))

    ###########################################################################
    # Public API
    ###########################################################################

    @property
    def widget_line_edit(self) -> ControlledLineEdit:
        """
        Get the line edit widget for entering integers.
        
        This is the primary widget for user interaction. It displays the current
        integer value and allows users to type new values.
        
        Returns
        -------
        ControlledLineEdit
            The line edit widget managed by this controller.
        
        Examples
        --------
        >>> line_edit = controller.widget_line_edit
        >>> layout.addWidget(line_edit)
        """
        return self._line_edit