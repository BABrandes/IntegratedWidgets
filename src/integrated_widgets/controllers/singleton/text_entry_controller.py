from __future__ import annotations

from typing import Callable, Optional
from logging import Logger

from ..core.base_singleton_controller import BaseSingletonController
from ..core.formatter_mixin import FormatterMixin
from ...controlled_widgets.controlled_line_edit import ControlledLineEdit
from ...controlled_widgets.controlled_qlabel import ControlledQLabel
from ...auxiliaries.resources import log_msg

from nexpy import Hook, XSingleValueProtocol
from nexpy.core import NexusManager
from nexpy import default as nexpy_default

class TextEntryController(BaseSingletonController[str], FormatterMixin[str]):
    """
    A controller for a text entry widget with validation support.
    
    This controller provides a text field for entering string values. It validates
    user input, optionally applying custom validation rules. Invalid entries are 
    automatically reverted to the last valid value.
    
    The controller can synchronize with observable values and hooks, making it suitable
    for reactive applications where text inputs need to be shared across components.
    
    Parameters
    ----------
    value_or_hook_or_observable : str | Hook[str] | XSingleValueProtocol[str]
        The initial string value or an observable/hook to sync with. Can be:
        - A direct string value
        - A Hook object for bidirectional synchronization
        - An XSingleValueProtocol for synchronization with reactive data
    validator : Optional[Callable[[str], bool]], optional
        Custom validation function that returns True if the value is valid, False
        otherwise. For example, use `lambda x: len(x) > 0` to only allow non-empty
        strings. Defaults to None (no custom validation).
    strip_whitespace : bool, optional
        If True, leading and trailing whitespace will be automatically removed from
        the input. Defaults to True.
    logger : Optional[Logger], optional
        Logger instance for debugging. Defaults to None.
    
    Attributes
    ----------
    value : str
        Property to get/set the current string value (inherited from base class).
    widget_line_edit : ControlledLineEdit
        The line edit widget for entering text.
    widget_enabled_hook : HookWithOwnerProtocol[bool]
        Hook that emits True/False when the widget is enabled/disabled.
    strip_whitespace : bool
        Property to get/set whether whitespace stripping is enabled.
    
    Examples
    --------
    Basic usage with a static value:
    
    >>> controller = TextEntryController("Hello World")
    >>> print(controller.value)
    'Hello World'
    >>> controller.value = "New text"
    
    With custom validation (non-empty strings only):
    
    >>> controller = TextEntryController(
    ...     value="Initial",
    ...     validator=lambda x: len(x) > 0
    ... )
    >>> # User cannot leave the field empty
    
    With length validation:
    
    >>> controller = TextEntryController(
    ...     value="test",
    ...     validator=lambda x: 3 <= len(x) <= 20
    ... )
    >>> # User can only enter text between 3 and 20 characters
    
    With pattern validation (email-like):
    
    >>> controller = TextEntryController(
    ...     value="user@example.com",
    ...     validator=lambda x: "@" in x and "." in x
    ... )
    >>> # Simple email validation
    
    With observables for reactive programming:
    
    >>> from nexpy import XValue
    >>> observable = XValue("Initial text")
    >>> controller = TextEntryController(observable)
    >>> # Changes sync automatically with observable
    
    Without whitespace stripping:
    
    >>> controller = TextEntryController(
    ...     value="  text  ",
    ...     strip_whitespace=False
    ... )
    >>> # Whitespace is preserved
    
    Accessing the widget:
    
    >>> line_edit = controller.widget_line_edit
    >>> layout.addWidget(line_edit)
    
    Notes
    -----
    - Invalid entries (failing validation) are rejected and the field reverts to 
      the last valid value
    - The value updates when the user finishes editing (presses Enter or loses focus)
    - Leading/trailing whitespace is automatically stripped by default (configurable)
    - The widget can be programmatically enabled/disabled using standard Qt methods
    """

    def __init__(
        self,
        value: str | Hook[str] | XSingleValueProtocol[str],
        *,
        validator: Optional[Callable[[str], bool]] = None,
        formatter: Callable[[str], str] = lambda x: x,
        strip_whitespace: bool = True,
        debounce_ms: int|Callable[[], int],
        nexus_manager: NexusManager = nexpy_default.NEXUS_MANAGER,
        logger: Optional[Logger] = None,
    ) -> None:
        
        self._validator = validator
        FormatterMixin.__init__(self, formatter=formatter, invalidate_widgets=self.invalidate_widgets) # type: ignore
        self._strip_whitespace = strip_whitespace
        
        def verification_method(x: str) -> tuple[bool, str]:
            # Verify the value is a string
            if not isinstance(x, str): # type: ignore
                return False, f"Value must be a string, got {type(x)}"
            if self._validator is not None and not self._validator(x):
                return False, f"Value '{x}' failed validation"
            return True, "Verification method passed"

        BaseSingletonController.__init__( # type: ignore
            self,
            value=value,
            verification_method=verification_method,
            debounce_ms=debounce_ms,
            nexus_manager=nexus_manager,
            logger=logger,
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
        self._text_label = ControlledQLabel(self, logger=self._logger)
        self._text_entry = ControlledLineEdit(self, logger=self._logger)

        text = self._formatter(self.value)
        self._text_label.setText(text)
        self._text_entry.setText(text)

        self._text_entry.editingFinished.connect(self._on_line_edit_editing_finished)

    def _on_line_edit_editing_finished(self) -> None:
        """
        Handle when the user finishes editing the line edit.
        
        This internal callback is triggered when the user presses Enter or the widget
        loses focus. It:
        1. Gets the text from the line edit
        2. Optionally strips whitespace if configured
        3. Applies custom validation if provided
        4. Updates the value if valid, or reverts to the current value if invalid
        
        Notes
        -----
        This method should not be called directly by users of the controller.
        """
        if self.is_blocking_signals:
            return
        
        # Get the new value from the line edit
        text: str = self._text_entry.text()
        
        if self._strip_whitespace:
            text = text.strip()
        
        log_msg(self, "on_line_edit_editing_finished", self._logger, f"New value: '{text}'")
        
        if self._validator is not None and not self._validator(text):
            log_msg(self, "on_line_edit_editing_finished", self._logger, "Invalid input, reverting to current value")
            self.invalidate_widgets()
            return
        
        # Update component values
        self.submit(text)

    def _invalidate_widgets_impl(self) -> None:
        """
        Update the line edit from component values.
        
        This internal method synchronizes the UI widget with the current value.
        It sets the text of the line edit to the current string value.
        
        The method is called automatically whenever the controller's value changes,
        whether from user interaction, programmatic changes, or synchronized observables.
        
        Notes
        -----
        This method should not be called directly. Use `invalidate_widgets()` instead
        if you need to manually trigger a widget update.
        """

        text = self._formatter(self.value)
        self._text_label.setText(text)
        self._text_entry.setText(text)

    ###########################################################################
    # Public API
    ###########################################################################

    #---------------------------------------------------------------------------
    # Widgets
    #---------------------------------------------------------------------------

    @property
    def widget_text_label(self) -> ControlledQLabel:
        """Get the label widget."""
        return self._text_label

    @property
    def widget_text_entry(self) -> ControlledLineEdit:
        """
        Get the line edit widget for entering text.
        
        This is the primary widget for user interaction. It displays the current
        string value and allows users to type new values.
        
        Returns
        -------
        ControlledLineEdit
            The line edit widget managed by this controller.
        
        Examples
        --------
        >>> text_label = controller.widget_text_label
        >>> text_entry = controller.widget_text_entry
        >>> layout.addWidget(text_label)
        >>> layout.addWidget(text_entry)
        """
        return self._text_entry

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
    def validator(self) -> Optional[Callable[[str], bool]]:
        """
        Get the current validation function.
        
        Returns
        -------
        Optional[Callable[[str], bool]]
            The current validation function, or None if no validation is applied.
        """
        return self._validator

    @validator.setter
    def validator(self, value: Optional[Callable[[str], bool]]) -> None:
        """
        Set the validation function.
        
        Parameters
        ----------
        value : Optional[Callable[[str], bool]]
            A function that takes a string and returns True if valid, False otherwise.
            Can be None to disable validation.
        
        Examples
        --------
        >>> controller.validator = lambda x: len(x) >= 5
        >>> # Now only strings with 5+ characters are accepted
        """
        self._validator = value

    #---------------------------------------------------------------------------
    # Value accessors and mutators
    #---------------------------------------------------------------------------

    @property
    def text(self) -> str:
        """
        Get the current text.
        """
        return self.value

    @text.setter
    def text(self, text: str) -> None:
        self.submit(text)

    def change_text(self, text: str, *, debounce_ms: Optional[int] = None, raise_submission_error_flag: bool = True) -> None:
        self.submit(text, debounce_ms=debounce_ms, raise_submission_error_flag=raise_submission_error_flag)

