from __future__ import annotations

from typing import Generic, Optional, TypeVar, Any, Mapping, overload

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QPushButton, QListWidgetItem

from integrated_widgets.widget_controllers.base_controller import BaseObservableController
from observables import ObservableMultiSelectionOptionLike, CarriesDistinctSetHook, HookLike, InitialSyncMode
from integrated_widgets.guarded_widgets import GuardedListWidget


T = TypeVar("T")


class DoubleListSelectionController(BaseObservableController, ObservableMultiSelectionOptionLike[T], Generic[T]):

    @classmethod
    def _mandatory_component_value_keys(cls) -> set[str]:
        """Get the mandatory component value keys for this controller."""
        return {"selected_options", "available_options"}
    """Controller providing two list views and two move buttons to manage a multi-selection.

    Left list shows available (unselected) items.
    Right list shows selected items.
    '>' moves selected items from left to right (adds to selected_options).
    '<' moves selected items from right to left (removes from selected_options).
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
        available_options: CarriesDistinctSetHook[T] | HookLike[set[T]],
        parent: Optional[QWidget] = None,
    ) -> None: ...

    @overload
    def __init__(
        self,
        selected_options: CarriesDistinctSetHook[T] | HookLike[set[T]],
        available_options: set[T],
        parent: Optional[QWidget] = None,
    ) -> None: ...

    @overload
    def __init__(
        self,
        selected_options: CarriesDistinctSetHook[T] | HookLike[set[T]],
        available_options: CarriesDistinctSetHook[T] | HookLike[set[T]],
        parent: Optional[QWidget] = None,
    ) -> None: ...

    def __init__(
        self,
        selected_options,
        available_options,
        parent: Optional[QWidget] = None,
    ) -> None:
        
        # Handle different types of selected_options and available_options
        if isinstance(selected_options, CarriesDistinctSetHook):
            # It's a hook - get initial value
            initial_selected_options: set[T] = selected_options.distinct_set_reference
            selected_options_hook: Optional[HookLike[set[T]]] = selected_options.distinct_set_hook
        elif isinstance(selected_options, HookLike):
            # It's a hook - get initial value
            initial_selected_options: set[T] = selected_options.value # type: ignore
            selected_options_hook: Optional[HookLike[set[T]]] = selected_options
        elif isinstance(selected_options, set):
            # It's a direct set
            initial_selected_options = set(selected_options) if selected_options else set()
            selected_options_hook: Optional[HookLike[set[T]]] = None
        else:
            raise ValueError(f"Invalid selected_options: {selected_options}")
        
        if isinstance(available_options, CarriesDistinctSetHook):
            # It's a hook - get initial value
            available_options_set = available_options.distinct_set_reference
            available_options_hook: Optional[HookLike[set[T]]] = available_options.distinct_set_hook
        elif isinstance(available_options, HookLike):
            # It's a hook - get initial value
            available_options_set = available_options.value # type: ignore
            available_options_hook: Optional[HookLike[set[T]]] = available_options
        elif isinstance(available_options, set):
            # It's a direct set
            available_options_set = set(available_options) if available_options else set()
            available_options_hook: Optional[HookLike[set[T]]] = None
        else:
            raise ValueError(f"Invalid available_options: {available_options}")
        
        def verification_method(x: Mapping[str, Any]) -> tuple[bool, str]:
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
            parent=parent
        )
        
        if available_options_hook is not None:
            self.bind_available_options_to(available_options_hook)
            
        if selected_options_hook is not None:
            self.bind_selected_options_to(selected_options_hook)

    ###########################################################################
    # Binding Methods
    ###########################################################################

    def bind_available_options_to(self, hook: CarriesDistinctSetHook[T] | HookLike[set[T]], initial_sync_mode: InitialSyncMode = InitialSyncMode.SELF_IS_UPDATED) -> None:
        """Establish a bidirectional binding for the available options set with another observable."""
        if isinstance(hook, CarriesDistinctSetHook):
            hook = hook.distinct_set_hook
        self.distinct_available_options_hook.connect_to(hook, initial_sync_mode)

    def bind_selected_options_to(self, hook: CarriesDistinctSetHook[T] | HookLike[set[T]], initial_sync_mode: InitialSyncMode = InitialSyncMode.SELF_IS_UPDATED) -> None:
        """Establish a bidirectional binding for the selected options set with another observable."""
        if isinstance(hook, CarriesDistinctSetHook):
            hook = hook.distinct_set_hook
        self.distinct_selected_options_hook.connect_to(hook, initial_sync_mode)

    def bind_to(self, observable: ObservableMultiSelectionOptionLike[T], initial_sync_mode: InitialSyncMode = InitialSyncMode.SELF_IS_UPDATED) -> None:
        """Establish a bidirectional binding with another observable."""
        if initial_sync_mode == InitialSyncMode.SELF_IS_UPDATED:
            self.set_selected_options_and_available_options(
                observable.selected_options,
                observable.available_options
            )
        elif initial_sync_mode == InitialSyncMode.SELF_UPDATES:
            observable.set_selected_options_and_available_options(
                self.selected_options,
                self.available_options
            )
        else:
            raise ValueError(f"Invalid initial sync mode: {initial_sync_mode}")
        
        self.bind_selected_options_to(observable.selected_options_hook, initial_sync_mode)
        self.bind_available_options_to(observable.available_options_hook, initial_sync_mode)

    def detach(self) -> None:
        self.distinct_selected_options_hook.detach()
        self.distinct_available_options_hook.detach()

    ###########################################################################
    # Hook Implementation
    ###########################################################################

    @property
    def distinct_selected_options_hook(self) -> HookLike[set[T]]:
        """Get the hook for the selected options set."""
        return self._component_hooks["selected_options"]
    
    @property
    def distinct_selected_options_reference(self) -> set[T]:
        """Get the reference for the selected options set."""
        return self._component_values["selected_options"]
    
    @property
    def distinct_available_options_hook(self) -> HookLike[set[T]]:
        """Get the hook for the available options set."""
        return self._component_hooks["available_options"]
    
    @property
    def distinct_available_options_reference(self) -> set[T]:
        """Get the reference for the available options set."""
        return self._component_values["available_options"]
    
    @property
    def selected_options_hook(self) -> HookLike[set[T]]:
        """Get the hook for the selected options set."""
        return self.distinct_selected_options_hook
    
    @property
    def available_options_hook(self) -> HookLike[set[T]]:
        """Get the hook for the available options set."""
        return self.distinct_available_options_hook

    def initialize_widgets(self) -> None:
        self._left = GuardedListWidget(self)
        self._right = GuardedListWidget(self)
        self._left.setSelectionMode(GuardedListWidget.SelectionMode.ExtendedSelection)
        self._right.setSelectionMode(GuardedListWidget.SelectionMode.ExtendedSelection)

        self._to_right = QPushButton(">", self._owner_widget)
        self._to_left = QPushButton("<", self._owner_widget)
        self._to_right.clicked.connect(self._on_move_to_right)
        self._to_left.clicked.connect(self._on_move_to_left)

        # Update move button enabled state on selection change
        self._left.itemSelectionChanged.connect(self._update_button_states)
        self._right.itemSelectionChanged.connect(self._update_button_states)

    def update_widgets_from_component_values(self) -> None:
        """Update the widgets from the component values."""
        if not hasattr(self, '_left'):
            return
            
        # Build left = options - selected, right = selected
        try:
            options = self.distinct_available_options_reference
        except Exception:
            options = set()
        try:
            selected = self.distinct_selected_options_reference
        except Exception:
            selected = set()
        available = [v for v in options if v not in selected]
        # Rebuild lists
        with self._internal_update():
            self._left.blockSignals(True)
            self._right.blockSignals(True)
            try:
                self._left.clear()
                self._right.clear()
                for v in sorted(available, key=lambda x: str(x)):
                    item = QListWidgetItem(str(v), self._left)
                    item.setData(Qt.ItemDataRole.UserRole, v)
                for v in sorted(selected, key=lambda x: str(x)):
                    item = QListWidgetItem(str(v), self._right)
                    item.setData(Qt.ItemDataRole.UserRole, v)
            finally:
                self._left.blockSignals(False)
                self._right.blockSignals(False)
        self._update_button_states()

    def update_component_values_from_widgets(self) -> None:
        """Update the component values from the widgets."""
        # Not used directly; mutations happen in move handlers
        pass

    ###########################################################################
    # Internal
    ###########################################################################
    def _update_button_states(self) -> None:
        self._to_right.setEnabled(len(self._left.selectedItems()) > 0)
        self._to_left.setEnabled(len(self._right.selectedItems()) > 0)

    def _on_move_to_right(self) -> None:
        if self.is_blocking_signals:
            return
        self._move(selected_from=self._left, direction=">")

    def _on_move_to_left(self) -> None:
        if self.is_blocking_signals:
            return
        self._move(selected_from=self._right, direction="<")

    def _move(self, selected_from: GuardedListWidget, direction: str) -> None:
        """Move selected items between lists."""
        # Collect items to move
        items = list(selected_from.selectedItems())
        if not items:
            return
        # Compute new selected set
        try:
            current_selected = self.distinct_selected_options_reference
        except Exception:
            current_selected = set()
        members = [it.data(Qt.ItemDataRole.UserRole) for it in items]
        if direction == ">":
            new_selected = current_selected.union(members)
        else:
            new_selected = {v for v in current_selected if v not in members}
        # Apply to component values
        self._set_component_values(
            {"selected_options": new_selected},
            notify_binding_system=True
        )
        # Rebuild UI from component values

    ###########################################################################
    # Public API
    ###########################################################################

    def set_selected_options_and_available_options(self, selected_options: set[T], available_options: set[T]) -> None:
        """Set the selected options and available options."""
        self._set_component_values(
            {"selected_options": selected_options, "available_options": available_options},
            notify_binding_system=False
        )

    def add_selected_option(self, option: T) -> None:
        """Add an option to the selected options."""
        self._set_component_values(
            {"selected_options": self.distinct_selected_options_reference.union({option})},
            notify_binding_system=True
        )
    
    def remove_selected_option(self, option: T) -> None:
        """Remove an option from the selected options."""
        self._set_component_values(
            {"selected_options": self.distinct_selected_options_reference.difference({option})},
            notify_binding_system=True
        )

    @property
    def selected_options(self) -> set[T]:
        """Get the currently selected options."""
        return self.distinct_selected_options_reference

    @selected_options.setter
    def selected_options(self, options: set[T]) -> None:
        """Set the selected options."""
        self._set_component_values(
            {"selected_options": options},
            notify_binding_system=True
        )

    @property
    def available_options(self) -> set[T]:
        """Get the available options."""
        return self.distinct_available_options_reference

    @available_options.setter
    def available_options(self, options: set[T]) -> None:
        """Set the available options."""
        self._set_component_values(
            {"available_options": options},
            notify_binding_system=True
        )

    ###########################################################################
    # Public accessors
    ###########################################################################
    @property
    def widget_left_list(self) -> GuardedListWidget:
        """Get the left list widget."""
        return self._left

    @property
    def widget_right_list(self) -> GuardedListWidget:
        """Get the right list widget."""
        return self._right

    @property
    def widget_to_right_button(self) -> QPushButton:
        """Get the move to right button."""
        return self._to_right

    @property
    def widget_to_left_button(self) -> QPushButton:
        """Get the move to left button."""
        return self._to_left

    ###########################################################################
    # Disposal
    ###########################################################################
    def dispose_before_children(self) -> None:
        try:
            self._to_right.clicked.disconnect()
        except Exception:
            pass
        try:
            self._to_left.clicked.disconnect()
        except Exception:
            pass
        try:
            self._left.itemSelectionChanged.disconnect()
        except Exception:
            pass
        try:
            self._right.itemSelectionChanged.disconnect()
        except Exception:
            pass


