from __future__ import annotations

# Standard library imports
from typing import Generic, Optional, TypeVar, Callable, Any, Mapping, Literal, AbstractSet
from logging import Logger

# BAB imports
from nexpy import XSetProtocol, Hook
from nexpy.x_objects.single_value_like.protocols import XSingleValueProtocol
from nexpy.x_objects.set_like.protocols import XOptionalSelectionOptionProtocol

# Local imports
from .core.base_complex_hook_controller import BaseComplexHookController
from ..controlled_widgets.controlled_combobox import ControlledComboBox
from ..controlled_widgets.controlled_qlabel import ControlledQLabel
from ..util.resources import log_msg, combo_box_find_data

T = TypeVar("T")

class ListOptionalSelectionController(BaseComplexHookController[Literal["selected_option", "available_options"], Any, Any, Any, "ListOptionalSelectionController"], XOptionalSelectionOptionProtocol[T], Generic[T]):
    """
    A controller for managing optional selection from a set of available options.
    
    This controller provides a combobox widget that allows users to select from a set of 
    options, with None as a valid selectable choice. It can synchronize with observable 
    values and hooks from the observables library, making it suitable for reactive 
    applications.
    
    The controller maintains two synchronized values:
    - selected_option: The currently selected option (can be None)
    - available_options: The set of options available for selection
    
    The controller ensures that the selected_option (if not None) is always present in 
    the available_options set. If you need to select None while having an empty set of 
    available_options, this is valid. However, selecting a non-None value requires that 
    value to be present in available_options.
    
    Parameters
    ----------
    selected_option : Optional[T] | Hook[Optional[T]] | XSingleValueProtocol[Optional[T], Hook[Optional[T]]] | XOptionalSelectionOptionProtocol[T]
        The initial selected option or an observable/hook to sync with. Can be:
        - A direct value (including None)
        - A Hook object for bidirectional synchronization
        - An XSingleValueProtocol for one-way or two-way synchronization
        - An XOptionalSelectionOptionProtocol that provides both selected and available options
    available_options : frozenset[T] | Hook[frozenset[T]] | XSetProtocol[T] | None
        The initial set of available options or an observable/hook to sync with. Can be:
        - A direct set value (can be empty set())
        - A Hook object for bidirectional synchronization
        - An XSetProtocol for synchronization
        - None only if selected_option is XOptionalSelectionOptionProtocol
    formatter : Callable[[T], str], optional
        Function to convert option values to display strings. Defaults to str().
    none_option_text : str, optional
        The text to display for the None option in the combobox. Defaults to "-".
    logger : Optional[Logger], optional
        Logger instance for debugging. Defaults to None.
    
    Raises
    ------
    ValueError
        If available_options is provided when selected_option is XOptionalSelectionOptionProtocol.
    ValueError
        If available_options has an invalid type.
    
    Attributes
    ----------
    formatter : Callable[[T], str]
        Property to get/set the formatter function.
    none_option_text : str
        Property to get/set the text displayed for the None option.
    widget_combobox : ControlledComboBox
        The combobox widget for user selection.
    widget_label : ControlledQLabel
        A label widget showing the current selection (created on first access).
    
    Examples
    --------
    Basic usage with static values:
    
    >>> controller = SelectionOptionalOptionController(
    ...     selected_option="apple",
    ...     available_options={"apple", "banana", "orange"}
    ... )
    >>> controller.selected_option
    'apple'
    >>> controller.selected_option = None  # Valid: clears selection
    >>> controller.selected_option = "banana"
    
    With an empty set (None must be selected):
    
    >>> controller = SelectionOptionalOptionController(
    ...     selected_option=None,
    ...     available_options=frozenset()  # Valid when selected_option is None
    ... )
    
    With observables for reactive programming:
    
    >>> from nexpy import XSetSingleSelectOptional
    >>> observable = XSetSingleSelectOptional(
    ...     selected_option="red",
    ...     available_options={"red", "green", "blue"}
    ... )
    >>> controller = SelectionOptionalOptionController(observable)
    >>> # Changes to controller.selected_option automatically sync with observable
    
    Custom formatting:
    
    >>> controller = SelectionOptionalOptionController(
    ...     selected_option=1,
    ...     available_options={1, 2, 3},
    ...     formatter=lambda x: f"Option {x}",
    ...     none_option_text="No selection"
    ... )
    
    Notes
    -----
    - The None option always appears first in the combobox dropdown
    - Options in the dropdown are sorted by their formatted text
    - The controller validates that selected_option (if not None) is in available_options
    - Empty available_options (set()) is valid only when selected_option is None
    """

    def __init__(
        self,
        selected_option: Optional[T] | Hook[Optional[T]] | XSingleValueProtocol[Optional[T], Hook[Optional[T]]] | XOptionalSelectionOptionProtocol[T],
        available_options: AbstractSet[T] | Hook[AbstractSet[T]] | XSetProtocol[T] | None,
        *,
        formatter: Callable[[T], str] = lambda item: str(item),
        none_option_text: str = "-",
        debounce_ms: Optional[int] = None,
        logger: Optional[Logger] = None,
    ) -> None:

        log_msg(self, "__init__", logger, f"Starting initialization with selected_option={selected_option}, available_options={available_options}, none_option_label='{none_option_text}'")
        
        self._formatter = formatter
        self._none_option_text = none_option_text
        log_msg(self, "__init__", logger, f"Formatter set: {formatter}, none_option_label: '{none_option_text}'")

        if isinstance(selected_option, XOptionalSelectionOptionProtocol):
            log_msg(self, "__init__", logger, "selected_option is XOptionalSelectionOptionProtocol")
            if available_options is not None:
                raise ValueError("available_options is not allowed when selected_option is an XOptionalSelectionOptionProtocol")

            initial_selected_option: Optional[T] = selected_option.selected_option # type: ignore
            hook_selected_option: Optional[Hook[Optional[T]]] = selected_option.selected_option_hook # type: ignore
            initial_available_options: AbstractSet[T] = selected_option.available_options # type: ignore
            hook_available_options: Optional[Hook[AbstractSet[T]]] = selected_option.available_options_hook # type: ignore
            
            log_msg(self, "__init__", logger, f"From XOptionalSelectionOptionProtocol: initial_selected_option={initial_selected_option}, initial_available_options={initial_available_options}")

        else:
            log_msg(self, "__init__", logger, "selected_option is not XOptionalSelectionOptionProtocol, processing manually")

            if selected_option is None:
                log_msg(self, "__init__", logger, "selected_option is None")
                initial_selected_option = None
                hook_selected_option = None

            elif isinstance(selected_option, Hook):
                # It's a hook - get initial value
                log_msg(self, "__init__", logger, "selected_option is Hook")
                initial_selected_option = selected_option.value # type: ignore
                hook_selected_option: Optional[Hook[Optional[T]]] = selected_option # type: ignore
                log_msg(self, "__init__", logger, f"From Hook: initial_selected_option={initial_selected_option}")

            elif isinstance(selected_option, XSingleValueProtocol):
                # It's an observable - get initial value
                log_msg(self, "__init__", logger, "selected_option is XSingleValueProtocol")
                initial_selected_option: Optional[T] = selected_option.value # type: ignore
                hook_selected_option: Optional[Hook[Optional[T]]] = selected_option.hook # type: ignore
                log_msg(self, "__init__", logger, f"From XSingleValueProtocol: initial_selected_option={initial_selected_option}")

            else:
                # It's a direct value
                log_msg(self, "__init__", logger, "selected_option is direct value")
                initial_selected_option = selected_option
                hook_selected_option = None
                log_msg(self, "__init__", logger, f"Direct value: initial_selected_option={initial_selected_option}")
            
            if isinstance(available_options, AbstractSet):
                # It's a direct value
                log_msg(self, "__init__", logger, "available_options is direct set")
                initial_available_options = set(available_options) if not isinstance(available_options, set) else available_options # type: ignore
                hook_available_options = None
                log_msg(self, "__init__", logger, f"Direct set: initial_available_options={initial_available_options}")

            elif isinstance(available_options, Hook):
                # It's a hook - get initial value
                log_msg(self, "__init__", logger, "available_options is Hook")
                initial_available_options = available_options.value # type: ignore
                hook_available_options = available_options
                log_msg(self, "__init__", logger, f"From Hook: initial_available_options={initial_available_options}")

            elif isinstance(available_options, XSetProtocol):
                # It's an observable - get initial value
                log_msg(self, "__init__", logger, "available_options is XSetProtocol")
                initial_available_options = available_options.set
                hook_available_options = available_options.set_hook
                log_msg(self, "__init__", logger, f"From XSetProtocol: initial_available_options={initial_available_options}")

            else:
                log_msg(self, "__init__", logger, f"ERROR: Invalid available_options type: {type(available_options)}")
                raise ValueError(f"Invalid available_options: {available_options}")
        
        log_msg(self, "__init__", logger, f"Final values: initial_selected_option={initial_selected_option}, initial_available_options={initial_available_options}")
        
        def verification_method(x: Mapping[Literal["selected_option", "available_options"], Any]) -> tuple[bool, str]:
            log_msg(self, "verification_method", logger, f"Verifying: {x}")
            # Handle partial updates by getting current values for missing keys

            if "selected_option" in x:
                selected_option: Optional[T] = x["selected_option"]
                log_msg(self, "verification_method", logger, f"selected_option from input: {selected_option}")
            else:
                selected_option = self.get_value_of_hook("selected_option") # type: ignore
                log_msg(self, "verification_method", logger, f"selected_option from current: {selected_option}")

            if "available_options" in x:
                available_options: frozenset[T] = x["available_options"]
                log_msg(self, "verification_method", logger, f"available_options from input: {available_options}")
            else:
                available_options = self.get_value_of_hook("available_options") # type: ignore
                log_msg(self, "verification_method", logger, f"available_options from current: {available_options}")

            if selected_option is not None and not selected_option in available_options:
                log_msg(self, "verification_method", logger, f"VERIFICATION FAILED: {selected_option} not in {available_options}")
                return False, f"Selected option {selected_option} not in available options: {available_options}"
            
            log_msg(self, "verification_method", logger, "VERIFICATION PASSED")
            return True, "Verification method passed"

        log_msg(self, "__init__", logger, "Calling super().__init__")
        super().__init__(
            {
                "selected_option": initial_selected_option,
                "available_options": initial_available_options
            },
            verification_method=verification_method,
            debounce_ms=debounce_ms,
            logger=logger
        )
        
        log_msg(self, "__init__", logger, "Super().__init__ completed, attaching hooks")
        
        if hook_available_options is not None:
            log_msg(self, "__init__", logger, f"Attaching available_options hook: {hook_available_options}")
            self.connect_hook(hook_available_options, "available_options", initial_sync_mode="use_target_value") # type: ignore
        if hook_selected_option is not None:
            log_msg(self, "__init__", logger, f"Attaching selected_option hook: {hook_selected_option}")
            self.connect_hook(hook_selected_option,"selected_option", initial_sync_mode="use_target_value") # type: ignore
        
        log_msg(self, "__init__", logger, "Initialization completed successfully")

    ###########################################################################
    # Widget methods
    ###########################################################################

    def _initialize_widgets_impl(self) -> None:
        """
        Create and configure all the user interface widgets.
        
        This method is called internally during initialization. It creates the combobox
        widget and connects its signals to the controller's internal handlers.
        
        Created Widgets
        ---------------
        - ControlledComboBox: The dropdown selection widget
        
        Notes
        -----
        This method should not be called directly by users of the controller.
        """
        log_msg(self, "initialize_widgets", self._logger, "Starting widget initialization")

        self._combobox = ControlledComboBox(self, logger=self._logger)
        log_msg(self, "initialize_widgets", self._logger, f"Created GuardedComboBox: {self._combobox}")

        # Connect UI -> model
        self._combobox.currentIndexChanged.connect(lambda _i: self._on_combobox_index_changed()) # type: ignore
        log_msg(self, "initialize_widgets", self._logger, "Connected currentIndexChanged signal")

        log_msg(self, "initialize_widgets", self._logger, "Widget initialization completed")

    def _on_combobox_index_changed(self) -> None:
        """
        Handle when the user selects a different option from the dropdown menu.
        
        This internal callback is triggered whenever the combobox index changes. It retrieves the selected option data from the combobox and submits the new value through the controller's validation system.
        
        Notes
        -----
        This method should not be called directly by users of the controller.
        """
        if self.is_blocking_signals:
            return

        new_option: Optional[T] = self._combobox.currentData()
        self.submit_value("selected_option", new_option)

    def _invalidate_widgets_impl(self) -> None:
        """
        Update the widgets from the component values.
        
        This internal method synchronizes the UI widgets with the current state of
        the controller's values. It:
        1. Clears the combobox
        2. Adds all available options (sorted by formatted text)
        3. Sets the combobox to display the currently selected option
        4. Updates the label widget if it exists
        
        The method is called automatically whenever the controller's state changes.
        """

        selected_option: Optional[T] = self.selected_option
        available_options: AbstractSet[T] = self.available_options
        self._combobox.clear()
        self._combobox.addItem(self._none_option_text, userData=None) # type: ignore

        sorted_options: list[T] = sorted(available_options, key=self._formatter)
        for option in sorted_options:
            formatted_text: str = self._formatter(option)
            self._combobox.addItem(formatted_text, userData=option) # type: ignore
        
        current_index: int = combo_box_find_data(self._combobox, selected_option)
        self._combobox.setCurrentIndex(current_index)

        if hasattr(self, "_label"):
            if self.selected_option is not None:
                self._label.setText(self._formatter(self.selected_option))
            else:
                self._label.setText(self._none_option_text)

    ###########################################################################
    # Public API
    ###########################################################################

    @property
    def formatter(self) -> Callable[[T], str]:
        """
        Get the formatter function.
        
        Returns
        -------
        Callable[[T], str]
            The current formatter function used to convert options to display strings.
        """
        return self._formatter

    @formatter.setter
    def formatter(self, formatter: Callable[[T], str]) -> None:
        """
        Set the formatter function.
        
        Changing the formatter will automatically update the widget display.
        
        Parameters
        ----------
        formatter : Callable[[T], str]
            A function that takes an option value and returns its display string.
        
        Examples
        --------
        >>> controller.formatter = lambda x: f"Item: {x}"
        >>> controller.formatter = str.upper
        """
        log_msg(self, "formatter.setter", self._logger, f"Setting formatter to: {formatter}")
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
            A function that takes an option value and returns its display string.
        """
        log_msg(self, "change_formatter", self._logger, f"Changing formatter to: {formatter}")
        self._formatter = formatter
        self.invalidate_widgets()

    @property
    def none_option_text(self) -> str:
        """
        Get the text displayed for the None option.
        
        Returns
        -------
        str
            The current text displayed for the None option in the combobox.
        """
        return self._none_option_text

    @none_option_text.setter
    def none_option_text(self, none_option_text: str) -> None:
        """
        Set the text displayed for the None option.
        
        Changing this text will automatically update the widget display.
        
        Parameters
        ----------
        none_option_text : str
            The new text to display for the None option in the combobox.
        
        Examples
        --------
        >>> controller.none_option_text = "No selection"
        >>> controller.none_option_text = "(None)"
        """
        log_msg(self, "none_option_text.setter", self._logger, f"Setting none option text to: {none_option_text}")
        self._none_option_text = none_option_text
        self.invalidate_widgets()
    
    def change_none_option_text(self, none_option_text: str) -> None:
        """
        Set the text displayed for the None option (alternative method name).
        
        This method is functionally identical to using the none_option_text property setter.
        Changing this text will automatically update the widget display.
        
        Parameters
        ----------
        none_option_text : str
            The new text to display for the None option in the combobox.
        """
        log_msg(self, "change_none_option_text", self._logger, f"Changing none option text to: {none_option_text}")
        self._none_option_text = none_option_text
        self.invalidate_widgets()

    @property
    def widget_combobox(self) -> ControlledComboBox:
        """
        Get the combobox widget for displaying and selecting options.
        
        This is the primary widget for user interaction. It displays all available
        options plus the None option, and allows the user to select one.
        
        Returns
        -------
        ControlledComboBox
            The combobox widget managed by this controller.
        """
        return self._combobox

    @property
    def widget_label(self) -> ControlledQLabel:
        """
        Get a label widget that displays the current selection.
        
        This label is created on first access and automatically updates to show
        the formatted text of the current selection (or the none_option_text if
        the selection is None).
        
        Returns
        -------
        ControlledQLabel
            A label widget showing the current selected option.
        
        Notes
        -----
        The label is created lazily on first access and is not part of the default
        widget set returned by `all_widgets_as_frame()`.
        """
        if not hasattr(self, "_label"):
            self._label = ControlledQLabel(self)
            if self.selected_option is not None:
                self._label.setText(self._formatter(self.selected_option))
            else:
                self._label.setText(self._none_option_text)
        return self._label