from __future__ import annotations

"""UnitComboBoxController

Controller that binds an editable combo box to a unit selection observable or
to a provided Unit/Dimension. It validates user-typed units against the
configured dimension, adds valid new units to the observable's options, and
reverts invalid edits.
"""

from typing import Callable, Optional, overload, Any, Mapping

from PySide6.QtWidgets import QWidget

from integrated_widgets.widget_controllers.base_controller import BaseObservableController
from observables import ObservableSelectionOptionLike, Hook, SyncMode, CarriesDistinctSingleValueHook, CarriesDistinctSetHook, HookLike
from integrated_widgets.guarded_widgets import GuardedEditableComboBox

from united_system import Unit, Dimension


class UnitComboBoxController(BaseObservableController, ObservableSelectionOptionLike[Unit]):

    @classmethod
    def _mandatory_component_value_keys(cls) -> set[str]:
        """Get the mandatory component value keys for this controller."""
        return {"selected_unit", "available_units"}

    @overload
    def __init__(
        self,
        selected_unit: Unit,
        available_units: set[Unit],
        formatter: Callable[[Unit], str] = lambda u: u.format_string(as_fraction=True),
        adding_unit_options_allowed: bool = True,
        parent: Optional[QWidget] = None,
    ) -> None: ...

    @overload
    def __init__(
        self,
        selected_unit: Unit,
        available_units: CarriesDistinctSetHook[Unit] | HookLike[set[Unit]],
        formatter: Callable[[Unit], str] = lambda u: u.format_string(as_fraction=True),
        adding_unit_options_allowed: bool = True,
        parent: Optional[QWidget] = None,
    ) -> None: ...

    @overload
    def __init__(
        self,
        selected_unit: CarriesDistinctSingleValueHook[Unit] | HookLike[Unit],
        available_units: set[Unit],
        formatter: Callable[[Unit], str] = lambda u: u.format_string(as_fraction=True),
        adding_unit_options_allowed: bool = True,
        parent: Optional[QWidget] = None,
    ) -> None: ...

    @overload
    def __init__(
        self,
        selected_unit: CarriesDistinctSingleValueHook[Unit] | HookLike[Unit],
        available_units: CarriesDistinctSetHook[Unit] | HookLike[set[Unit]],
        formatter: Callable[[Unit], str] = lambda u: u.format_string(as_fraction=True),
        adding_unit_options_allowed: bool = True,
        parent: Optional[QWidget] = None,
    ) -> None: ...

    @overload
    def __init__(
        self,
        selected_unit: None = None,
        *,
        available_units: set[Unit] = set(),
        formatter: Callable[[Unit], str] = lambda u: u.format_string(as_fraction=True),
        adding_unit_options_allowed: bool = True,
        parent: Optional[QWidget] = None,
    ) -> None: ...

    def __init__( # type: ignore
        self,
        selected_unit=None,
        *,
        available_units: set[Unit] = set(),
        formatter: Callable[[Unit], str] = lambda u: u.format_string(as_fraction=True),
        adding_unit_options_allowed: bool = True,
        parent: Optional[QWidget] = None,
    ) -> None:

        self._formatter = formatter
        self._adding_unit_options_allowed = adding_unit_options_allowed

        # Handle different types of selected_unit and available_units
        if selected_unit is None:
            initial_selected_unit = None
            selected_unit_hook = None
        elif isinstance(selected_unit, CarriesDistinctSingleValueHook):
            # It's a hook - get initial value
            initial_selected_unit: Optional[Unit] = selected_unit._get_single_value()
            selected_unit_hook = selected_unit._get_single_value_hook()
        elif isinstance(selected_unit, HookLike):
            # It's a hook - get initial value
            initial_selected_unit = selected_unit.value # type: ignore
            selected_unit_hook = selected_unit
        elif isinstance(selected_unit, Unit):
            # It's a direct value
            initial_selected_unit = selected_unit
            selected_unit_hook = None
        else:
            raise ValueError(f"Invalid selected_unit: {selected_unit}")
        
        if isinstance(available_units, CarriesDistinctSetHook):
            # It's a hook - get initial value
            available_units_set: set[Unit] = available_units._get_set_value()
            available_units_hook: Optional[HookLike[set[Unit]]] = available_units._get_set_hook()
        elif isinstance(available_units, HookLike):
            # It's a hook - get initial value
            available_units_set: set[Unit] = available_units.value # type: ignore
            available_units_hook: Optional[HookLike[set[Unit]]] = available_units
        elif isinstance(available_units, set):
            # It's a direct set
            available_units_set: set[Unit] = set(available_units) if available_units else set()
            available_units_hook: Optional[HookLike[set[Unit]]] = None
        else:
            raise ValueError(f"Invalid available_units: {available_units}")
        
        # Validate that selected unit is in available units (if both are provided)
        if initial_selected_unit is not None and available_units_set and initial_selected_unit not in available_units_set:
            raise ValueError(f"Selected unit {initial_selected_unit} not in available units {available_units_set}")
        
        def verification_method(x: Mapping[str, Any]) -> tuple[bool, str]:
            # Handle partial updates by getting current values for missing keys
            current_selected = x.get("selected_unit", initial_selected_unit)
            current_units = x.get("available_units", available_units_set)
            
            if current_units is not None and not isinstance(current_units, set):
                return False, "Available units is not a set"
            
            if current_selected is not None and current_units and current_selected not in current_units:
                return False, f"Selected unit {current_selected} not in available units {current_units}"

            return True, "Verification method passed"

        super().__init__(
            {
                "selected_unit": initial_selected_unit,
                "available_units": available_units_set
            },
            {
                "selected_unit": Hook(self, self._get_single_value, self._set_single_value),
                "available_units": Hook(self, self._get_set_value, self._set_set_value)
            },
            verification_method=verification_method,
            parent=parent
        )
        
        if available_units_hook is not None:
            self.bind_available_options_to_observable(available_units_hook)
            
        if selected_unit_hook is not None:
            self.bind_selected_option_to_observable(selected_unit_hook)

    ###########################################################################
    # Binding Methods
    ###########################################################################

    def bind_available_options_to_observable(self, observable_or_hook: CarriesDistinctSetHook[Unit] | HookLike[set[Unit]], initial_sync_mode: SyncMode = SyncMode.UPDATE_SELF_FROM_OBSERVABLE) -> None:
        """Establish a bidirectional binding for the options set with another observable."""
        if isinstance(observable_or_hook, CarriesDistinctSetHook):
            observable_or_hook = observable_or_hook._get_set_hook()
        self._get_set_hook().establish_binding(observable_or_hook, initial_sync_mode)

    def bind_selected_option_to_observable(self, observable_or_hook: CarriesDistinctSingleValueHook[Optional[Unit]] | HookLike[Optional[Unit]], initial_sync_mode: SyncMode = SyncMode.UPDATE_SELF_FROM_OBSERVABLE) -> None:
        """Establish a bidirectional binding for the selected option with another observable."""
        if isinstance(observable_or_hook, CarriesDistinctSingleValueHook):
            observable_or_hook = observable_or_hook._get_single_value_hook()
        self._get_single_value_hook().establish_binding(observable_or_hook, initial_sync_mode)

    ###########################################################################
    # Hook Implementation
    ###########################################################################

    def _get_single_value(self) -> Optional[Unit]:
        """Get the currently selected unit."""
        return self._get_component_value("selected_unit")

    def _get_single_value_hook(self) -> HookLike[Optional[Unit]]:
        """Get self as a hook for binding."""
        return self._component_hooks["selected_unit"]

    def _set_single_value(self, value: Optional[Unit]) -> None:
        """Set the selected unit."""
        self._set_component_value("selected_unit", value)

    def _get_set_value(self) -> set[Unit]:
        """Get the available units."""
        return self._get_component_value("available_units")

    def _get_set_hook(self) -> HookLike[set[Unit]]:
        """Get self as a set hook for binding."""
        return self._component_hooks["available_units"]

    def _set_set_value(self, units: set[Unit]) -> None:
        """Set the available units."""
        self._set_component_value("available_units", units)

    def initialize_widgets(self) -> None:
        self._combo = GuardedEditableComboBox(self)
        self._combo.currentIndexChanged.connect(lambda _i: self._on_index_changed())
        self._combo.lineEdit().editingFinished.connect(self._on_edit_finished)  # type: ignore[union-attr]

    def update_widgets_from_component_values(self) -> None:
        """Update the combo box from the component values."""
        if not hasattr(self, '_combo'):
            return
            
        # Rebuild from component values
        available_units = self._get_set_value()
        selected_unit = self._get_single_value()
        
        self._combo.blockSignals(True)
        try:
            self._combo.clear()
            for unit_option in sorted(available_units, key=lambda x: str(x)):
                self._combo.addItem(str(unit_option), userData=unit_option)
            # select
            if selected_unit is not None:
                for i in range(self._combo.count()):
                    if self._combo.itemData(i) == selected_unit:
                        self._combo.setCurrentIndex(i)
                        break
                formatted_selected_text: str = self._formatter(selected_unit)
                self._combo.setEditText(formatted_selected_text)
        finally:
            self._combo.blockSignals(False)

    def update_component_values_from_widgets(self) -> None:
        """Update the component values from the combo box."""
        idx = self._combo.currentIndex()
        if idx < 0:
            return
        u = self._combo.itemData(idx)
        try:
            self._set_single_value(u)
        except Exception:
            pass

    def _on_index_changed(self) -> None:
        """Handle combo box index change."""
        if self.is_blocking_signals:
            return
        self.update_component_values_from_widgets()

    def _on_edit_finished(self) -> None:    
        """Handle combo box editing finished."""
        if self.is_blocking_signals:
            return

        current_text: str = self._combo.currentText().strip()
        if current_text == "":
            self.update_widgets_from_component_values()
            return
        try:
            parsed_unit: Unit = Unit(current_text)

            selected_unit: Optional[Unit] = self._get_single_value()
            if selected_unit is not None:
                if not parsed_unit.compatible_to(selected_unit.dimension):
                    raise ValueError("unit incompatible with dimension")
                if parsed_unit not in self._get_set_value():
                    if not self._adding_unit_options_allowed:
                        raise ValueError("unit not in options and adding unit options is not allowed")
                    # Add to available units
                    available_units = self._get_set_value().copy()
                    available_units.add(parsed_unit)
                    self._set_set_value(available_units)
        except Exception:
            # revert
            self.update_widgets_from_component_values()
            return
        # Add if new and select
        try:
            available_units = self._get_set_value().copy()
            if parsed_unit not in available_units:
                available_units.add(parsed_unit)
                self._set_set_value(available_units)
            self._set_single_value(parsed_unit)
            self.update_widgets_from_component_values()
        except Exception:
            pass

    ###########################################################################
    # Public API
    ###########################################################################

    @property
    def selected_unit(self) -> Optional[Unit]:
        """Get the currently selected unit."""
        return self._get_single_value()

    @selected_unit.setter
    def selected_unit(self, value: Optional[Unit]) -> None:
        """Set the selected unit."""
        self._set_single_value(value)

    @property
    def available_units(self) -> set[Unit]:
        """Get the available units."""
        return self._get_set_value()

    @available_units.setter
    def available_units(self, units: set[Unit]) -> None:
        """Set the available units."""
        self._set_set_value(units)

    @property
    def widget_combobox(self) -> GuardedEditableComboBox:
        """Get the combo box widget."""
        return self._combo
    
    @property
    def adding_unit_options_allowed(self) -> bool:
        """Check if adding new unit options is allowed."""
        return self._adding_unit_options_allowed
    
    @adding_unit_options_allowed.setter
    def adding_unit_options_allowed(self, value: bool) -> None:
        """Set whether adding new unit options is allowed."""
        self._adding_unit_options_allowed = value


