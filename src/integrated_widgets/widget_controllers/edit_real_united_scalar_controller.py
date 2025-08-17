from __future__ import annotations

from typing import Callable, Optional, overload

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget

from united_system import RealUnitedScalar, Unit, Dimension

from integrated_widgets.widget_controllers.base_controller import BaseObservableController
from observables import ObservableSingleValueLike, HookLike, InitialSyncMode
from observables import CarriesDistinctSingleValueHook
from integrated_widgets.guarded_widgets import GuardedLineEdit, GuardedLabel
from integrated_widgets.util.general import DEFAULT_FLOAT_FORMAT_VALUE

class EditRealUnitedScalarController(BaseObservableController, ObservableSingleValueLike[RealUnitedScalar]):

    @classmethod
    def _mandatory_component_value_keys(cls) -> set[str]:
        """Get the mandatory component value keys for this controller."""
        return {"value"}

    @overload
    def __init__(
        self,
        value: RealUnitedScalar,
        *,
        allowed_dimension: Optional[Dimension] = None,
        validator: Optional[Callable[[RealUnitedScalar], bool]] = None,
        formatter: Callable[[RealUnitedScalar], str] = DEFAULT_FLOAT_FORMAT_VALUE,
        parent: Optional[QWidget] = None,
    ) -> None: ...

    @overload
    def __init__(
        self,
        observable_or_hook: ObservableSingleValueLike[RealUnitedScalar] | HookLike[RealUnitedScalar],
        *,
        allowed_dimension: Optional[Dimension] = None,
        validator: Optional[Callable[[RealUnitedScalar], bool]] = None,
        formatter: Callable[[RealUnitedScalar], str] = DEFAULT_FLOAT_FORMAT_VALUE,
        parent: Optional[QWidget] = None,
    ) -> None: ...

    def __init__(  # type: ignore
        self,
        value_or_observable_or_hook,
        *,
        allowed_dimension: Optional[Dimension] = None,
        validator: Optional[Callable[[RealUnitedScalar], bool]] = None,
        formatter: Callable[[RealUnitedScalar], str] = DEFAULT_FLOAT_FORMAT_VALUE,
        parent: Optional[QWidget] = None,
    ) -> None:
        
        # Handle different types of value_or_observable_or_hook
        if isinstance(value_or_observable_or_hook, RealUnitedScalar):
            initial_value: RealUnitedScalar = value_or_observable_or_hook
            value_hook: Optional[HookLike[RealUnitedScalar]] = None
        elif isinstance(value_or_observable_or_hook, HookLike):
            # It's a hook - set it and get initial value
            initial_value = value_or_observable_or_hook.value  # type: ignore
            value_hook: Optional[HookLike[RealUnitedScalar]] = value_or_observable_or_hook
        elif isinstance(value_or_observable_or_hook, ObservableSingleValueLike):
            initial_value: RealUnitedScalar = value_or_observable_or_hook.distinct_single_value_reference
            value_hook: Optional[HookLike[RealUnitedScalar]] = value_or_observable_or_hook.distinct_single_value_hook
        else:
            raise TypeError(f"Invalid type for value_or_observable_or_hook: {type(value_or_observable_or_hook)}")

        self._allowed_dimension = allowed_dimension
        self._validator = validator
        self._formatter = formatter 

        super().__init__(
            {"value": initial_value},
            parent=parent
        )

        if value_hook is not None:
            self.bind_to(value_hook)

    ###########################################################################
    # Hooks
    ###########################################################################

    @property
    def distinct_single_value_hook(self) -> HookLike[RealUnitedScalar]:
        """Get the hook for the single value."""
        return self._component_hooks["value"]
    
    @property
    def distinct_single_value_reference(self) -> RealUnitedScalar:
        """Get the reference for the single value."""
        return self._component_values["value"]

    ###########################################################################
    # Widget Management
    ###########################################################################

    def initialize_widgets(self) -> None:
        # Display label for the full RealUnitedScalar (e.g., "10.000 m")
        self._display_label = GuardedLabel(self)
        with self._internal_update():
            self._display_label.setText("")
        # Separate edits for value and unit
        self._value_edit = GuardedLineEdit(self)
        self._value_edit.setPlaceholderText("value (e.g., 10)")
        self._unit_edit = GuardedLineEdit(self)
        self._unit_edit.setPlaceholderText("unit (e.g., m, km, V)")
        # Combined entry that accepts strings like "10 m"
        self._combined_edit = GuardedLineEdit(self)
        self._combined_edit.setPlaceholderText("value with unit (e.g., 10 m)")
        # Connect UI -> model
        self._value_edit.editingFinished.connect(self._on_edited)
        self._unit_edit.editingFinished.connect(self._on_edited)
        self._combined_edit.editingFinished.connect(self._on_combined_edited)

    def update_widgets_from_component_values(self) -> None:
        try:
            value = self.distinct_single_value_reference
        except Exception:
            with self._internal_update():
                self._value_edit.setText("")
                self._unit_edit.setText("")
            return
        # Update discrete widgets
        with self._internal_update():
            # Value field shows only the numeric part
            self._value_edit.setText(f"{value.value():.3f}")
            # Unit field shows unit symbol
            self._unit_edit.setText(str(value.unit))
            # Display label shows the fully formatted value (using provided formatter)
            self._display_label.setText(self._formatter(value))
            # Combined text mirrors the formatted label for convenience
            self._combined_edit.setText(f"{value.value():.3f} {value.unit}")

    def update_component_values_from_widgets(self) -> None:
        # Discrete fields only: parse value and unit separately
        unit_text = self._unit_edit.text().strip()
        value_text = self._value_edit.text().strip()
        
        # Get current value for fallback
        cur = self.distinct_single_value_reference
        
        # Handle case where only value is provided (use current unit)
        if value_text and not unit_text:
            try:
                desired_value = float(value_text)
                new_value = RealUnitedScalar(desired_value, cur.unit)
                # Skip if no change
                if abs(new_value.value() - cur.value()) < 1e-12:
                    return
                # Validate
                if self._validator is not None and not self._validator(new_value):
                    with self._internal_update():
                        self._value_edit.setText(f"{cur.value():.3f}")
                    return
                self._set_component_values(
                    {"value": new_value},
                    notify_binding_system=True
                )
                return
            except Exception:
                with self._internal_update():
                    self._value_edit.setText(f"{cur.value():.3f}")
                return
        
        # Handle case where only unit is provided (use current value)
        if unit_text and not value_text:
            try:
                desired_unit = Unit(unit_text)
                new_value = RealUnitedScalar(cur.value(), desired_unit)
                # Enforce allowed dimension
                if self._allowed_dimension is not None and not new_value.unit.compatible_to(self._allowed_dimension):
                    with self._internal_update():
                        self._unit_edit.setText(str(cur.unit))
                    return
                # Skip if no change
                if str(new_value.unit) == str(cur.unit):
                    return
                # Validate
                if self._validator is not None and not self._validator(new_value):
                    with self._internal_update():
                        self._unit_edit.setText(str(cur.unit))
                    return
                self._set_component_values(
                    {"value": new_value},
                    notify_binding_system=True
                )
                return
            except Exception:
                with self._internal_update():
                    self._unit_edit.setText(str(cur.unit))
                return
        
        # Handle case where both are provided
        if not unit_text or not value_text:
            return
        try:
            desired_unit = Unit(unit_text)
        except Exception:
            with self._internal_update():
                self._unit_edit.setText(str(cur.unit))
            return
        try:
            desired_value = float(value_text)
        except Exception:
            with self._internal_update():
                self._value_edit.setText(f"{cur.value():.3f}")
            return
        new_value = RealUnitedScalar(desired_value, desired_unit)
        # Enforce allowed dimension
        if self._allowed_dimension is not None and not new_value.unit.compatible_to(self._allowed_dimension):
            with self._internal_update():
                self._combined_edit.setText(f"{cur.value():.3f} {cur.unit}")
                self._unit_edit.setText(str(cur.unit))
            return
        # Skip if no change (compare numeric value in current unit and symbol)
        if str(new_value.unit) == str(cur.unit) and abs(new_value.value() - cur.value()) < 1e-12:
            return
        # Validate
        if self._validator is not None and not self._validator(new_value):
            with self._internal_update():
                self._value_edit.setText(f"{cur.value():.3f}")
                self._unit_edit.setText(str(cur.unit))
                self._combined_edit.setText(f"{cur.value():.3f} {cur.unit}")
            return
        self._set_component_values(
            {"value": new_value},
            notify_binding_system=True
        )

    def _on_combined_edited(self) -> None:
        if self.is_blocking_signals:
            return
        text = self._combined_edit.text().strip()
        if not text:
            return
        try:
            new_value = RealUnitedScalar(text)
        except Exception:
            # Revert combined field on parse error
            cur = self.distinct_single_value_reference
            with self._internal_update():
                self._combined_edit.setText(f"{cur.value():.3f} {cur.unit}")
            return
        cur = self.distinct_single_value_reference
        if self._allowed_dimension is not None and not new_value.unit.compatible_to(self._allowed_dimension):
            with self._internal_update():
                self._combined_edit.setText(f"{cur.value():.3f} {cur.unit}")
            return
        if self._validator is not None and not self._validator(new_value):
            with self._internal_update():
                self._combined_edit.setText(f"{cur.value():.3f} {cur.unit}")
            return
        if str(new_value.unit) == str(cur.unit) and abs(new_value.value() - cur.value()) < 1e-12:
            return
        self._set_component_values(
            {"value": new_value},
            notify_binding_system=True
        )

    ###########################################################################
    # Binding
    ###########################################################################

    def bind_to(self, observable_or_hook: ObservableSingleValueLike[RealUnitedScalar] | CarriesDistinctSingleValueHook[RealUnitedScalar] | HookLike[RealUnitedScalar], initial_sync_mode: InitialSyncMode = InitialSyncMode.SELF_IS_UPDATED) -> None:
        """Bind this controller to an observable."""
        if isinstance(observable_or_hook, CarriesDistinctSingleValueHook):
            observable_or_hook = observable_or_hook.distinct_single_value_hook
        elif isinstance(observable_or_hook, ObservableSingleValueLike):
            observable_or_hook = observable_or_hook.distinct_single_value_hook
        self.distinct_single_value_hook.connect_to(observable_or_hook, initial_sync_mode)

    def detach(self) -> None:
        """Detach the edit real united scalar controller from the observable."""
        self.distinct_single_value_hook.detach()

    ###########################################################################
    # Events / disposal
    ###########################################################################
    
    def _on_edited(self) -> None:
        if self.is_blocking_signals:
            return
        self.update_component_values_from_widgets()

        # No separate handler needed for the combined entry; parsing handled in update_component_values_from_widgets

    def dispose_before_children(self) -> None:
        try:
            self._value_edit.editingFinished.disconnect()
        except Exception:
            pass
        try:
            self._unit_edit.editingFinished.disconnect()
        except Exception:
            pass

    ###########################################################################
    # Public API
    ###########################################################################

    @property
    def single_value(self) -> RealUnitedScalar:
        """Get the current RealUnitedScalar value."""
        return self.distinct_single_value_reference

    @single_value.setter
    def single_value(self, new_value: RealUnitedScalar) -> None:
        """Set the RealUnitedScalar value."""
        self._set_component_values(
            {"value": new_value},
            notify_binding_system=True
        )

    ###########################################################################
    # Public accessors
    ###########################################################################
    
    @property
    def widget_value_line_edit(self) -> GuardedLineEdit:
        return self._value_edit

    @property
    def widget_unit_line_edit(self) -> GuardedLineEdit:
        return self._unit_edit

    @property
    def widget_display_label(self) -> GuardedLabel:
        return self._display_label

    @property
    def widget_value_with_unit_line_edit(self) -> GuardedLineEdit:
        return self._combined_edit


