from __future__ import annotations

# Standard library imports
from typing import Generic, Optional, TypeVar, Callable, Any, Mapping, Literal, AbstractSet
from logging import Logger

# BAB imports
from nexpy import XSetProtocol, Hook
from nexpy.x_objects.single_value_like.protocols import XSingleValueProtocol
from nexpy.x_objects.set_like.protocols import XSelectionOptionsProtocol

# Local imports
from .core.base_complex_hook_controller import BaseComplexHookController
from ..controlled_widgets.controlled_combobox import ControlledComboBox
from ..controlled_widgets.controlled_qlabel import ControlledQLabel
from ..util.resources import log_msg, combo_box_find_data

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
    available_options : AbstractSet[T] | Hook[AbstractSet[T]] | XSetProtocol[T] | None
        The initial set of available options or an observable/hook to sync with. Can be:
        - A direct set value (must be non-empty)
        - A Hook object for bidirectional synchronization
        - An XSetProtocol for synchronization
        - None only if selected_option is XSelectionOptionsProtocol
    formatter : Callable[[T], str], optional
        Function to convert option values to display strings. Defaults to str().
    debounce_ms : Optional[int], optional
        Debounce delay in milliseconds for value updates. Defaults to None.
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
    formatter : Callable[[T], str]
        Property to get/set the formatter function.
    widget_combobox : ControlledComboBox
        The combobox widget for user selection.
    widget_label : ControlledQLabel
        A label widget showing the current selection (created on first access).
    
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
        available_options: AbstractSet[T] | Hook[AbstractSet[T]] | XSetProtocol[T] | None,
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
            initial_available_options: AbstractSet[T] = selected_option.available_options # type: ignore
            hook_available_options: Optional[Hook[AbstractSet[T]]] = selected_option.available_options_hook # type: ignore
            
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
                selected_option: T = x["selected_option"]
                log_msg(self, "verification_method", logger, f"selected_option from input: {selected_option}")
            else:
                selected_option = self.get_value_of_hook("selected_option") #type: ignore
                log_msg(self, "verification_method", logger, f"selected_option from current: {selected_option}")

            if "available_options" in x:
                available_options: AbstractSet[T] = x["available_options"]
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
        
        This internal callback is triggered whenever the combobox index changes. It retrieves the selected option data from the combobox and submits the new value through the controller's validation system.
        
        Notes
        -----
        This method should not be called directly by users of the controller.
        """
        if self.is_blocking_signals:
            return

        new_option: T = self._combobox.currentData()
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

        selected_option: T = self.selected_option
        available_options: AbstractSet[T] = self.available_options
        self._combobox.clear()

        sorted_options: list[T] = sorted(available_options, key=self._formatter)
        for option in sorted_options:
            formatted_text: str = self._formatter(option)
            self._combobox.addItem(formatted_text, userData=option) # type: ignore
        
        current_index: int = combo_box_find_data(self._combobox, selected_option)
        self._combobox.setCurrentIndex(current_index)

        if hasattr(self, "_label"):
            self._label.setText(self._formatter(selected_option))
        
    ###########################################################################
    # Public API
    ###########################################################################

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