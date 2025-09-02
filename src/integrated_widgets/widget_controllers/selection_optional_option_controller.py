from __future__ import annotations

# Standard library imports
from typing import Generic, Optional, TypeVar, Callable, Any, Mapping, Literal
from logging import Logger
from PySide6.QtWidgets import QWidget, QFrame, QVBoxLayout

# BAB imports
from observables import ObservableSingleValueLike, HookLike, ObservableSetLike, ObservableOptionalSelectionOptionLike

# Local imports
from ..widget_controllers.base_controller import BaseWidgetController
from ..guarded_widgets.guarded_combobox import GuardedComboBox
from ..util.resources import log_msg, log_bool

T = TypeVar("T")

class SelectionOptionalOptionController(BaseWidgetController[Literal["selected_option", "available_options"], Any], ObservableOptionalSelectionOptionLike[T], Generic[T]):

    def __init__(
        self,
        selected_option: Optional[T] | HookLike[Optional[T]] | ObservableSingleValueLike[Optional[T]] | ObservableOptionalSelectionOptionLike[T],
        available_options: set[T] | HookLike[set[T]] | ObservableSetLike[T] | None,
        *,
        formatter: Callable[[T], str] = lambda item: str(item),
        none_option_label: str = "-",
        parent: Optional[QWidget] = None,
        logger: Optional[Logger] = None,
    ) -> None:

        log_msg(self, "__init__", logger, f"Starting initialization with selected_option={selected_option}, available_options={available_options}, none_option_label='{none_option_label}'")
        
        self._formatter = formatter
        self._none_option_label = none_option_label
        log_msg(self, "__init__", logger, f"Formatter set: {formatter}, none_option_label: '{none_option_label}'")

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
                initial_selected_option: Optional[T] = None
                hook_selected_option: Optional[HookLike[Optional[T]]] = None

            elif isinstance(selected_option, HookLike):
                # It's a hook - get initial value
                log_msg(self, "__init__", logger, "selected_option is HookLike")
                initial_selected_option: Optional[T] = selected_option.value # type: ignore
                hook_selected_option: Optional[HookLike[Optional[T]]] = selected_option
                log_msg(self, "__init__", logger, f"From HookLike: initial_selected_option={initial_selected_option}")

            elif isinstance(selected_option, ObservableSingleValueLike):
                # It's an observable - get initial value
                log_msg(self, "__init__", logger, "selected_option is ObservableSingleValueLike")
                initial_selected_option: Optional[T] = selected_option.single_value
                hook_selected_option: Optional[HookLike[Optional[T]]] = selected_option.single_value_hook
                log_msg(self, "__init__", logger, f"From ObservableSingleValueLike: initial_selected_option={initial_selected_option}")

            else:
                # It's a direct value
                log_msg(self, "__init__", logger, "selected_option is direct value")
                initial_selected_option: Optional[T] = selected_option
                hook_selected_option: Optional[HookLike[Optional[T]]] = None
                log_msg(self, "__init__", logger, f"Direct value: initial_selected_option={initial_selected_option}")
            
            if isinstance(available_options, set):
                # It's a direct value
                log_msg(self, "__init__", logger, "available_options is direct set")
                initial_available_options: set[T] = available_options
                hook_available_options: Optional[HookLike[set[T]]] = None
                log_msg(self, "__init__", logger, f"Direct set: initial_available_options={initial_available_options}")

            elif isinstance(available_options, HookLike):
                # It's a hook - get initial value
                log_msg(self, "__init__", logger, "available_options is HookLike")
                initial_available_options: set[T] = available_options.value # type: ignore
                hook_available_options: Optional[HookLike[set[T]]] = available_options
                log_msg(self, "__init__", logger, f"From HookLike: initial_available_options={initial_available_options}")

            elif isinstance(available_options, ObservableSetLike):
                # It's an observable - get initial value
                log_msg(self, "__init__", logger, "available_options is ObservableSetLike")
                initial_available_options: set[T] = available_options.set_value
                hook_available_options: Optional[HookLike[set[T]]] = available_options.set_value_hook
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
                selected_option: Optional[T] = self.get_value("selected_option")
                log_msg(self, "verification_method", logger, f"selected_option from current: {selected_option}")

            if "available_options" in x:
                available_options: set[T] = x["available_options"]
                log_msg(self, "verification_method", logger, f"available_options from input: {available_options}")
            else:
                available_options: set[T] = self.get_value("available_options")
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
            parent=parent,
            logger=logger
        )
        
        log_msg(self, "__init__", logger, "Super().__init__ completed, attaching hooks")
        
        if hook_available_options is not None:
            log_msg(self, "__init__", logger, f"Attaching available_options hook: {hook_available_options}")
            self.attach(hook_available_options, "available_options")
        if hook_selected_option is not None:
            log_msg(self, "__init__", logger, f"Attaching selected_option hook: {hook_selected_option}")
            self.attach(hook_selected_option,"selected_option")
        
        log_msg(self, "__init__", logger, "Initialization completed successfully")

    @property
    def can_be_disabled(self) -> bool:
        """Whether the controller can be disabled."""
        return True

    ###########################################################################
    # Widget methods
    ###########################################################################

    def _initialize_widgets(self) -> None:
        """
        Create and configure all the user interface widgets.
        
        """
        log_msg(self, "initialize_widgets", self._logger, "Starting widget initialization")

        self._combobox = GuardedComboBox(self, logger=self._logger)
        log_msg(self, "initialize_widgets", self._logger, f"Created GuardedComboBox: {self._combobox}")

        # Connect UI -> model
        self._combobox.currentIndexChanged.connect(lambda _i: self._on_combobox_index_changed())
        log_msg(self, "initialize_widgets", self._logger, "Connected currentIndexChanged signal")

        log_msg(self, "initialize_widgets", self._logger, "Widget initialization completed")

    def _disable_widgets(self) -> None:
        """
        Disable all widgets.
        """
        self._combobox.clear()
        self._combobox.setEnabled(False)

    def _enable_widgets(self, initial_component_values: dict[Literal["selected_option", "available_options"], Any]) -> None:
        """
        Enable all widgets.
        """
        self._combobox.setEnabled(True)

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
            new_option = self.get_value("selected_option")
            log_msg(self, "_on_combobox_index_changed", self._logger, f"Current value: {new_option}")

        dict_to_set["selected_option"] = new_option
        dict_to_set["available_options"] = self.get_value("available_options")
        log_msg(self, "_on_combobox_index_changed", self._logger, f"Dict to set: {dict_to_set}")

        if self._verification_method is not None:
            log_msg(self, "_on_combobox_index_changed", self._logger, "Running verification method")
            success, message = self._verification_method(dict_to_set)
            log_bool(self, "_on_combobox_index_changed", self._logger, success, message)
            if not success:
                log_msg(self, "_on_combobox_index_changed", self._logger, "Verification failed, reverting widgets")
                self.apply_component_values_to_widgets()
                return
        else:
            log_msg(self, "_on_combobox_index_changed", self._logger, "No verification method")

        log_msg(self, "_on_combobox_index_changed", self._logger, "Updating widgets and component values")
        self._update_component_values_and_widgets(dict_to_set)
        
        log_msg(self, "_on_combobox_index_changed", self._logger, "Combo box change handling completed")

    def _fill_widgets_from_component_values(self, component_values: dict[Literal["selected_option", "available_options"], Any]) -> None:
        """Update the widgets from the component values."""
        log_msg(self, "_fill_widgets_from_component_values", self._logger, f"Filling widgets with: {component_values}")

        selected_option: Optional[T] = component_values["selected_option"]
        available_options: set[T] = component_values["available_options"]
        log_msg(self, "_fill_widgets_from_component_values", self._logger, f"selected_option: {selected_option}, available_options: {available_options}")
        
        log_msg(self, "_fill_widgets_from_component_values", self._logger, "Starting widget update")
        
        self._combobox.clear()
        log_msg(self, "_fill_widgets_from_component_values", self._logger, "Cleared combo box")
        
        # Add None option first
        log_msg(self, "_fill_widgets_from_component_values", self._logger, f"Adding None option with label: '{self._none_option_label}'")
        self._combobox.addItem(self._none_option_label, userData=None)
        
        sorted_options = sorted(available_options, key=self._formatter)
        log_msg(self, "_fill_widgets_from_component_values", self._logger, f"Sorted options: {sorted_options}")
        
        for option in sorted_options:
            formatted_text = self._formatter(option)
            log_msg(self, "_fill_widgets_from_component_values", self._logger, f"Adding item: '{formatted_text}' with data: {option}")
            self._combobox.addItem(formatted_text, userData=option)
        
        current_index = self._combobox.findData(selected_option)
        log_msg(self, "_fill_widgets_from_component_values", self._logger, f"Setting current index to: {current_index} for selected_option: {selected_option}")
        self._combobox.setCurrentIndex(current_index)
        
        log_msg(self, "_fill_widgets_from_component_values", self._logger, "Widget update completed")

    ###########################################################################
    # Public API
    ###########################################################################

    @property
    def selected_option(self) -> Optional[T]:
        """Get the currently selected option."""
        value = self.get_value("selected_option")
        log_msg(self, "selected_option.getter", self._logger, f"Getting selected_option: {value}")
        return value
    
    @selected_option.setter
    def selected_option(self, value: Optional[T]) -> None:
        """Set the selected option."""
        log_msg(self, "selected_option.setter", self._logger, f"Setting selected_option to: {value}")
        self._update_component_values_and_widgets({"selected_option": value})

    def change_selected_option(self, value: Optional[T]) -> None:
        """Set the selected option."""
        log_msg(self, "change_selected_option", self._logger, f"Changing selected_option to: {value}")
        self._update_component_values_and_widgets({"selected_option": value})
    
    @property
    def available_options(self) -> set[T]:
        """Get the available options."""
        value = self.get_value("available_options")
        log_msg(self, "available_options.getter", self._logger, f"Getting available_options: {value}")
        return value
    
    @available_options.setter
    def available_options(self, options: set[T]) -> None:
        """Set the available options."""
        log_msg(self, "available_options.setter", self._logger, f"Setting available_options to: {options}")
        self._update_component_values_and_widgets({"available_options": options})

    def change_available_options(self, options: set[T]) -> None:
        """Set the available options."""
        log_msg(self, "change_available_options", self._logger, f"Changing available_options to: {options}")
        self._set_component_values({"available_options": options}, notify_binding_system=True)
        self.apply_component_values_to_widgets()
    
    @property
    def selected_option_hook(self) -> HookLike[Optional[T]]:
        """Get the hook for the selected option."""
        hook = self.get_hook("selected_option")
        log_msg(self, "selected_option_hook.getter", self._logger, f"Getting selected_option_hook: {hook}")
        return hook
    
    @property
    def available_options_hook(self) -> HookLike[set[T]]:
        """Get the hook for the available options."""
        hook = self.get_hook("available_options")
        log_msg(self, "available_options_hook.getter", self._logger, f"Getting available_options_hook: {hook}")
        return hook

    def change_selected_option_and_available_options(self, selected_option: Optional[T], available_options: set[T]) -> None:
        """Set the selected option and available options at once."""
        log_msg(self, "change_selected_option_and_available_options", self._logger, f"Changing both: selected_option={selected_option}, available_options={available_options}")
        self._update_component_values_and_widgets({"selected_option": selected_option, "available_options": available_options})

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

    def clear_selection(self) -> None:
        """Clear the current selection (set to None)."""
        log_msg(self, "clear_selection", self._logger, "Clearing selection (setting to None)")
        self.selected_option = None

    @property
    def widget_combobox(self) -> GuardedComboBox:
        """Get the combobox widget."""
        return self._combobox
    
    ###########################################################################
    # Debugging
    ###########################################################################

    def all_widgets_as_frame(self) -> QFrame:
        """Return all widgets as a QFrame."""
        log_msg(self, "all_widgets_as_frame", self._logger, "Creating demo frame")
        frame = QFrame()
        layout = QVBoxLayout()
        frame.setLayout(layout)
        layout.addWidget(self.widget_combobox)
        log_msg(self, "all_widgets_as_frame", self._logger, "Demo frame created successfully")
        return frame