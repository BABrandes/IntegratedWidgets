from __future__ import annotations

from typing import Optional, overload, Callable, Any, Mapping

from PySide6.QtWidgets import QWidget

from integrated_widgets.widget_controllers.base_controller import BaseObservableController
from observables import ObservableSingleValueLike, SyncMode, HookLike, Hook, CarriesDistinctSingleValueHook
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
        observable_or_hook: CarriesDistinctSingleValueHook[bool]|HookLike[bool],
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
            initial_value: bool = value_or_observable_or_hook._get_single_value()
            value_hook: Optional[HookLike[bool]] = value_or_observable_or_hook._get_single_value_hook()
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
            {
                "value": initial_value
            },
            {
                "value": Hook(self, self._get_single_value, self._set_single_value)
            },
            verification_method=verification_method,
            parent=parent
        )

        if value_hook is not None:
            self.bind_to(value_hook)

    ###########################################################################
    # Binding Methods
    ###########################################################################

    def bind_to(self, observable_or_hook: CarriesDistinctSingleValueHook[bool]|HookLike[bool], initial_sync_mode: SyncMode = SyncMode.UPDATE_SELF_FROM_OBSERVABLE) -> None:
        """Establish a bidirectional binding with another observable or hook."""
        if isinstance(observable_or_hook, CarriesDistinctSingleValueHook):
            observable_or_hook = observable_or_hook._get_single_value_hook()
        self._get_single_value_hook().establish_binding(observable_or_hook, initial_sync_mode)

    def unbind_from(self, observable_or_hook: CarriesDistinctSingleValueHook[bool]|HookLike[bool]) -> None:
        """Remove the bidirectional binding with another observable."""
        if isinstance(observable_or_hook, CarriesDistinctSingleValueHook):
            observable_or_hook = observable_or_hook._get_single_value_hook()
        self._get_single_value_hook().remove_binding(observable_or_hook)

    def _on_value_changed(self) -> None:
        """Handle changes in the bound value."""
        self._set_component_value("value", self._get_single_value())
        self.update_widgets_from_component_values()

    ###########################################################################
    # Hook Implementation
    ###########################################################################

    def _get_single_value(self) -> bool:
        """Get the current boolean value."""
        return self._get_component_value("value")

    def _get_single_value_hook(self) -> HookLike[bool]:
        """Get self as a hook for binding."""
        return self._component_hooks["value"]

    def _set_single_value(self, value: bool) -> None:
        """Set the boolean value."""
        self._set_component_value("value", bool(value))

    def initialize_widgets(self) -> None:
        self._check = GuardedCheckBox(self, self._text)
        self._check.stateChanged.connect(lambda _s: self._on_changed())

    def update_widgets_from_component_values(self) -> None:
        """Update the check box from the component values."""
        if not hasattr(self, '_check'):
            return
            
        self._check.blockSignals(True)
        try:
            self._check.setChecked(self._get_single_value())
        finally:
            self._check.blockSignals(False)

    def update_component_values_from_widgets(self) -> None:
        """Update the component values from the check box."""
        self._set_single_value(self._check.isChecked())

    def _on_changed(self) -> None:
        """Handle check box state change."""
        if self.is_blocking_signals:
            return
        self.update_component_values_from_widgets()

    ###########################################################################
    # Public API
    ###########################################################################

    @property
    def value(self) -> bool:
        """Get the current boolean value."""
        return self._get_single_value()

    @value.setter
    def value(self, new_value: bool) -> None:
        """Set the boolean value."""
        self._set_single_value(new_value)

    @property
    def widget_check_box(self) -> GuardedCheckBox:
        """Get the check box widget."""
        return self._check


