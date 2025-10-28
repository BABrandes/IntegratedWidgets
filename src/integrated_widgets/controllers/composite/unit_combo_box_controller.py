from __future__ import annotations

"""UnitComboBoxController

Controller that binds an editable combo box to a unit selection observable or
to a provided Unit/Dimension. It validates user-typed units against the
configured dimension, adds valid new units to the observable's options, and
reverts invalid edits.
"""

# Standard library imports
from typing import Callable, Optional, Any, Mapping, Literal, AbstractSet
from logging import Logger
from types import MappingProxyType

# BAB imports
from united_system import Unit, Dimension
from nexpy import XDictProtocol, Hook, UpdateFunctionValues, XSingleValueProtocol
from nexpy.core import NexusManager
from nexpy import default as nexpy_default

# Local imports
from ..core.base_composite_controller import BaseCompositeController
from ...controlled_widgets.controlled_editable_combobox import ControlledEditableComboBox
from ...controlled_widgets.controlled_line_edit import ControlledLineEdit
from ...controlled_widgets.controlled_combobox import ControlledComboBox
from ...controlled_widgets.blankable_widget import BlankableWidget

class UnitComboBoxController(BaseCompositeController[Literal["selected_unit", "available_units"], Any, Optional[Unit]|dict[Dimension, AbstractSet[Unit]], Any]):

    def __init__(
        self,
        selected_unit: Optional[Unit] | Hook[Optional[Unit]] | XSingleValueProtocol[Optional[Unit]],
        available_units: Mapping[Dimension, AbstractSet[Unit]] | Hook[Mapping[Dimension, AbstractSet[Unit]]] | XDictProtocol[Dimension, AbstractSet[Unit]],
        *,
        allowed_dimensions: Optional[AbstractSet[Dimension]] = None,
        formatter: Callable[[Unit], str] = lambda u: u.format_string(as_fraction=True),
        blank_if_none: bool = True,
        debounce_ms: int|Callable[[], int],
        nexus_manager: NexusManager = nexpy_default.NEXUS_MANAGER,
        logger: Optional[Logger] = None,
    ) -> None:

        self._formatter = formatter
        self._blank_if_none = blank_if_none
        self._allowed_dimensions = allowed_dimensions

        # Handle different types of selected_unit and available_units
        if isinstance(selected_unit, Unit):
            # It's a direct value
            initial_selected_unit: Optional[Unit] = selected_unit
            hook_selected_unit: Optional[Hook[Unit]] = None

        elif isinstance(selected_unit, Hook):
            # It's a hook - get initial value
            initial_selected_unit = selected_unit.value # type: ignore
            hook_selected_unit = selected_unit # type: ignore

        elif isinstance(selected_unit, XSingleValueProtocol):
            # It's an observable - get initial value
            initial_selected_unit = selected_unit.value
            hook_selected_unit = selected_unit.hook # type: ignore

        else:
            raise ValueError(f"Invalid selected_unit: {selected_unit}")
        
        if isinstance(available_units, dict):
            # It's a direct value
            initial_available_units: Mapping[Dimension, AbstractSet[Unit]] = available_units
            hook_available_units: Optional[Hook[Mapping[Dimension, AbstractSet[Unit]]]] = None

        elif isinstance(available_units, Hook):
            # It's a hook - get initial value
            initial_available_units = available_units.value # type: ignore
            hook_available_units = available_units

        elif isinstance(available_units, XDictProtocol): # type: ignore
            # It's an observable - get initial value
            initial_available_units = available_units.dict
            hook_available_units = available_units.dict_hook

        else:
            raise ValueError(f"Invalid available_units: {available_units}")

        if allowed_dimensions is not None:
            raise ValueError(f"Not implemented yet. Eventually this could limit the allowed dimensions, both user entries and programmatic entries.")
        
        def verification_method(x: Mapping[Literal["selected_unit", "available_units"], Any]) -> tuple[bool, str]:
            # Handle partial updates by getting current values for missing keys
            selected_unit: Optional[Unit] = x.get("selected_unit", initial_selected_unit)
            available_units: dict[Dimension, frozenset[Unit]] = x.get("available_units", initial_available_units)

            if selected_unit is not None:
                if selected_unit.dimension not in available_units:
                    return False, f"Selected unit {selected_unit} not in available units for dimension {selected_unit.dimension}: {available_units}"
                unit_options: frozenset[Unit] = available_units[selected_unit.dimension]
                if not selected_unit in unit_options:
                    return False, f"Selected unit {selected_unit} not in available units for dimension {selected_unit.dimension}: {unit_options}"
            
            return True, "Verification method passed"

        def add_values_to_be_updated_callback(self_ref: "UnitComboBoxController", values: UpdateFunctionValues[Literal["selected_unit", "available_units"], Any]) -> Mapping[Literal["selected_unit", "available_units"], Any]:

            def deep_copy_available_units(available_units: Mapping[Dimension, AbstractSet[Unit]]) -> dict[Dimension, AbstractSet[Unit]]:
                # Create a new dict with frozenset values copied
                return {dimension: set(units) for dimension, units in available_units.items()}

            current_values = values.current
            changed_values = values.submitted

            match "selected_unit" in changed_values, "available_units" in changed_values:
                case True, True:
                    # Both are in changed_values - check current_values for the NEW value being submitted
                    selected_unit: Optional[Unit] = current_values.get("selected_unit") if "selected_unit" in current_values else changed_values.get("selected_unit")
                    available_units: dict[Dimension, AbstractSet[Unit]] = current_values.get("available_units") if "available_units" in current_values else changed_values.get("available_units")  # type: ignore
                    if selected_unit is not None:
                        if selected_unit.dimension not in available_units:
                            new_available_units = deep_copy_available_units(available_units)
                            new_available_units[selected_unit.dimension] = set({selected_unit})
                            return {"available_units": new_available_units}
                        elif selected_unit not in available_units[selected_unit.dimension]:
                            new_available_units = deep_copy_available_units(available_units)
                            new_available_units[selected_unit.dimension] = available_units[selected_unit.dimension] | {selected_unit}
                            return {"available_units": new_available_units}
                    return {}

                case True, False:
                    selected_unit = changed_values["selected_unit"]
                    available_units = current_values["available_units"]
                    if selected_unit is not None:
                        if selected_unit.dimension not in available_units:
                            # Add the dimension to the available units
                            new_available_units = deep_copy_available_units(available_units)
                            new_available_units[selected_unit.dimension] = frozenset({selected_unit})
                            return {"available_units": MappingProxyType(new_available_units)}
                        else:
                            if not selected_unit in available_units[selected_unit.dimension]:
                                new_available_units = deep_copy_available_units(available_units)
                                # Add the unit to the frozenset using union operator
                                new_available_units[selected_unit.dimension] = available_units[selected_unit.dimension] | {selected_unit}
                                return {"available_units": MappingProxyType(new_available_units)}
                            else:
                                return {}
                    else:
                        return {}

                case False, True:
                    return {}

                case False, False:
                    raise ValueError("Both selected_unit and available_units are not in changed_values")

        super().__init__(
            {
                "selected_unit": initial_selected_unit,
                "available_units": initial_available_units
            },
            validate_complete_primary_values_callback=verification_method,
            add_values_to_be_updated_callback=add_values_to_be_updated_callback, # type: ignore
            debounce_ms=debounce_ms,
            nexus_manager=nexus_manager,
            logger=logger
        )
        
        if hook_available_units is not None:
            self.connect_hook(hook_available_units, "available_units", initial_sync_mode="use_target_value") # type: ignore
        if hook_selected_unit is not None:
            self.connect_hook(hook_selected_unit,"selected_unit", initial_sync_mode="use_target_value") # type: ignore

    ###########################################################################
    # Widget methods
    ###########################################################################

    def _initialize_widgets_impl(self) -> None:
        """
        Create and configure all the user interface widgets.
        """

        self._unit_combobox = ControlledComboBox(self, logger=self._logger)
        self._unit_editable_combobox = ControlledEditableComboBox(self, logger=self._logger)
        self._unit_line_edit = ControlledLineEdit(self, logger=self._logger)

        # Connect UI -> model
        self._unit_combobox.currentIndexChanged.connect(lambda _i: self._on_combobox_index_changed()) # type: ignore
        self._unit_editable_combobox.editingFinished.connect(self._on_combobox_edit_finished) # type: ignore
        self._unit_editable_combobox.currentIndexChanged.connect(lambda _i: self._on_editable_combobox_index_changed()) # type: ignore
        self._unit_line_edit.editingFinished.connect(self._on_unit_line_edit_edit_finished) # type: ignore

        self._blankable_widget_unit_combobox = BlankableWidget(self._unit_combobox)
        self._blankable_widget_unit_editable_combobox = BlankableWidget(self._unit_editable_combobox)
        self._blankable_widget_unit_line_edit = BlankableWidget(self._unit_line_edit)

    def _on_combobox_index_changed(self) -> None:
        """
        Handle when the user selects a different unit from the dropdown menu.
        """

        if self.is_blocking_signals:
            return

        new_unit: Optional[Unit] = self._unit_combobox.currentData()
        if new_unit is None or not isinstance(new_unit, Unit): # type: ignore
            self.invalidate_widgets()
            return
        
        self.submit_value("selected_unit", new_unit)

        ################################################################

    def _on_unit_line_edit_edit_finished(self) -> None:
        """
        Handle when the user types a new unit in the unit text field.
        
        This method is called when the user types a unit symbol or name in the 
        "Unit edit" field and presses Enter or clicks outside the field. This is
        the most flexible way to add new units or change to units not in the dropdown.
        
        **What the user can type:**
        - Basic units: "m", "kg", "s", "V", "A"
        - Prefixed units: "km", "mg", "kV", "mA", "µm"
        - Complex units: "m/s", "kg/m^3", "W/m^2", "rad/s"
        """

        if self.is_blocking_signals:
            return

        try:
            new_unit: Unit = Unit(self._unit_line_edit.text())
        except Exception:
            self.invalidate_widgets()
            return
        
        self.submit_value("selected_unit", new_unit)

        ################################################################

    def _on_editable_combobox_index_changed(self) -> None:
        """
        Handle editable combo box index change.
        """

        if self.is_blocking_signals:
            return

        new_unit: Optional[Unit] = self._unit_editable_combobox.currentData()
        if new_unit is None or not isinstance(new_unit, Unit): # type: ignore
            self.invalidate_widgets()
            return
        
        self.submit_value("selected_unit", new_unit)

        ################################################################

    def _on_combobox_edit_finished(self, text: str) -> None:    
        """
        Handle combo box editing finished.
        """

        if self.is_blocking_signals:
            return

        try:
            new_unit: Unit = Unit(text)
        except Exception:
            self.invalidate_widgets()
            return
        
        self.submit_value("selected_unit", new_unit)
        
    def _invalidate_widgets_impl(self) -> None:
        """
        Synchronize all widget displays with the current internal state.
        
        This method is called automatically whenever the underlying data changes,
        either through user interaction or programmatic updates via observables.
        It ensures that all visible widgets show consistent, up-to-date information.
        
        **What gets updated:**
        - Combo boxes show the current selected unit
        - Line edit displays the current unit text
        - All widgets reflect the current state consistently
        
        **When this is called:**
        - After successful user edits
        - When connected observable values change
        - When validation fails and the display needs to revert
        - During initialization to show initial values
        
        **Internal Use:**
        This is an internal method. Users don't typically call this directly,
        but it's essential for maintaining UI consistency.
        """

        selected_unit: Optional[Unit] = self.value_by_key("selected_unit") # type: ignore
        if selected_unit is None:
            if self._blank_if_none:
                self._blankable_widget_unit_line_edit.blank()
                self._blankable_widget_unit_editable_combobox.blank()
                self._blankable_widget_unit_combobox.blank()
            else:
                self._blankable_widget_unit_line_edit.unblank()
                self._blankable_widget_unit_editable_combobox.unblank()
                self._blankable_widget_unit_combobox.unblank()

            self._unit_line_edit.setText("")
            self._unit_combobox.clear()
            self._unit_editable_combobox.clear()

        else:
            self._blankable_widget_unit_line_edit.unblank()
            self._blankable_widget_unit_editable_combobox.unblank()
            self._blankable_widget_unit_combobox.unblank()

            available_units: AbstractSet[Unit] = self.value_by_key("available_units")[selected_unit.dimension] # type: ignore
            
            self._unit_line_edit.setText(self._formatter(selected_unit)) # type: ignore

            self._unit_combobox.clear()
            for unit in sorted(available_units, key=lambda u: self._formatter(u)): # type: ignore
                self._unit_combobox.addItem(self._formatter(unit), userData=unit) # type: ignore
            self._unit_combobox.setCurrentIndex(self._unit_combobox.findData(selected_unit))

            self._unit_editable_combobox.clear()
            for unit in sorted(available_units, key=lambda u: self._formatter(u)): # type: ignore
                self._unit_editable_combobox.addItem(self._formatter(unit), userData=unit) # type: ignore
            self._unit_editable_combobox.setCurrentIndex(self._unit_editable_combobox.findData(selected_unit))
        
    ###########################################################################
    # Public API
    ###########################################################################

    def change_selected_option_and_available_options(self, selected_option: Optional[Unit], available_options: dict[Dimension, AbstractSet[Unit]], *, debounce_ms: Optional[int] = None, raise_submission_error_flag: bool = True) -> None:
        """Change the selected option and available options at once."""
        self.submit_values({"selected_unit": selected_option, "available_units": available_options}, debounce_ms=debounce_ms, raise_submission_error_flag=raise_submission_error_flag) # type: ignore

    @property
    def selected_unit(self) -> Optional[Unit]:
        """Get the currently selected unit."""
        return self.value_by_key("selected_unit") # type: ignore

    @selected_unit.setter
    def selected_unit(self, value: Optional[Unit]) -> None:
        """Set the selected unit."""
        self.submit_value("selected_unit", value) # type: ignore

    def change_selected_unit(self, value: Optional[Unit], *, debounce_ms: Optional[int] = None, raise_submission_error_flag: bool = True) -> None:
        """Change the selected unit."""
        self.submit_value("selected_unit", value, debounce_ms=debounce_ms, raise_submission_error_flag=raise_submission_error_flag) # type: ignore

    @property
    def selected_unit_hook(self) -> Hook[Optional[Unit]]:
        """Get the hook for the selected unit."""
        hook: Hook[Optional[Unit]] = self.hook_by_key("selected_unit") # type: ignore
        return hook

    @property
    def available_units(self) -> dict[Dimension, AbstractSet[Unit]]:
        """Get the available units."""
        return self.value_by_key("available_units") # type: ignore

    @available_units.setter
    def available_units(self, units: dict[Dimension, AbstractSet[Unit]]) -> None:
        """Set the available units."""
        self.submit_value("available_units", units) # type: ignore

    def change_available_units(self, units: dict[Dimension, AbstractSet[Unit]], *, debounce_ms: Optional[int] = None, raise_submission_error_flag: bool = True) -> None:
        """Change the available units."""
        self.submit_value("available_units", units, debounce_ms=debounce_ms, raise_submission_error_flag=raise_submission_error_flag) # type: ignore

    @property
    def available_units_hook(self) -> Hook[dict[Dimension, AbstractSet[Unit]]]:
        """Get the hook for the available units."""
        hook: Hook[dict[Dimension, AbstractSet[Unit]]] = self.hook_by_key("available_units") # type: ignore
        return hook

    # Widgets

    @property
    def widget_combobox(self) -> BlankableWidget[ControlledComboBox]:
        """Get the combo box widget."""
        return self._blankable_widget_unit_combobox
    
    @property
    def widget_editable_combobox(self) -> BlankableWidget[ControlledEditableComboBox]:
        """Get the editable combo box widget."""
        return self._blankable_widget_unit_editable_combobox
    
    @property
    def widget_line_edit(self) -> BlankableWidget[ControlledLineEdit]:
        """Get the line edit widget."""
        return self._blankable_widget_unit_line_edit