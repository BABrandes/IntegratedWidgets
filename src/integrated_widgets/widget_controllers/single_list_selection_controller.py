from __future__ import annotations

from typing import Generic, Optional, TypeVar, Any, Mapping, Literal, Callable
from logging import Logger

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QListWidgetItem, QFrame, QVBoxLayout

from ..util.base_complex_hook_controller import BaseComplexHookController
from observables import ObservableOptionalSelectionOptionLike, ObservableSetLike, ObservableSingleValueLike
from observables.core import HookLike, OwnedHookLike
from integrated_widgets.controlled_widgets.controlled_list_widget import ControlledListWidget
from integrated_widgets.util.resources import log_msg

T = TypeVar("T")

class SingleListSelectionController(BaseComplexHookController[Literal["selected_option", "available_options"], Any, Optional[T] | set[T], Any, "SingleListSelectionController"], ObservableOptionalSelectionOptionLike[T], Generic[T]):
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
        selected_option: Optional[T] | HookLike[Optional[T]] | ObservableSingleValueLike[Optional[T]] | ObservableOptionalSelectionOptionLike[T],
        available_options: set[T] | HookLike[set[T]] | ObservableSetLike[T] | None,
        order_by_callable: Callable[[T], Any] = lambda x: str(x),
        allow_deselection: bool = True,
        parent_of_widgets: Optional[QWidget] = None,
        logger: Optional[Logger] = None,
    ) -> None:
        """Initialize the SingleListSelectionController.

        Parameters
        ----------
        selected_option : Optional[T] | HookLike[Optional[T]] | ObservableSingleValueLike[Optional[T]] | ObservableOptionalSelectionOptionLike[T]
            The initially selected option, or an observable/hook to sync with.
        available_options : set[T] | HookLike[set[T]] | ObservableSetLike[T] | None
            The set of available options, or an observable/hook to sync with.
            Can be None if selected_option is ObservableOptionalSelectionOptionLike.
        order_by_callable : Callable[[T], Any], optional
            Function to determine sort order of options in the list. Defaults to str().
        allow_deselection : bool, optional
            If True, clicking the selected item will deselect it (set to None).
            If False, there must always be a selection. Defaults to True.
        parent_of_widgets : Optional[QWidget], optional
            The parent widget for created UI widgets. Defaults to None.
        logger : Optional[Logger], optional
            Logger instance for debugging. Defaults to None.
        """

        self._order_by_callable: Callable[[T], Any] = order_by_callable
        self._allow_deselection: bool = allow_deselection
        
        # Handle different types of selected_option and available_options
        # Check if selected_option is an ObservableOptionalSelectionOptionLike
        if isinstance(selected_option, ObservableOptionalSelectionOptionLike):
            if available_options is not None:
                raise ValueError("available_options must be None when selected_option is ObservableOptionalSelectionOptionLike")
            # Get both selected option and available options from the observable
            selected_option_initial_value = selected_option.selected_option
            selected_option_hook = selected_option.selected_option_hook
            available_options_initial_value = selected_option.available_options
            available_options_hook = selected_option.available_options_hook
        else:
            # Handle selected_option
            if isinstance(selected_option, ObservableSingleValueLike):
                # It's an observable - get initial value
                selected_option_initial_value = selected_option.value
                selected_option_hook = selected_option.hook
            elif isinstance(selected_option, HookLike):
                # It's a hook - get initial value
                selected_option_initial_value: Optional[T] = selected_option.value # type: ignore
                selected_option_hook: Optional[HookLike[Optional[T]]] = selected_option
            else:
                # It's a direct value (could be None or T)
                selected_option_initial_value = selected_option
                selected_option_hook = None
            
            # Handle available_options
            if available_options is None:
                raise ValueError("available_options cannot be None when selected_option is not ObservableOptionalSelectionOptionLike")
            
            if isinstance(available_options, ObservableSetLike):
                # It's an observable - get initial value
                available_options_initial_value = available_options.value
                available_options_hook = available_options.value_hook
            elif isinstance(available_options, HookLike):
                # It's a hook - get initial value
                available_options_initial_value: set[T] = available_options.value # type: ignore
                available_options_hook = available_options
            elif isinstance(available_options, set):
                # It's a direct set
                available_options_initial_value = set(available_options) if available_options else set()
                available_options_hook = None
            else:
                raise ValueError(f"Invalid available_options: {available_options}")
        
        def verification_method(x: Mapping[Literal["selected_option", "available_options"], Any]) -> tuple[bool, str]:
            # Verify both values are correct types
            current_selected = x.get("selected_option", selected_option_initial_value)
            current_available = x.get("available_options", available_options_initial_value)
            
            if not isinstance(current_available, set):
                return False, "Available options must be a set"
            
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
            parent_of_widgets=parent_of_widgets,
            logger=logger,
        )

        if available_options_hook is not None:
            self.connect_hook(available_options_hook, to_key="available_options", initial_sync_mode="use_target_value") # type: ignore
        
        if selected_option_hook is not None:
            self.connect_hook(selected_option_hook, to_key="selected_option", initial_sync_mode="use_target_value") # type: ignore

    ###########################################################################
    # Widget methods
    ###########################################################################

    def _initialize_widgets(self) -> None:
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
                self.submit_values({"selected_option": None})
            else:
                # Re-select the current option if deselection is not allowed
                self._invalidate_widgets_called_by_hook_system()
        else:
            # Get the selected value
            selected_item = selected_items[0]
            selected_value: T = selected_item.data(Qt.ItemDataRole.UserRole)
            
            # Check if clicking the already-selected item
            current_selected = self.get_value_reference_of_hook("selected_option")
            if self._allow_deselection and selected_value == current_selected:
                # Deselect by setting to None
                self.submit_values({"selected_option": None})
            else:
                self.submit_values({"selected_option": selected_value})

    def _invalidate_widgets_impl(self) -> None:

        component_values: dict[Literal["selected_option", "available_options"], Any] = self.get_dict_of_values()

        log_msg(self, "_invalidate_widgets_impl", self._logger, f"Filling widgets with: {component_values}")

        available_options_reference: set[T] = self.get_value_of_hook("available_options") # type: ignore
        selected_option_reference: Optional[T] = self.get_value_of_hook("selected_option") # type: ignore

        available_list: list[T] = sorted(available_options_reference, key=self._order_by_callable)

        self._list_widget.blockSignals(True)
        try:
            self._list_widget.clear()
            for value in available_list:
                item = QListWidgetItem(str(value), self._list_widget)
                item.setData(Qt.ItemDataRole.UserRole, value)
                
                # Select the item if it matches the selected option
                if selected_option_reference is not None and value == selected_option_reference:
                    item.setSelected(True)
        finally:
            self._list_widget.blockSignals(False)

    ###########################################################################
    # Public API
    ###########################################################################

    def set_selected_option_and_available_options(self, selected_option: Optional[T], available_options: set[T]) -> None:
        """Set the selected option and available options."""
        self.submit_values({"selected_option": selected_option, "available_options": available_options})

    def select_option(self, item: Optional[T]) -> None:
        """Set the selected option."""
        self.submit_values({"selected_option": item})
    
    def clear_selection(self) -> None:
        """Clear the selection (set to None)."""
        if not self._allow_deselection:
            raise ValueError("Deselection is not allowed for this controller")
        self.submit_values({"selected_option": None})

    @property
    def selected_option_hook(self) -> OwnedHookLike[Optional[T]]:
        """Get the hook for the selected option."""
        hook: OwnedHookLike[Optional[T]] = self.get_hook("selected_option") # type: ignore
        return hook

    @property
    def selected_option(self) -> Optional[T]:
        """Get the currently selected option."""
        value: Optional[T] = self.get_value_of_hook("selected_option") # type: ignore
        return value

    @selected_option.setter
    def selected_option(self, selected_option: Optional[T]) -> None:
        """Set the selected option."""
        self.submit_values({"selected_option": selected_option})

    def change_selected_option(self, selected_option: Optional[T]) -> None:
        """Change the selected option."""
        self.submit_values({"selected_option": selected_option})

    @property
    def available_options_hook(self) -> OwnedHookLike[set[T]]:
        """Get the hook for the available options."""
        hook: OwnedHookLike[set[T]] = self.get_hook("available_options") # type: ignore
        return hook

    @property
    def available_options(self) -> set[T]:
        """Get the available options."""
        value: set[T] = self.get_value_of_hook("available_options") # type: ignore
        return value

    @available_options.setter
    def available_options(self, options: set[T]) -> None:
        """Set the available options."""
        self.submit_values({"available_options": options})

    def change_available_options(self, available_options: set[T]) -> None:
        """Change the available options."""
        self.submit_values({"available_options": available_options})

    def change_selected_option_and_available_options(self, selected_option: Optional[T], available_options: set[T]) -> None:
        """Change the selected option and available options."""
        self.submit_values({"selected_option": selected_option, "available_options": available_options})

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

