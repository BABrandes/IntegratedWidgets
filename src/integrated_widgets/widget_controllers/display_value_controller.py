from __future__ import annotations

# Standard library imports
from typing import Optional, Generic, TypeVar, Callable
from logging import Logger
from PySide6.QtWidgets import QWidget

# BAB imports
from observables import ObservableSingleValueLike, HookLike

# Local imports
from ..util.base_single_hook_controller import BaseSingleHookController
from ..controlled_widgets.controlled_label import ControlledLabel
from ..util.resources import log_msg

T = TypeVar("T")

class DisplayValueController(BaseSingleHookController[T, "DisplayValueController"], Generic[T]):
    """
    A controller for displaying a value with a read-only label widget.
    
    This controller provides a simple, non-editable display of any value type. It
    automatically updates the label text when the underlying value changes, making
    it ideal for status displays, read-only fields, and monitoring applications.
    
    The controller can format values using a custom formatter function, enabling
    flexible presentation of numbers, dates, complex objects, or any other data type.
    
    Parameters
    ----------
    value_or_hook_or_observable : T | HookLike[T] | ObservableSingleValueLike[T]
        The initial value to display or an observable/hook to sync with. Can be:
        - A direct value of any type
        - A HookLike object for synchronization with external data
        - An ObservableSingleValueLike for reactive updates
    formatter : Optional[Callable[[T], str]], optional
        Function to convert the value to a display string. If None, uses str().
        Defaults to None.
    parent_of_widgets : Optional[QWidget], optional
        The parent widget for the created UI widgets. Defaults to None.
    logger : Optional[Logger], optional
        Logger instance for debugging. Defaults to None.
    
    Attributes
    ----------
    value : T
        Property to get/set the currently displayed value.
    formatter : Optional[Callable[[T], str]]
        Property to get/set the formatter function.
    widget_label : ControlledLabel
        The label widget that displays the formatted value.
    
    Examples
    --------
    Basic usage displaying a number:
    
    >>> controller = DisplayValueController(42)
    >>> print(controller.value)
    42
    >>> controller.value = 100  # Update the display
    
    With custom formatting:
    
    >>> controller = DisplayValueController(
    ...     value=3.14159,
    ...     formatter=lambda x: f"{x:.2f}"
    ... )
    >>> # Label shows "3.14"
    
    Displaying complex objects:
    
    >>> from datetime import datetime
    >>> controller = DisplayValueController(
    ...     value=datetime.now(),
    ...     formatter=lambda dt: dt.strftime("%Y-%m-%d %H:%M:%S")
    ... )
    
    With observables for real-time monitoring:
    
    >>> from observables import ObservableSingleValue
    >>> temperature = ObservableSingleValue(20.5)
    >>> controller = DisplayValueController(
    ...     value_or_hook_or_observable=temperature,
    ...     formatter=lambda t: f"{t:.1f}°C"
    ... )
    >>> # Label automatically updates when temperature changes
    >>> temperature.value = 22.3  # Display updates to "22.3°C"
    
    Accessing the widget:
    
    >>> label = controller.widget_label
    >>> layout.addWidget(label)
    
    Notes
    -----
    - The label is read-only and cannot be edited by users
    - The display updates automatically when the value changes
    - The formatter can be changed at runtime to alter the display format
    """

    def __init__(
        self,
        value_or_hook_or_observable: T | HookLike[T] | ObservableSingleValueLike[T],
        formatter: Optional[Callable[[T], str]] = None,
        parent_of_widgets: Optional[QWidget] = None,
        logger: Optional[Logger] = None) -> None:

        self._formatter = formatter
        
        BaseSingleHookController.__init__( # type: ignore
            self,
            value_or_hook_or_observable=value_or_hook_or_observable,
            logger=logger
        )

    ###########################################################################
    # Widget methods
    ###########################################################################

    def _initialize_widgets_impl(self) -> None:
        """
        Initialize the display label widget.
        
        This method is called internally during initialization. It creates a
        read-only label widget that will display the formatted value.
        
        Notes
        -----
        This method should not be called directly by users of the controller.
        """
        self._label = ControlledLabel(self)

    def _invalidate_widgets_impl(self) -> None:
        """
        Update the label from component values.
        
        This internal method synchronizes the label widget with the current value.
        It applies the formatter function (if set) or uses str() to convert the
        value to display text.
        
        The method is called automatically whenever the controller's value changes,
        whether from programmatic changes or synchronized observables.
        
        Notes
        -----
        This method should not be called directly. Use `invalidate_widgets()` instead
        if you need to manually trigger a widget update.
        """

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
        """
        Get the current value.
        
        Returns
        -------
        T
            The currently displayed value.
        """
        value: T = self.get_value_of_hook("value") # type: ignore
        return value # type: ignore

    @value.setter
    def value(self, value: T) -> None:
        """
        Set the current value.
        
        Updates the displayed value and automatically refreshes the label widget.
        
        Parameters
        ----------
        value : T
            The new value to display.
        """
        self.submit(value)

    def change_value(self, value: T) -> None:
        """
        Set the current value (alternative method name).
        
        This method is functionally identical to using the value property setter.
        
        Parameters
        ----------
        value : T
            The new value to display.
        """
        self.submit(value)

    @property
    def formatter(self) -> Optional[Callable[[T], str]]:
        """
        Get the formatter function.
        
        Returns
        -------
        Optional[Callable[[T], str]]
            The current formatter function, or None if using default str() conversion.
        """
        return self._formatter

    @formatter.setter
    def formatter(self, formatter: Callable[[T], str]) -> None:
        """
        Set the formatter function.
        
        Changing the formatter will automatically update the widget display with
        the new formatting applied to the current value.
        
        Parameters
        ----------
        formatter : Callable[[T], str]
            A function that takes a value and returns its display string.
        
        Examples
        --------
        >>> controller.formatter = lambda x: f"Value: {x}"
        >>> controller.formatter = str.upper  # For string values
        """
        self._formatter = formatter
        self.invalidate_widgets()

    def change_formatter(self, formatter: Callable[[T], str]) -> None:
        """
        Set the formatter function (alternative method name).
        
        This method is functionally identical to using the formatter property setter.
        Changing the formatter will automatically update the widget display.
        
        Parameters
        ----------
        formatter : Callable[[T], str]
            A function that takes a value and returns its display string.
        """
        self._formatter = formatter
        self.invalidate_widgets()

    ###########################################################################
    # Public API
    ###########################################################################

    @property
    def widget_label(self) -> ControlledLabel:
        """
        Get the display label widget.
        
        This is the read-only label that displays the formatted value. It can be
        added to any Qt layout.
        
        Returns
        -------
        ControlledLabel
            The label widget managed by this controller.
        
        Examples
        --------
        >>> label = controller.widget_label
        >>> layout.addWidget(label)
        """
        return self._label