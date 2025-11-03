from __future__ import annotations

from typing import Callable, Optional
from logging import Logger

from ..core.base_singleton_controller import BaseSingletonController
from ..core.formatter_mixin import FormatterMixin
from ...controlled_widgets.controlled_line_edit import ControlledLineEdit
from ...controlled_widgets.controlled_qlabel import ControlledQLabel

from nexpy import Hook, XSingleValueProtocol
from nexpy.core import NexusManager
from nexpy import default as nexpy_default


class IntegerEntryController(BaseSingletonController[int], FormatterMixin[int]):
    """
    A controller for an integer entry widget with validation support.
    
    This controller provides a text field for entering integer values. It validates
    user input, rejecting non-integer values and optionally applying custom validation
    rules. Invalid entries are automatically reverted to the last valid value.
    
    The controller can synchronize with observable values and hooks, making it suitable
    for reactive applications where integer inputs need to be shared across components.
    
    Parameters
    ----------
    value_or_hook_or_observable : int | Hook[int] | XSingleValueProtocol[int]
        The initial integer value or an observable/hook to sync with. Can be:
        - A direct integer value
        - A Hook object for bidirectional synchronization
        - An XSingleValueProtocol for synchronization with reactive data
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
    
    >>> from nexpy import XValue
    >>> observable = XValue(25)
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
        value: int | Hook[int] | XSingleValueProtocol[int],
        *,
        validator: Optional[Callable[[int], bool]] = None,
        formatter: Callable[[int], str] = lambda x: str(x),
        debounce_ms: int|Callable[[], int],
        logger: Optional[Logger] = None,
        nexus_manager: NexusManager = nexpy_default.NEXUS_MANAGER,
    ) -> None:
        
        self._validator = validator
        FormatterMixin.__init__(self, formatter=formatter, invalidate_widgets=self.invalidate_widgets) # type: ignore

        def verification_method(x: int) -> tuple[bool, str]:
            
            # Verify the value is or can be converted to an integer
            if not isinstance(x, int): # type: ignore
                return False, f"Value must be an integer, got {type(x)}"

            if self._validator is not None and not self._validator(x):
                return False, f"Value {x} failed validation"
            return True, "Verification method passed"

        BaseSingletonController.__init__( # type: ignore
            self,
            value=value,
            verification_method=verification_method,
            debounce_ms=debounce_ms,
            logger=logger,
            nexus_manager=nexus_manager
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

        self._label = ControlledQLabel(self, logger=self._logger)
        self._line_edit = ControlledLineEdit(self, logger=self._logger)

        text = self._formatter(self.value)
        self._label.setText(text)
        self._line_edit.setText(text)
        
        self._line_edit.userInputFinishedSignal.connect(self.evaluate)

    def _read_widget_single_value_impl(self) -> tuple[bool, int]:
        """
        Read the value from the integer entry widget.
        
        This method reads the current text from the widget, parses it as an integer,
        and returns it as a boolean and the value.
        
        Returns:
            A tuple containing a boolean indicating if the value is valid and the value.
            If the value is invalid, the boolean will be False and the value will be the last valid value.
        """
        # Get the new value from the line edit
        text: str = self._line_edit.text().strip()
        
        try:
            new_value: int = int(text)
        except ValueError:
            return False, self.value
        
        if self._validator is not None and not self._validator(new_value):
            return False, self.value
        
        return True, new_value

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

        text = self._formatter(self.value)
        self._label.setText(text)
        self._line_edit.setText(text)

    ###########################################################################
    # Public API
    ###########################################################################

    @property
    def widget_integer_label(self) -> ControlledQLabel:
        """Get the label widget."""
        return self._label

    @property
    def widget_integer_entry(self) -> ControlledLineEdit:
        """
        Get the integer entry widget.
        
        This is the primary widget for user interaction. It displays the current
        integer value and allows users to type new values.
        
        Returns
        -------
        ControlledLineEdit
            The line edit widget managed by this controller.
        
        Examples
        --------
        >>> line_edit = controller.widget_integer_entry
        >>> layout.addWidget(line_edit)
        """
        return self._line_edit