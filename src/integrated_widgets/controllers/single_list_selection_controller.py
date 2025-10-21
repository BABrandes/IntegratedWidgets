from __future__ import annotations

from typing import Generic, Optional, TypeVar, Any, Mapping, Literal, Callable
from logging import Logger

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QListWidgetItem, QFrame, QVBoxLayout

from ..util.base_complex_hook_controller import BaseComplexHookController
from nexpy import XSetProtocol, Hook
from nexpy.x_objects.single_value_like.protocols import XSingleValueProtocol
from nexpy.x_objects.set_like.protocols import XOptionalSelectionOptionProtocol
from integrated_widgets.controlled_widgets.controlled_list_widget import ControlledListWidget
from integrated_widgets.util.resources import log_msg

T = TypeVar("T")

class SingleListSelectionController(BaseComplexHookController[Literal["selected_option", "available_options"], Any, Optional[T] | frozenset[T], Any, "SingleListSelectionController"], Generic[T]):
    """Controller providing a single list view for managing an optional single selection.

    The list shows all available options.
    The currently selected option is highlighted in the list.
    Clicking an option selects it (or deselects if clicking the already-selected option).
    """

    @classmethod
    def _mandatory_component_value_keys(cls) -> set[str]:
        return {"selected_option", "available_options"}

    def __init__(
        self,
        selected_option: Optional[T] | Hook[Optional[T]] | XSingleValueProtocol[Optional[T], Hook[Optional[T]]] | XOptionalSelectionOptionProtocol[T],
        available_options: frozenset[T] | Hook[frozenset[T]] | XSetProtocol[T] | None,
        *,
        order_by_callable: Callable[[T], Any] = lambda x: str(x),
        formatter: Callable[[T], str] = str,
        debounce_ms: Optional[int] = None,
        allow_deselection: bool = True,
        logger: Optional[Logger] = None,
    ) -> None:
        """Initialize the SingleListSelectionController.

        Parameters
        ----------
        selected_option : Optional[T] | Hook[Optional[T]] | XSingleValueProtocol[Optional[T], Hook[Optional[T]]] | XOptionalSelectionOptionProtocol[T]
            The initially selected option, or an observable/hook to sync with.
        available_options : frozenset[T] | Hook[frozenset[T]] | XSetProtocol[T] | None
            The frozenset of available options, or an observable/hook to sync with.
            Can be None if selected_option is XOptionalSelectionOptionProtocol.
        order_by_callable : Callable[[T], Any], optional
            Function to determine sort order of options in the list. Defaults to str().
        formatter : Callable[[T], str], optional
            Function to format each option for display in the list. Defaults to str.
        allow_deselection : bool, optional
            If True, clicking the selected item will deselect it (set to None).
            If False, there must always be a selection. Defaults to True.
        logger : Optional[Logger], optional
            Logger instance for debugging. Defaults to None.
        """

        self._order_by_callable: Callable[[T], Any] = order_by_callable
        self._formatter: Callable[[T], str] = formatter
        self._allow_deselection: bool = allow_deselection
        
        # Handle different types of selected_option and available_options
        # Check if selected_option is an XOptionalSelectionOptionProtocol
        if isinstance(selected_option, XOptionalSelectionOptionProtocol):
            if available_options is not None:
                raise ValueError("available_options must be None when selected_option is XOptionalSelectionOptionProtocol")
            # Get both selected option and available options from the observable
            selected_option_initial_value: Optional[T] = selected_option.selected_option # type: ignore
            selected_option_hook: Optional[Hook[Optional[T]]] = selected_option.selected_option_hook # type: ignore
            available_options_initial_value: frozenset[T] = selected_option.available_options # type: ignore
            available_options_hook: Optional[Hook[frozenset[T]]] = selected_option.available_options_hook # type: ignore
        else:
            # Handle selected_option
            if isinstance(selected_option, XSingleValueProtocol):
                # It's an observable - get initial value
                selected_option_initial_value: Optional[T] = selected_option.value # type: ignore
                selected_option_hook = selected_option.hook # type: ignore
            elif isinstance(selected_option, Hook):
                # It's a hook - get initial value
                selected_option_initial_value: Optional[T] = selected_option.value # type: ignore
                selected_option_hook: Optional[Hook[Optional[T]]] = selected_option # type: ignore
            else:
                # It's a direct value (could be None or T)
                selected_option_initial_value = selected_option
                selected_option_hook = None
            
            # Handle available_options
            if available_options is None:
                raise ValueError("available_options cannot be None when selected_option is not XOptionalSelectionOptionProtocol")
            
            if isinstance(available_options, XSetProtocol):
                # It's an observable - get initial value (already returns frozenset)
                available_options_initial_value: frozenset[T] = available_options.value # type: ignore
                available_options_hook: Optional[Hook[frozenset[T]]] = available_options.value_hook # type: ignore
            elif isinstance(available_options, Hook):
                # It's a hook - get initial value
                available_options_initial_value: frozenset[T] = available_options.value # type: ignore
                available_options_hook = available_options
            elif isinstance(available_options, (frozenset, set)): # type: ignore
                # It's a direct frozenset or set - convert to frozenset
                available_options_initial_value = frozenset(available_options) if available_options else frozenset()
                available_options_hook = None
            else:
                raise ValueError(f"Invalid available_options: {available_options}")
        
        def verification_method(x: Mapping[Literal["selected_option", "available_options"], Any]) -> tuple[bool, str]:
            # Verify both values are correct types
            current_selected: Optional[T] = x.get("selected_option", selected_option_initial_value) # type: ignore
            current_available = x.get("available_options", available_options_initial_value)
            
            if not isinstance(current_available, (frozenset, set)): # type: ignore
                return False, "Available options must be a frozenset or set"
            
            # Convert to frozenset if it's a set
            if isinstance(current_available, set):
                current_available = frozenset(current_available)
            
            # If selected option is not None, it must be in available options
            if current_selected is not None and current_selected not in current_available:
                return False, f"Selected option {current_selected} must be in available options"
            
            # If deselection is not allowed, selected option must not be None (unless available is empty)
            if not self._allow_deselection and current_selected is None and len(current_available) > 0:
                return False, "Selected option cannot be None when deselection is not allowed and available options is not empty"
            
            return True, "Verification method passed"

        super().__init__(
            {"selected_option": selected_option_initial_value, "available_options": available_options_initial_value},
            verification_method=verification_method,
            logger=logger,
            debounce_ms=debounce_ms,
        )

        if available_options_hook is not None:
            self.connect_hook(available_options_hook, to_key="available_options", initial_sync_mode="use_target_value") # type: ignore
        
        if selected_option_hook is not None:
            self.connect_hook(selected_option_hook, to_key="selected_option", initial_sync_mode="use_target_value") # type: ignore

    ###########################################################################
    # Widget methods
    ###########################################################################

    def _initialize_widgets_impl(self) -> None:
        self._list_widget = ControlledListWidget(self)
        self._list_widget.setSelectionMode(ControlledListWidget.SelectionMode.SingleSelection)
        
        # Connect selection change signal
        self._list_widget.itemSelectionChanged.connect(self._on_selection_changed)

    def _on_selection_changed(self) -> None:
        if self.is_blocking_signals:
            return
        
        selected_items = self._list_widget.selectedItems()
        
        if not selected_items:
            # Nothing selected
            if self._allow_deselection:
                self.submit_value("selected_option", None)
            else:
                # Re-select the current option if deselection is not allowed
                self.invalidate_widgets()
        else:
            # Get the selected value
            selected_item = selected_items[0]
            selected_value: T = selected_item.data(Qt.ItemDataRole.UserRole)
            
            # Check if clicking the already-selected item
            current_selected = self.get_value_of_hook("selected_option")
            if self._allow_deselection and selected_value == current_selected:
                # Deselect by setting to None
                self.submit_value("selected_option", None)
            else:
                self.submit_value("selected_option", selected_value)

    def _invalidate_widgets_impl(self) -> None:

        component_values: dict[Literal["selected_option", "available_options"], Any] = self.get_dict_of_values()

        log_msg(self, "_invalidate_widgets_impl", self._logger, f"Filling widgets with: {component_values}")

        available_options_reference: frozenset[T] = self.get_value_of_hook("available_options") # type: ignore
        selected_option_reference: Optional[T] = self.get_value_of_hook("selected_option") # type: ignore

        available_list: list[T] = sorted(available_options_reference, key=self._order_by_callable)

        self._list_widget.blockSignals(True)
        try:
            self._list_widget.clear()
            for value in available_list:
                item = QListWidgetItem(self._formatter(value), self._list_widget)
                item.setData(Qt.ItemDataRole.UserRole, value)
                
                # Select the item if it matches the selected option
                if selected_option_reference is not None and value == selected_option_reference:
                    item.setSelected(True)
        finally:
            self._list_widget.blockSignals(False)

    ###########################################################################
    # Public API
    ###########################################################################

    def set_selected_option_and_available_options(self, selected_option: Optional[T], available_options: frozenset[T]) -> None:
        """Set the selected option and available options."""
        self.submit_primary_values({"selected_option": selected_option, "available_options": available_options})

    def select_option(self, item: Optional[T]) -> None:
        """Set the selected option."""
        self.submit_value("selected_option", item)
    
    def clear_selection(self) -> None:
        """Clear the selection (set to None)."""
        if not self._allow_deselection:
            raise ValueError("Deselection is not allowed for this controller")
        self.submit_value("selected_option", None)

    @property
    def selected_option_hook(self) -> Hook[Optional[T]]:
        """Get the hook for the selected option."""
        hook: Hook[Optional[T]] = self.get_hook("selected_option") # type: ignore
        return hook

    @property
    def selected_option(self) -> Optional[T]:
        """Get the currently selected option."""
        value: Optional[T] = self.get_value_of_hook("selected_option") # type: ignore
        return value

    @selected_option.setter
    def selected_option(self, selected_option: Optional[T]) -> None:
        """Set the selected option."""
        self.submit_value("selected_option", selected_option)

    def change_selected_option(self, selected_option: Optional[T], *, debounce_ms: Optional[int] = None, raise_submission_error_flag: bool = True) -> None:
        """Change the selected option."""
        self.submit_value("selected_option", selected_option, debounce_ms=debounce_ms, raise_submission_error_flag=raise_submission_error_flag)

    @property
    def available_options_hook(self) -> Hook[frozenset[T]]:
        """Get the hook for the available options."""
        hook: Hook[frozenset[T]] = self.get_hook("available_options") # type: ignore
        return hook

    @property
    def available_options(self) -> frozenset[T]:
        """Get the available options."""
        value: frozenset[T] = self.get_value_of_hook("available_options") # type: ignore
        return value

    @available_options.setter
    def available_options(self, options: frozenset[T]) -> None:
        """Set the available options."""
        self.submit_value("available_options", options)

    def change_available_options(self, available_options: frozenset[T], *, debounce_ms: Optional[int] = None, raise_submission_error_flag: bool = True) -> None:
        """Change the available options."""
        self.submit_value("available_options", available_options, debounce_ms=debounce_ms, raise_submission_error_flag=raise_submission_error_flag)

    def change_selected_option_and_available_options(self, selected_option: Optional[T], available_options: frozenset[T], *, debounce_ms: Optional[int] = None, raise_submission_error_flag: bool = True) -> None:
        """Change the selected option and available options."""
        self.submit_primary_values({"selected_option": selected_option, "available_options": available_options}, debounce_ms=debounce_ms, raise_submission_error_flag=raise_submission_error_flag)

    @property
    def allow_deselection(self) -> bool:
        """Get whether deselection is allowed."""
        return self._allow_deselection
    
    @allow_deselection.setter
    def allow_deselection(self, value: bool) -> None:
        """Set whether deselection is allowed."""
        self._allow_deselection = value

    ###########################################################################
    # Debugging helpers
    ###########################################################################
    def all_widgets_as_frame(self) -> QFrame:
        frame = QFrame()
        layout = QVBoxLayout()
        frame.setLayout(layout)
        layout.addWidget(self._list_widget)
        return frame

    ###########################################################################
    # Public accessors
    ###########################################################################
    
    @property
    def widget_list(self) -> ControlledListWidget:
        """Get the list widget."""
        return self._list_widget

    ###########################################################################
    # Disposal
    ###########################################################################
    
    def dispose_before_children(self) -> None:
        try:
            self._list_widget.itemSelectionChanged.disconnect()
        except Exception:
            pass

