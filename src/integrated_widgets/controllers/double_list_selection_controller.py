from __future__ import annotations

from typing import Generic, Optional, TypeVar, Any, Mapping, Literal, Callable
from logging import Logger

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton, QListWidgetItem, QFrame, QVBoxLayout

from ..util.base_complex_hook_controller import BaseComplexHookController
from nexpy import XSetProtocol, Hook
from integrated_widgets.controlled_widgets.controlled_list_widget import ControlledListWidget
from integrated_widgets.util.resources import log_msg

T = TypeVar("T")

class DoubleListSelectionController(BaseComplexHookController[Literal["selected_options", "available_options"], Any, frozenset[T], Any, "DoubleListSelectionController"], Generic[T]):

    @classmethod
    def _mandatory_component_value_keys(cls) -> set[str]:
        return {"selected_options", "available_options"}

    """Controller providing two list views and two move buttons to manage a multi-selection.

    Available list shows available (unselected) items.
    Selected list shows selected items.
    '>' moves items from available to selected (adds to selected_options).
    '<' moves items from selected to available (removes from selected_options).
    """

    def __init__(
        self,
        selected_options: frozenset[T] | Hook[frozenset[T]] | XSetProtocol[T],
        available_options: frozenset[T] | Hook[frozenset[T]] | XSetProtocol[T],
        order_by_callable: Callable[[T], Any] = lambda x: str(x),
        debounce_ms: Optional[int] = None,
        logger: Optional[Logger] = None,
    ) -> None:

        self._order_by_callable: Callable[[T], Any] = order_by_callable
        
        # Handle different types of selected_options and available_options
        if isinstance(selected_options, XSetProtocol):
            # It's an observable - get initial value (already returns frozenset)
            selected_options_initial_value: frozenset[T] = selected_options.value # type: ignore
            selected_options_hook: Optional[Hook[frozenset[T]]] = selected_options.value_hook # type: ignore
        elif isinstance(selected_options, Hook):
            # It's a hook - get initial value
            selected_options_initial_value: frozenset[T] = selected_options.value # type: ignore
            selected_options_hook = selected_options
        elif isinstance(selected_options, (frozenset, set)): # type: ignore
            # It's a direct frozenset or set - convert to frozenset
            selected_options_initial_value = frozenset(selected_options) if selected_options else frozenset()
            selected_options_hook = None
        else:
            raise ValueError(f"Invalid selected_options: {selected_options}")
        
        if isinstance(available_options, XSetProtocol):
            # It's an observable - get initial value (already returns frozenset)
            available_options_initial_value: frozenset[T] = available_options.value # type: ignore
            available_options_hook = available_options.value_hook
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
        
        def verification_method(x: Mapping[Literal["selected_options", "available_options"], Any]) -> tuple[bool, str]:
            # Verify both values are frozensets or sets
            current_selected = x.get("selected_options", selected_options_initial_value)
            current_available = x.get("available_options", available_options_initial_value)
            
            if not isinstance(current_selected, (frozenset, set)):
                return False, "Selected options must be a frozenset or set"
            if not isinstance(current_available, (frozenset, set)):
                return False, "Available options must be a frozenset or set"
            
            # Convert to frozenset if they're sets
            if isinstance(current_selected, set):
                current_selected = frozenset(current_selected)
            if isinstance(current_available, set):
                current_available = frozenset(current_available)
            
            return True, "Verification method passed"

        super().__init__(
            {"selected_options": selected_options_initial_value, "available_options": available_options_initial_value},
            verification_method=verification_method,
            debounce_ms=debounce_ms,
            logger=logger,
        )

        if available_options_hook is not None:
            self.connect_hook(available_options_hook, to_key="available_options", initial_sync_mode="use_target_value") # type: ignore
        
        if selected_options_hook is not None:
            self.connect_hook(selected_options_hook, to_key="selected_options", initial_sync_mode="use_target_value") # type: ignore

    ###########################################################################
    # Widget methods
    ###########################################################################

    def _initialize_widgets_impl(self) -> None:
        self._available_list = ControlledListWidget(self)
        self._selected_list = ControlledListWidget(self)
        self._available_list.setSelectionMode(ControlledListWidget.SelectionMode.ExtendedSelection)
        self._selected_list.setSelectionMode(ControlledListWidget.SelectionMode.ExtendedSelection)

        self._button_move_to_selected = QPushButton("move to selected")
        self._button_remove_from_selected = QPushButton("remove from selected")
        self._button_move_to_selected.setToolTip("Move selected items to the selected list")
        self._button_remove_from_selected.setToolTip("Remove selected items from the selected list")
        self._button_move_to_selected.clicked.connect(self._on_move_to_selected)
        self._button_remove_from_selected.clicked.connect(self._on_move_to_available)

        # Update move button enabled state on selection change
        self._available_list.itemSelectionChanged.connect(self._update_button_states)
        self._selected_list.itemSelectionChanged.connect(self._update_button_states)

    def _on_move_to_selected(self) -> None:
        if self.is_blocking_signals:
            return
        self._move(selected_from=self._available_list, direction=">")

    def _on_move_to_available(self) -> None:
        if self.is_blocking_signals:
            return
        self._move(selected_from=self._selected_list, direction="<")

    def _invalidate_widgets_impl(self) -> None:

        component_values: dict[Literal["selected_options", "available_options"], Any] = self.get_dict_of_values() # type: ignore

        log_msg(self, "_invalidate_widgets_impl", self._logger, f"Filling widgets with: {component_values}")

        options_as_reference: frozenset[T] = self.get_value_of_hook("available_options") # type: ignore
        selected_as_reference: frozenset[T] = self.get_value_of_hook("selected_options") # type: ignore

        available: list[T] = [v for v in options_as_reference if v not in selected_as_reference] # type: ignore
        selected: list[T] = [v for v in selected_as_reference if v in options_as_reference] # type: ignore

        self._available_list.blockSignals(True)
        self._selected_list.blockSignals(True)
        try:
            self._available_list.clear()
            self._selected_list.clear()
            for v in sorted(available, key=self._order_by_callable):
                item = QListWidgetItem(str(v), self._available_list)
                item.setData(Qt.ItemDataRole.UserRole, v)
            for v in sorted(selected, key=self._order_by_callable):
                item = QListWidgetItem(str(v), self._selected_list)
                item.setData(Qt.ItemDataRole.UserRole, v)
        finally:
            self._available_list.blockSignals(False)
            self._selected_list.blockSignals(False)
        self._update_button_states()

    ###########################################################################
    # Internal
    ###########################################################################

    def _update_button_states(self) -> None:
        self._button_move_to_selected.setEnabled(len(self._available_list.selectedItems()) > 0)
        self._button_remove_from_selected.setEnabled(len(self._selected_list.selectedItems()) > 0)

    def _move(self, selected_from: ControlledListWidget, direction: str) -> None:
        """Move selected items between lists."""
        # Collect items to move
        items = list(selected_from.selectedItems())
        if not items:
            return
        # Compute new selected frozenset
        try:
            current_selected: frozenset[T] = self.get_value_of_hook("selected_options") # type: ignore
            assert isinstance(current_selected, frozenset)
        except Exception:
            current_selected = frozenset()
        members: list[T] = [it.data(Qt.ItemDataRole.UserRole) for it in items]
        if direction == ">":
            new_selected = current_selected.union(members) # type: ignore
        else:
            new_selected = frozenset(v for v in current_selected if v not in members) # type: ignore
        # Apply to component values
        self.submit_value("selected_options", new_selected)

    ###########################################################################
    # Public API
    ###########################################################################

    def set_selected_options_and_available_options(self, selected_options: frozenset[T], available_options: frozenset[T]) -> None:
        """Set the selected options and available options."""
        self.submit_values({"selected_options": selected_options, "available_options": available_options}) # type: ignore

    def add_selected_option(self, item: T) -> None:
        """Add an option to the selected options."""
        selected_options_reference: frozenset[T] = self.get_value_of_hook("selected_options") # type: ignore
        assert isinstance(selected_options_reference, frozenset)  
        self.submit_values({"selected_options": selected_options_reference.union({item})}) # type: ignore
    
    def remove_selected_option(self, item: T) -> None:
        """Remove an option from the selected options."""
        selected_options_reference: frozenset[T] = self.get_value_of_hook("selected_options") # type: ignore
        assert isinstance(selected_options_reference, frozenset)
        self.submit_values({"selected_options": selected_options_reference.difference({item})}) # type: ignore

    @property
    def selected_options_hook(self) -> Hook[frozenset[T]]:
        """Get the hook for the selected options."""
        return self.get_hook("selected_options") # type: ignore

    @property
    def selected_options(self) -> frozenset[T]:
        """Get the currently selected options."""
        selected_options_reference: frozenset[T] = self.get_value_of_hook("selected_options") # type: ignore    
        assert isinstance(selected_options_reference, frozenset)
        return selected_options_reference # type: ignore

    @selected_options.setter
    def selected_options(self, value: frozenset[T] | set[T]) -> None:
        """Set the selected options."""
        # Ensure value is a frozenset
        if isinstance(value, set) and not isinstance(value, frozenset):
            value = frozenset(value)
        self.submit_values({"selected_options": value}) # type: ignore

    def change_selected_options(self, selected_options: frozenset[T] | set[T], *, debounce_ms: Optional[int] = None, raise_submission_error_flag: bool = True) -> None:
        """Change the selected options."""
        # Ensure value is a frozenset
        if isinstance(selected_options, set) and not isinstance(selected_options, frozenset):
            selected_options = frozenset(selected_options)
        self.submit_values({"selected_options": selected_options}, debounce_ms=debounce_ms, raise_submission_error_flag=raise_submission_error_flag) # type: ignore

    @property
    def available_options_hook(self) -> Hook[frozenset[T]]:
        """Get the hook for the available options."""
        return self.get_hook("available_options") # type: ignore

    @property
    def available_options(self) -> frozenset[T]:
        """Get the available options."""
        available_options_reference: frozenset[T] = self.get_value_of_hook("available_options") # type: ignore
        assert isinstance(available_options_reference, frozenset)
        return available_options_reference # type: ignore

    @available_options.setter
    def available_options(self, value: frozenset[T] | set[T]) -> None:
        """Set the available options."""
        # Ensure value is a frozenset
        if isinstance(value, set) and not isinstance(value, frozenset):
            value = frozenset(value)
        self.submit_values({"available_options": value}) # type: ignore

    def change_available_options(self, available_options: frozenset[T] | set[T], *, debounce_ms: Optional[int] = None, raise_submission_error_flag: bool = True) -> None:
        """Change the available options."""
        # Ensure value is a frozenset
        if isinstance(available_options, set) and not isinstance(available_options, frozenset):
            available_options = frozenset(available_options)
        self.submit_values({"available_options": available_options}, debounce_ms=debounce_ms, raise_submission_error_flag=raise_submission_error_flag) # type: ignore

    def change_selected_options_and_available_options(self, selected_options: frozenset[T] | set[T], available_options: frozenset[T] | set[T], *, debounce_ms: Optional[int] = None, raise_submission_error_flag: bool = True) -> None:
        """Change the selected options and available options."""
        # Ensure values are frozensets
        if isinstance(selected_options, set) and not isinstance(selected_options, frozenset):
            selected_options = frozenset(selected_options)
        if isinstance(available_options, set) and not isinstance(available_options, frozenset):
            available_options = frozenset(available_options)
        self.submit_values({"selected_options": selected_options, "available_options": available_options}, debounce_ms=debounce_ms, raise_submission_error_flag=raise_submission_error_flag) # type: ignore

    ###########################################################################
    # Debugging helpers
    ###########################################################################
    def all_widgets_as_frame(self) -> QFrame:
        frame = QFrame()
        layout = QVBoxLayout()
        frame.setLayout(layout)
        layout.addWidget(self._available_list)
        layout.addWidget(self._button_move_to_selected)
        layout.addWidget(self._button_remove_from_selected)
        layout.addWidget(self._selected_list)
        return frame

    ###########################################################################
    # Public accessors
    ###########################################################################
    
    @property
    def widget_available_list(self) -> ControlledListWidget:
        """Get the available list widget."""
        return self._available_list

    @property
    def widget_selected_list(self) -> ControlledListWidget:
        """Get the selected list widget."""
        return self._selected_list

    @property
    def widget_button_move_to_selected(self) -> QPushButton:
        """Get the move-to-selected button."""
        return self._button_move_to_selected

    @property
    def widget_button_remove_from_selected(self) -> QPushButton:
        """Get the move-to-available button."""
        return self._button_remove_from_selected

    ###########################################################################
    # Disposal
    ###########################################################################
    
    def dispose_before_children(self) -> None:
        try:
            self._button_move_to_selected.clicked.disconnect()
        except Exception:
            pass
        try:
            self._button_remove_from_selected.clicked.disconnect()
        except Exception:
            pass
        try:
            self._available_list.itemSelectionChanged.disconnect()
        except Exception:
            pass
        try:
            self._selected_list.itemSelectionChanged.disconnect()
        except Exception:
            pass


