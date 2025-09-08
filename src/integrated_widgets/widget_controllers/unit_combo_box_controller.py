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
from observables import HookLike, ObservableSingleValueLike, ObservableDictLike, InitialSyncMode

# Local imports
from ..widget_controllers.base_controller_with_disable import BaseWidgetControllerWithDisable
from ..guarded_widgets.guarded_editable_combobox import GuardedEditableComboBox
from ..guarded_widgets.guarded_line_edit import GuardedLineEdit
from ..guarded_widgets.guarded_combobox import GuardedComboBox
from ..util.resources import log_bool, log_msg

class UnitComboBoxController(BaseWidgetControllerWithDisable[Literal["selected_unit", "available_units"], Any]):

    def __init__(
        self,
        selected_unit: Unit | HookLike[Unit] | ObservableSingleValueLike[Unit],
        available_units: dict[Dimension, set[Unit]] | HookLike[dict[Dimension, set[Unit]]] | ObservableDictLike[Dimension, set[Unit]],
        formatter: Callable[[Unit], str] = lambda u: u.format_string(as_fraction=True),
        parent: Optional[QWidget] = None,
        logger: Optional[Logger] = None,
    ) -> None:

        self._formatter = formatter

        # Handle different types of selected_unit and available_units
        if isinstance(selected_unit, Unit):
            # It's a direct value
            initial_selected_unit: Unit = selected_unit
            hook_selected_unit: Optional[HookLike[Unit]] = None

        elif isinstance(selected_unit, HookLike):
            # It's a hook - get initial value
            initial_selected_unit = selected_unit.value # type: ignore
            hook_selected_unit = selected_unit

        elif isinstance(selected_unit, ObservableSingleValueLike):
            # It's an observable - get initial value
            initial_selected_unit = selected_unit.value
            hook_selected_unit = selected_unit.value_hook

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
        
        def verification_method(x: Mapping[Literal["selected_unit", "available_units"], Any]) -> tuple[bool, str]:
            # Handle partial updates by getting current values for missing keys

            if "selected_unit" in x:
                selected_unit: Unit = x["selected_unit"]
            else:
                selected_unit = self.get_value("selected_unit")

            if "available_units" in x:
                available_units: dict[Dimension, set[Unit]] = x["available_units"]
            else:
                available_units = self.get_value("available_units")

            unit_options: set[Unit] = available_units[selected_unit.dimension]

            if not selected_unit in unit_options:
                return False, f"Selected unit {selected_unit} not in available units for dimension {selected_unit.dimension}: {unit_options}"
            
            return True, "Verification method passed"

        super().__init__(
            {
                "selected_unit": initial_selected_unit,
                "available_units": initial_available_units
            },
            verification_method=verification_method,
            parent=parent,
            logger=logger
        )
        
        if hook_available_units is not None:
            self.connect(hook_available_units, "available_units", initial_sync_mode=InitialSyncMode.USE_TARGET_VALUE)
        if hook_selected_unit is not None:
            self.connect(hook_selected_unit,"selected_unit", initial_sync_mode=InitialSyncMode.USE_TARGET_VALUE)

    ###########################################################################
    # Widget methods
    ###########################################################################

    def _initialize_widgets(self) -> None:
        """
        Create and configure all the user interface widgets.
        
        """

        self._unit_combobox = GuardedComboBox(self, logger=self._logger)
        self._unit_editable_combobox = GuardedEditableComboBox(self, logger=self._logger)
        self._unit_line_edit = GuardedLineEdit(self, logger=self._logger)

        # Connect UI -> model
        self._unit_combobox.currentIndexChanged.connect(lambda _i: self._on_combobox_index_changed())
        self._unit_editable_combobox.userEditingFinished.connect(lambda text: self._on_combobox_edit_finished(text))
        self._unit_editable_combobox.currentIndexChanged.connect(lambda _i: self._on_editable_combobox_index_changed())
        self._unit_line_edit.editingFinished.connect(self._on_unit_line_edit_edit_finished)

    def _disable_widgets(self) -> None:
        """
        Disable all widgets.
        """

        self._unit_combobox.clear()
        self._unit_editable_combobox.clear()
        self._unit_line_edit.setText("")
        self._unit_combobox.setEnabled(False)
        self._unit_editable_combobox.setEnabled(False)
        self._unit_line_edit.setEnabled(False)

    def _enable_widgets(self, initial_component_values: dict[Literal["selected_unit", "available_units"], Any]) -> None:
        """
        Enable all widgets.
        """

        self._unit_combobox.setEnabled(True)
        self._unit_editable_combobox.setEnabled(True)
        self._unit_line_edit.setEnabled(True)

        self._set_incomplete_primary_component_values(initial_component_values)

    def _on_combobox_index_changed(self) -> None:
        """
        Handle when the user selects a different unit from the dropdown menu.
        """

        if self.is_blocking_signals:
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
        new_unit_options: dict[Dimension, set[Unit]] = self._get_component_value_reference("available_units").copy()
        if new_unit.dimension not in new_unit_options:
            # The new unit must have the same dimension as the current unit!
            self.invalidate_widgets()
            return
        if new_unit not in new_unit_options[new_unit.dimension]:
            new_unit_options[new_unit.dimension].add(new_unit)

        ################# Verify the new value #################

        dict_to_set["available_units"] = new_unit_options
        dict_to_set["selected_unit"] = new_unit

        if self._verification_method is not None:
            success, message = self._verification_method(dict_to_set)
            log_bool(self, "verification_method", self._logger, success, message)
            if not success:
                self.invalidate_widgets()
                return
        
        ################# Updating the widgets and setting the component values #################

        log_msg(self, "_on_combobox_index_changed", self._logger, f"dict_to_set: {dict_to_set}")

        self._set_incomplete_primary_component_values(dict_to_set)

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
        new_unit_options: dict[Dimension, set[Unit]] = self._get_component_value_reference("available_units").copy()
        if new_unit.dimension not in new_unit_options:
            new_unit_options[new_unit.dimension] = set()
        if new_unit not in new_unit_options[new_unit.dimension]:
            new_unit_options[new_unit.dimension].add(new_unit)

        ################# Verify the new value #################

        dict_to_set["selected_unit"] = new_unit
        dict_to_set["available_units"] = new_unit_options

        if self._verification_method is not None:
            success, message = self._verification_method(dict_to_set)
            log_bool(self, "verification_method", self._logger, success, message)
            if not success:
                self.invalidate_widgets()
                return

        ################# Updating the widgets and setting the component values #################

        log_msg(self, "_on_unit_line_edit_edit_finished", self._logger, f"dict_to_set: {dict_to_set}")

        self._set_incomplete_primary_component_values(dict_to_set)

        ################################################################

    def _on_editable_combobox_index_changed(self) -> None:
        """
        Handle editable combo box index change.
        """

        if self.is_blocking_signals:
            return

        ################# Processing user input #################

        dict_to_set: dict[Literal["selected_unit", "available_units"], Any] = {}

        current_unit: Unit = self._get_component_value_reference("selected_unit")

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

        new_unit_options: dict[Dimension, set[Unit]] = self._get_component_value_reference("available_units").copy()
        update_unit_options: bool = False
        if new_unit.dimension not in new_unit_options:
            new_unit_options[new_unit.dimension] = set()
            update_unit_options = True

        ################# Verify the new value #################

        dict_to_set["selected_unit"] = new_unit
        dict_to_set["available_units"] = new_unit_options

        if self._verification_method is not None:
            success, message = self._verification_method(dict_to_set)
            log_bool(self, "verification_method", self._logger, success, message)
            if not success:
                self.invalidate_widgets()
                return

        ################# Updating the widgets and setting the component values #################

        log_msg(self, "_on_editable_combobox_index_changed", self._logger, f"dict_to_set: {dict_to_set}")

        self._set_incomplete_primary_component_values(dict_to_set)

        ################################################################

    def _on_combobox_edit_finished(self, text: str) -> None:    
        """
        Handle combo box editing finished.
        """

        if self.is_blocking_signals:
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
        
        current_unit: Unit = self._get_component_value_reference("selected_unit")

        if new_unit.dimension != current_unit.dimension:
            log_bool(self, "on_combobox_edit_finished", self._logger, False, "Unit dimension mismatch")
            self.invalidate_widgets()
            return
        
        new_unit_options: dict[Dimension, set[Unit]] = self._get_component_value_reference("available_units").copy()
        if new_unit.dimension not in new_unit_options:
            new_unit_options[new_unit.dimension] = set()
        if new_unit not in new_unit_options[new_unit.dimension]:
            new_unit_options[new_unit.dimension].add(new_unit)

        ################# Verify the new value #################

        dict_to_set["selected_unit"] = new_unit
        dict_to_set["available_units"] = new_unit_options

        if self._verification_method is not None:
            success, message = self._verification_method(dict_to_set)
            log_bool(self, "verification_method", self._logger, success, message)
            if not success:
                self.invalidate_widgets()
                return
            
        ################# Updating the widgets and setting the component values #################
        
        log_msg(self, "_on_combobox_edit_finished", self._logger, f"dict_to_set: {dict_to_set}")
        
        self._set_incomplete_primary_component_values(dict_to_set)
        
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

        component_values: dict[Literal["selected_unit", "available_units"], Any] = self.component_values_dict

        selected_unit: Unit = component_values["selected_unit"]
        available_units: set[Unit] = component_values["available_units"][selected_unit.dimension]
        log_msg(self, "_invalidate_widgets", self._logger, f"selected_unit: {selected_unit}")
        log_msg(self, "_invalidate_widgets", self._logger, f"available_units: {available_units}")

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

    def change_selected_option_and_available_options(self, selected_option: Optional[Unit], available_options: set[Unit]) -> None:
        """Change the selected option and available options at once."""
        self._set_incomplete_primary_component_values({"selected_unit": selected_option, "available_units": available_options})

    @property
    def selected_unit(self) -> Unit:
        """Get the currently selected unit."""
        if self.is_disabled:
            raise ValueError("Controller is disabled")
        return self.get_value("selected_unit")

    @selected_unit.setter
    def selected_unit(self, value: Optional[Unit]) -> None:
        """Set the selected unit."""
        self._set_incomplete_primary_component_values({"selected_unit": value})

    @property
    def selected_unit_hook(self) -> HookLike[Unit]:
        """Get the hook for the selected unit."""
        return self.get_component_hook("selected_unit")

    @property
    def available_units(self) -> set[Unit]:
        """Get the available units."""
        return self.get_value("available_units")

    @available_units.setter
    def available_units(self, units: set[Unit]) -> None:
        """Set the available units."""
        self._set_incomplete_primary_component_values({"available_units": units})

    @property
    def available_units_hook(self) -> HookLike[set[Unit]]:
        """Get the hook for the available units."""
        return self.get_component_hook("available_units")

    # Widgets

    @property
    def widget_combobox(self) -> GuardedComboBox:
        """Get the combo box widget."""
        return self._unit_combobox
    
    @property
    def widget_editable_combobox(self) -> GuardedEditableComboBox:
        """Get the editable combo box widget."""
        return self._unit_editable_combobox
    
    @property
    def widget_line_edit(self) -> GuardedLineEdit:
        """Get the line edit widget."""
        return self._unit_line_edit
    
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