from __future__ import annotations

# Standard library imports
from typing import Generic, Optional, TypeVar, Callable, Any, Mapping, Literal
from logging import Logger
from PySide6.QtWidgets import QWidget, QFrame, QVBoxLayout, QButtonGroup
from PySide6.QtCore import QObject, Signal, SignalInstance

# BAB imports
from observables import ObservableSingleValueLike, HookLike, ObservableSetLike, ObservableSelectionOptionLike

# Local imports
from ..widget_controllers.base_controller import BaseWidgetController
from ..guarded_widgets.guarded_radio_button import GuardedRadioButton
from ..util.resources import log_msg, log_bool

T = TypeVar("T")

class RadioButtonsController(BaseWidgetController[Literal["selected_option", "available_options"], Any], ObservableSelectionOptionLike[T], Generic[T]):

    class _ButtonsNotifier(QObject):
        countChanged = Signal(int)

    def __init__(
        self,
        selected_option: T | HookLike[T] | ObservableSingleValueLike[T] | ObservableSelectionOptionLike[T],
        available_options: set[T] | HookLike[set[T]] | ObservableSetLike[T] | None,
        *,
        formatter: Callable[[T], str] = lambda item: str(item),
        sorter: Callable[[T], Any] = lambda item: str(item),
        parent: Optional[QWidget] = None,
        logger: Optional[Logger] = None,
    ) -> None:

        log_msg(self, "__init__", logger, f"Starting initialization with selected_option={selected_option}, available_options={available_options}")
        
        self._formatter = formatter
        self._sorter = sorter
        log_msg(self, "__init__", logger, f"Formatter set: {formatter}")

        if isinstance(selected_option, ObservableSelectionOptionLike):
            log_msg(self, "__init__", logger, "selected_option is ObservableSelectionOptionLike")
            if available_options is not None:
                raise ValueError("available_options is not allowed when selected_option is an ObservableSelectionOptionLike")

            initial_selected_option: T = selected_option.selected_option
            hook_selected_option: Optional[HookLike[T]] = selected_option.selected_option_hook
            initial_available_options: set[T] = selected_option.available_options
            hook_available_options: Optional[HookLike[set[T]]] = selected_option.available_options_hook
            
            log_msg(self, "__init__", logger, f"From ObservableSelectionOptionLike: initial_selected_option={initial_selected_option}, initial_available_options={initial_available_options}")

        else:
            log_msg(self, "__init__", logger, "selected_option is not ObservableSelectionOptionLike, processing manually")
            if isinstance(selected_option, HookLike):
                # It's a hook - get initial value
                log_msg(self, "__init__", logger, "selected_option is HookLike")
                initial_selected_option: T = selected_option.value # type: ignore
                hook_selected_option: Optional[HookLike[T]] = selected_option
                log_msg(self, "__init__", logger, f"From HookLike: initial_selected_option={initial_selected_option}")

            elif isinstance(selected_option, ObservableSingleValueLike):
                # It's an observable - get initial value
                log_msg(self, "__init__", logger, "selected_option is ObservableSingleValueLike")
                initial_selected_option: T = selected_option.single_value
                hook_selected_option: Optional[HookLike[T]] = selected_option.single_value_hook
                log_msg(self, "__init__", logger, f"From ObservableSingleValueLike: initial_selected_option={initial_selected_option}")

            else:
                # It's a direct value
                log_msg(self, "__init__", logger, "selected_option is direct value")
                initial_selected_option: T = selected_option
                hook_selected_option: Optional[HookLike[T]] = None
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
                selected_option: T = x["selected_option"]
                log_msg(self, "verification_method", logger, f"selected_option from input: {selected_option}")
            else:
                selected_option: T = self.get_value("selected_option")
                log_msg(self, "verification_method", logger, f"selected_option from current: {selected_option}")

            if "available_options" in x:
                available_options: set[T] = x["available_options"]
                log_msg(self, "verification_method", logger, f"available_options from input: {available_options}")
            else:
                available_options: set[T] = self.get_value("available_options")
                log_msg(self, "verification_method", logger, f"available_options from current: {available_options}")

            if not selected_option in available_options:
                log_msg(self, "verification_method", logger, f"VERIFICATION FAILED: {selected_option} not in {available_options}")
                return False, f"Selected option {selected_option} not in available options: {available_options}"
            
            log_msg(self, "verification_method", logger, "VERIFICATION PASSED")
            return True, "Verification method passed"

        # Create notifier early so it's available during initial rebuild in _initialize_widgets
        self._buttons_notifier: RadioButtonsController._ButtonsNotifier = RadioButtonsController._ButtonsNotifier()

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

    ###########################################################################
    # Widget methods
    ###########################################################################

    def _initialize_widgets(self) -> None:
        """
        Create and configure all the user interface widgets.
        
        """
        log_msg(self, "initialize_widgets", self._logger, "Starting widget initialization")

        self._button_group = QButtonGroup(self._owner_widget)
        self._radio_buttons: list[GuardedRadioButton] = []
        
        log_msg(self, "initialize_widgets", self._logger, f"Created QButtonGroup: {self._button_group}")
        
        # Build initial radio buttons
        self._rebuild_radio_buttons()
        
        # Connect UI -> model after building buttons
        for button in self._radio_buttons:
            button.toggled.connect(lambda checked, btn=button: self._on_radio_button_toggled(checked, btn))
            log_msg(self, "initialize_widgets", self._logger, f"Connected toggled signal for button: {button}")

        log_msg(self, "initialize_widgets", self._logger, "Widget initialization completed")

    def _disable_widgets(self) -> None:
        """
        Disable all widgets.
        """
        for button in self._radio_buttons:
            button.setChecked(False)
            button.setEnabled(False)

    def _enable_widgets(self, initial_component_values: dict[Literal["selected_option", "available_options"], Any]) -> None:
        """
        Enable all widgets.
        """

        for button in self._radio_buttons:
            button.setEnabled(True)

        self._update_component_values_and_widgets(initial_component_values)

    def _on_radio_button_toggled(self, checked: bool, button: GuardedRadioButton) -> None:
        """
        Handle when the user toggles a radio button.
        """
        log_msg(self, "_on_radio_button_toggled", self._logger, f"Radio button toggled: checked={checked}, button={button}")

        if self.is_blocking_signals:
            log_msg(self, "_on_radio_button_toggled", self._logger, "Signals are blocked, returning")
            return
        
        if not checked:
            log_msg(self, "_on_radio_button_toggled", self._logger, "Button unchecked, ignoring")
            return
        
        ################# Processing user input #################
        log_msg(self, "_on_radio_button_toggled", self._logger, "Processing user input")

        # Get the new option from the radio button
        new_option: T = button.property("value")
        log_msg(self, "_on_radio_button_toggled", self._logger, f"New option from radio button: {new_option}")

        dict_to_set: dict[Literal["selected_option", "available_options"], Any] = {
            "selected_option": new_option,
            "available_options": self.get_value("available_options")
        }
        log_msg(self, "_on_radio_button_toggled", self._logger, f"Dict to set: {dict_to_set}")

        if self._verification_method is not None:
            log_msg(self, "_on_radio_button_toggled", self._logger, "Running verification method")
            success, message = self._verification_method(dict_to_set)
            log_bool(self, "_on_radio_button_toggled", self._logger, success, message)
            if not success:
                log_msg(self, "_on_radio_button_toggled", self._logger, "Verification failed, reverting widgets")
                self.apply_component_values_to_widgets()
                return
        else:
            log_msg(self, "_on_radio_button_toggled", self._logger, "No verification method")

        log_msg(self, "_on_radio_button_toggled", self._logger, "Updating widgets and component values")
        self._update_component_values_and_widgets(dict_to_set)
        
        log_msg(self, "_on_radio_button_toggled", self._logger, "Radio button toggle handling completed")

    def _fill_widgets_from_component_values(self, component_values: dict[Literal["selected_option", "available_options"], Any]) -> None:
        """
        Update the widgets from the component values.
        """
        
        log_msg(self, "_fill_widgets_from_component_values", self._logger, f"Filling widgets with: {component_values}")

        # Remove the incorrect signal blocking check - this method is called from apply_component_values_to_widgets
        # which properly manages signal blocking
        
        selected_option: Optional[T] = component_values["selected_option"]
        available_options: set[T] = component_values["available_options"]
        log_msg(self, "_fill_widgets_from_component_values", self._logger, f"selected_option: {selected_option}, available_options: {available_options}")

        log_msg(self, "_fill_widgets_from_component_values", self._logger, "Starting widget update")
        
        # Rebuild radio buttons if needed
        if len(self._radio_buttons) != len(available_options):
            log_msg(self, "_fill_widgets_from_component_values", self._logger, "Rebuilding radio buttons due to count mismatch")
            self._rebuild_radio_buttons()
        
        # Set the correct button as checked
        if selected_option is not None:
            for button in self._radio_buttons:
                button_value = button.property("value")
                if button_value == selected_option:
                    button.setChecked(True)
                    log_msg(self, "_fill_widgets_from_component_values", self._logger, f"Set button checked: {button_value}")
                    break
            else:
                log_msg(self, "_fill_widgets_from_component_values", self._logger, f"WARNING: No button found for selected_option: {selected_option}")

        log_msg(self, "_fill_widgets_from_component_values", self._logger, "Widget update completed")
        
        log_msg(self, "_fill_widgets_from_component_values", self._logger, "Widget filling completed")

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
        available_options = set(self.get_value("available_options"))
        sorted_options = sorted(available_options, key=self._sorter)
        
        for option in sorted_options:
            formatted_text = self._formatter(option)
            button = GuardedRadioButton(self._owner_widget, formatted_text)
            button.setProperty("value", option)
            self._button_group.addButton(button)
            self._radio_buttons.append(button)
            log_msg(self, "_rebuild_radio_buttons", self._logger, f"Created button for option: {option} with text: '{formatted_text}'")
        
        # Reconnect signals for new buttons
        for button in self._radio_buttons:
            button.toggled.connect(lambda checked, btn=button: self._on_radio_button_toggled(checked, btn))
        
        log_msg(self, "_rebuild_radio_buttons", self._logger, f"Radio button rebuild completed. Created {len(self._radio_buttons)} buttons")
        # Notify listeners that the number of buttons changed
        self._buttons_notifier.countChanged.emit(len(self._radio_buttons))
        
    ###########################################################################
    # Public API
    ###########################################################################

    @property
    def selected_option(self) -> T:
        """Get the currently selected option."""
        value = self.get_value("selected_option")
        log_msg(self, "selected_option.getter", self._logger, f"Getting selected_option: {value}")
        return value
    
    @selected_option.setter
    def selected_option(self, value: T) -> None:
        """Set the selected option."""
        log_msg(self, "selected_option.setter", self._logger, f"Setting selected_option to: {value}")
        self._update_component_values_and_widgets({"selected_option": value})

    def change_selected_option(self, value: T) -> None:
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
        self._update_component_values_and_widgets({"available_options": options})
    
    @property
    def selected_option_hook(self) -> HookLike[T]:
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

    def change_selected_option_and_available_options(self, selected_option: T, available_options: set[T]) -> None:
        """Set the selected option and available options at once."""
        log_msg(self, "change_selected_option_and_available_options", self._logger, f"Changing both: selected_option={selected_option}, available_options={available_options}")
        self._update_component_values_and_widgets({"selected_option": selected_option, "available_options": available_options})

    def add_option(self, option: T) -> None:
        """Add a new option to the available options."""
        log_msg(self, "add_option", self._logger, f"Adding option: {option}")
        current_options = set(self.available_options)
        current_options.add(option)
        self.available_options = current_options

    def remove_option(self, option: T) -> None:
        """Remove an option from the available options."""
        log_msg(self, "remove_option", self._logger, f"Removing option: {option}")
        current_options = set(self.available_options)
        current_options.discard(option)
        self.available_options = current_options

    @property
    def widget_radio_buttons(self) -> list[GuardedRadioButton]:
        """Get the radio button widgets."""
        return list(self._radio_buttons)
    
    @property
    def signal_number_of_radio_buttons_changed(self) -> SignalInstance:
        """Signal emitted with the current count whenever radio buttons are rebuilt."""
        return self._buttons_notifier.countChanged
    
    ###########################################################################
    # Debugging
    ###########################################################################

    def all_widgets_as_frame(self) -> QFrame:
        """Return all widgets as a QFrame."""
        log_msg(self, "all_widgets_as_frame", self._logger, "Creating demo frame")
        frame = QFrame()
        layout = QVBoxLayout()
        frame.setLayout(layout)
        
        for button in self.widget_radio_buttons:
            layout.addWidget(button)

        # When the number of buttons changes, refresh the frame's layout contents
        def _refresh_layout_on_count_change(_new_count: int) -> None:
            # Clear existing widgets from the frame layout
            try:
                while layout.count():
                    item = layout.takeAt(0)
                    w = item.widget()
                    if w is not None:
                        layout.removeWidget(w)
                        # Do not delete; new radio buttons will be added
                # Add current radio buttons
                for btn in self.widget_radio_buttons:
                    layout.addWidget(btn)
            except Exception as e:
                log_msg(self, "all_widgets_as_frame", self._logger, f"Error refreshing layout: {e}")

        try:
            # Connect the controller-level signal to refresh this specific frame
            self._buttons_notifier.countChanged.connect(_refresh_layout_on_count_change)
        except Exception as e:
            log_msg(self, "all_widgets_as_frame", self._logger, f"Error connecting countChanged: {e}")
        
        log_msg(self, "all_widgets_as_frame", self._logger, f"Demo frame created successfully with {len(self.widget_radio_buttons)} radio buttons")
        return frame


