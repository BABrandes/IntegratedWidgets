from __future__ import annotations

from typing import Generic, Optional, TypeVar, Any, Mapping, Literal, Callable
from logging import Logger

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QPushButton, QListWidgetItem, QFrame, QVBoxLayout

from ..util.base_complex_hook_controller import BaseComplexHookController
from observables import ObservableMultiSelectionOptionLike, ObservableSetLike, HookLike
from observables.core import HookWithOwnerLike
from integrated_widgets.controlled_widgets.controlled_list_widget import ControlledListWidget
from integrated_widgets.util.resources import log_msg

T = TypeVar("T")

class DoubleListSelectionController(BaseComplexHookController[Literal["selected_options", "available_options"], Any, set[T], Any, "DoubleListSelectionController"], ObservableMultiSelectionOptionLike[T], Generic[T]):

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
        selected_options: set[T] | HookLike[set[T]] | ObservableSetLike[T],
        available_options: set[T] | HookLike[set[T]] | ObservableSetLike[T],
        order_by_callable: Callable[[T], Any] = lambda x: str(x),
        parent_of_widgets: Optional[QWidget] = None,
        logger: Optional[Logger] = None,
    ) -> None:

        self._order_by_callable: Callable[[T], Any] = order_by_callable
        
        # Handle different types of selected_options and available_options
        if isinstance(selected_options, ObservableSetLike):
            # It's an observable - get initial value
            selected_options_initial_value = selected_options.value
            selected_options_hook = selected_options.value_hook
        elif isinstance(selected_options, HookLike):
            # It's a hook - get initial value
            selected_options_initial_value: set[T] = selected_options.value # type: ignore
            selected_options_hook: Optional[HookLike[set[T]]] = selected_options
        elif isinstance(selected_options, set):
            # It's a direct set
            selected_options_initial_value = set(selected_options) if selected_options else set()
            selected_options_hook = None
        else:
            raise ValueError(f"Invalid selected_options: {selected_options}")
        
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
        
        def verification_method(x: Mapping[Literal["selected_options", "available_options"], Any]) -> tuple[bool, str]:
            # Verify both values are sets
            current_selected = x.get("selected_options", selected_options_initial_value)
            current_available = x.get("available_options", available_options_initial_value)
            
            if not isinstance(current_selected, set):
                return False, "Selected options must be a set"
            if not isinstance(current_available, set):
                return False, "Available options must be a set"
            
            return True, "Verification method passed"

        super().__init__(
            {"selected_options": selected_options_initial_value, "available_options": available_options_initial_value},
            verification_method=verification_method,
            logger=logger,
        )

        if available_options_hook is not None:
            self.connect_hook(available_options_hook, to_key="available_options", initial_sync_mode="use_target_value") # type: ignore
        
        if selected_options_hook is not None:
            self.connect_hook(selected_options_hook, to_key="selected_options", initial_sync_mode="use_target_value") # type: ignore

    ###########################################################################
    # Widget methods
    ###########################################################################

    def _initialize_widgets(self) -> None:
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

        component_values: dict[Literal["selected_options", "available_options"], Any] = self.get_dict_of_values()

        log_msg(self, "_invalidate_widgets_impl", self._logger, f"Filling widgets with: {component_values}")

        options_as_reference: set[T] = self.get_value_reference_of_hook("available_options")
        selected_as_reference: set[T] = self.get_value_reference_of_hook("selected_options")

        available: list[T] = [v for v in options_as_reference if v not in selected_as_reference]
        selected: list[T] = [v for v in selected_as_reference if v in options_as_reference]

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
        # Compute new selected set
        try:
            current_selected: set[T] = self.get_value_reference_of_hook("selected_options")
            assert isinstance(current_selected, set)
        except Exception:
            current_selected = set()
        members: list[T] = [it.data(Qt.ItemDataRole.UserRole) for it in items]
        if direction == ">":
            new_selected = current_selected.union(members)
        else:
            new_selected = {v for v in current_selected if v not in members}
        # Apply to component values
        self.submit_values({"selected_options": new_selected})

    ###########################################################################
    # Public API
    ###########################################################################

    def set_selected_options_and_available_options(self, selected_options: set[T], available_options: set[T]) -> None:
        """Set the selected options and available options."""
        self.submit_values({"selected_options": selected_options, "available_options": available_options})

    def add_selected_option(self, item: T) -> None:
        """Add an option to the selected options."""
        selected_options_reference: set[T] = self.get_value_reference_of_hook("selected_options")
        assert isinstance(selected_options_reference, set)  
        self.submit_values({"selected_options": selected_options_reference.union({item})})
    
    def remove_selected_option(self, item: T) -> None:
        """Remove an option from the selected options."""
        selected_options_reference: set[T] = self.get_value_reference_of_hook("selected_options")
        assert isinstance(selected_options_reference, set)
        self.submit_values({"selected_options": selected_options_reference.difference({item})})

    @property
    def selected_options_hook(self) -> HookWithOwnerLike[set[T]]:
        """Get the hook for the selected options."""
        return self.get_hook("selected_options")

    @property
    def selected_options(self) -> set[T]:
        """Get the currently selected options."""
        selected_options_reference: set[T] = self.get_value_reference_of_hook("selected_options")
        assert isinstance(selected_options_reference, set)
        return selected_options_reference.copy()

    @selected_options.setter
    def selected_options(self, value: set[T]) -> None:
        """Set the selected options."""
        self.submit_values({"selected_options": value})

    def change_selected_options(self, selected_options: set[T]) -> None:
        """Change the selected options."""
        self.submit_values({"selected_options": selected_options})

    @property
    def available_options_hook(self) -> HookWithOwnerLike[set[T]]:
        """Get the hook for the available options."""
        return self.get_hook("available_options")

    @property
    def available_options(self) -> set[T]:
        """Get the available options."""
        available_options_reference: set[T] = self.get_value_reference_of_hook("available_options")
        assert isinstance(available_options_reference, set)
        return available_options_reference.copy()

    @available_options.setter
    def available_options(self, value: set[T]) -> None:
        """Set the available options."""
        self.submit_values({"available_options": value})

    def change_available_options(self, available_options: set[T]) -> None:
        """Change the available options."""
        self.submit_values({"available_options": available_options})

    def change_selected_options_and_available_options(self, selected_options: set[T], available_options: set[T]) -> None:
        """Change the selected options and available options."""
        self.submit_values({"selected_options": selected_options, "available_options": available_options})

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


