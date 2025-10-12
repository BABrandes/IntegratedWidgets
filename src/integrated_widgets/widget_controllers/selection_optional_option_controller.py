from __future__ import annotations

# Standard library imports
from typing import Generic, Optional, TypeVar, Callable, Any, Mapping, Literal
from logging import Logger
from PySide6.QtWidgets import QWidget, QFrame, QVBoxLayout
from enum import Enum

# BAB imports
from observables import ObservableSingleValueLike, HookLike, ObservableSetLike, ObservableOptionalSelectionOptionLike, InitialSyncMode, OwnedHookLike

# Local imports
from ..util.base_complex_hook_controller import BaseComplexHookController
from ..controlled_widgets.controlled_combobox import ControlledComboBox
from ..controlled_widgets.controlled_label import ControlledLabel
from ..util.resources import log_msg, log_bool

T = TypeVar("T")

class OptionalHandlingMode(Enum):
    """
    The mode for handling the optional selection option.
    
    Attributes
    ----------
    NONE_IS_USER_SELECTABLE : str
        None appears as a selectable option in the dropdown (default behavior).
    NONE_DISABLES_WIDGETS : str
        When None is selected, associated widgets are disabled (not yet implemented).
    """
    NONE_IS_USER_SELECTABLE = "none_is_user_selectable"
    NONE_DISABLES_WIDGETS = "none_disables_widgets"

class SelectionOptionalOptionController(BaseComplexHookController[Literal["selected_option", "available_options"], Any, Any, Any, "SelectionOptionalOptionController"], ObservableOptionalSelectionOptionLike[T], Generic[T]):
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
    selected_option : Optional[T] | HookLike[Optional[T]] | ObservableSingleValueLike[Optional[T]] | ObservableOptionalSelectionOptionLike[T]
        The initial selected option or an observable/hook to sync with. Can be:
        - A direct value (including None)
        - A HookLike object for bidirectional synchronization
        - An ObservableSingleValueLike for one-way or two-way synchronization
        - An ObservableOptionalSelectionOptionLike that provides both selected and available options
    available_options : set[T] | HookLike[set[T]] | ObservableSetLike[T] | None
        The initial set of available options or an observable/hook to sync with. Can be:
        - A direct set value (can be empty set())
        - A HookLike object for bidirectional synchronization
        - An ObservableSetLike for synchronization
        - None only if selected_option is ObservableOptionalSelectionOptionLike
    formatter : Callable[[T], str], optional
        Function to convert option values to display strings. Defaults to str().
    none_option_text : str, optional
        The text to display for the None option in the combobox. Defaults to "-".
    parent_of_widgets : Optional[QWidget], optional
        The parent widget for the created UI widgets. Defaults to None.
    logger : Optional[Logger], optional
        Logger instance for debugging. Defaults to None.
    
    Raises
    ------
    ValueError
        If available_options is provided when selected_option is ObservableOptionalSelectionOptionLike.
    ValueError
        If available_options has an invalid type.
    
    Attributes
    ----------
    selected_option : Optional[T]
        Property to get/set the currently selected option.
    available_options : set[T]
        Property to get/set the available options.
    selected_option_hook : OwnedHookLike[Optional[T]]
        Hook for the selected option that can be connected to observables.
    available_options_hook : OwnedHookLike[set[T]]
        Hook for the available options that can be connected to observables.
    formatter : Callable[[T], str]
        Property to get/set the formatter function.
    none_option_text : str
        Property to get/set the text displayed for the None option.
    widget_combobox : ControlledComboBox
        The combobox widget for user selection.
    widget_label : ControlledLabel
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
    ...     available_options=set()  # Valid when selected_option is None
    ... )
    
    With observables for reactive programming:
    
    >>> from observables import ObservableOptionalSelectionOption
    >>> observable = ObservableOptionalSelectionOption(
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
        selected_option: Optional[T] | HookLike[Optional[T]] | ObservableSingleValueLike[Optional[T]] | ObservableOptionalSelectionOptionLike[T],
        available_options: set[T] | HookLike[set[T]] | ObservableSetLike[T] | None,
        *,
        formatter: Callable[[T], str] = lambda item: str(item),
        none_option_text: str = "-",
        parent_of_widgets: Optional[QWidget] = None,
        logger: Optional[Logger] = None,
    ) -> None:

        log_msg(self, "__init__", logger, f"Starting initialization with selected_option={selected_option}, available_options={available_options}, none_option_label='{none_option_text}'")
        
        self._formatter = formatter
        self._none_option_text = none_option_text
        log_msg(self, "__init__", logger, f"Formatter set: {formatter}, none_option_label: '{none_option_text}'")

        if isinstance(selected_option, ObservableOptionalSelectionOptionLike):
            log_msg(self, "__init__", logger, "selected_option is ObservableOptionalSelectionOptionLike")
            if available_options is not None:
                raise ValueError("available_options is not allowed when selected_option is an ObservableOptionalSelectionOptionLike")

            initial_selected_option: Optional[T] = selected_option.selected_option
            hook_selected_option: Optional[HookLike[Optional[T]]] = selected_option.selected_option_hook
            initial_available_options: set[T] = selected_option.available_options
            hook_available_options: Optional[HookLike[set[T]]] = selected_option.available_options_hook
            
            log_msg(self, "__init__", logger, f"From ObservableOptionalSelectionOptionLike: initial_selected_option={initial_selected_option}, initial_available_options={initial_available_options}")

        else:
            log_msg(self, "__init__", logger, "selected_option is not ObservableOptionalSelectionOptionLike, processing manually")

            if selected_option is None:
                log_msg(self, "__init__", logger, "selected_option is None")
                initial_selected_option = None
                hook_selected_option = None

            elif isinstance(selected_option, HookLike):
                # It's a hook - get initial value
                log_msg(self, "__init__", logger, "selected_option is HookLike")
                initial_selected_option = selected_option.value # type: ignore
                hook_selected_option = selected_option
                log_msg(self, "__init__", logger, f"From HookLike: initial_selected_option={initial_selected_option}")

            elif isinstance(selected_option, ObservableSingleValueLike):
                # It's an observable - get initial value
                log_msg(self, "__init__", logger, "selected_option is ObservableSingleValueLike")
                initial_selected_option = selected_option.value
                hook_selected_option = selected_option.hook
                log_msg(self, "__init__", logger, f"From ObservableSingleValueLike: initial_selected_option={initial_selected_option}")

            else:
                # It's a direct value
                log_msg(self, "__init__", logger, "selected_option is direct value")
                initial_selected_option = selected_option
                hook_selected_option = None
                log_msg(self, "__init__", logger, f"Direct value: initial_selected_option={initial_selected_option}")
            
            if isinstance(available_options, set):
                # It's a direct value
                log_msg(self, "__init__", logger, "available_options is direct set")
                initial_available_options = available_options
                hook_available_options = None
                log_msg(self, "__init__", logger, f"Direct set: initial_available_options={initial_available_options}")

            elif isinstance(available_options, HookLike):
                # It's a hook - get initial value
                log_msg(self, "__init__", logger, "available_options is HookLike")
                initial_available_options = available_options.value # type: ignore
                hook_available_options = available_options
                log_msg(self, "__init__", logger, f"From HookLike: initial_available_options={initial_available_options}")

            elif isinstance(available_options, ObservableSetLike):
                # It's an observable - get initial value
                log_msg(self, "__init__", logger, "available_options is ObservableSetLike")
                initial_available_options = available_options.value
                hook_available_options = available_options.value_hook
                log_msg(self, "__init__", logger, f"From ObservableSetLike: initial_available_options={initial_available_options}")

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
                selected_option = self.get_value_of_hook("selected_option")
                log_msg(self, "verification_method", logger, f"selected_option from current: {selected_option}")

            if "available_options" in x:
                available_options: set[T] = x["available_options"]
                log_msg(self, "verification_method", logger, f"available_options from input: {available_options}")
            else:
                available_options = self.get_value_of_hook("available_options")
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
            parent_of_widgets=parent_of_widgets,
            logger=logger
        )
        
        log_msg(self, "__init__", logger, "Super().__init__ completed, attaching hooks")
        
        if hook_available_options is not None:
            log_msg(self, "__init__", logger, f"Attaching available_options hook: {hook_available_options}")
            self.connect_hook(hook_available_options, "available_options", initial_sync_mode=InitialSyncMode.USE_TARGET_VALUE)
        if hook_selected_option is not None:
            log_msg(self, "__init__", logger, f"Attaching selected_option hook: {hook_selected_option}")
            self.connect_hook(hook_selected_option,"selected_option", initial_sync_mode=InitialSyncMode.USE_TARGET_VALUE)
        
        log_msg(self, "__init__", logger, "Initialization completed successfully")

    ###########################################################################
    # Widget methods
    ###########################################################################

    def _initialize_widgets(self) -> None:
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
        self._combobox.currentIndexChanged.connect(lambda _i: self._on_combobox_index_changed())
        log_msg(self, "initialize_widgets", self._logger, "Connected currentIndexChanged signal")

        log_msg(self, "initialize_widgets", self._logger, "Widget initialization completed")

    def _on_combobox_index_changed(self) -> None:
        """
        Handle when the user selects a different option from the dropdown menu.
        
        This internal callback is triggered whenever the combobox index changes. It:
        1. Checks if signals are currently blocked (to prevent feedback loops)
        2. Retrieves the selected option data from the combobox
        3. Submits the new value through the controller's validation system
        
        The method correctly handles None as a valid user selection when the None
        option is chosen from the dropdown.
        
        Notes
        -----
        This method should not be called directly by users of the controller.
        """
        log_msg(self, "_on_combobox_index_changed", self._logger, "Combo box index changed")

        if self.is_blocking_signals:
            log_msg(self, "_on_combobox_index_changed", self._logger, "Signals are blocked, returning")
            return
        
        ################# Processing user input #################
        log_msg(self, "_on_combobox_index_changed", self._logger, "Processing user input")

        dict_to_set: dict[Literal["selected_option", "available_options"], Any] = {}

        # Get the new option from the combo box
        new_option: Optional[T] = self._combobox.currentData()
        log_msg(self, "_on_combobox_index_changed", self._logger, f"New option from combo box: {new_option}")

        # Note: new_option can be None if the user selected the "None" option (first item in dropdown)
        # We should preserve this None value rather than overriding it with the current value

        dict_to_set["selected_option"] = new_option
        dict_to_set["available_options"] = self.get_value_of_hook("available_options")
        log_msg(self, "_on_combobox_index_changed", self._logger, f"Dict to set: {dict_to_set}")

        log_msg(self, "_on_combobox_index_changed", self._logger, "Updating widgets and component values")
        self._submit_values_on_widget_changed(dict_to_set)
        
        log_msg(self, "_on_combobox_index_changed", self._logger, "Combo box change handling completed")

    def _invalidate_widgets_impl(self) -> None:
        """
        Update the widgets from the component values.
        
        This internal method synchronizes the UI widgets with the current state of
        the controller's values. It:
        1. Clears the combobox
        2. Adds the None option with the configured text
        3. Adds all available options (sorted by formatted text)
        4. Sets the combobox to display the currently selected option
        5. Updates the label widget if it exists
        
        The method is called automatically whenever the controller's state changes,
        whether from user interaction, programmatic changes, or synchronized observables.
        
        Notes
        -----
        This method should not be called directly. Use `invalidate_widgets()` instead
        if you need to manually trigger a widget update.
        """

        component_values: dict[Literal["selected_option", "available_options"], Any] = self.get_dict_of_values()

        log_msg(self, "_invalidate_widgets", self._logger, f"Filling widgets with: {component_values}")

        selected_option: Optional[T] = component_values["selected_option"]
        available_options: set[T] = component_values["available_options"]
        log_msg(self, "_invalidate_widgets", self._logger, f"selected_option: {selected_option}, available_options: {available_options}")
        
        log_msg(self, "_invalidate_widgets", self._logger, "Starting widget update")
        
        self._combobox.clear()
        log_msg(self, "_invalidate_widgets", self._logger, "Cleared combo box")
        
        # Add None option first
        log_msg(self, "_invalidate_widgets", self._logger, f"Adding None option with label: '{self._none_option_text}'")
        self._combobox.addItem(self._none_option_text, userData=None)
        
        sorted_options = sorted(available_options, key=self._formatter)
        log_msg(self, "_invalidate_widgets", self._logger, f"Sorted options: {sorted_options}")
        
        for option in sorted_options:
            formatted_text = self._formatter(option)
            log_msg(self, "_invalidate_widgets", self._logger, f"Adding item: '{formatted_text}' with data: {option}")
            self._combobox.addItem(formatted_text, userData=option)
        
        current_index = self._combobox.findData(selected_option)
        log_msg(self, "_invalidate_widgets", self._logger, f"Setting current index to: {current_index} for selected_option: {selected_option}")
        self._combobox.setCurrentIndex(current_index)

        if hasattr(self, "_label"):
            if self.selected_option is not None:
                self._label.setText(self._formatter(self.selected_option))
            else:
                self._label.setText(self._none_option_text)
        
        log_msg(self, "_invalidate_widgets", self._logger, "Widget update completed")

    ###########################################################################
    # Public API
    ###########################################################################

    @property
    def selected_option(self) -> Optional[T]:
        """
        Get the currently selected option.
        
        Returns
        -------
        Optional[T]
            The currently selected option, or None if no option is selected.
        """
        value = self.get_value_of_hook("selected_option")
        log_msg(self, "selected_option.getter", self._logger, f"Getting selected_option: {value}")
        return value
    
    @selected_option.setter
    def selected_option(self, selected_option: Optional[T]) -> None:
        """
        Set the selected option.
        
        Parameters
        ----------
        selected_option : Optional[T]
            The option to select, or None to clear the selection.
        
        Raises
        ------
        ValueError
            If the selected_option is not None and is not in available_options.
        """
        log_msg(self, "selected_option.setter", self._logger, f"Setting selected_option to: {selected_option}")
        self.submit_values({"selected_option": selected_option})

    def change_selected_option(self, selected_option: Optional[T]) -> None:
        """
        Set the selected option (alternative method name).
        
        This method is functionally identical to using the selected_option property setter.
        
        Parameters
        ----------
        selected_option : Optional[T]
            The option to select, or None to clear the selection.
        
        Raises
        ------
        ValueError
            If the selected_option is not None and is not in available_options.
        """
        log_msg(self, "change_selected_option", self._logger, f"Changing selected_option to: {selected_option}")
        self.submit_values({"selected_option": selected_option})
    
    @property
    def available_options(self) -> set[T]:
        """
        Get the available options.
        
        Returns
        -------
        set[T]
            The set of currently available options. Can be an empty set if no
            options are available (in which case selected_option must be None).
        """
        value = self.get_value_of_hook("available_options")
        log_msg(self, "available_options.getter", self._logger, f"Getting available_options: {value}")
        return value
    
    @available_options.setter
    def available_options(self, options: set[T]) -> None:
        """
        Set the available options.
        
        Parameters
        ----------
        options : set[T]
            The new set of available options. Can be an empty set (set()) if no
            options should be available, but in this case selected_option will be
            validated and must be None.
        
        Raises
        ------
        ValueError
            If the currently selected_option is not None and is not in the new options set.
        """
        log_msg(self, "available_options.setter", self._logger, f"Setting available_options to: {options}")
        self.submit_values({"available_options": options})

    def change_available_options(self, available_options: set[T]) -> None:
        """
        Set the available options (alternative method name).
        
        This method is functionally identical to using the available_options property setter.
        
        Parameters
        ----------
        available_options : set[T]
            The new set of available options. Can be an empty set (set()).
        
        Raises
        ------
        ValueError
            If the currently selected_option is not None and is not in the new options set.
        """
        log_msg(self, "change_available_options", self._logger, f"Changing available_options to: {available_options}")
        self.submit_values({"available_options": available_options})
    
    @property
    def selected_option_hook(self) -> OwnedHookLike[Optional[T]]:
        """
        Get the hook for the selected option.
        
        The hook can be connected to observables for bidirectional synchronization.
        
        Returns
        -------
        OwnedHookLike[Optional[T]]
            The hook object for the selected_option value.
        """
        hook = self.get_hook("selected_option")
        log_msg(self, "selected_option_hook.getter", self._logger, f"Getting selected_option_hook: {hook}")
        return hook
    
    @property
    def available_options_hook(self) -> OwnedHookLike[set[T]]:
        """
        Get the hook for the available options.
        
        The hook can be connected to observables for bidirectional synchronization.
        
        Returns
        -------
        OwnedHookLike[set[T]]
            The hook object for the available_options value.
        """
        hook = self.get_hook("available_options")
        log_msg(self, "available_options_hook.getter", self._logger, f"Getting available_options_hook: {hook}")
        return hook

    def change_selected_option_and_available_options(self, selected_option: Optional[T], available_options: set[T]) -> None:
        """
        Set the selected option and available options atomically.
        
        This method allows you to change both values in a single operation, which
        is useful when you need to ensure consistency or avoid intermediate validation
        failures.
        
        Parameters
        ----------
        selected_option : Optional[T]
            The new selected option, or None to clear the selection.
        available_options : set[T]
            The new set of available options.
        
        Raises
        ------
        ValueError
            If selected_option is not None and is not in available_options.
        
        Examples
        --------
        >>> controller.change_selected_option_and_available_options(
        ...     selected_option="orange",
        ...     available_options={"orange", "grape", "melon"}
        ... )
        """
        log_msg(self, "change_selected_option_and_available_options", self._logger, f"Changing both: selected_option={selected_option}, available_options={available_options}")
        self.submit_values({"selected_option": selected_option, "available_options": available_options})

    def add_option(self, option: T) -> None:
        """
        Add a new option to the available options.
        
        If the option already exists in available_options, this has no effect.
        
        Parameters
        ----------
        option : T
            The option to add to the available options set.
        
        Examples
        --------
        >>> controller.add_option("kiwi")
        >>> controller.add_option("kiwi")  # No effect, already exists
        """
        log_msg(self, "add_option", self._logger, f"Adding option: {option}")
        current_options = self.available_options.copy()
        current_options.add(option)
        self.available_options = current_options

    def remove_option(self, option: T) -> None:
        """
        Remove an option from the available options.
        
        If the option doesn't exist in available_options, this has no effect.
        
        Parameters
        ----------
        option : T
            The option to remove from the available options set.
        
        Raises
        ------
        ValueError
            If the option being removed is currently the selected_option (not None).
            You must either clear the selection or select a different option first.
        
        Examples
        --------
        >>> controller.remove_option("banana")  # OK if not currently selected
        >>> controller.selected_option = "apple"
        >>> controller.remove_option("apple")  # Raises ValueError
        """
        log_msg(self, "remove_option", self._logger, f"Removing option: {option}")
        current_options = self.available_options.copy()
        current_options.discard(option)
        self.available_options = current_options

    def clear_selection(self) -> None:
        """
        Clear the current selection (set to None).
        
        This is a convenience method equivalent to setting selected_option = None.
        
        Examples
        --------
        >>> controller.clear_selection()
        >>> assert controller.selected_option is None
        """
        log_msg(self, "clear_selection", self._logger, "Clearing selection (setting to None)")
        self.selected_option = None

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
    def widget_label(self) -> ControlledLabel:
        """
        Get a label widget that displays the current selection.
        
        This label is created on first access and automatically updates to show
        the formatted text of the current selection (or the none_option_text if
        the selection is None).
        
        Returns
        -------
        ControlledLabel
            A label widget showing the current selected option.
        
        Notes
        -----
        The label is created lazily on first access and is not part of the default
        widget set returned by `all_widgets_as_frame()`.
        """
        if not hasattr(self, "_label"):
            self._label = ControlledLabel(self)
            if self.selected_option is not None:
                self._label.setText(self._formatter(self.selected_option))
            else:
                self._label.setText(self._none_option_text)
        return self._label
    
    ###########################################################################
    # Debugging
    ###########################################################################

    def all_widgets_as_frame(self) -> QFrame:
        """
        Return all primary widgets organized in a QFrame for easy layout.
        
        This is a convenience method for adding the controller's widgets to a UI.
        It creates a vertical layout containing the combobox widget.
        
        Returns
        -------
        QFrame
            A frame containing the controller's primary widgets in a vertical layout.
        
        Notes
        -----
        This method only includes the combobox widget, not the label widget
        (which is accessed via `widget_label` and is created on demand).
        
        Examples
        --------
        >>> frame = controller.all_widgets_as_frame()
        >>> main_layout.addWidget(frame)
        """
        log_msg(self, "all_widgets_as_frame", self._logger, "Creating demo frame")
        frame = QFrame()
        layout = QVBoxLayout()
        frame.setLayout(layout)
        layout.addWidget(self.widget_combobox)
        log_msg(self, "all_widgets_as_frame", self._logger, "Demo frame created successfully")
        return frame