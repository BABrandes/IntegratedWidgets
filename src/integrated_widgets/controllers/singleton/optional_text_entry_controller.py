from __future__ import annotations

from typing import Callable, Optional
from logging import Logger

from ..core.base_singleton_controller import BaseSingletonController
from ...controlled_widgets.controlled_line_edit import ControlledLineEdit
from ...util.resources import log_msg

from nexpy import Hook, XSingleValueProtocol
from nexpy.core import NexusManager
from nexpy import default as nexpy_default


class OptionalTextEntryController(BaseSingletonController[Optional[str]]):
    """
    A controller for an optional text entry widget with validation support.
    
    This controller provides a text field for entering optional string values, where
    None is a valid value. It validates user input, optionally applying custom validation
    rules. Invalid entries are automatically reverted to the last valid value.
    
    The controller uses a configurable `none_value` string to represent None in the UI.
    When the user enters text matching `none_value`, it's treated as None. When displaying
    None, the `none_value` text is shown.
    
    The controller can synchronize with observable values and hooks, making it suitable
    for reactive applications where optional text inputs need to be shared across components.
    
    Parameters
    ----------
    value_or_hook_or_observable : Optional[str] | Hook[Optional[str]] | XSingleValueProtocol[Optional[str]]
        The initial string value (or None) or an observable/hook to sync with. Can be:
        - A direct string value or None
        - A Hook object for bidirectional synchronization
        - An XSingleValueProtocol for synchronization with reactive data
    validator : Optional[Callable[[Optional[str]], bool]], optional
        Custom validation function that returns True if the value is valid, False
        otherwise. The validator receives Optional[str], so it can validate None.
        For example, use `lambda x: x is None or len(x) > 0` to allow None or non-empty
        strings. Defaults to None (no custom validation).
    none_value : str, optional
        The text representation of None in the UI. When the user enters this exact text,
        it's treated as None. When the value is None, this text is displayed.
        Defaults to "" (empty string).
    strip_whitespace : bool, optional
        If True, leading and trailing whitespace will be automatically removed from
        the input before checking if it matches `none_value` or validating.
        Defaults to True.
    parent_of_widgets : Optional[QWidget], optional
        The parent widget for the created UI widgets. Defaults to None.
    logger : Optional[Logger], optional
        Logger instance for debugging. Defaults to None.
    
    Attributes
    ----------
    value : Optional[str]
        Property to get/set the current string value or None (inherited from base class).
    widget_line_edit : ControlledLineEdit
        The line edit widget for entering text.
    widget_enabled_hook : OwnedHook[bool]
        Hook that emits True/False when the widget is enabled/disabled.
    strip_whitespace : bool
        Property to get/set whether whitespace stripping is enabled.
    none_value : str
        Property to get/set the text representation of None.
    
    Examples
    --------
    Basic usage with default none_value (empty string):
    
    >>> controller = OptionalTextEntryController("Hello World")
    >>> print(controller.value)
    'Hello World'
    >>> controller.value = None  # Displays as empty string
    >>> controller.value = ""    # Also treated as None
    
    With custom none_value:
    
    >>> controller = OptionalTextEntryController(
    ...     value=None,
    ...     none_value="-"
    ... )
    >>> # Empty field shows "-", entering "-" sets value to None
    
    With validation allowing None or non-empty strings:
    
    >>> controller = OptionalTextEntryController(
    ...     value="Initial",
    ...     validator=lambda x: x is None or len(x) > 0,
    ...     none_value=""
    ... )
    >>> # User can leave empty (None) or enter non-empty text
    
    With validation requiring minimum length when not None:
    
    >>> controller = OptionalTextEntryController(
    ...     value=None,
    ...     validator=lambda x: x is None or len(x) >= 3,
    ...     none_value="<none>"
    ... )
    >>> # User can enter "<none>" for None or text with 3+ characters
    
    With observables for reactive programming:
    
    >>> from nexpy import XValue
    >>> observable = XValue[Optional[str]](None)
    >>> controller = OptionalTextEntryController(observable)
    >>> # Changes sync automatically with observable
    
    Custom none_value for clarity:
    
    >>> controller = OptionalTextEntryController(
    ...     value=None,
    ...     none_value="(not set)"
    ... )
    >>> # None is displayed as "(not set)"
    
    Accessing the widget:
    
    >>> line_edit = controller.widget_line_edit
    >>> layout.addWidget(line_edit)
    
    Notes
    -----
    - When the entered text equals `none_value` (after optional whitespace stripping),
      the value is set to None
    - When the value is None, the line edit displays `none_value`
    - Invalid entries (failing validation) are rejected and the field reverts to 
      the last valid value
    - The value updates when the user finishes editing (presses Enter or loses focus)
    - Leading/trailing whitespace is automatically stripped by default (configurable)
    - The widget can be programmatically enabled/disabled using standard Qt methods
    """

    def __init__(
        self,
        value: Optional[str] | Hook[Optional[str]] | XSingleValueProtocol[Optional[str]],
        *,
        validator: Optional[Callable[[Optional[str]], bool]] = None,
        none_value: str = "",
        debounce_ms: Optional[int] = None,
        strip_whitespace: bool = True,
        logger: Optional[Logger] = None,
        nexus_manager: NexusManager = nexpy_default.NEXUS_MANAGER,
    ) -> None:
        
        self._validator = validator
        self._none_value = none_value
        self._strip_whitespace = strip_whitespace
        
        def verification_method(x: Optional[str]) -> tuple[bool, str]:
            # Verify the value is a string or None
            if x is not None and not isinstance(x, str): # type: ignore
                return False, f"Value must be a string or None, got {type(x)}"
            if self._validator is not None and not self._validator(x):
                return False, f"Value '{x}' failed validation"
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
        
        # Connect UI -> model
        self._line_edit.editingFinished.connect(self._on_line_edit_editing_finished)

    def _on_line_edit_editing_finished(self) -> None:
        """
        Handle when the user finishes editing the line edit.
        
        This internal callback is triggered when the user presses Enter or the widget
        loses focus. It:
        1. Gets the text from the line edit
        2. Optionally strips whitespace if configured
        3. Checks if the text matches `none_value` (treats as None)
        4. Applies custom validation if provided
        5. Updates the value if valid, or reverts to the current value if invalid
        
        Notes
        -----
        This method should not be called directly by users of the controller.
        """
        if self.is_blocking_signals:
            return
        
        # Get the new value from the line edit
        text: str = self._line_edit.text()
        
        if self._strip_whitespace:
            text = text.strip()
        
        # Check if the text matches the none_value
        new_value: Optional[str]
        if text == self._none_value:
            new_value = None
            log_msg(self, "on_line_edit_editing_finished", self._logger, f"Text matches none_value, setting to None")
        else:
            new_value = text
            log_msg(self, "on_line_edit_editing_finished", self._logger, f"New value: '{text}'")
        
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
        If the value is None, it displays the `none_value` text. Otherwise, it
        displays the actual string value.
        
        The method is called automatically whenever the controller's value changes,
        whether from user interaction, programmatic changes, or synchronized observables.
        
        Notes
        -----
        This method should not be called directly. Use `invalidate_widgets()` instead
        if you need to manually trigger a widget update.
        """

        current_value = self.value
        if current_value is None:
            self._line_edit.setText(self._none_value)
        else:
            self._line_edit.setText(current_value)

    ###########################################################################
    # Public API
    ###########################################################################

    #---------------------------------------------------------------------------
    # Widgets
    #---------------------------------------------------------------------------

    @property
    def widget_line_edit(self) -> ControlledLineEdit:
        """
        Get the line edit widget for entering text.
        
        This is the primary widget for user interaction. It displays the current
        string value (or none_value if None) and allows users to type new values.
        
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

    #---------------------------------------------------------------------------
    # Settings
    #---------------------------------------------------------------------------

    @property
    def strip_whitespace(self) -> bool:
        """
        Get whether whitespace stripping is enabled.
        
        Returns
        -------
        bool
            True if leading/trailing whitespace is automatically stripped, False otherwise.
        """
        return self._strip_whitespace

    @strip_whitespace.setter
    def strip_whitespace(self, value: bool) -> None:
        """
        Set whether whitespace stripping is enabled.
        
        Parameters
        ----------
        value : bool
            True to enable automatic whitespace stripping, False to disable.
        """
        self._strip_whitespace = value

    @property
    def none_value(self) -> str:
        """
        Get the text representation of None.
        
        Returns
        -------
        str
            The text that represents None in the UI.
        """
        return self._none_value

    @none_value.setter
    def none_value(self, value: str) -> None:
        """
        Set the text representation of None.
        
        Changing this will automatically update the widget if the current value is None.
        
        Parameters
        ----------
        value : str
            The text to display when the value is None, and to recognize as None
            when entered by the user.
        
        Examples
        --------
        >>> controller.none_value = "<empty>"
        >>> # Now None is displayed as "<empty>"
        """
        self._none_value = value
        # Update the widget if the current value is None
        if self.value is None:
            self.invalidate_widgets()

    @property
    def validator(self) -> Optional[Callable[[Optional[str]], bool]]:
        """
        Get the current validation function.
        
        Returns
        -------
        Optional[Callable[[Optional[str]], bool]]
            The current validation function, or None if no validation is applied.
        """
        return self._validator

    @validator.setter
    def validator(self, value: Optional[Callable[[Optional[str]], bool]]) -> None:
        """
        Set the validation function.
        
        Parameters
        ----------
        value : Optional[Callable[[Optional[str]], bool]]
            A function that takes an optional string and returns True if valid, 
            False otherwise. Can be None to disable validation.
        
        Examples
        --------
        >>> controller.validator = lambda x: x is None or len(x) >= 5
        >>> # Now only None or strings with 5+ characters are accepted
        """
        self._validator = value

    #---------------------------------------------------------------------------
    # Value accessors and mutators
    #---------------------------------------------------------------------------

    @property
    def text(self) -> Optional[str]:
        """
        Get the current text.
        """
        return self.value

    @text.setter
    def text(self, value: Optional[str]) -> None:
        self.submit(value)

    def change_text(self, value: Optional[str], *, debounce_ms: Optional[int] = None, raise_submission_error_flag: bool = True) -> None:
        self.submit(value, debounce_ms=debounce_ms, raise_submission_error_flag=raise_submission_error_flag)