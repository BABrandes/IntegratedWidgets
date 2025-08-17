from __future__ import annotations

from typing import Callable, Optional, overload, Any, Mapping

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget

from united_system import RealUnitedScalar, Unit

from integrated_widgets.widget_controllers.base_controller import BaseObservableController
from observables import ObservableSingleValueLike, HookLike, CarriesDistinctSingleValueHook, InitialSyncMode
from integrated_widgets.guarded_widgets import GuardedLabel, GuardedComboBox
from integrated_widgets.util.general import DEFAULT_FLOAT_FORMAT_VALUE


class DisplayRealUnitedScalarController(BaseObservableController):

    @classmethod
    def _mandatory_component_value_keys(cls) -> set[str]:
        """Get the mandatory component value keys for this controller."""
        return {"value", "display_unit"}
    
    @overload
    def __init__(
        self,
        value: RealUnitedScalar,
        unit_options: Optional[list[Unit]] = None,
        formatter: Callable[[RealUnitedScalar], str] = DEFAULT_FLOAT_FORMAT_VALUE,
        *,
        parent: Optional[QWidget] = None,
    ) -> None: ...

    @overload
    def __init__(
        self,
        value: ObservableSingleValueLike[RealUnitedScalar] | HookLike[RealUnitedScalar] | CarriesDistinctSingleValueHook[RealUnitedScalar],
        unit_options: Optional[list[Unit]] = None,
        formatter: Callable[[RealUnitedScalar], str] = DEFAULT_FLOAT_FORMAT_VALUE,
        *,
        parent: Optional[QWidget] = None,
    ) -> None: ...

    def __init__(
        self,
        value,
        unit_options: Optional[list[Unit]] = None,
        formatter: Callable[[RealUnitedScalar], str] = DEFAULT_FLOAT_FORMAT_VALUE,
        *,
        parent: Optional[QWidget] = None,
    ) -> None:
        
        self._formatter = formatter
        self._unit_options_input = unit_options
        
        # Handle different types of value
        if isinstance(value, HookLike):
            # It's a hook - get initial value
            initial_value: RealUnitedScalar = value.value  # type: ignore
            value_hook: Optional[HookLike[RealUnitedScalar]] = value
        elif isinstance(value, CarriesDistinctSingleValueHook):
            # It's a hook - get initial value
            initial_value: RealUnitedScalar = value.distinct_single_value_reference
            value_hook: Optional[HookLike[RealUnitedScalar]] = value.distinct_single_value_hook
        elif isinstance(value, ObservableSingleValueLike):
            # It's an ObservableSingleValue - get initial value
            initial_value: RealUnitedScalar = value.distinct_single_value_reference
            value_hook: Optional[HookLike[RealUnitedScalar]] = value.distinct_single_value_hook
        elif isinstance(value, RealUnitedScalar):
            # It's a direct value
            initial_value = value
            value_hook: Optional[HookLike[RealUnitedScalar]] = None
        else:
            raise ValueError(f"Invalid value: {value}")
        
        display_unit: Unit = initial_value.unit
        
        def verification_method(x: Mapping[str, Any]) -> tuple[bool, str]:
            # Verify the value is a RealUnitedScalar
            current_value = x.get("value", initial_value)
            if not isinstance(current_value, RealUnitedScalar):
                return False, f"Value must be a RealUnitedScalar, got {type(current_value)}"
            return True, "Verification method passed"

        super().__init__(
            {
                "value": initial_value,
                "display_unit": display_unit
            },
            verification_method=verification_method,
            parent=parent
        )
        
        if value_hook is not None:
            self.bind_value_to(value_hook)

    ###########################################################################
    # Binding Methods
    ###########################################################################

    def bind_value_to(self, observable_or_hook: ObservableSingleValueLike[RealUnitedScalar] | HookLike[RealUnitedScalar] | CarriesDistinctSingleValueHook[RealUnitedScalar], initial_sync_mode: InitialSyncMode = InitialSyncMode.SELF_IS_UPDATED) -> None:
        """Establish a bidirectional binding with another observable or hook."""
        if isinstance(observable_or_hook, CarriesDistinctSingleValueHook):
            observable_or_hook = observable_or_hook.distinct_single_value_hook
        elif isinstance(observable_or_hook, ObservableSingleValueLike):
            observable_or_hook = observable_or_hook.distinct_single_value_hook
        self.distinct_single_value_hook.connect_to(observable_or_hook, initial_sync_mode)

    def bind_display_unit_to(self, observable_or_hook: ObservableSingleValueLike[Unit] | HookLike[Unit] | CarriesDistinctSingleValueHook[Unit], initial_sync_mode: InitialSyncMode = InitialSyncMode.SELF_IS_UPDATED) -> None:
        """Establish a bidirectional binding with another observable or hook."""
        if isinstance(observable_or_hook, CarriesDistinctSingleValueHook):
            observable_or_hook = observable_or_hook.distinct_single_value_hook
        elif isinstance(observable_or_hook, ObservableSingleValueLike):
            observable_or_hook = observable_or_hook.distinct_single_value_hook
        self.distinct_display_unit_hook.connect_to(observable_or_hook, initial_sync_mode)
        
    def disconnect_value_from(self, observable_or_hook: ObservableSingleValueLike[RealUnitedScalar] | HookLike[RealUnitedScalar] | CarriesDistinctSingleValueHook[RealUnitedScalar]) -> None:
        """Remove the bidirectional binding with another observable."""
        self.distinct_single_value_hook.detach()

    def disconnect_display_unit_from(self, observable_or_hook: ObservableSingleValueLike[Unit] | HookLike[Unit] | CarriesDistinctSingleValueHook[Unit]) -> None:
        """Remove the bidirectional binding with another observable."""
        self.distinct_display_unit_hook.detach()

    ###########################################################################
    # Hook Implementation
    ###########################################################################

    @property
    def distinct_single_value_hook(self) -> HookLike[RealUnitedScalar]:
        """Get the hook for the single value."""
        return self._component_hooks["value"]
    
    @property
    def distinct_single_value_reference(self) -> RealUnitedScalar:
        """Get the reference for the single value."""
        return self._component_values["value"]
    
    @property
    def distinct_display_unit_hook(self) -> HookLike[Unit]:
        """Get the hook for the display unit."""
        return self._component_hooks["display_unit"]
    
    @property
    def distinct_display_unit_reference(self) -> Unit:
        """Get the reference for the display unit."""
        return self._component_values["display_unit"]

    def initialize_widgets(self) -> None:
        self._label = GuardedLabel(self)
        self._label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self._combo = GuardedComboBox(self)
        self._combo.currentIndexChanged.connect(lambda _i: self._on_unit_changed())

    def update_widgets_from_component_values(self) -> None:
        """Update the widgets from the component values."""
        if not hasattr(self, '_label'):
            return
            
        try:
            value = self.distinct_single_value_reference
        except Exception:
            self._label.blockSignals(True)
            try:
                self._label.setText("")
                self._combo.clear()
            finally:
                self._label.blockSignals(False)
            return
        # Label
        with self._internal_update():
            self._label.setText(self._formatter(value))
        # Units
        units = self._unit_options_input or self._unit_options_for(value)
        self._rebuild_units(units)
        self._select_unit(value.unit)

        self._update_real_united_scalar_value_label()

    def update_component_values_from_widgets(self) -> None:
        """Update the component values from the widgets."""
        print("DEBUG: update_component_values_from_widgets called")
        idx = self._combo.currentIndex()
        print(f"DEBUG: currentIndex={idx}")
        if idx < 0:
            print("DEBUG: No valid index, returning")
            return
        new_unit = self._combo.itemData(idx)
        print(f"DEBUG: new_unit={new_unit}")
        if new_unit is None:
            print("DEBUG: No unit data, returning")
            return
        current = self.distinct_single_value_reference
        print(f"DEBUG: current value={current}, current.unit={current.unit}")
        if current.unit == new_unit:
            print("DEBUG: Unit unchanged, returning")
            return
        print(f"DEBUG: Creating new RealUnitedScalar with canonical_value={current.canonical_value}, dimension={current.dimension}, display_unit={new_unit}")
        new_value: RealUnitedScalar = RealUnitedScalar(current.canonical_value, current.dimension, display_unit=new_unit)
        print(f"DEBUG: New value created: {new_value}")
        print("DEBUG: Calling _set_single_value")
        self._set_component_values(
            {"value": new_value},
            notify_binding_system=True
        )

    def _update_real_united_scalar_value_label(self) -> None:
        """Update the real united scalar value label."""
        print("DEBUG: _update_real_united_scalar_value_label called")
        current_value = self.distinct_single_value_reference
        print(f"DEBUG: Current value for label update: {current_value}")
        formatted_text = self._formatter(current_value)
        print(f"DEBUG: Formatted text: {formatted_text}")
        with self._internal_update():
            self._label.setText(formatted_text)
        print("DEBUG: Label text set successfully")

    ###########################################################################
    # Internal
    ###########################################################################

    def _on_unit_changed(self) -> None:
        """Handle unit combo box change."""
        print(f"DEBUG: _on_unit_changed called, _internal_widget_update={self._internal_widget_update}")
        if self._internal_widget_update:
            print("DEBUG: Skipping due to internal widget update")
            return
        print("DEBUG: Calling update_component_values_from_widgets")
        self.update_component_values_from_widgets()

    def _unit_options_for(self, value: RealUnitedScalar) -> list[Unit]:
        canonical = value.dimension.canonical_unit
        units: list[Unit] = [canonical]
        try:
            km = Unit("km")
            if km.compatible_to(value.dimension) and km != canonical:
                units.append(km)
        except Exception:
            pass
        if value.unit not in units:
            units.append(value.unit)
        return units

    def _rebuild_units(self, units: list[Unit]) -> None:
        """Rebuild the unit combo box."""
        with self._internal_update():
            self._combo.clear()
            for unit in units:
                self._combo.addItem(str(unit), userData=unit)

    def _select_unit(self, unit: Unit) -> None:
        """Select the specified unit in the combo box."""
        with self._internal_update():
            for i in range(self._combo.count()):
                if self._combo.itemData(i) == unit:
                    self._combo.setCurrentIndex(i)
                    return
            self._combo.setCurrentIndex(-1)

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
    def widget_real_united_scalar_label(self) -> GuardedLabel:
        """Get the value label widget."""
        return self._label

    @property
    def widget_unit_combo(self) -> GuardedComboBox:
        """Get the unit combo box widget."""
        return self._combo

    def dispose_before_children(self) -> None:
        try:
            self._combo.currentIndexChanged.disconnect()
        except Exception:
            pass


