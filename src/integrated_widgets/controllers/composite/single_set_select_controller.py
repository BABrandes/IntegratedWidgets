from __future__ import annotations

# Standard library imports
from typing import Generic, TypeVar, Callable, Any, Mapping, Literal, AbstractSet, Optional
from logging import Logger

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QListWidgetItem, QRadioButton

# BAB imports
from nexpy import XSetProtocol, Hook, XSingleValueProtocol, XBase
from nexpy.core import NexusManager
from nexpy import default as nexpy_default

# Local imports
from ..core.base_composite_controller import BaseCompositeController
from ...controlled_widgets.controlled_combobox import ControlledComboBox
from ...controlled_widgets.controlled_list_widget import ControlledListWidget
from ...controlled_widgets.controlled_radio_button_group import ControlledRadioButtonGroup
from ...auxiliaries.resources import combo_box_find_data, list_widget_find_data
from ...controlled_widgets.controlled_qlabel import ControlledQLabel

T = TypeVar("T")

class SingleSetSelectController(BaseCompositeController[Literal["selected_option", "available_options"], Any, Any, Any], Generic[T]):
    """Controller for required selection from a set of available options.
    
    Provides a combobox widget for selecting from available options. Something must always be selected.
    Validates that selected_option is present in available_options.
    """

    def __init__(
        self,
        selected_option: T | Hook[T] | XSingleValueProtocol[T],
        available_options: AbstractSet[T] | Hook[AbstractSet[T]] | XSetProtocol[T] | None,
        controlled_widgets: set[Literal["combobox", "list_view", "radio_buttons"]],
        *,
        formatter: Callable[[T], str] = lambda item: str(item),
        sorter: Callable[[T], Any] = lambda item: str(item),
        debounce_ms: int|Callable[[], int],
        nexus_manager: NexusManager = nexpy_default.NEXUS_MANAGER,
        logger: Optional[Logger] = None,
    ) -> None:

        self._formatter = formatter
        self._sorter = sorter
        self._controlled_widgets = controlled_widgets

        ###########################################################################
        # Determine the initial values and external hooks
        ###########################################################################

        #--------------------- selected_option ---------------------

        if isinstance(selected_option, Hook):
            # It's a hook
            selected_option_initial_value = selected_option.value # type: ignore
            selected_option_external_hook: Hook[T] | None = selected_option # type: ignore

        elif isinstance(selected_option, XSingleValueProtocol):
            # It's an observable
            selected_option_initial_value: T = selected_option.value # type: ignore
            selected_option_external_hook: Hook[T] | None = selected_option.value_hook # type: ignore

        elif isinstance(selected_option, XBase):
            raise ValueError(f"selected_option must be a value, a hook or a XSingleValueProtocol, got a non-supported XObject: {selected_option.__class__.__name__}") # type: ignore

        elif isinstance(selected_option, XBase):
            raise ValueError(f"selected_option must be a value, a hook or a XSingleValueProtocol, got a non-supported XObject: {selected_option.__class__.__name__}") # type: ignore

        else:
            # It's a direct value
            selected_option_initial_value = selected_option
            selected_option_external_hook = None

        #--------------------- available_options ---------------------

        if available_options is None:
            # available_options is None - should have been extracted from selected_option
            available_options_initial_value: AbstractSet[T] = {selected_option_initial_value} # type: ignore
            available_options_external_hook: Hook[AbstractSet[T]] | None = None

        elif isinstance(available_options, XSetProtocol):
            # It's an XSetProtocol
            available_options_initial_value = available_options.set # type: ignore
            available_options_external_hook = available_options.set_hook # type: ignore

        elif isinstance(available_options, Hook):
            # It's a hook
            available_options_initial_value = available_options.value # type: ignore
            available_options_external_hook = available_options

        elif isinstance(available_options, AbstractSet): # type: ignore
            # It's a direct set
            available_options_initial_value = available_options
            available_options_external_hook = None

        else:
            raise ValueError(f"Invalid available_options: {available_options}")

        ###########################################################################
        # Initialize the base controller
        ###########################################################################

        #---------------------------------------------------- validate_complete_primary_values_callback ----------------------------------------------------

        def validate_complete_primary_values_callback(x: Mapping[Literal["selected_option", "available_options"], Any]) -> tuple[bool, str]:
            # Handle partial updates by getting current values for missing keys
            selected_option: T = x.get("selected_option", selected_option_initial_value) # type: ignore
            available_options: AbstractSet[T] = x.get("available_options", available_options_initial_value) # type: ignore
            
            if not isinstance(available_options, AbstractSet): # type: ignore
                return False, "available_options must be a AbstractSet"

            if not selected_option in available_options:
                return False, f"selected_option {selected_option} not in available_options: {available_options}"
            
            return True, "validate_complete_primary_values_callback passed"

        #---------------------------------------------------- initialize BaseCompositeController ----------------------------------------------------

        BaseCompositeController.__init__( # type: ignore
            self,
            {
                "selected_option": selected_option_initial_value,
                "available_options": available_options_initial_value
            },
            validate_complete_primary_values_callback=validate_complete_primary_values_callback,
            debounce_ms=debounce_ms,
            nexus_manager=nexus_manager,
            logger=logger
        )

        ###########################################################################
        # Join external hooks
        ###########################################################################

        self._join("available_options", available_options_external_hook, initial_sync_mode="use_target_value") if available_options_external_hook is not None else None
        self._join("selected_option", selected_option_external_hook, initial_sync_mode="use_target_value") if selected_option_external_hook is not None else None # type: ignore

        ###########################################################################
        # Initialization completed successfully
        ###########################################################################

    ###########################################################################
    # Widget methods
    ###########################################################################

    def _initialize_widgets_impl(self) -> None:
        """Create and configure the combobox widget."""

        self._selected_option_label = ControlledQLabel(self, logger=self._logger)
        self._selected_option_label.setText(self._formatter(self.value_by_key("selected_option")))

        if "combobox" in self._controlled_widgets:
            self._combobox = ControlledComboBox(self, logger=self._logger)
            self._combobox.userInputFinishedSignal.connect(lambda _i: self._on_combobox_index_changed()) # type: ignore

        if "list_view" in self._controlled_widgets:
            self._list_widget = ControlledListWidget(self, logger=self._logger)
            self._list_widget.setSelectionMode(ControlledListWidget.SelectionMode.SingleSelection)
            self._list_widget.userInputFinishedSignal.connect(self._on_list_widget_item_selection_changed) # type: ignore

        if "radio_buttons" in self._controlled_widgets:
            self._button_group = ControlledRadioButtonGroup(self, logger=self._logger)
            self._button_group.userInputFinishedSignal.connect(lambda arg: self._on_radio_button_toggled(*arg) if isinstance(arg, tuple) else None) # type: ignore

    def _read_widget_primary_values_impl(self) -> Optional[Mapping[Literal["selected_option", "available_options"], Any]]:
        """
        Read the primary values from the single set select widgets.
        
        Returns:
            A mapping of the primary values from the single set select widgets. If the values are invalid, return None.
        """
        new_selected_option: T | None = None
        
        # Read from the active widget
        if "combobox" in self._controlled_widgets:
            new_selected_option = self._combobox.currentData()
            if new_selected_option is None:
                return None
        
        elif "list_view" in self._controlled_widgets:
            selected_items = self._list_widget.selectedItems()
            if not selected_items:
                # For required selection, this is invalid
                return None
            if len(selected_items) != 1:
                return None
            new_selected_option = selected_items[0].data(Qt.ItemDataRole.UserRole) # type: ignore
        
        elif "radio_buttons" in self._controlled_widgets:
            checked_button = self._button_group.checkedButton()
            if checked_button is None: # type: ignore
                return None
            button_id = self._button_group.id(checked_button)
            sorted_available_options: list[T] = sorted(self.value_by_key("available_options"), key=self._sorter)
            if button_id < 1 or button_id > len(sorted_available_options):
                return None
            new_selected_option = sorted_available_options[button_id - 1]
        
        if new_selected_option is None:
            return None
        
        return {"selected_option": new_selected_option}

    def _on_combobox_index_changed(self) -> None:
        """Handle combobox selection changes."""
        new_selected_option: T = self._combobox.currentData()
        self.submit_value("selected_option", new_selected_option)

    def _on_list_widget_item_selection_changed(self) -> None:
        """Handle list widget item selection changes."""
        selected_items = self._list_widget.selectedItems()
        if not selected_items:
            # For required selection, prevent deselection by reselecting the current value
            current_selected_option: T = self.value_by_key("selected_option")
            current_index = list_widget_find_data(self._list_widget, current_selected_option)
            if current_index >= 0:
                self._list_widget.setCurrentRow(current_index)
            return
        if len(selected_items) != 1:
            # This shouldn't happen with SingleSelection mode, but handle gracefully
            return
        
        new_selected_option: T = selected_items[0].data(Qt.ItemDataRole.UserRole) # type: ignore
        self.submit_value("selected_option", new_selected_option)

    def _on_radio_button_toggled(self, button: QRadioButton, checked: bool) -> None:
        """Handle radio button toggle changes."""
        if not checked:
            return

        # Get the ID of the button
        button_id = self._button_group.id(button)

        # Get the sorted available options
        sorted_available_options: list[T] = sorted(self.value_by_key("available_options"), key=self._sorter)

        # Get the option at the button ID
        new_selected_option: T = sorted_available_options[button_id - 1]
        self.submit_value("selected_option", new_selected_option)

    def _invalidate_widgets_impl(self) -> None:
        """Update widgets from component values."""

        selected_option: T = self.value_by_key("selected_option")
        available_options: AbstractSet[T] = self.value_by_key("available_options")
        sorted_available_options: list[T] = sorted(available_options, key=self._sorter)

        self._selected_option_label.setText(self._formatter(selected_option))

        if "combobox" in self._controlled_widgets:
            self._combobox.clear()
            for option in sorted_available_options:
                formatted_text: str = self._formatter(option)
                self._combobox.addItem(formatted_text, userData=option) # type: ignore
            
            current_index: int = combo_box_find_data(self._combobox, selected_option)
            self._combobox.setCurrentIndex(current_index)

        if "list_view" in self._controlled_widgets:
            self._list_widget.clear()
            for option in sorted_available_options:
                item = QListWidgetItem(self._formatter(option), self._list_widget)
                item.setData(Qt.ItemDataRole.UserRole, option)
            current_index = list_widget_find_data(self._list_widget, selected_option)
            self._list_widget.setCurrentRow(current_index)

        if "radio_buttons" in self._controlled_widgets:

            # Build new buttons and register them with the button group
            buttons: list[QRadioButton] = []
            for option in sorted_available_options:
                formatted_text = self._formatter(option)
                button = QRadioButton(formatted_text)
                button.setChecked(option == selected_option)
                buttons.append(button)
            self._button_group.set_buttons(buttons, start_id=1)

    ###########################################################################
    # Public API - values
    ###########################################################################

    @property
    def selected_option_hook(self) -> Hook[T]:
        """Get the hook for selected option."""
        hook: Hook[T] = self.hook_by_key("selected_option")
        return hook

    @property
    def available_options_hook(self) -> Hook[AbstractSet[T]]:
        """Get the hook for available options."""
        hook: Hook[AbstractSet[T]] = self.hook_by_key("available_options")
        return hook

    #--------------------------------------------------------------------------
    # Formatters
    #--------------------------------------------------------------------------

    @property
    def formatter(self) -> Callable[[T], str]:
        """Get the formatter function."""
        return self._formatter

    @formatter.setter
    def formatter(self, formatter: Callable[[T], str]) -> None:
        """Set the formatter function."""
        self._formatter = formatter
        self.invalidate_widgets()

    def change_formatter(self, formatter: Callable[[T], str]) -> None:
        """Set the formatter function (alternative method)."""
        self._formatter = formatter
        self.invalidate_widgets()

    #--------------------------------------------------------------------------
    # Sorters
    #--------------------------------------------------------------------------

    @property
    def sorter(self) -> Callable[[T], Any]:
        """Get the sorter function."""
        return self._sorter
    
    @sorter.setter
    def sorter(self, sorter: Callable[[T], Any]) -> None:
        """Set the sorter function."""
        self._sorter = sorter
        self.invalidate_widgets()

    def change_sorter(self, sorter: Callable[[T], Any]) -> None:
        """Set the sorter function (alternative method)."""
        self._sorter = sorter
        self.invalidate_widgets()
        
    ###########################################################################
    # Public API - widgets
    ###########################################################################

    @property
    def widget_selected_option_label(self) -> ControlledQLabel:
        """Get the selected option label widget."""
        return self._selected_option_label

    @property
    def widget_combobox(self) -> ControlledComboBox:
        """Get the combobox widget."""
        if "combobox" in self._controlled_widgets:
            return self._combobox
        else:
            raise ValueError("combobox is not in the controlled_widgets set")

    @property
    def widget_list_view(self) -> ControlledListWidget:
        """Get the list view widget."""
        if "list_view" in self._controlled_widgets:
            return self._list_widget
        else:
            raise ValueError("list_widget is not in the controlled_widgets set")

    @property
    def widget_radio_button_group(self) -> ControlledRadioButtonGroup:
        """Get the radio button group widget."""
        if "radio_buttons" in self._controlled_widgets:
            return self._button_group
        else:
            raise ValueError("radio_buttons is not in the controlled_widgets set")
