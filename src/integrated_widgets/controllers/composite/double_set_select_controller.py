from __future__ import annotations

from typing import Generic, Optional, TypeVar, Any, Mapping, Literal, Callable, Iterable, AbstractSet
from logging import Logger

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton, QListWidgetItem

from ..core.base_composite_controller import BaseCompositeController
from nexpy import XSetProtocol, Hook, XListProtocol
from nexpy.core import NexusManager
from nexpy import default as nexpy_default
from integrated_widgets.controlled_widgets.controlled_list_widget import ControlledListWidget
from integrated_widgets.util.resources import log_msg

T = TypeVar("T")

class DoubleSetSelectController(BaseCompositeController[
    Literal["selected_options", "available_options"],
    Any,
    AbstractSet[T],
    Any],
    Generic[T]):

    """Controller providing two set views and two move buttons to manage a double set selection.

    Available set shows available (unselected) items.
    Selected set shows selected items.
    '>' moves items from available to selected (adds to selected_options).
    '<' moves items from selected to available (removes from selected_options).
    """

    def __init__(
        self,
        selected_options: AbstractSet[T] | Hook[AbstractSet[T]] | XSetProtocol[T] | XListProtocol[T],
        available_options: AbstractSet[T] | Hook[AbstractSet[T]] | XSetProtocol[T] | XListProtocol[T],
        *,
        order_by_callable: Callable[[T], Any] = lambda x: str(x),
        debounce_ms: Optional[int] = None,
        logger: Optional[Logger] = None,
        nexus_manager: NexusManager = nexpy_default.NEXUS_MANAGER,
    ) -> None:

        self._order_by_callable: Callable[[T], Any] = order_by_callable
        
        ###########################################################################
        # Determine the initial values and external hooks
        ###########################################################################

        #--------------------- selected_options ---------------------

        if isinstance(selected_options, XSetProtocol):
            # It's an XSetProtocol
            selected_options_initial_value: AbstractSet = selected_options.set # type: ignore
            selected_options_external_hook: Optional[Iterable[T]] = selected_options.set_hook # type: ignore
        
        elif isinstance(selected_options, XListProtocol):
            # It's an XListProtocol
            selected_options_initial_value = frozenset(selected_options.list) # type: ignore
            selected_options_external_hook = selected_options.list_hook # type: ignore

        elif isinstance(selected_options, Hook):
            # It's a hook
            selected_options_initial_value = selected_options.value # type: ignore
            selected_options_external_hook = selected_options # type: ignore

        elif isinstance(selected_options, Iterable): # type: ignore
            # It's an iterable
            selected_options_initial_value = frozenset(selected_options) # type: ignore
            selected_options_external_hook = None

        else:
            raise ValueError(f"Invalid selected_options: {selected_options}")

        #--------------------- available_options ---------------------

        if isinstance(selected_options, XSetProtocol):
            # It's an XSetProtocol
            available_options_initial_value: AbstractSet = selected_options.set # type: ignore
            available_options_external_hook: Optional[Iterable[T]] = selected_options.set_hook # type: ignore
        
        elif isinstance(selected_options, XListProtocol):
            # It's an XListProtocol
            available_options_initial_value = frozenset(selected_options.list) # type: ignore
            available_options_external_hook = selected_options.list_hook # type: ignore

        elif isinstance(selected_options, Hook):
            # It's a hook
            available_options_initial_value = selected_options.value # type: ignore
            available_options_external_hook = selected_options # type: ignore

        elif isinstance(selected_options, Iterable): # type: ignore
            # It's an iterable
            available_options_initial_value = frozenset(selected_options) # type: ignore
            available_options_external_hook = None

        else:
            raise ValueError(f"Invalid selected_options: {selected_options}")

        ###########################################################################
        # Initialize the base controller
        ###########################################################################

        #---------------------------------------------------- validate_complete_primary_values_callback ----------------------------------------------------

        def validate_complete_primary_values_callback(x: Mapping[Literal["selected_options", "available_options"], Any]) -> tuple[bool, str]:
            # Verify both values are frozensets or sets
            selected: AbstractSet = x.get("selected_options", selected_options_initial_value) # type: ignore
            available: AbstractSet = x.get("available_options", available_options_initial_value) # type: ignore
            
            if not isinstance(selected, AbstractSet): # type: ignore
                return False, "selected_options must be a AbstractSet"
            if not isinstance(available, AbstractSet): # type: ignore
                return False, "available_options must be a AbstractSet"
            
            if selected in available:
                return True, "validate_complete_primary_values_callback passed"
            else:
                return False, "selected_options must be a subset of available_options"

        #---------------------------------------------------- initialize BaseCompositeController ----------------------------------------------------

        BaseCompositeController.__init__( # type: ignore
            initial_hook_values={
                "selected_options": selected_options_initial_value,
                "available_options": available_options_initial_value}, # type: ignore
            validate_complete_primary_values_callback=validate_complete_primary_values_callback,
            debounce_ms=debounce_ms,
            logger=logger,
            nexus_manager=nexus_manager,
        )

        ###########################################################################
        # Join external hooks
        ###########################################################################

        if available_options_external_hook is not None:
            self.join_by_key("available_options", available_options_external_hook, initial_sync_mode="use_target_value") # type: ignore
        
        if selected_options_external_hook is not None:
            self.join_by_key("selected_options", selected_options_external_hook, initial_sync_mode="use_target_value") # type: ignore

        ###########################################################################
        # Initialization completed successfully
        ###########################################################################

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

        available_as_reference: AbstractSet[T] = self._get_value_of_hook("available_options") # type: ignore
        selected_as_reference: AbstractSet[T] = self._get_value_of_hook("selected_options") # type: ignore

        available_as_list: list[T] = [v for v in available_as_reference if v not in selected_as_reference] # type: ignore
        selected_as_list: list[T] = [v for v in selected_as_reference if v in available_as_reference] # type: ignore

        self._available_list.blockSignals(True)
        self._selected_list.blockSignals(True)
        try:
            self._available_list.clear()
            self._selected_list.clear()
            for v in sorted(available_as_list, key=self._order_by_callable):
                item = QListWidgetItem(str(v), self._available_list)
                item.setData(Qt.ItemDataRole.UserRole, v)
            for v in sorted(selected_as_list, key=self._order_by_callable):
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
            current_selected: AbstractSet[T] = self._get_value_of_hook("selected_options") # type: ignore
            assert isinstance(current_selected, AbstractSet)
        except Exception:
            current_selected = set()
        members_as_list: list[T] = [it.data(Qt.ItemDataRole.UserRole) for it in items]
        if direction == ">":
            new_selected: AbstractSet[T] = current_selected.union(members_as_list) # type: ignore
        else:
            new_selected = frozenset(v for v in current_selected if v not in members_as_list) # type: ignore
        # Apply to component values
        self.submit_value("selected_options", new_selected) # type: ignore

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


    ###########################################################################
    # Public API - values
    ###########################################################################

    @property
    def selected_options_hook(self) -> Hook[AbstractSet[T]]:
        """Get the hook for the selected options."""
        hook: Hook[AbstractSet[T]] = self.hook_by_key("selected_options")
        return hook

    @property
    def available_options_hook(self) -> Hook[AbstractSet[T]]:
        """Get the hook for the available options."""
        hook: Hook[AbstractSet[T]] = self.hook_by_key("available_options")
        return hook

    ###########################################################################
    # Public API - widgets
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

