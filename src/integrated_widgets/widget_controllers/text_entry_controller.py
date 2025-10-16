from __future__ import annotations

from typing import Callable, Optional
from logging import Logger
from PySide6.QtWidgets import QWidget, QFrame, QVBoxLayout, QGroupBox

from ..util.base_single_hook_controller import BaseSingleHookController
from ..controlled_widgets.controlled_line_edit import ControlledLineEdit
from ..util.resources import log_msg

from observables import ObservableSingleValueLike, HookLike
from observables.core import HookWithOwnerLike, OwnedHook


class TextEntryController(BaseSingleHookController[str, "TextEntryController"]):
    """
    A controller for a text entry widget with validation support.
    
    This controller provides a text field for entering string values. It validates
    user input, optionally applying custom validation rules. Invalid entries are 
    automatically reverted to the last valid value.
    
    The controller can synchronize with observable values and hooks, making it suitable
    for reactive applications where text inputs need to be shared across components.
    
    Parameters
    ----------
    value_or_hook_or_observable : str | HookLike[str] | ObservableSingleValueLike[str]
        The initial string value or an observable/hook to sync with. Can be:
        - A direct string value
        - A HookLike object for bidirectional synchronization
        - An ObservableSingleValueLike for synchronization with reactive data
    validator : Optional[Callable[[str], bool]], optional
        Custom validation function that returns True if the value is valid, False
        otherwise. For example, use `lambda x: len(x) > 0` to only allow non-empty
        strings. Defaults to None (no custom validation).
    strip_whitespace : bool, optional
        If True, leading and trailing whitespace will be automatically removed from
        the input. Defaults to True.
    parent_of_widgets : Optional[QWidget], optional
        The parent widget for the created UI widgets. Defaults to None.
    logger : Optional[Logger], optional
        Logger instance for debugging. Defaults to None.
    
    Attributes
    ----------
    value : str
        Property to get/set the current string value (inherited from base class).
    widget_line_edit : ControlledLineEdit
        The line edit widget for entering text.
    widget_enabled_hook : OwnedHook[bool]
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
    
    >>> from observables import ObservableSingleValue
    >>> observable = ObservableSingleValue("Initial text")
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
        value_or_hook_or_observable: str | HookLike[str] | ObservableSingleValueLike[str],
        *,
        validator: Optional[Callable[[str], bool]] = None,
        strip_whitespace: bool = True,
        logger: Optional[Logger] = None,
    ) -> None:
        
        self._validator = validator
        self._strip_whitespace = strip_whitespace
        
        def verification_method(x: str) -> tuple[bool, str]:
            # Verify the value is a string
            if not isinstance(x, str):
                return False, f"Value must be a string, got {type(x)}"
            if self._validator is not None and not self._validator(x):
                return False, f"Value '{x}' failed validation"
            return True, "Verification method passed"

        BaseSingleHookController.__init__(
            self,
            value_or_hook_or_observable=value_or_hook_or_observable,
            verification_method=verification_method,
            logger=logger
        )

        self._widget_enabled_hook = OwnedHook[bool](
            self, self._line_edit.isEnabled(),
            logger=logger
        )
        self._line_edit.enabledChanged.connect(self._widget_enabled_hook.submit_value)

    ###########################################################################
    # Widget methods
    ###########################################################################

    def _initialize_widgets(self) -> None:
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
        3. Applies custom validation if provided
        4. Updates the value if valid, or reverts to the current value if invalid
        
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
        
        log_msg(self, "on_line_edit_editing_finished", self._logger, f"New value: '{text}'")
        
        if self._validator is not None and not self._validator(text):
            log_msg(self, "on_line_edit_editing_finished", self._logger, "Invalid input, reverting to current value")
            self._invalidate_widgets_called_by_hook_system()
            return
        
        # Update component values
        self._submit_values_debounced(text)

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

        self._line_edit.setText(self.value)

    ###########################################################################
    # Public API
    ###########################################################################

    @property
    def widget_line_edit(self) -> ControlledLineEdit:
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
        >>> line_edit = controller.widget_line_edit
        >>> layout.addWidget(line_edit)
        """
        return self._line_edit

    @property
    def widget_enabled_hook(self) -> OwnedHook[bool]:
        """
        Get the widget enabled hook.
        
        This hook emits True when the line edit widget is enabled and False when
        it's disabled. This is useful for reactive applications that need to respond
        to changes in widget enabled state.
        
        Returns
        -------
        OwnedHook[bool]
            Hook that tracks the line edit widget's enabled state.
        
        Examples
        --------
        >>> def on_enabled_changed(is_enabled: bool):
        ...     print(f"Text entry is now {'enabled' if is_enabled else 'disabled'}")
        >>> controller.widget_enabled_hook.add_callback(on_enabled_changed)
        """
        return self._widget_enabled_hook

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

    ###########################################################################
    # Debugging
    ###########################################################################

    def all_widgets_as_frame(self) -> QFrame:
        """
        Return all widgets organized in a QFrame for easy layout.
        
        This is a convenience method for adding the controller's widgets to a UI.
        It creates a vertical layout containing the line edit widget inside a group box.
        
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
        
        # Line Edit
        line_edit_group = QGroupBox("Text Entry")
        line_edit_layout = QVBoxLayout()
        line_edit_layout.addWidget(self.widget_line_edit)
        line_edit_group.setLayout(line_edit_layout)
        layout.addWidget(line_edit_group)

        return frame

