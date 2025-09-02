from __future__ import annotations

from typing import Generic, Optional, TypeVar, Any, Mapping, overload, Literal
from logging import Logger

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QPushButton, QListWidgetItem, QFrame, QVBoxLayout

from integrated_widgets.widget_controllers.base_controller import BaseWidgetController
from observables import ObservableMultiSelectionOptionLike, HookLike, InitialSyncMode
from integrated_widgets.guarded_widgets import GuardedListWidget


T = TypeVar("T")


class DoubleListSelectionController(BaseWidgetController[Literal["selected_options", "available_options"], Any], ObservableMultiSelectionOptionLike[T], Generic[T]):

    @classmethod
    def _mandatory_component_value_keys(cls) -> set[str]:
        return {"selected_options", "available_options"}

    """Controller providing two list views and two move buttons to manage a multi-selection.

    Available list shows available (unselected) items.
    Selected list shows selected items.
    '>' moves items from available to selected (adds to selected_options).
    '<' moves items from selected to available (removes from selected_options).
    """

    @overload
    def __init__(
        self,
        selected_options: set[T],
        available_options: set[T],
        parent: Optional[QWidget] = None,
    ) -> None: ...

    @overload
    def __init__(
        self,
        selected_options: set[T],
        available_options: HookLike[set[T]],
        parent: Optional[QWidget] = None,
    ) -> None: ...

    @overload
    def __init__(
        self,
        selected_options: HookLike[set[T]],
        available_options: set[T],
        parent: Optional[QWidget] = None,
    ) -> None: ...

    @overload
    def __init__(
        self,
        selected_options: HookLike[set[T]],
        available_options: HookLike[set[T]],
        parent: Optional[QWidget] = None,
    ) -> None: ...

    def __init__(
        self,
        selected_options,
        available_options,
        parent: Optional[QWidget] = None,
        logger: Optional[Logger] = None,
    ) -> None:
        
        # Handle different types of selected_options and available_options
        if isinstance(selected_options, HookLike):
            # It's a hook - get initial value
            initial_selected_options: set[T] = selected_options.value # type: ignore
            selected_options_hook: Optional[HookLike[set[T]]] = selected_options
        elif isinstance(selected_options, set):
            # It's a direct set
            initial_selected_options = set(selected_options) if selected_options else set()
            selected_options_hook: Optional[HookLike[set[T]]] = None
        else:
            raise ValueError(f"Invalid selected_options: {selected_options}")
        
        if isinstance(available_options, HookLike):
            # It's a hook - get initial value
            available_options_set = available_options.value # type: ignore
            available_options_hook: Optional[HookLike[set[T]]] = available_options
        elif isinstance(available_options, set):
            # It's a direct set
            available_options_set = set(available_options) if available_options else set()
            available_options_hook: Optional[HookLike[set[T]]] = None
        else:
            raise ValueError(f"Invalid available_options: {available_options}")
        
        def verification_method(x: Mapping[Literal["selected_options", "available_options"], Any]) -> tuple[bool, str]:
            # Verify both values are sets
            current_selected = x.get("selected_options", initial_selected_options)
            current_available = x.get("available_options", available_options_set)
            
            if not isinstance(current_selected, set):
                return False, "Selected options must be a set"
            if not isinstance(current_available, set):
                return False, "Available options must be a set"
            
            return True, "Verification method passed"

        super().__init__(
            {"selected_options": initial_selected_options, "available_options": available_options_set},
            verification_method=verification_method,
            parent=parent,
            logger=logger,
        )

        if available_options_hook is not None:
            self.attach(available_options_hook, to_key="available_options", initial_sync_mode=InitialSyncMode.PULL_FROM_TARGET)
        
        if selected_options_hook is not None:
            self.attach(selected_options_hook, to_key="selected_options", initial_sync_mode=InitialSyncMode.PULL_FROM_TARGET)

    @property
    def can_be_disabled(self) -> bool:
        """Whether the controller can be disabled."""
        return True

    ###########################################################################
    # Widget methods
    ###########################################################################

    def _initialize_widgets(self) -> None:
        self._available_list = GuardedListWidget(self)
        self._selected_list = GuardedListWidget(self)
        self._available_list.setSelectionMode(GuardedListWidget.SelectionMode.ExtendedSelection)
        self._selected_list.setSelectionMode(GuardedListWidget.SelectionMode.ExtendedSelection)

        self._button_move_to_selected = QPushButton("move to selected", self._owner_widget)
        self._button_remove_from_selected = QPushButton("remove from selected", self._owner_widget)
        self._button_move_to_selected.setToolTip("Move selected items to the selected list")
        self._button_remove_from_selected.setToolTip("Remove selected items from the selected list")
        self._button_move_to_selected.clicked.connect(self._on_move_to_selected)
        self._button_remove_from_selected.clicked.connect(self._on_move_to_available)

        # Update move button enabled state on selection change
        self._available_list.itemSelectionChanged.connect(self._update_button_states)
        self._selected_list.itemSelectionChanged.connect(self._update_button_states)

    def _disable_widgets(self) -> None:
        self._available_list.setEnabled(False)
        self._selected_list.setEnabled(False)
        self._button_remove_from_selected.setEnabled(False)
        self._button_move_to_selected.setEnabled(False)

    def _enable_widgets(self, initial_component_values: dict[Literal["selected_options", "available_options"], Any]) -> None:
        self._available_list.setEnabled(True)
        self._selected_list.setEnabled(True)
        self._button_remove_from_selected.setEnabled(True)
        self._button_move_to_selected.setEnabled(True)
        self.__internal_apply_component_values_to_widgets(initial_component_values)

    def _on_move_to_selected(self) -> None:
        if self.is_blocking_signals:
            return
        self._move(selected_from=self._available_list, direction=">")

    def _on_move_to_available(self) -> None:
        if self.is_blocking_signals:
            return
        self._move(selected_from=self._selected_list, direction="<")

    def _fill_widgets_from_component_values(self, component_values: dict[Literal["selected_options", "available_options"], Any]) -> None:
        options_as_reference: set[T] = component_values["available_options"]
        selected_as_reference: set[T] = component_values["selected_options"]

        available: list[T] = [v for v in options_as_reference if v not in selected_as_reference]
        selected: list[T] = [v for v in selected_as_reference if v in options_as_reference]

        self._available_list.blockSignals(True)
        self._selected_list.blockSignals(True)
        try:
            self._available_list.clear()
            self._selected_list.clear()
            for v in sorted(available, key=lambda x: str(x)):
                item = QListWidgetItem(str(v), self._available_list)
                item.setData(Qt.ItemDataRole.UserRole, v)
            for v in sorted(selected, key=lambda x: str(x)):
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

    def _move(self, selected_from: GuardedListWidget, direction: str) -> None:
        """Move selected items between lists."""
        # Collect items to move
        items = list(selected_from.selectedItems())
        if not items:
            return
        # Compute new selected set
        try:
            current_selected: set[T] = self._get_component_value_reference("selected_options")
            assert isinstance(current_selected, set)
        except Exception:
            current_selected = set()
        members: list[T] = [it.data(Qt.ItemDataRole.UserRole) for it in items]
        if direction == ">":
            new_selected = current_selected.union(members)
        else:
            new_selected = {v for v in current_selected if v not in members}
        # Apply to component values
        self._update_component_values_and_widgets({"selected_options": new_selected})

    ###########################################################################
    # Public API
    ###########################################################################

    def set_selected_options_and_available_options(self, selected_options: set[T], available_options: set[T]) -> None:
        """Set the selected options and available options."""
        self._update_component_values_and_widgets({"selected_options": selected_options, "available_options": available_options})

    def add_selected_option(self, option: T) -> None:
        """Add an option to the selected options."""
        selected_options_reference: set[T] = self._get_component_value_reference("selected_options")
        assert isinstance(selected_options_reference, set)  
        self._update_component_values_and_widgets({"selected_options": selected_options_reference.union({option})})
    
    def remove_selected_option(self, option: T) -> None:
        """Remove an option from the selected options."""
        selected_options_reference: set[T] = self._get_component_value_reference("selected_options")
        assert isinstance(selected_options_reference, set)
        self._update_component_values_and_widgets({"selected_options": selected_options_reference.difference({option})})

    @property
    def selected_options(self) -> set[T]:
        """Get the currently selected options."""
        selected_options_reference: set[T] = self._get_component_value_reference("selected_options")
        assert isinstance(selected_options_reference, set)
        return selected_options_reference.copy()

    @selected_options.setter
    def selected_options(self, options: set[T]) -> None:
        """Set the selected options."""
        self._update_component_values_and_widgets({"selected_options": options})

    @property
    def available_options(self) -> set[T]:
        """Get the available options."""
        available_options_reference: set[T] = self._get_component_value_reference("available_options")
        assert isinstance(available_options_reference, set)
        return available_options_reference.copy()

    @available_options.setter
    def available_options(self, options: set[T]) -> None:
        """Set the available options."""
        self._update_component_values_and_widgets({"available_options": options})

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
    def widget_available_list(self) -> GuardedListWidget:
        """Get the available list widget."""
        return self._available_list

    @property
    def widget_selected_list(self) -> GuardedListWidget:
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


