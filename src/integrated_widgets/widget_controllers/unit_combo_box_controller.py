from __future__ import annotations

"""UnitComboBoxController

Controller that binds an editable combo box to a unit selection observable or
to a provided Unit/Dimension. It validates user-typed units against the
configured dimension, adds valid new units to the observable's options, and
reverts invalid edits.
"""

# Standard library imports
from typing import Callable, Optional, Any, Mapping, Literal
from logging import Logger
from PySide6.QtWidgets import QWidget, QFrame, QVBoxLayout

# BAB imports
from united_system import Unit, Dimension
from observables import ObservableSingleValueLike, ObservableDictLike, ObservableSetLike
from observables.core import HookLike, OwnedHookLike

# Local imports
from ..util.base_complex_hook_controller import BaseComplexHookController
from ..controlled_widgets.controlled_editable_combobox import ControlledEditableComboBox
from ..controlled_widgets.controlled_line_edit import ControlledLineEdit
from ..controlled_widgets.controlled_combobox import ControlledComboBox
from ..util.resources import log_bool, log_msg
from ..controlled_widgets.blankable_widget import BlankableWidget

class UnitComboBoxController(BaseComplexHookController[Literal["selected_unit", "available_units"], Any, Optional[Unit]|dict[Dimension, set[Unit]], Any, "UnitComboBoxController"]):

    def __init__(
        self,
        selected_unit: Optional[Unit] | HookLike[Optional[Unit]] | ObservableSingleValueLike[Optional[Unit]],
        available_units: dict[Dimension, set[Unit]] | HookLike[dict[Dimension, set[Unit]]] | ObservableDictLike[Dimension, set[Unit]],
        allowed_dimensions: None | set[Dimension]| HookLike[set[Dimension]] | ObservableSetLike[Dimension] = None,
        formatter: Callable[[Unit], str] = lambda u: u.format_string(as_fraction=True),
        blank_if_none: bool = True,
        parent_of_widgets: Optional[QWidget] = None,
        logger: Optional[Logger] = None,
    ) -> None:

        self._formatter = formatter
        self._blank_if_none = blank_if_none

        # Handle different types of selected_unit and available_units
        if isinstance(selected_unit, Unit):
            # It's a direct value
            initial_selected_unit: Optional[Unit] = selected_unit
            hook_selected_unit: Optional[HookLike[Unit]] = None

        elif isinstance(selected_unit, HookLike):
            # It's a hook - get initial value
            initial_selected_unit = selected_unit.value # type: ignore
            hook_selected_unit = selected_unit # type: ignore

        elif isinstance(selected_unit, ObservableSingleValueLike):
            # It's an observable - get initial value
            initial_selected_unit = selected_unit.value
            hook_selected_unit = selected_unit.hook # type: ignore

        else:
            raise ValueError(f"Invalid selected_unit: {selected_unit}")
        
        if isinstance(available_units, dict):
            # It's a direct value
            initial_available_units: dict[Dimension, set[Unit]] = available_units
            hook_available_units: Optional[HookLike[dict[Dimension, set[Unit]]]] = None

        elif isinstance(available_units, HookLike):
            # It's a hook - get initial value
            initial_available_units = available_units.value # type: ignore
            hook_available_units = available_units

        elif isinstance(available_units, ObservableDictLike):
            # It's an observable - get initial value
            initial_available_units = available_units.value
            hook_available_units = available_units.value_hook

        else:
            raise ValueError(f"Invalid available_units: {available_units}")

        if allowed_dimensions is not None:
            raise ValueError(f"Not implemented yet. Eventually this could limit the allowed dimensions, both user entries and programmatic entries.")
        
        def verification_method(x: Mapping[Literal["selected_unit", "available_units"], Any]) -> tuple[bool, str]:
            # Handle partial updates by getting current values for missing keys

            selected_unit: Optional[Unit] = x.get("selected_unit", initial_selected_unit)
            available_units: dict[Dimension, set[Unit]] = x.get("available_units", initial_available_units)

            if selected_unit is not None:
                if selected_unit.dimension not in available_units:
                    return False, f"Selected unit {selected_unit} not in available units for dimension {selected_unit.dimension}: {available_units}"
                unit_options: set[Unit] = available_units[selected_unit.dimension]
                if not selected_unit in unit_options:
                    return False, f"Selected unit {selected_unit} not in available units for dimension {selected_unit.dimension}: {unit_options}"
            else:
                pass
            
            return True, "Verification method passed"

        def add_values_to_be_updated_callback(self_ref: "UnitComboBoxController", changed_values: Mapping[Literal["selected_unit", "available_units"], Any], current_values: Mapping[Literal["selected_unit", "available_units"], Any]) -> Mapping[Literal["selected_unit", "available_units"], Any]:

            match "selected_unit" in changed_values, "available_units" in changed_values:
                case True, True:
                    # Both are in changed_values - check current_values for the NEW value being submitted
                    selected_unit: Optional[Unit] = current_values.get("selected_unit") if "selected_unit" in current_values else changed_values.get("selected_unit")
                    available_units: dict[Dimension, set[Unit]] = current_values.get("available_units") if "available_units" in current_values else changed_values.get("available_units")  # type: ignore
                    
                    if selected_unit is not None:
                        if selected_unit.dimension not in available_units:
                            new_available_units: dict[Dimension, set[Unit]] = self_ref._deep_copy_available_units()
                            new_available_units[selected_unit.dimension] = {selected_unit}
                            return {"available_units": new_available_units}
                        elif selected_unit not in available_units[selected_unit.dimension]:
                            new_available_units = self_ref._deep_copy_available_units()
                            new_available_units[selected_unit.dimension].add(selected_unit)
                            return {"available_units": new_available_units}
                    
                    return {}

                case True, False:
                    selected_unit = changed_values["selected_unit"]
                    available_units: dict[Dimension, set[Unit]] = current_values["available_units"]
                    
                    if selected_unit is not None:
                        if selected_unit.dimension not in available_units:
                            # Add the dimension to the available units
                            new_available_units = self_ref._deep_copy_available_units()
                            new_available_units[selected_unit.dimension] = set()    
                            new_available_units[selected_unit.dimension].add(selected_unit)
                            return {"available_units": new_available_units}
                        else:
                            if not selected_unit in available_units[selected_unit.dimension]:
                                new_available_units = self_ref._deep_copy_available_units()
                                # Must copy the set too, otherwise we modify the original
                                new_available_units[selected_unit.dimension] = available_units[selected_unit.dimension].copy()
                                new_available_units[selected_unit.dimension].add(selected_unit)
                                return {"available_units": new_available_units}
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
            verification_method=verification_method,
            add_values_to_be_updated_callback=add_values_to_be_updated_callback, # type: ignore
            parent_of_widgets=parent_of_widgets,
            logger=logger
        )
        
        if hook_available_units is not None:
            self.connect_hook(hook_available_units, "available_units", initial_sync_mode="use_target_value")
        if hook_selected_unit is not None:
            self.connect_hook(hook_selected_unit,"selected_unit", initial_sync_mode="use_target_value")

    def _deep_copy_available_units(self) -> dict[Dimension, set[Unit]]:
        """Deep copy the available units."""
        available_units: dict[Dimension, set[Unit]] = self.get_value_reference_of_hook("available_units") # type: ignore
        return {dimension: set(units) for dimension, units in available_units.items()}

    ###########################################################################
    # Widget methods
    ###########################################################################

    def _initialize_widgets(self) -> None:
        """
        Create and configure all the user interface widgets.
        """

        self._unit_combobox = ControlledComboBox(self, logger=self._logger)
        self._unit_editable_combobox = ControlledEditableComboBox(self, logger=self._logger)
        self._unit_line_edit = ControlledLineEdit(self, logger=self._logger)

        # Connect UI -> model
        self._unit_combobox.currentIndexChanged.connect(lambda _i: self._on_combobox_index_changed())
        self._unit_editable_combobox.userEditingFinished.connect(lambda text: self._on_combobox_edit_finished(text))
        self._unit_editable_combobox.currentIndexChanged.connect(lambda _i: self._on_editable_combobox_index_changed())
        self._unit_line_edit.editingFinished.connect(self._on_unit_line_edit_edit_finished)

        self._blankable_widget_unit_combobox = BlankableWidget(self._unit_combobox)
        self._blankable_widget_unit_editable_combobox = BlankableWidget(self._unit_editable_combobox)
        self._blankable_widget_unit_line_edit = BlankableWidget(self._unit_line_edit)

    def _on_combobox_index_changed(self) -> None:
        """
        Handle when the user selects a different unit from the dropdown menu.
        """

        if self.is_blocking_signals:
            return

        currently_selected_unit: Optional[Unit] = self.get_value_reference_of_hook("selected_unit") # type: ignore
        if currently_selected_unit is None:
            self.invalidate_widgets()
            return
               
        ################# Processing user input #################

        dict_to_set: dict[Literal["selected_unit", "available_units"], Any] = {}

        # Get the new unit from the combo box

        new_unit: Optional[Unit] = self._unit_combobox.currentData()

        log_msg(self, "_on_combobox_index_changed", self._logger, f"new_unit: {new_unit}")

        if new_unit is None:
            log_bool(self, "_on_combobox_index_changed", self._logger, False, "No unit selected")
            self.invalidate_widgets()
            return

        # Take care of the unit options
        new_unit_options: dict[Dimension, set[Unit]] = self.get_value_reference_of_hook("available_units").copy() # type: ignore
        if new_unit.dimension not in new_unit_options:
            # The new unit must have the same dimension as the current unit!
            self.invalidate_widgets()
            return
        if new_unit not in new_unit_options[new_unit.dimension]:
            new_unit_options[new_unit.dimension].add(new_unit)

        ################# Verify the new value #################

        dict_to_set["available_units"] = new_unit_options
        dict_to_set["selected_unit"] = new_unit

        ################# Updating the widgets and setting the component values #################

        log_msg(self, "_on_combobox_index_changed", self._logger, f"dict_to_set: {dict_to_set}")

        self._submit_values_on_widget_changed(dict_to_set)

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

        currently_selected_unit: Optional[Unit] = self.get_value_reference_of_hook("selected_unit") # type: ignore
        if currently_selected_unit is None:
            self.invalidate_widgets()
            return
        
        ################# Processing user input #################
     
        dict_to_set: dict[Literal["selected_unit", "available_units"], Any] = {}

        # Get the new value from the line edit
        text: str = self._unit_line_edit.text().strip()

        log_msg(self, "_on_unit_line_edit_edit_finished", self._logger, f"text: {text}")
        
        try:
            new_unit: Unit = Unit(text)
        except Exception as e:
            log_bool(self, "_on_unit_line_edit_edit_finished", self._logger, False, str(e))
            self.invalidate_widgets()
            return

        # Take care of the unit options
        new_unit_options: dict[Dimension, set[Unit]] = self.get_value_of_hook("available_units") # type: ignore
        if new_unit.dimension not in new_unit_options:
            new_unit_options[new_unit.dimension] = set()
        if new_unit not in new_unit_options[new_unit.dimension]:
            new_unit_options[new_unit.dimension].add(new_unit)

        ################# Verify the new value #################

        dict_to_set["selected_unit"] = new_unit
        dict_to_set["available_units"] = new_unit_options

        ################# Updating the widgets and setting the component values #################

        log_msg(self, "_on_unit_line_edit_edit_finished", self._logger, f"dict_to_set: {dict_to_set}")

        self._submit_values_on_widget_changed(dict_to_set)

        ################################################################

    def _on_editable_combobox_index_changed(self) -> None:
        """
        Handle editable combo box index change.
        """

        if self.is_blocking_signals:
            return

        currently_selected_unit: Optional[Unit] = self.get_value_reference_of_hook("selected_unit") # type: ignore
        if currently_selected_unit is None:
            self.invalidate_widgets()
            return

        ################# Processing user input #################

        dict_to_set: dict[Literal["selected_unit", "available_units"], Any] = {}

        current_unit: Unit = self.get_value_reference_of_hook("selected_unit") # type: ignore

        # Get the new value from the editable combo box
        new_unit: Optional[Unit] = self._unit_editable_combobox.currentData()

        log_msg(self, "_on_editable_combobox_index_changed", self._logger, f"new_unit: {new_unit}")

        if new_unit is None:
            self.invalidate_widgets()
            return
        
        if new_unit.dimension != current_unit.dimension:
            self.invalidate_widgets()
            return
        
        # Take care of the unit options

        new_unit_options: dict[Dimension, set[Unit]] = self.get_value_reference_of_hook("available_units").copy() # type: ignore
        update_unit_options: bool = False
        if new_unit.dimension not in new_unit_options:
            new_unit_options[new_unit.dimension] = set()
            update_unit_options = True

        ################# Verify the new value #################

        dict_to_set["selected_unit"] = new_unit
        dict_to_set["available_units"] = new_unit_options

        ################# Updating the widgets and setting the component values #################

        log_msg(self, "_on_editable_combobox_index_changed", self._logger, f"dict_to_set: {dict_to_set}")

        self._submit_values_on_widget_changed(dict_to_set)

        ################################################################

    def _on_combobox_edit_finished(self, text: str) -> None:    
        """
        Handle combo box editing finished.
        """

        if self.is_blocking_signals:
            return

        currently_selected_unit: Optional[Unit] = self.get_value_reference_of_hook("selected_unit") # type: ignore
        if currently_selected_unit is None:
            self.invalidate_widgets()
            return
        
        ################# Processing user input #################

        dict_to_set: dict[Literal["selected_unit", "available_units"], Any] = {}

        log_msg(self, "_on_combobox_edit_finished", self._logger, f"text: {text}")
        
        try:
            new_unit: Unit = Unit(text)
        except Exception:
            log_bool(self, "on_combobox_edit_finished", self._logger, False, "Invalid unit text")
            self.invalidate_widgets()
            return
        
        current_unit: Unit = self.get_value_reference_of_hook("selected_unit") # type: ignore

        if new_unit.dimension != current_unit.dimension:
            log_bool(self, "on_combobox_edit_finished", self._logger, False, "Unit dimension mismatch")
            self.invalidate_widgets()
            return
        
        new_unit_options: dict[Dimension, set[Unit]] = self.get_value_of_hook("available_units") # type: ignore
        if new_unit.dimension not in new_unit_options:
            new_unit_options[new_unit.dimension] = set()
        if new_unit not in new_unit_options[new_unit.dimension]:
            new_unit_options[new_unit.dimension].add(new_unit)

        ################# Updating the widgets and setting the component values #################

        dict_to_set["selected_unit"] = new_unit
        dict_to_set["available_units"] = new_unit_options
        
        log_msg(self, "_on_combobox_edit_finished", self._logger, f"dict_to_set: {dict_to_set}")
        
        self._submit_values_on_widget_changed(dict_to_set)
        
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

        selected_unit: Optional[Unit] = self.get_value_reference_of_hook("selected_unit") # type: ignore
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

            available_units: set[Unit] = self.get_value_reference_of_hook("available_units")[selected_unit.dimension] # type: ignore
            
            self._unit_line_edit.setText(self._formatter(selected_unit))

            self._unit_combobox.clear()
            for unit in sorted(available_units, key=lambda u: self._formatter(u)):
                self._unit_combobox.addItem(self._formatter(unit), userData=unit)
            self._unit_combobox.setCurrentIndex(self._unit_combobox.findData(selected_unit))

            self._unit_editable_combobox.clear()
            for unit in sorted(available_units, key=lambda u: self._formatter(u)):
                self._unit_editable_combobox.addItem(self._formatter(unit), userData=unit)
            self._unit_editable_combobox.setCurrentIndex(self._unit_editable_combobox.findData(selected_unit))
        
    ###########################################################################
    # Public API
    ###########################################################################

    @property
    def selectable_unit_options(self) -> set[Unit]:
        """Get all the currently selectable units. Those should be the available units for the selected unit's dimension."""
        if self.selected_unit is not None:
            return self.available_units[self.selected_unit.dimension]
        else:
            return set()

    def change_selected_unit_and_selectable_units(self, selected_unit: Unit, selectable_units: set[Unit]) -> None:
        """
        Change the selected unit and selectable units for the unit's dimension.
        
        ** Careful: This changers the selectable units for the selected unit's dimension.
        """
        available_options_dict: dict[Dimension, set[Unit]] = self._deep_copy_available_units()
        if selected_unit is not None:
            available_options_dict[selected_unit.dimension] = selectable_units
        self.submit_values({"selected_unit": selected_unit, "available_units": available_options_dict})

    @property
    def selected_unit(self) -> Optional[Unit]:
        """Get the currently selected unit."""
        return self.get_value_of_hook("selected_unit") # type: ignore

    @selected_unit.setter
    def selected_unit(self, value: Optional[Unit]) -> None:
        """Set the selected unit."""
        self.submit_values({"selected_unit": value})

    @property
    def selected_unit_hook(self) -> OwnedHookLike[Optional[Unit]]:
        """Get the hook for the selected unit."""
        return self.get_hook("selected_unit") # type: ignore

    @property
    def available_units(self) -> Mapping[Dimension, set[Unit]]:
        """Get the available units."""
        return self.get_value_of_hook("available_units") # type: ignore

    @available_units.setter
    def available_units(self, units: set[Unit]) -> None:
        """Set the available units."""
        self.submit_values({"available_units": units})

    @property
    def available_units_hook(self) -> OwnedHookLike[dict[Dimension, set[Unit]]]:
        """Get the hook for the available units."""
        return self.get_hook("available_units") # type: ignore

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
    
    ###########################################################################
    # Debugging
    ###########################################################################

    def all_widgets_as_frame(self) -> QFrame:
        """
        Create a comprehensive demo frame containing all available widgets.
        """
        frame = QFrame()
        layout = QVBoxLayout()
        layout.addWidget(self.widget_combobox)
        layout.addWidget(self.widget_editable_combobox)
        layout.addWidget(self.widget_line_edit)
        frame.setLayout(layout)
        return frame