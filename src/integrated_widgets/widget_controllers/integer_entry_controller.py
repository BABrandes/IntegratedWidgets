from __future__ import annotations

from typing import Callable, Optional, overload, Any, Mapping

from PySide6.QtWidgets import QWidget

from integrated_widgets.widget_controllers.base_controller import BaseObservableController
from observables import ObservableSingleValueLike, Hook, SyncMode, HookLike, CarriesDistinctSingleValueHook
from integrated_widgets.guarded_widgets import GuardedLineEdit


class IntegerEntryController(BaseObservableController, ObservableSingleValueLike[int]):

    @classmethod
    def _mandatory_component_value_keys(cls) -> set[str]:
        """Get the mandatory component value keys for this controller."""
        return {"value"}

    @overload
    def __init__(
        self,
        value: int,
        *,
        validator: Optional[Callable[[int], bool]] = None,
        parent: Optional[QWidget] = None,
    ) -> None: ...

    @overload
    def __init__(
        self,
        value: ObservableSingleValueLike[int] | HookLike[int] | CarriesDistinctSingleValueHook[int],
        *,
        validator: Optional[Callable[[int], bool]] = None,
        parent: Optional[QWidget] = None,
    ) -> None: ...

    def __init__(
        self,
        value,
        *,
        validator: Optional[Callable[[int], bool]] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        
        self._validator = validator
        
        # Handle different types of value
        if isinstance(value, HookLike):
            # It's a hook - get initial value
            initial_value: int = value.value  # type: ignore
            value_hook: Optional[HookLike[int]] = value
        elif isinstance(value, CarriesDistinctSingleValueHook):
            # It's a hook - get initial value
            initial_value: int = value._get_single_value()
            value_hook: Optional[HookLike[int]] = value._get_single_value_hook()
        elif isinstance(value, int):
            # It's a direct value
            initial_value = int(value)
            value_hook: Optional[HookLike[int]] = None
        else:
            raise ValueError(f"Invalid value: {value}")
        
        def verification_method(x: Mapping[str, Any]) -> tuple[bool, str]:
            # Verify the value is an integer
            current_value = x.get("value", initial_value)
            if not isinstance(current_value, int):
                return False, f"Value must be an integer, got {type(current_value)}"
            if self._validator is not None and not self._validator(current_value):
                return False, f"Value {current_value} failed validation"
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
        
        # Store hook for later binding
        self._value_hook = value_hook
        
        if value_hook is not None:
            self.bind_to(value_hook)

    ###########################################################################
    # Binding Methods
    ###########################################################################

    def bind_to(self, observable_or_hook: ObservableSingleValueLike[int] | HookLike[int] | CarriesDistinctSingleValueHook[int], initial_sync_mode: SyncMode = SyncMode.UPDATE_SELF_FROM_OBSERVABLE) -> None:
        """Establish a bidirectional binding with another observable or hook."""
        if isinstance(observable_or_hook, CarriesDistinctSingleValueHook):
            observable_or_hook = observable_or_hook._get_single_value_hook()
        self._get_single_value_hook().establish_binding(observable_or_hook, initial_sync_mode)

    def unbind_from(self, observable_or_hook: ObservableSingleValueLike[int] | HookLike[int] | CarriesDistinctSingleValueHook[int]) -> None:
        """Remove the bidirectional binding with another observable."""
        if isinstance(observable_or_hook, CarriesDistinctSingleValueHook):
            observable_or_hook = observable_or_hook._get_single_value_hook()
        self._get_single_value_hook().remove_binding(observable_or_hook)

    ###########################################################################
    # Hook Implementation
    ###########################################################################

    def _get_single_value(self) -> int:
        """Get the current integer value."""
        return self._get_component_value("value")

    def _get_single_value_hook(self) -> HookLike[int]:
        """Get self as a hook for binding."""
        return self._component_hooks["value"]

    def _set_single_value(self, value: int) -> None:
        """Set the integer value."""
        self._set_component_value("value", int(value))

    def initialize_widgets(self) -> None:
        self._edit = GuardedLineEdit(self._owner_widget)
        self._edit.editingFinished.connect(self._on_edited)

    def update_widgets_from_component_values(self) -> None:
        """Update the line edit from the component values."""
        if not hasattr(self, '_edit'):
            return
            
        self._edit.blockSignals(True)
        try:
            self._edit.setText(str(self._get_single_value()))
        finally:
            self._edit.blockSignals(False)

    def update_component_values_from_widgets(self) -> None:
        """Update the component values from the line edit."""
        try:
            value = int(self._edit.text().strip())
            if self._validator is not None and not self._validator(value):
                self.update_widgets_from_component_values()
                return
        except Exception:
            self.update_widgets_from_component_values()
            return
        self._set_single_value(value)

    def _on_edited(self) -> None:
        """Handle line edit editing finished."""
        if self.is_blocking_signals:
            return
        self.update_component_values_from_widgets()

    ###########################################################################
    # Public API
    ###########################################################################

    @property
    def value(self) -> int:
        """Get the current integer value."""
        return self._get_single_value()

    @value.setter
    def value(self, new_value: int) -> None:
        """Set the integer value."""
        self._set_single_value(new_value)

    @property
    def widget_line_edit(self) -> GuardedLineEdit:
        """Get the line edit widget."""
        return self._edit


