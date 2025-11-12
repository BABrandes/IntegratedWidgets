from __future__ import annotations

# Standard library imports
from typing import Generic, Optional, TypeVar, Callable, Any, Mapping, Literal, AbstractSet
from logging import Logger

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QListWidgetItem

# BAB imports
from nexpy import XSetProtocol, Hook, XBase
from nexpy.core import NexusManager
from nexpy.x_objects.single_value_like.protocols import XSingleValueProtocol
from nexpy import default as nexpy_default

# Local imports
from ..core.base_composite_controller import BaseCompositeController
from ...controlled_widgets.controlled_combobox import ControlledComboBox
from ...controlled_widgets.controlled_list_widget import ControlledListWidget
from ...controlled_widgets.controlled_qlabel import ControlledQLabel
from ...auxiliaries.resources import combo_box_find_data, list_widget_find_data

T = TypeVar("T")

class SingleSetOptionalSelectController(BaseCompositeController[Literal["selected_option", "available_options"], Any, Any, Any], Generic[T]):
    """Controller for optional selection from a set of available options.
    
    Provides a combobox widget for selecting from available options, with None as a valid choice.
    Validates that selected_option (if not None) is present in available_options.
    """

    def __init__(
        self,
        selected_option: Optional[T] | Hook[Optional[T]] | XSingleValueProtocol[Optional[T]],
        available_options: AbstractSet[T] | Hook[AbstractSet[T]] | XSetProtocol[T] | None,
        controlled_widgets: set[Literal["combobox", "list_view"]],
        *,
        formatter: Callable[[T], str] = lambda item: str(item),
        none_option_text: str = "-",
        custom_validator: Optional[Callable[[Mapping[Literal["selected_option", "available_options"], Any]], tuple[bool, str]]] = None,
        debounce_ms: int|Callable[[], int],
        nexus_manager: NexusManager = nexpy_default.NEXUS_MANAGER,
        logger: Optional[Logger] = None,
    ) -> None:

        self._formatter = formatter
        self._none_option_text = none_option_text
        self._controlled_widgets = controlled_widgets

        ###########################################################################
        # Determine the initial values and external hooks
        ###########################################################################

        #--------------------- selected_option ---------------------

        if isinstance(selected_option, Hook): # type: ignore
            # It's a hook
            selected_option_initial_value = selected_option.value # type: ignore
            selected_option_external_hook: Optional[Hook[Optional[T]]] = selected_option # type: ignore

        elif isinstance(selected_option, XSingleValueProtocol):
            # It's an observable
            selected_option_initial_value: Optional[T] = selected_option.value # type: ignore
            selected_option_external_hook: Optional[Hook[Optional[T]]] = selected_option.value_hook # type: ignore

        elif selected_option is None:
            # It's None
            selected_option_initial_value = None
            selected_option_external_hook = None

        elif isinstance(selected_option, XBase):
            raise ValueError(f"selected_option must be a value, a hook or a XSingleValueProtocol, got a non-supported XObject: {selected_option.__class__.__name__}") # type: ignore

        else:
            # It's a direct value
            selected_option_initial_value = selected_option
            selected_option_external_hook = None

        #--------------------- available_options ---------------------

        if available_options is None:
            # available_options is None - should have been extracted from selected_option
            available_options_initial_value: AbstractSet[T] = {selected_option_initial_value} if selected_option_initial_value is not None else set() # type: ignore
            available_options_external_hook: Optional[Hook[AbstractSet[T]]] = None # type: ignore

        elif isinstance(available_options, XSetProtocol):
            # It's an XSetProtocol
            available_options_initial_value: AbstractSet[T] = available_options.set # type: ignore
            available_options_external_hook: Optional[Hook[AbstractSet[T]]] = available_options.set_hook # type: ignore

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
            selected_option: Optional[T] = x.get("selected_option", selected_option_initial_value) # type: ignore
            available_options: AbstractSet[T] = x.get("available_options", available_options_initial_value) # type: ignore

            if not isinstance(available_options, AbstractSet): # type: ignore
                return False, "available_options must be a AbstractSet"

            if selected_option is not None and not selected_option in available_options:
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
            custom_validator=custom_validator,
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
        """Create and configure the widgets."""

        self._selected_option_label = ControlledQLabel(self, logger=self._logger)

        if "combobox" in self._controlled_widgets:
            self._combobox = ControlledComboBox(self, logger=self._logger)
            self._combobox.userInputFinishedSignal.connect(lambda _i: self._on_combobox_index_changed()) # type: ignore

        if "list_view" in self._controlled_widgets:
            self._list_widget = ControlledListWidget(self, logger=self._logger)
            self._list_widget.setSelectionMode(ControlledListWidget.SelectionMode.SingleSelection)
            self._list_widget.userInputFinishedSignal.connect(self._on_list_widget_item_selection_changed) # type: ignore

    def _read_widget_primary_values_impl(self) -> Optional[Mapping[Literal["selected_option", "available_options"], Any]]:
        """
        Read the primary values from the single set optional select widgets.
        
        Returns:
            A mapping of the primary values from the single set optional select widgets. If the values are invalid, return None.
        """
        new_selected_option: Optional[T] = None
        
        # Read from the active widget
        if "combobox" in self._controlled_widgets:
            new_selected_option = self._combobox.currentData()
        
        elif "list_view" in self._controlled_widgets:
            selected_items = self._list_widget.selectedItems()
            if not selected_items:
                # No selection means None (valid for optional)
                new_selected_option = None
            elif len(selected_items) == 1:
                new_selected_option = selected_items[0].data(Qt.ItemDataRole.UserRole) # type: ignore
            else:
                # Multiple selections shouldn't happen
                return None
        
        return {"selected_option": new_selected_option}

    def _on_combobox_index_changed(self) -> None:
        """Handle combobox selection changes."""
        new_option: Optional[T] = self._combobox.currentData()
        self.submit_value("selected_option", new_option)

    def _on_list_widget_item_selection_changed(self) -> None:
        """Handle list widget item selection changes."""
        selected_items = self._list_widget.selectedItems()
        if not selected_items:
            # No selection means None
            self.submit_value("selected_option", None)
            return
        if len(selected_items) != 1:
            # This shouldn't happen with SingleSelection mode, but handle gracefully
            return
        
        new_selected_option: Optional[T] = selected_items[0].data(Qt.ItemDataRole.UserRole) # type: ignore
        self.submit_value("selected_option", new_selected_option)

    def _invalidate_widgets_impl(self) -> None:
        """Update widgets from component values."""

        selected_option: Optional[T] = self.value_by_key("selected_option")
        available_options: AbstractSet[T] = self.value_by_key("available_options")
        sorted_available_options: list[T] = sorted(available_options, key=self._formatter)

        self._selected_option_label.setText(self._formatter(selected_option) if selected_option is not None else self._none_option_text)

        if "combobox" in self._controlled_widgets:
            self._combobox.clear()
            self._combobox.addItem(self._none_option_text, userData=None) # type: ignore
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
            
            if selected_option is not None:
                current_index = list_widget_find_data(self._list_widget, selected_option)
                self._list_widget.setCurrentRow(current_index)
            else:
                # Clear selection when selected_option is None
                self._list_widget.clearSelection()

    ###########################################################################
    # Public API - values
    ###########################################################################

    @property
    def selected_options_hook(self) -> Hook[AbstractSet[T]]:
        """Get the hook for selected options."""
        hook: Hook[AbstractSet[T]] = self.hook_by_key("selected_options")
        return hook

    @property
    def available_options_hook(self) -> Hook[AbstractSet[T]]:
        """Get the hook for available options."""
        hook: Hook[AbstractSet[T]] = self.hook_by_key("available_options")
        return hook

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

    @property
    def none_option_text(self) -> str:
        """Get the text displayed for the None option."""
        return self._none_option_text

    @none_option_text.setter
    def none_option_text(self, none_option_text: str) -> None:
        """Set the text displayed for the None option."""
        self._none_option_text = none_option_text
        self.invalidate_widgets()
    
    def change_none_option_text(self, none_option_text: str) -> None:
        """Set the text displayed for the None option (alternative method)."""
        self._none_option_text = none_option_text
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