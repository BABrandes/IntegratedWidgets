from __future__ import annotations

from typing import Optional, overload, Callable, Any, Mapping

from PySide6.QtWidgets import QWidget

from integrated_widgets.widget_controllers.base_controller import BaseObservableController
from observables import ObservableSingleValueLike, InitialSyncMode, HookLike, CarriesDistinctSingleValueHook
from integrated_widgets.guarded_widgets import GuardedCheckBox


class CheckBoxController(BaseObservableController, ObservableSingleValueLike[bool]):

    @classmethod
    def _mandatory_component_value_keys(cls) -> set[str]:
        """Get the mandatory component value keys for this controller."""
        return {"value"}

    @overload
    def __init__(
        self,
        value: bool,
        *,
        text: str = "",
        parent: Optional[QWidget] = None,
    ) -> None: ...

    @overload
    def __init__(
        self,
        observable_or_hook: CarriesDistinctSingleValueHook[bool, Any]|HookLike[bool]|ObservableSingleValueLike[bool],
        *,
        text: str = "",
        parent: Optional[QWidget] = None,
    ) -> None: ...

    def __init__(  # type: ignore
        self,
        value_or_observable_or_hook,
        *,
        text: str = "",
        parent: Optional[QWidget] = None,
    ) -> None:

        self._text = text
        
        # Handle different types of value_or_observable_or_hook
        if isinstance(value_or_observable_or_hook, HookLike):
            # It's a hook - get initial value
            initial_value: bool = value_or_observable_or_hook.value # type: ignore
            value_hook: Optional[HookLike[bool]] = value_or_observable_or_hook
        elif isinstance(value_or_observable_or_hook, CarriesDistinctSingleValueHook):
            initial_value: bool = value_or_observable_or_hook.distinct_single_value_reference
            value_hook: Optional[HookLike[bool]] = value_or_observable_or_hook.distinct_single_value_hook
        elif isinstance(value_or_observable_or_hook, ObservableSingleValueLike):
            # It's an ObservableSingleValue - get initial value
            initial_value: bool = value_or_observable_or_hook.distinct_single_value_reference
            value_hook: Optional[HookLike[bool]] = value_or_observable_or_hook.distinct_single_value_hook
        elif isinstance(value_or_observable_or_hook, bool):
            # It's a direct value
            initial_value = bool(value_or_observable_or_hook)
            value_hook: Optional[HookLike[bool]] = None
        else:
            raise ValueError(f"Invalid value: {value_or_observable_or_hook}")
        
        def verification_method(x: Mapping[str, Any]) -> tuple[bool, str]:
            # Verify the value is a boolean
            current_value = x.get("value", initial_value)
            if not isinstance(current_value, bool):
                return False, f"Value must be a boolean, got {type(current_value)}"
            return True, "Verification method passed"

        super().__init__(
            {"value": initial_value},
            verification_method=verification_method,
            parent=parent
        )

        if value_hook is not None:
            self.attach(value_hook, to_key="value", initial_sync_mode=InitialSyncMode.SELF_IS_UPDATED)

        # Update the widget text if provided
        if text:
            self._check.setText(text)

    ###########################################################################
    # Hook Implementation
    ###########################################################################

    @property
    def distinct_single_value_hook(self) -> HookLike[bool]:
        """Get the hook for the single value."""
        return self._component_hooks["value"]
    
    @property
    def distinct_single_value_reference(self) -> bool:
        """Get the reference for the single value."""
        return self._component_values["value"]
    
    @distinct_single_value_reference.setter
    def distinct_single_value_reference(self, value: bool) -> None:
        """Set the reference for the single value."""
        self._set_component_values({"value": value}, notify_binding_system=True)

    def initialize_widgets(self) -> None:
        self._check = GuardedCheckBox(self, self._text)
        self._check.stateChanged.connect(lambda _s: self._on_changed())

    def update_widgets_from_component_values(self) -> None:
        """Update the check box from the component values."""
        if not hasattr(self, '_check'):
            return
            
        self._check.blockSignals(True)
        try:
            self._check.setChecked(self.distinct_single_value_reference)
        finally:
            self._check.blockSignals(False)

    def update_component_values_from_widgets(self) -> None:
        """Update the component values from the check box."""
        self._set_component_values({"value": self._check.isChecked()}, notify_binding_system=True)

    def _on_changed(self) -> None:
        """Handle check box state change."""
        if self.is_blocking_signals:
            return
        self.update_component_values_from_widgets()

    ###########################################################################
    # Public API
    ###########################################################################
    
    @property
    def single_value(self) -> bool:
        """Get the current value of the check box."""
        return self.distinct_single_value_reference
    
    @single_value.setter
    def single_value(self, value: bool) -> None:
        """Set the value of the check box."""
        self._set_component_values({"value": value}, notify_binding_system=True)

    @property
    def widget_check_box(self) -> GuardedCheckBox:
        """Get the check box widget."""
        return self._check


