from __future__ import annotations

# Standard library imports
from typing import Generic, Optional, TypeVar, Callable, Any, Mapping, Literal
from logging import Logger

# BAB imports
from nexpy import XSetProtocol, Hook
from nexpy.x_objects.single_value_like.protocols import XSingleValueProtocol
from nexpy.x_objects.set_like.protocols import XSelectionOptionsProtocol

# Local imports
from ..util.base_complex_hook_controller import BaseComplexHookController
from ..controlled_widgets.controlled_combobox import ControlledComboBox
from ..controlled_widgets.controlled_qlabel import ControlledQLabel
from ..util.resources import log_msg
from ..util.resources import combo_box_find_data

T = TypeVar("T")

class ListSelectionController(BaseComplexHookController[Literal["selected_option", "available_options"], Any, Any, Any, "ListSelectionController"], XSelectionOptionsProtocol[T], Generic[T]):
    """
    A controller for managing selection from a non-empty set of available options.
    
    This controller provides a combobox widget that allows users to select from a set of 
    options. Unlike SelectionOptionalOptionController, this controller always requires a
    selection - None is not allowed as a value. It can synchronize with observable values
    and hooks from the observables library, making it suitable for reactive applications.
    
    The controller maintains two synchronized values:
    - selected_option: The currently selected option (never None)
    - available_options: The set of options available for selection (must be non-empty)
    
    The controller ensures that the selected_option is always present in the available_options
    set. If the selected option is removed from available options, an error will occur.
    
    Parameters
    ----------
    selected_option : T | Hook[T] | XSingleValueProtocol[T, Hook[T]] | XSelectionOptionsProtocol[T]
        The initial selected option or an observable/hook to sync with. Can be:
        - A direct value (not None)
        - A Hook object for bidirectional synchronization
        - An XSingleValueProtocol for synchronization
        - An XSelectionOptionsProtocol that provides both selected and available options
    available_options : frozenset[T] | Hook[frozenset[T]] | XSetProtocol[T] | None
        The initial set of available options or an observable/hook to sync with. Can be:
        - A direct set value (must be non-empty)
        - A Hook object for bidirectional synchronization
        - An XSetProtocol for synchronization
        - None only if selected_option is XSelectionOptionsProtocol
    formatter : Callable[[T], str], optional
        Function to convert option values to display strings. Defaults to str().
    parent_of_widgets : Optional[QWidget], optional
        The parent widget for the created UI widgets. Defaults to None.
    logger : Optional[Logger], optional
        Logger instance for debugging. Defaults to None.
    
    Raises
    ------
    ValueError
        If available_options is provided when selected_option is XSelectionOptionsProtocol.
    ValueError
        If available_options has an invalid type.
    ValueError
        If selected_option is not in available_options.
    ValueError
        If available_options is empty.
    
    Attributes
    ----------
    selected_option : T
        Property to get/set the currently selected option.
    available_options : frozenset[T]
        Property to get/set the available options.
    selected_option_hook : OwnedHook[T]
        Hook for the selected option that can be connected to observables.
    available_options_hook : OwnedHook[frozenset[T]]
        Hook for the available options that can be connected to observables.
    formatter : Callable[[T], str]
        Property to get/set the formatter function.
    widget_combobox : ControlledComboBox
        The combobox widget for user selection.
    widget_label : ControlledQLabel
        A label widget showing the current selection (created on first access).
    
    Examples
    --------
    Basic usage with static values:
    
    >>> controller = SelectionOptionController(
    ...     selected_option="apple",
    ...     available_options={"apple", "banana", "orange"}
    ... )
    >>> controller.selected_option
    'apple'
    >>> controller.selected_option = "banana"
    
    With observables for reactive programming:
    
    >>> from nexpy import XSetSingleSelect
    >>> observable = XSetSingleSelect(
    ...     selected_option="red",
    ...     available_options={"red", "green", "blue"}
    ... )
    >>> controller = SelectionOptionController(observable)
    >>> # Changes to controller.selected_option automatically sync with observable
    
    Custom formatting:
    
    >>> controller = SelectionOptionController(
    ...     selected_option=1,
    ...     available_options={1, 2, 3},
    ...     formatter=lambda x: f"Option {x}"
    ... )
    
    Notes
    -----
    - Options in the dropdown are sorted by their formatted text
    - The controller validates that selected_option is always in available_options
    - available_options must never be empty
    - Unlike SelectionOptionalOptionController, None is not a valid selection
    """

    def __init__(
        self,
        selected_option: T | Hook[T] | XSingleValueProtocol[T, Hook[T]] | XSelectionOptionsProtocol[T],
        available_options: frozenset[T] | Hook[frozenset[T]] | XSetProtocol[T] | None,
        *,
        formatter: Callable[[T], str] = lambda item: str(item),
        debounce_ms: Optional[int] = None,
        logger: Optional[Logger] = None,
    ) -> None:

        log_msg(self, "__init__", logger, f"Starting initialization with selected_option={selected_option}, available_options={available_options}")
        
        self._formatter = formatter
        log_msg(self, "__init__", logger, f"Formatter set: {formatter}")

        if isinstance(selected_option, XSelectionOptionsProtocol):
            log_msg(self, "__init__", logger, "selected_option is XSelectionOptionsProtocol")
            if available_options is not None:
                raise ValueError("available_options is not allowed when selected_option is an XSelectionOptionsProtocol")

            initial_selected_option: T = selected_option.selected_option # type: ignore
            hook_selected_option: Optional[Hook[T]] = selected_option.selected_option_hook # type: ignore
            initial_available_options: frozenset[T] = selected_option.available_options # type: ignore
            hook_available_options: Optional[Hook[frozenset[T]]] = selected_option.available_options_hook # type: ignore
            
            log_msg(self, "__init__", logger, f"From XSelectionOptionsProtocol: initial_selected_option={initial_selected_option}, initial_available_options={initial_available_options}")

        else:
            log_msg(self, "__init__", logger, "selected_option is not XSelectionOptionsProtocol, processing manually")
            if isinstance(selected_option, Hook):
                # It's a hook - get initial value
                log_msg(self, "__init__", logger, "selected_option is Hook")
                initial_selected_option: T = selected_option.value # type: ignore
                hook_selected_option: Optional[Hook[T]] = selected_option # type: ignore
                log_msg(self, "__init__", logger, f"From Hook: initial_selected_option={initial_selected_option}")

            elif isinstance(selected_option, XSingleValueProtocol):
                # It's an observable - get initial value
                log_msg(self, "__init__", logger, "selected_option is XSingleValueProtocol")
                initial_selected_option: T = selected_option.value # type: ignore
                hook_selected_option: Optional[Hook[T]] = selected_option.hook # type: ignore
                log_msg(self, "__init__", logger, f"From XSingleValueProtocol: initial_selected_option={initial_selected_option}")

            else:
                # It's a direct value
                log_msg(self, "__init__", logger, "selected_option is direct value")
                initial_selected_option = selected_option
                hook_selected_option = None
                log_msg(self, "__init__", logger, f"Direct value: initial_selected_option={initial_selected_option}")
            
            if isinstance(available_options, (set, frozenset)):
                # It's a direct value
                log_msg(self, "__init__", logger, "available_options is direct set or frozenset")
                initial_available_options = frozenset(available_options) if not isinstance(available_options, frozenset) else available_options # type: ignore
                hook_available_options = None
                log_msg(self, "__init__", logger, f"Direct set/frozenset: initial_available_options={initial_available_options}")

            elif isinstance(available_options, Hook):
                # It's a hook - get initial value
                log_msg(self, "__init__", logger, "available_options is Hook")
                initial_available_options = available_options.value # type: ignore
                hook_available_options = available_options
                log_msg(self, "__init__", logger, f"From Hook: initial_available_options={initial_available_options}")

            elif isinstance(available_options, XSetProtocol):
                # It's an observable - get initial value
                log_msg(self, "__init__", logger, "available_options is XSetProtocol")
                initial_available_options = available_options.value
                hook_available_options = available_options.value_hook
                log_msg(self, "__init__", logger, f"From XSetProtocol: initial_available_options={initial_available_options}")

            else:
                log_msg(self, "__init__", logger, f"ERROR: Invalid available_options type: {type(available_options)}")
                raise ValueError(f"Invalid available_options: {available_options}")
        
        log_msg(self, "__init__", logger, f"Final values: initial_selected_option={initial_selected_option}, initial_available_options={initial_available_options}")
        
        def verification_method(x: Mapping[Literal["selected_option", "available_options"], Any]) -> tuple[bool, str]:
            log_msg(self, "verification_method", logger, f"Verifying: {x}")
            # Handle partial updates by getting current values for missing keys

            if "selected_option" in x:
                selected_option: T = x["selected_option"]
                log_msg(self, "verification_method", logger, f"selected_option from input: {selected_option}")
            else:
                selected_option = self.get_value_of_hook("selected_option") #type: ignore
                log_msg(self, "verification_method", logger, f"selected_option from current: {selected_option}")

            if "available_options" in x:
                available_options: frozenset[T] = x["available_options"]
                log_msg(self, "verification_method", logger, f"available_options from input: {available_options}")
            else:
                available_options = self.get_value_of_hook("available_options") #type: ignore
                log_msg(self, "verification_method", logger, f"available_options from current: {available_options}")

            if not selected_option in available_options:
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

        if new_option is None:
            log_msg(self, "_on_combobox_index_changed", self._logger, "New option is None, using current value")
            new_option = self.get_value_of_hook("selected_option") # type: ignore
            log_msg(self, "_on_combobox_index_changed", self._logger, f"Current value: {new_option}")

        dict_to_set["selected_option"] = new_option
        dict_to_set["available_options"] = self.get_value_of_hook("available_options")
        log_msg(self, "_on_combobox_index_changed", self._logger, f"Dict to set: {dict_to_set}")

        log_msg(self, "_on_combobox_index_changed", self._logger, "Updating widgets and component values")
        self.submit_values(dict_to_set)
        
        log_msg(self, "_on_combobox_index_changed", self._logger, "Combo box change handling completed")

    def _invalidate_widgets_impl(self) -> None:
        """Update the widgets from the component values."""

        component_values: dict[Literal["selected_option", "available_options"], Any] = self.get_dict_of_values()

        log_msg(self, "_invalidate_widgets", self._logger, f"Filling widgets with: {component_values}")

        selected_option: T = component_values["selected_option"]
        available_options: frozenset[T] = component_values["available_options"]
        log_msg(self, "_invalidate_widgets", self._logger, f"selected_option: {selected_option}, available_options: {available_options}")
        
        log_msg(self, "_invalidate_widgets", self._logger, "Starting widget update")
        
        self._combobox.clear()
        log_msg(self, "_invalidate_widgets", self._logger, "Cleared combo box")
        
        sorted_options = sorted(available_options, key=self._formatter)
        log_msg(self, "_invalidate_widgets", self._logger, f"Sorted options: {sorted_options}")
        
        for option in sorted_options:
            formatted_text = self._formatter(option)
            log_msg(self, "_invalidate_widgets", self._logger, f"Adding item: '{formatted_text}' with data: {option}")
            self._combobox.addItem(formatted_text, userData=option) # type: ignore
        
        current_index = combo_box_find_data(self._combobox, selected_option)
        log_msg(self, "_invalidate_widgets", self._logger, f"Setting current index to: {current_index} for selected_option: {selected_option}")
        self._combobox.setCurrentIndex(current_index)

        if hasattr(self, "_label"):
            self._label.setText(self._formatter(selected_option))
        
        log_msg(self, "_invalidate_widgets", self._logger, "Widget update completed")
        
    ###########################################################################
    # Public API
    ###########################################################################

    @property
    def selected_option(self) -> T:
        """Get the currently selected option."""
        value: T = self.get_value_of_hook("selected_option") # type: ignore
        log_msg(self, "selected_option.getter", self._logger, f"Getting selected_option: {value}")
        return value
    
    @selected_option.setter
    def selected_option(self, selected_option: T) -> None:
        """Set the selected option."""
        log_msg(self, "selected_option.setter", self._logger, f"Setting selected_option to: {selected_option}")
        self.submit_values({"selected_option": selected_option})

    def change_selected_option(self, selected_option: T) -> None:
        """Set the selected option."""
        log_msg(self, "change_selected_option", self._logger, f"Changing selected_option to: {selected_option}")
        self.submit_values({"selected_option": selected_option})

    @property
    def available_options(self) -> frozenset[T]:
        """Get the available options."""
        value: frozenset[T] = self.get_value_of_hook("available_options") # type: ignore
        log_msg(self, "available_options.getter", self._logger, f"Getting available_options: {value}")
        return value
    
    @available_options.setter
    def available_options(self, options: frozenset[T]) -> None:
        """Set the available options."""
        log_msg(self, "available_options.setter", self._logger, f"Setting available_options to: {options}")
        self.submit_values({"available_options": options})

    def change_available_options(self, available_options: frozenset[T]) -> None:
        """Set the available options."""
        log_msg(self, "change_available_options", self._logger, f"Changing available_options to: {available_options}")
        self.submit_values({"available_options": available_options})
    
    @property
    def selected_option_hook(self) -> Hook[T]:
        """Get the hook for the selected option."""
        hook = self.get_hook("selected_option") # type: ignore
        log_msg(self, "selected_option_hook.getter", self._logger, f"Getting selected_option_hook: {hook}")
        return hook
    
    @property
    def available_options_hook(self) -> Hook[frozenset[T]]:
        """Get the hook for the available options."""
        hook = self.get_hook("available_options") # type: ignore
        log_msg(self, "available_options_hook.getter", self._logger, f"Getting available_options_hook: {hook}")
        return hook

    def change_selected_option_and_available_options(self, selected_option: T, available_options: frozenset[T]) -> None:
        """Set the selected option and available options at once."""
        log_msg(self, "change_selected_option_and_available_options", self._logger, f"Changing both: selected_option={selected_option}, available_options={available_options}")
        self.submit_values({"selected_option": selected_option, "available_options": available_options})

    def add_option(self, option: T) -> None:
        """Add a new option to the available options."""
        log_msg(self, "add_option", self._logger, f"Adding option: {option}")
        current_options = self.available_options.copy()
        current_options.add(option)
        self.available_options = current_options

    def remove_option(self, option: T) -> None:
        """Remove an option from the available options."""
        log_msg(self, "remove_option", self._logger, f"Removing option: {option}")
        current_options = self.available_options.copy()
        current_options.discard(option)
        self.available_options = current_options

    @property
    def formatter(self) -> Callable[[T], str]:
        """Get the formatter function."""
        return self._formatter

    @formatter.setter
    def formatter(self, formatter: Callable[[T], str]) -> None:
        """Set the formatter function."""
        log_msg(self, "formatter.setter", self._logger, f"Setting formatter to: {formatter}")
        self._formatter = formatter
        self.invalidate_widgets()

    def change_formatter(self, formatter: Callable[[T], str]) -> None:
        """Set the formatter function."""
        log_msg(self, "change_formatter", self._logger, f"Changing formatter to: {formatter}")
        self._formatter = formatter
        self.invalidate_widgets()

    @property
    def widget_combobox(self) -> ControlledComboBox:
        """Get the combobox widget."""
        return self._combobox

    @property
    def widget_label(self) -> ControlledQLabel:
        """Get the label widget."""
        if not hasattr(self, "_label"):
            self._label = ControlledQLabel(self)
            self._label.setText(self._formatter(self.selected_option))
        return self._label