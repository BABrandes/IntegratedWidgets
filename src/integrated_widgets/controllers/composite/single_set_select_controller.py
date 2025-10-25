from __future__ import annotations

# Standard library imports
from typing import Generic, TypeVar, Callable, Any, Mapping, Literal, AbstractSet, Optional
from logging import Logger

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QListWidgetItem

# BAB imports
from nexpy import XSetProtocol, Hook
from nexpy.x_objects.single_value_like.protocols import XSingleValueProtocol
from nexpy.x_objects.set_like.protocols import XSelectionOptionsProtocol

# Local imports
from ..core.base_composite_controller import BaseCompositeController
from ...controlled_widgets.controlled_combobox import ControlledComboBox
from ...controlled_widgets.controlled_list_widget import ControlledListWidget
from ...util.resources import combo_box_find_data, list_widget_find_data

T = TypeVar("T")

class SingleSetSelectController(BaseCompositeController[Literal["selected_option", "available_options"], Any, Any, Any, "SingleSetSelectController"], Generic[T]):
    """Controller for required selection from a set of available options.
    
    Provides a combobox widget for selecting from available options. Something must always be selected.
    Validates that selected_option is present in available_options.
    """

    def __init__(
        self,
        selected_option: T | Hook[T] | XSingleValueProtocol[T, Hook[T]] | XSelectionOptionsProtocol[T],
        available_options: AbstractSet[T] | Hook[AbstractSet[T]] | XSetProtocol[T] | None,
        controlled_widgets: set[Literal["combobox", "list_view"]] = {"combobox"},
        *,
        formatter: Callable[[T], str] = lambda item: str(item),
        debounce_ms: Optional[int] = None,
        logger: Optional[Logger] = None,
    ) -> None:

        self._formatter = formatter
        self._controlled_widgets = controlled_widgets

        ###########################################################################
        # Determine the initial values and external hooks
        ###########################################################################

        #--------------------- selected_option ---------------------

        if isinstance(selected_option, XSelectionOptionsProtocol):
            # It's an XSelectionOptionProtocol
            if available_options is not None:
                raise ValueError("available_options is not allowed when selected_option is an XSelectionOptionProtocol")
            
            initial_selected_option: T = selected_option.selected_option # type: ignore
            hook_selected_option: Hook[T] | None = selected_option.selected_option_hook # type: ignore
            initial_available_options: AbstractSet[T] = selected_option.available_options # type: ignore
            hook_available_options: Hook[AbstractSet[T]] | None = selected_option.available_options_hook # type: ignore

        elif isinstance(selected_option, Hook):
            # It's a hook
            initial_selected_option = selected_option.value # type: ignore
            hook_selected_option: Hook[T] | None = selected_option # type: ignore

        elif isinstance(selected_option, XSingleValueProtocol):
            # It's an observable
            initial_selected_option: T = selected_option.value # type: ignore
            hook_selected_option: Hook[T] | None = selected_option.hook # type: ignore

        else:
            # It's a direct value
            initial_selected_option = selected_option
            hook_selected_option = None

        #--------------------- available_options ---------------------

        if isinstance(available_options, XSetProtocol):
            # It's an XSetProtocol
            initial_available_options: AbstractSet[T] = available_options.set # type: ignore
            hook_available_options: Hook[AbstractSet[T]] | None = available_options.set_hook # type: ignore

        elif isinstance(available_options, Hook):
            # It's a hook
            initial_available_options = available_options.value # type: ignore
            hook_available_options = available_options

        elif isinstance(available_options, AbstractSet):
            # It's a direct set
            initial_available_options = available_options
            hook_available_options = None

        else:
            raise ValueError(f"Invalid available_options: {available_options}")

        ###########################################################################
        # Initialize the base controller
        ###########################################################################

        #---------------------------------------------------- validate_complete_primary_values_callback ----------------------------------------------------

        def validate_complete_primary_values_callback(x: Mapping[Literal["selected_option", "available_options"], Any]) -> tuple[bool, str]:
            # Handle partial updates by getting current values for missing keys
            selected_option: T = x.get("selected_option", initial_selected_option) # type: ignore
            available_options: AbstractSet[T] = x.get("available_options", initial_available_options) # type: ignore
            
            if not isinstance(available_options, AbstractSet[T]): # type: ignore
                return False, "available_options must be a AbstractSet[T]"

            if not selected_option in available_options:
                return False, f"selected_option {selected_option} not in available_options: {available_options}"
            
            return True, "validate_complete_primary_values_callback passed"

        #---------------------------------------------------- initialize BaseCompositeController ----------------------------------------------------

        BaseCompositeController.__init__( # type: ignore
            {
                "selected_option": initial_selected_option,
                "available_options": initial_available_options
            },
            validate_complete_primary_values_callback=validate_complete_primary_values_callback,
            debounce_ms=debounce_ms,
            logger=logger
        )

        ###########################################################################
        # Join external hooks
        ###########################################################################

        if hook_available_options is not None:
            self.join_by_key(hook_available_options, "available_options", initial_sync_mode="use_target_value") # type: ignore
        
        if hook_selected_option is not None:
            self.join_by_key(hook_selected_option, "selected_option", initial_sync_mode="use_target_value") # type: ignore

        ###########################################################################
        # Initialization completed successfully
        ###########################################################################

    ###########################################################################
    # Widget methods
    ###########################################################################

    def _initialize_widgets_impl(self) -> None:
        """Create and configure the combobox widget."""

        if "combobox" in self._controlled_widgets:
            self._combobox = ControlledComboBox(self, logger=self._logger)
            self._combobox.currentIndexChanged.connect(lambda _i: self._on_combobox_index_changed()) # type: ignore

        if "list_view" in self._controlled_widgets:
            self._list_widget = ControlledListWidget(self, logger=self._logger)
            self._list_widget.setSelectionMode(ControlledListWidget.SelectionMode.SingleSelection)
            self._list_widget.itemSelectionChanged.connect(self._on_list_widget_item_selection_changed) # type: ignore

    def _on_combobox_index_changed(self) -> None:
        """Handle combobox selection changes."""
        if self.is_blocking_signals:
            return

        new_selected_option: T = self._combobox.currentData()
        self.submit_value("selected_option", new_selected_option)

    def _on_list_widget_item_selection_changed(self) -> None:
        """Handle list widget item selection changes."""
        if self.is_blocking_signals:
            return

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

    def _invalidate_widgets_impl(self) -> None:
        """Update widgets from component values."""

        selected_option: T = self.value_by_key("selected_option")
        available_options: AbstractSet[T] = self.value_by_key("available_options")
        sorted_available_options: list[T] = sorted(available_options, key=self._formatter)

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

    ###########################################################################
    # Public API - widgets
    ###########################################################################

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
