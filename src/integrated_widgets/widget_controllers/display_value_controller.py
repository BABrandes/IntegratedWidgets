from __future__ import annotations

from typing import Any, Optional
from PySide6.QtWidgets import QWidget

from integrated_widgets.widget_controllers.base_controller import BaseObservableController
from integrated_widgets.guarded_widgets.guarded_label import GuardedLabel
from observables import HookLike, ObservableSingleValueLike, CarriesDistinctSingleValueHook, InitialSyncMode


class DisplayValueController(BaseObservableController, ObservableSingleValueLike[Any]):
    """Controller for displaying a value with a read-only label."""

    @classmethod
    def _mandatory_component_value_keys(cls) -> set[str]:
        return {"value"}

    def __init__(self, value: Any | HookLike[Any], parent: Optional[QWidget] = None) -> None:
        # Handle different types of value input
        if isinstance(value, HookLike):
            # It's a hook - get initial value
            initial_value: Any = value.value
            value_hook: Optional[HookLike[Any]] = value
        elif isinstance(value, CarriesDistinctSingleValueHook):
            # It's a hook - get initial value
            initial_value: Any = value.distinct_single_value_reference
            value_hook: Optional[HookLike[Any]] = value.distinct_single_value_hook
        elif isinstance(value, ObservableSingleValueLike):
            # It's an ObservableSingleValue - get initial value
            initial_value: Any = value.distinct_single_value_reference
            value_hook: Optional[HookLike[Any]] = value.distinct_single_value_hook
        else:
            # It's a direct value
            initial_value = value
            value_hook = None
        
        super().__init__(
            {"value": initial_value},
            parent=parent
        )

        if value_hook is not None:
            self.bind_to(value_hook)

    def initialize_widgets(self) -> None:
        """Initialize the display label widget."""
        self._label = GuardedLabel(self)
        # Note: Base controller automatically calls update_widgets_from_component_values() after this

    def update_widgets_from_component_values(self) -> None:
        """Update the label from component values."""
        print(f"DEBUG: DisplayValueController.update_widgets_from_component_values called")
        if hasattr(self, '_label'):
            current_value = self._component_values["value"]
            print(f"DEBUG: DisplayValueController._update_label called, current_value={current_value}")
            with self._internal_update():
                self._label.setText(str(current_value))
                print(f"DEBUG: DisplayValueController._update_label set label text to: {str(current_value)}")

    def update_component_values_from_widgets(self) -> None:
        """Update the component values from the widgets."""
        # This is a read-only controller, so this method does nothing
        print(f"DEBUG: DisplayValueController.update_component_values_from_widgets called (no-op)")
        pass

    def _on_component_values_changed(self) -> None:
        """Handle component value changes and trigger widget updates."""
        self.update_widgets_from_component_values()

    ###########################################################################
    # Binding Methods
    ###########################################################################

    def bind_to(self, observable_or_hook: ObservableSingleValueLike[Any] | HookLike[Any] | CarriesDistinctSingleValueHook[Any], initial_sync_mode: InitialSyncMode = InitialSyncMode.SELF_IS_UPDATED) -> None:
        """Establish a bidirectional binding with another observable or hook."""
        print(f"DEBUG: DisplayValueController.bind_to called with {observable_or_hook}, sync_mode={initial_sync_mode}")
        if isinstance(observable_or_hook, CarriesDistinctSingleValueHook):
            observable_or_hook = observable_or_hook.distinct_single_value_hook
            print(f"DEBUG: Converted CarriesDistinctSingleValueHook to distinct_single_value_hook: {observable_or_hook}")
        elif isinstance(observable_or_hook, ObservableSingleValueLike):
            observable_or_hook = observable_or_hook.distinct_single_value_hook
            print(f"DEBUG: Converted ObservableSingleValueLike to distinct_single_value_hook: {observable_or_hook}")
        else:
            print(f"DEBUG: Using observable_or_hook directly: {observable_or_hook}")
        
        print(f"DEBUG: About to connect {self.distinct_single_value_hook} to {observable_or_hook}")
        self.distinct_single_value_hook.connect_to(observable_or_hook, initial_sync_mode)
        print(f"DEBUG: Binding completed successfully")

    def detach(self) -> None:
        """Remove the bidirectional binding with another observable."""
        self.distinct_single_value_hook.detach()

    ###########################################################################
    # Hook Implementation
    ###########################################################################

    @property
    def distinct_single_value_hook(self) -> HookLike[Any]:
        """Get the hook for the display value (read-only)."""
        return self._component_hooks["value"]
    
    @property
    def distinct_single_value_reference(self) -> Any:
        """Get the reference for the display value."""
        return self._component_values["value"]

    ###########################################################################
    # Public API
    ###########################################################################

    @property
    def widget_label(self) -> GuardedLabel:
        """Get the display label widget."""
        return self._label

    @property
    def single_value(self) -> Any:
        """Get the current display value."""
        return self.distinct_single_value_reference