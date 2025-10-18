from __future__ import annotations

# Standard library imports
from typing import Generic, Optional, TypeVar, Callable, Any, Mapping, Literal
from logging import Logger
from PySide6.QtWidgets import QButtonGroup
from PySide6.QtCore import QObject, Signal, SignalInstance

# BAB imports
from observables import ObservableSingleValueProtocol, ObservableSetProtocol, ObservableSelectionOptionProtocol, Hook

# Local imports
from ..util.base_complex_hook_controller import BaseComplexHookController
from ..controlled_widgets.controlled_radio_button import ControlledRadioButton
from ..util.resources import log_msg

T = TypeVar("T")

class RadioButtonsController(BaseComplexHookController[Literal["selected_option", "available_options"], Any, T|set[T], Any, "RadioButtonsController[T]"], ObservableSelectionOptionProtocol[T], Generic[T]):

    class _ButtonsNotifier(QObject):
        countChanged = Signal(int)

    def __init__(
        self,
        selected_option: T | Hook[T] | ObservableSingleValueProtocol[T] | ObservableSelectionOptionProtocol[T],
        available_options: set[T] | Hook[set[T]] | ObservableSetProtocol[T] | None,
        *,
        formatter: Callable[[T], str] = lambda item: str(item),
        sorter: Callable[[T], Any] = lambda item: str(item),
        debounce_ms: Optional[int] = None,
        logger: Optional[Logger] = None,
    ) -> None:

        log_msg(self, "__init__", logger, f"Starting initialization with selected_option={selected_option}, available_options={available_options}")
        
        self._formatter = formatter
        self._sorter = sorter
        log_msg(self, "__init__", logger, f"Formatter set: {formatter}")

        if isinstance(selected_option, ObservableSelectionOptionProtocol):
            if available_options is not None:
                raise ValueError("available_options is not allowed when selected_option is an ObservableSelectionOptionProtocol")

            initial_selected_option: T = selected_option.selected_option # type: ignore # type: ignore
            hook_selected_option: Optional[Hook[T]] = selected_option.selected_option_hook # type: ignore
            initial_available_options: set[T] = selected_option.available_options # type: ignore
            hook_available_options: Optional[Hook[set[T]]] = selected_option.available_options_hook # type: ignore
            
        else:
            if isinstance(selected_option, Hook):
                # It's a hook - get initial value
                initial_selected_option = selected_option.value # type: ignore
                hook_selected_option = selected_option # type: ignore

            elif isinstance(selected_option, ObservableSingleValueProtocol):
                # It's an observable - get initial value
                initial_selected_option = selected_option.value # type: ignore
                hook_selected_option = selected_option.hook # type: ignore

            else:
                # It's a direct value
                initial_selected_option = selected_option
                hook_selected_option = None
            
            if isinstance(available_options, set):
                # It's a direct value
                initial_available_options = available_options
                hook_available_options = None

            elif isinstance(available_options, Hook):
                # It's a hook - get initial value
                initial_available_options = available_options.value # type: ignore
                hook_available_options = available_options # type: ignore

            elif isinstance(available_options, ObservableSetProtocol):
                # It's an observable - get initial value
                initial_available_options = available_options.value
                hook_available_options = available_options.value_hook

            else:
                raise ValueError(f"Invalid available_options: {available_options}")
        
        def verification_method(x: Mapping[Literal["selected_option", "available_options"], Any]) -> tuple[bool, str]:
            # Handle partial updates by getting current values for missing keys

            if "selected_option" in x:
                selected_option: T = x["selected_option"] # type: ignore
            else:
                selected_option = self.get_value_of_hook("selected_option") # type: ignore

            if "available_options" in x:
                available_options = x["available_options"]
            else:
                available_options = self.get_value_of_hook("available_options") # type: ignore

            if not selected_option in available_options: # type: ignore
                return False, f"Selected option {selected_option} not in available options: {available_options}"
            
            return True, "Verification method passed"

        # Create notifier early so it's available during initial rebuild in _initialize_widgets
        self._buttons_notifier: RadioButtonsController._ButtonsNotifier = RadioButtonsController._ButtonsNotifier()

        super().__init__(
            {
                "selected_option": initial_selected_option,
                "available_options": initial_available_options
            },
            verification_method=verification_method,
            debounce_ms=debounce_ms,
            logger=logger
        )
        
        if hook_available_options is not None:
            self.connect_hook(hook_available_options, "available_options", initial_sync_mode="use_target_value") # type: ignore
        if hook_selected_option is not None:
            self.connect_hook(hook_selected_option,"selected_option", initial_sync_mode="use_target_value") # type: ignore

    ###########################################################################
    # Widget methods
    ###########################################################################

    def _initialize_widgets_impl(self) -> None:
        """
        Create and configure all the user interface widgets.
        
        """

        self._button_group = QButtonGroup()
        self._radio_buttons: list[ControlledRadioButton] = []
        
        # Build initial radio buttons
        self._rebuild_radio_buttons()
        
        # Connect UI -> model after building buttons
        for button in self._radio_buttons:
            button.toggled.connect(lambda checked, btn=button: self._on_radio_button_toggled(checked, btn)) # type: ignore

    def _on_radio_button_toggled(self, checked: bool, button: ControlledRadioButton) -> None:
        """
        Handle when the user toggles a radio button.
        """
        if self.is_blocking_signals:
            return
        
        if not checked:
            return
        
        ################# Processing user input #################
        log_msg(self, "_on_radio_button_toggled", self._logger, "Processing user input")

        # Get the new option from the radio button
        new_option: T = button.property("value")
        log_msg(self, "_on_radio_button_toggled", self._logger, f"New option from radio button: {new_option}")

        dict_to_set: dict[Literal["selected_option", "available_options"], Any] = {
            "selected_option": new_option,
            "available_options": self.get_value_of_hook("available_options") # type: ignore
        }
        self.submit_values(dict_to_set)

    def _invalidate_widgets_impl(self) -> None:
        """
        Update the widgets from the component values.
        """
    
        log_msg(self, "_invalidate_widgets", self._logger, f"Filling widgets with: {self.get_dict_of_values()}")

        # Remove the incorrect signal blocking check - this method is called from apply_component_values_to_widgets
        # which properly manages signal blocking
        
        selected_option: Optional[T] = self.get_value_of_hook("selected_option") # type: ignore
        available_options: set[T] = self.get_value_of_hook("available_options") # type: ignore
        log_msg(self, "_invalidate_widgets", self._logger, f"selected_option: {selected_option}, available_options: {available_options}")

        log_msg(self, "_invalidate_widgets", self._logger, "Starting widget update")
        
        # Rebuild radio buttons if needed
        if len(self._radio_buttons) != len(available_options): # type: ignore
            log_msg(self, "_invalidate_widgets", self._logger, "Rebuilding radio buttons due to count mismatch")
            self._rebuild_radio_buttons()
        
        # Set the correct button as checked
        if selected_option is not None:
            for button in self._radio_buttons:
                button_value = button.property("value")
                if button_value == selected_option:
                    button.setChecked(True)
                    log_msg(self, "_invalidate_widgets", self._logger, f"Set button checked: {button_value}")
                    break
            else:
                log_msg(self, "_invalidate_widgets", self._logger, f"WARNING: No button found for selected_option: {selected_option}")

        log_msg(self, "_invalidate_widgets", self._logger, "Widget update completed")
        
        log_msg(self, "_invalidate_widgets", self._logger, "Widget filling completed")

    def _rebuild_radio_buttons(self) -> None:
        """Rebuild the radio button widgets."""
        log_msg(self, "_rebuild_radio_buttons", self._logger, "Starting radio button rebuild")
        
        # Disconnect old buttons
        for button in self._radio_buttons:
            try:
                button.toggled.disconnect()
                self._button_group.removeButton(button)
                button.setParent(None)
            except Exception as e:
                log_msg(self, "_rebuild_radio_buttons", self._logger, f"Error disconnecting button {button}: {e}")
        
        self._radio_buttons.clear()
        
        # Build new buttons
        available_options: set[T] = set(self.get_value_of_hook("available_options")) # type: ignore
        sorted_options: list[T] = sorted(available_options, key=self._sorter)
        
        for option in sorted_options:
            formatted_text = self._formatter(option)
            button = ControlledRadioButton(self, formatted_text)
            button.setProperty("value", option)
            self._button_group.addButton(button)
            self._radio_buttons.append(button)
            log_msg(self, "_rebuild_radio_buttons", self._logger, f"Created button for option: {option} with text: '{formatted_text}'")
        
        # Reconnect signals for new buttons
        for button in self._radio_buttons:
            button.toggled.connect(lambda checked, btn=button: self._on_radio_button_toggled(checked, btn)) # type: ignore
        
        log_msg(self, "_rebuild_radio_buttons", self._logger, f"Radio button rebuild completed. Created {len(self._radio_buttons)} buttons")
        # Notify listeners that the number of buttons changed
        self._buttons_notifier.countChanged.emit(len(self._radio_buttons))
        
    ###########################################################################
    # Public API
    ###########################################################################

    @property
    def selected_option(self) -> T:
        """Get the currently selected option."""
        value: T = self.get_value_of_hook("selected_option") # type: ignore
        return value # type: ignore
    
    @selected_option.setter
    def selected_option(self, selected_option: T) -> None:
        """Set the selected option."""
        self.submit_value("selected_option", selected_option) # type: ignore

    def change_selected_option(self, selected_option: T) -> None:
        """Set the selected option."""
        log_msg(self, "change_selected_option", self._logger, f"Changing selected_option to: {selected_option}")
        self.submit_value("selected_option", selected_option) # type: ignore

    @property
    def available_options(self) -> set[T]:
        """Get the available options."""
        value: set[T] = self.get_value_of_hook("available_options") # type: ignore
        return value # type: ignore
    
    @available_options.setter
    def available_options(self, options: set[T]) -> None:
        """Set the available options."""
        self.submit_value("available_options", options) # type: ignore

    def change_available_options(self, available_options: set[T]) -> None:
        """Set the available options."""
        self.submit_value("available_options", available_options) # type: ignore
    
    @property
    def selected_option_hook(self) -> Hook[T]:
        """Get the hook for the selected option."""
        hook: Hook[T] = self.get_hook("selected_option") # type: ignore
        return hook
    
    @property
    def available_options_hook(self) -> Hook[set[T]]:
        """Get the hook for the available options."""
        hook: Hook[set[T]] = self.get_hook("available_options") # type: ignore
        return hook

    def change_selected_option_and_available_options(self, selected_option: T, available_options: set[T]) -> None:
        """Set the selected option and available options at once."""
        self.submit_values({"selected_option": selected_option, "available_options": available_options}) # type: ignore

    def add_option(self, option: T) -> None:
        """Add a new option to the available options."""
        current_options = set(self.available_options)
        current_options.add(option)
        self.available_options = current_options

    def remove_option(self, option: T) -> None:
        """Remove an option from the available options."""
        current_options = set(self.available_options)
        current_options.discard(option)
        self.available_options = current_options

    @property
    def widget_radio_buttons(self) -> list[ControlledRadioButton]:
        """Get the radio button widgets."""
        return list(self._radio_buttons)
    
    @property
    def signal_number_of_radio_buttons_changed(self) -> SignalInstance:
        """Signal emitted with the current count whenever radio buttons are rebuilt."""
        return self._buttons_notifier.countChanged

