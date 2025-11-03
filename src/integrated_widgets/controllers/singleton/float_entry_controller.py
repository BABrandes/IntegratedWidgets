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


class FloatEntryController(BaseSingletonController[float], FormatterMixin[float]):
    """
    A controller for a float entry widget with validation support.
    
    This controller provides a text field for entering floating-point values. It validates
    user input, rejecting non-numeric values and optionally applying custom validation
    rules. Invalid entries are automatically reverted to the last valid value.
    
    The controller can synchronize with observable values and hooks, making it suitable
    for reactive applications where float inputs need to be shared across components.
    
    Parameters
    ----------
    value_or_hook_or_observable : float | Hook[float] | XSingleValueProtocol[float]
        The initial float value or an observable/hook to sync with. Can be:
        - A direct float value
        - A Hook object for bidirectional synchronization
        - An XSingleValueProtocol for synchronization with reactive data
    validator : Optional[Callable[[float], bool]], optional
        Custom validation function that returns True if the value is valid, False
        otherwise. For example, use `lambda x: x > 0.0` to only allow positive values.
        Defaults to None (no custom validation).
    parent_of_widgets : Optional[QWidget], optional
        The parent widget for the created UI widgets. Defaults to None.
    logger : Optional[Logger], optional
        Logger instance for debugging. Defaults to None.
    
    Attributes
    ----------
    value : float
        Property to get/set the current float value (inherited from base class).
    widget_float_entry : ControlledLineEdit
        The float entry widget.
    widget_float_label : ControlledQLabel
        The label widget for displaying the float value.
    widget_enabled_hook : OwnedHook[bool]
        Hook that emits True/False when the widget is enabled/disabled.
    
    Examples
    --------
    Basic usage with a static value:
    
    >>> controller = FloatEntryController(3.14159)
    >>> print(controller.value)
    3.14159
    >>> controller.value = 2.71828
    
    With custom validation (only positive values):
    
    >>> controller = FloatEntryController(
    ...     value=1.5,
    ...     validator=lambda x: x > 0.0
    ... )
    >>> # User can only enter positive floats
    
    With range validation:
    
    >>> controller = FloatEntryController(
    ...     value=0.5,
    ...     validator=lambda x: 0.0 <= x <= 1.0
    ... )
    >>> # User can only enter values between 0 and 1
    
    With observables for reactive programming:
    
    >>> from nexpy import XValue
    >>> observable = XValue(98.6)
    >>> controller = FloatEntryController(observable)
    >>> # Changes sync automatically with observable
    
    Accessing the widget:
    
    >>> line_edit = controller.widget_float_entry
    >>> label = controller.widget_float_label
    >>> layout.addWidget(line_edit)
    >>> layout.addWidget(label)
    
    Notes
    -----
    - Invalid entries (non-floats or failing validation) are rejected and the
      field reverts to the last valid value
    - The value updates when the user finishes editing (presses Enter or loses focus)
    - Leading/trailing whitespace is automatically stripped
    - Both decimal notation (e.g., "3.14") and scientific notation (e.g., "1.5e-3") are supported
    - The widget can be programmatically enabled/disabled using standard Qt methods
    """

    def __init__(
        self,
        value: float | Hook[float] | XSingleValueProtocol[float],
        *,
        validator: Optional[Callable[[float], bool]] = None,
        formatter: Callable[[float], str] = lambda x: str(x),
        debounce_ms: int|Callable[[], int],
        logger: Optional[Logger] = None,
        nexus_manager: NexusManager = nexpy_default.NEXUS_MANAGER,
    ) -> None:
        
        self._validator: Optional[Callable[[float], bool]] = validator
        FormatterMixin.__init__(self, formatter=formatter, invalidate_widgets=self.invalidate_widgets) # type: ignore

        def verification_method(x: float) -> tuple[bool, str]:
            # Verify the value is a float
            if not isinstance(x, float):
                return False, f"Value must be a float, got {type(x)}"
            if self._validator is not None and not self._validator(x):
                return False, f"Value {x} failed validation"
            return True, "Verification method passed"

        BaseSingletonController.__init__( # type: ignore
            self,
            value=value,
            verification_method=verification_method,
            logger=logger,
            debounce_ms=debounce_ms,
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
        self._line_edit = ControlledLineEdit(self, logger=self._logger)
        self._label = ControlledQLabel(self, logger=self._logger)

        text = self._formatter(self.value)
        self._label.setText(text)
        self._line_edit.setText(text)

        # Connect UI -> model
        self._line_edit.userInputFinishedSignal.connect(lambda: self.evaluate())

    def _read_widget_single_value_impl(self) -> tuple[bool, float]:
        """
        Read the value from the float entry widget.
        
        This method reads the current text from the widget, parses it as a float,
        and returns it as a boolean and the value.

        Returns:
            A tuple containing a boolean indicating if the value is valid and the value.
            If the value is invalid, the boolean will be False and the value will be the last valid value.
        """
        text: str = self._line_edit.text().strip()
        try:
            new_value: float = float(text)
        except ValueError:
            # Invalid input, revert to current value
            return False, self.value
        return True, new_value

    def _invalidate_widgets_impl(self) -> None:
        """
        Update the line edit from component values.
        
        This internal method synchronizes the UI widget with the current value.
        It formats the float value to a string for display in the line edit.

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
    def widget_float_label(self) -> ControlledQLabel:
        """Get the label widget."""
        return self._label

    @property
    def widget_float_entry(self) -> ControlledLineEdit:
        """Get the float entry widget."""
        return self._line_edit