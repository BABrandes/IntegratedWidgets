from __future__ import annotations

from typing import Callable, Optional, overload, Any, Mapping

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget

from united_system import RealUnitedScalar, Unit

from integrated_widgets.widget_controllers.base_controller import BaseObservableController
from observables import ObservableSingleValueLike, Hook, SyncMode, HookLike, CarriesDistinctSingleValueHook
from integrated_widgets.guarded_widgets import GuardedLabel, GuardedComboBox
from integrated_widgets.util.general import DEFAULT_FLOAT_FORMAT_VALUE


class DisplayRealUnitedScalarController(BaseObservableController, ObservableSingleValueLike[RealUnitedScalar]):

    @classmethod
    def _mandatory_component_value_keys(cls) -> set[str]:
        """Get the mandatory component value keys for this controller."""
        return {"value"}
    
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
            initial_value: RealUnitedScalar = value._get_single_value()
            value_hook: Optional[HookLike[RealUnitedScalar]] = value._get_single_value_hook()
        elif isinstance(value, RealUnitedScalar):
            # It's a direct value
            initial_value = value
            value_hook: Optional[HookLike[RealUnitedScalar]] = None
        else:
            raise ValueError(f"Invalid value: {value}")
        
        def verification_method(x: Mapping[str, Any]) -> tuple[bool, str]:
            # Verify the value is a RealUnitedScalar
            current_value = x.get("value", initial_value)
            if not isinstance(current_value, RealUnitedScalar):
                return False, f"Value must be a RealUnitedScalar, got {type(current_value)}"
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

    def bind_to(self, observable_or_hook: ObservableSingleValueLike[RealUnitedScalar] | HookLike[RealUnitedScalar] | CarriesDistinctSingleValueHook[RealUnitedScalar], initial_sync_mode: SyncMode = SyncMode.UPDATE_SELF_FROM_OBSERVABLE) -> None:
        """Establish a bidirectional binding with another observable or hook."""
        if isinstance(observable_or_hook, CarriesDistinctSingleValueHook):
            observable_or_hook = observable_or_hook._get_single_value_hook()
        self._get_single_value_hook().establish_binding(observable_or_hook, initial_sync_mode)

    def unbind_from(self, observable_or_hook: ObservableSingleValueLike[RealUnitedScalar] | HookLike[RealUnitedScalar] | CarriesDistinctSingleValueHook[RealUnitedScalar]) -> None:
        """Remove the bidirectional binding with another observable."""
        if isinstance(observable_or_hook, CarriesDistinctSingleValueHook):
            observable_or_hook = observable_or_hook._get_single_value_hook()
        self._get_single_value_hook().remove_binding(observable_or_hook)

    ###########################################################################
    # Hook Implementation
    ###########################################################################

    def _get_single_value(self) -> RealUnitedScalar:
        """Get the current RealUnitedScalar value."""
        return self._get_component_value("value")

    def _get_single_value_hook(self) -> HookLike[RealUnitedScalar]:
        """Get self as a hook for binding."""
        return self._component_hooks["value"]

    def _set_single_value(self, value: RealUnitedScalar) -> None:
        """Set the RealUnitedScalar value."""
        self._set_component_value("value", value)

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
            value = self._get_single_value()
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

    def update_component_values_from_widgets(self) -> None:
        """Update the component values from the widgets."""
        idx = self._combo.currentIndex()
        if idx < 0:
            return
        new_unit = self._combo.itemData(idx)
        if new_unit is None:
            return
        current = self._get_single_value()
        if current.unit == new_unit:
            return
        new_value: RealUnitedScalar = RealUnitedScalar(current.canonical_value, current.dimension, display_unit=new_unit)
        self._set_single_value(new_value)

    ###########################################################################
    # Internal
    ###########################################################################

    def _on_unit_changed(self) -> None:
        """Handle unit combo box change."""
        if self.is_blocking_signals:
            return
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
    def value(self) -> RealUnitedScalar:
        """Get the current RealUnitedScalar value."""
        return self._get_single_value()

    @value.setter
    def value(self, new_value: RealUnitedScalar) -> None:
        """Set the RealUnitedScalar value."""
        self._set_single_value(new_value)

    ###########################################################################
    # Public accessors
    ###########################################################################

    @property
    def widget_value_label(self) -> GuardedLabel:
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


