from __future__ import annotations

# Standard library imports
from typing import Callable, Optional, Any, Mapping, Literal
from logging import Logger
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QFrame, QVBoxLayout, QGroupBox

# BAB imports
from united_system import RealUnitedScalar, Unit, Dimension
from observables import ObservableSingleValueLike, HookLike, InitialSyncMode, ObservableDictLike, ObservableSingleValue, ObservableDict

# Local imports
from ..widget_controllers.base_controller_with_disable import BaseWidgetControllerWithDisable
from ..widget_controllers.display_value_controller import DisplayValueController
from ..guarded_widgets.guarded_label import GuardedLabel
from ..guarded_widgets.guarded_combobox import GuardedComboBox
from ..guarded_widgets.guarded_line_edit import GuardedLineEdit
from ..guarded_widgets.guarded_editable_combobox import GuardedEditableComboBox
from ..util.general import DEFAULT_FLOAT_FORMAT_VALUE
from ..util.resources import log_bool, log_msg

class RealUnitedScalarController(BaseWidgetControllerWithDisable[Literal["value", "unit_options"], Any]):
    """
    A comprehensive widget controller for displaying and editing physical quantities with units.
    
    This controller provides a complete user interface for working with RealUnitedScalar values,
    which represent physical quantities like "100.5 km", "23.7 kg", or "120 V". Users can:
    
    - **View** the quantity in multiple formats (full display, numeric value only, unit only)
    - **Edit** the complete quantity as text (e.g., "50 m/s")
    - **Edit** just the numeric value while keeping the same unit
    - **Change** the unit from a dropdown of compatible units
    - **Type** new units to extend available options
    
    ## User Interface Components
    
    The controller creates several widgets that users can interact with:
    
    1. **Display Labels**: Show the current value in formatted text
       - Real United Scalar Label: Shows full quantity (e.g., "100.000 km")
       - Value Label: Shows only the numeric part (e.g., "100.000")
    
    2. **Unit Selector**: Dropdown menu for changing units
       - Contains all compatible units for the current dimension
       - Automatically converts the value when a new unit is selected
       - Example: Changing from "km" to "m" converts "1.5 km" to "1500 m"
    
    3. **Edit Fields**: Allow users to modify the quantity
       - Real United Scalar Edit: Edit the complete quantity (e.g., type "50 m/s")
       - Value Edit: Edit only the numeric value (keeps current unit)
       - Unit Edit: Type new units to add them to available options
    
    ## Practical Examples
    
    **Distance measurements:**
    - Start with "100 km"
    - Use unit selector to change to "m" → automatically becomes "100000 m"
    - Edit value to "50" → becomes "50 m"
    - Type "cm" in unit field → adds centimeters to available options
    
    **Voltage measurements:**
    - Type "1.5 V" in the complete edit field
    - Use unit selector to change to "mV" → becomes "1500 mV"
    - Type "kV" in unit field to add kilovolts as an option
    
    ## Integration with Observable System
    
    The controller automatically synchronizes with observable values, making it perfect
    for real-time applications where the displayed quantity might change programmatically
    or need to be shared between multiple UI components.
    
    ## Unit Compatibility and Validation
    
    The controller ensures that only compatible units can be selected or entered.
    For example, you cannot change a distance measurement to a time unit. Invalid
    entries are automatically rejected and the display reverts to the last valid state.
    """

    def __init__(
        self,
        value: Optional[RealUnitedScalar | HookLike[RealUnitedScalar] | ObservableSingleValueLike[RealUnitedScalar]] = None,
        display_unit_options: Optional[dict[Dimension, set[Unit]]] | HookLike[dict[Dimension, set[Unit]]] | ObservableDictLike[Dimension, set[Unit]] = None,
        value_formatter: Callable[[RealUnitedScalar], str] = DEFAULT_FLOAT_FORMAT_VALUE,
        unit_formatter: Callable[[Unit], str] = lambda u: u.format_string(as_fraction=True),
        unit_options_sorter: Callable[[set[Unit]], list[Unit]] = lambda u: sorted(u, key=lambda x: x.format_string(as_fraction=True)),
        *,
        allowed_dimensions: Optional[set[Dimension]] = None,
        parent: Optional[QWidget] = None,
        logger: Optional[Logger] = None,
    ) -> None:
        """
        Create a new RealUnitedScalarController for displaying and editing physical quantities.
        
        This constructor sets up all the widgets and connects them to the underlying data model.
        The controller can work with static values or connect to observable data sources for
        real-time updates.
        
        Args:
            value: The initial physical quantity to display. Can be:
                - A RealUnitedScalar object (e.g., RealUnitedScalar(100, Unit("km")))
                - An observable that provides RealUnitedScalar values
                - A hook for two-way data binding
                - None to start with an empty/default value
                
            display_unit_options: Available units for the dropdown selector. Can be:
                - A dictionary mapping dimensions to sets of units
                  Example: {Dimension.LENGTH: {Unit("m"), Unit("km"), Unit("cm")}}
                - An observable dictionary for dynamic unit options
                - None to start with minimal default options
                
            formatter: Function to format the quantity for display labels.
                Default shows values like "100.000 km" with 3 decimal places.
                
            unit_options_sorter: Function to sort units in the dropdown.
                Default sorts alphabetically by unit symbol.
                
            allowed_dimensions: Optional restriction on which physical dimensions
                are permitted. For example, only allow length measurements by
                passing {NamedQuantity.LENGTH}. None allows all dimensions.
                
            parent: Parent Qt widget for proper widget hierarchy and cleanup.
                
        Example Usage:
            ```python
            # Simple static value
            controller = RealUnitedScalarController(
                value=RealUnitedScalar(100, Unit("km"))
            )
            
            # With custom unit options
            unit_options = {
                Dimension.LENGTH: {Unit("m"), Unit("km"), Unit("cm"), Unit("mm")},
                Dimension.TIME: {Unit("s"), Unit("min"), Unit("h")}
            }
            controller = RealUnitedScalarController(
                value=RealUnitedScalar(5, Unit("km")),
                display_unit_options=unit_options
            )
            
            # Connected to observable data
            observable_value = ObservableSingleValue(RealUnitedScalar(50, Unit("m")))
            controller = RealUnitedScalarController(value=observable_value)
            ```
        """
        
        self._value_formatter = value_formatter
        self._unit_formatter = unit_formatter
        self._unit_options_sorter = unit_options_sorter
        self._allowed_dimensions = allowed_dimensions

        # Handle different types of value
        if value is None:
            initial_value: Optional[RealUnitedScalar] = None
            value_hook: Optional[HookLike[RealUnitedScalar]] = None
        elif isinstance(value, RealUnitedScalar):
            initial_value: Optional[RealUnitedScalar] = value
            value_hook: Optional[HookLike[RealUnitedScalar]] = None
        elif isinstance(value, HookLike):
            # It's a hook - get initial value
            initial_value: Optional[RealUnitedScalar] = value.value  # type: ignore
            value_hook: Optional[HookLike[RealUnitedScalar]] = value

        elif isinstance(value, ObservableSingleValueLike):
            # It's an ObservableSingleValue - get initial value
            initial_value: Optional[RealUnitedScalar] = value.value
            value_hook: Optional[HookLike[RealUnitedScalar]] = value.hook_value 

        else:
            raise ValueError(f"Invalid value: {value}")
        
        # Handle different types of display_unit_options
        if isinstance(display_unit_options, HookLike):
            # It's a hook - get initial value
            initial_display_unit_options: dict[Dimension, set[Unit]] = display_unit_options.value
            display_unit_options_hook: Optional[HookLike[dict[Dimension, set[Unit]]]] = display_unit_options

        elif isinstance(display_unit_options, ObservableDictLike):
            # It's an ObservableDictLike - get initial value
            initial_display_unit_options: dict[Dimension, set[Unit]] = display_unit_options.value
            display_unit_options_hook: Optional[HookLike[dict[Dimension, set[Unit]]]] = display_unit_options.hook_value

        elif isinstance(display_unit_options, dict):
            # It's a direct dict
            initial_display_unit_options: dict[Dimension, set[Unit]] = display_unit_options
            display_unit_options_hook: Optional[HookLike[dict[Dimension, set[Unit]]]] = None

        else:
            raise ValueError(f"Invalid display_unit_options: {display_unit_options}")
        
        def verification_method(x: Mapping[Literal["value", "unit_options"], Any]) -> tuple[bool, str]:

            # Get the unit options
            if "unit_options" in x:
                unit_options_dict: dict[Dimension, set[Unit]] = x.get("unit_options", initial_display_unit_options)
            else:
                unit_options_dict: dict[Dimension, set[Unit]] = self._get_component_value_reference("unit_options")

            # Check if the unit options are valid
            if not isinstance(unit_options_dict, dict):
                return False, f"Unit options must be a dict, got {type(unit_options_dict)}"
            for dimension, units in unit_options_dict.items():
                if not isinstance(dimension, Dimension):
                    return False, f"Unit options dimension must be a Dimension, got {type(dimension)}"
                if allowed_dimensions is not None and dimension not in allowed_dimensions:
                    return False, f"Unit options dimension {dimension} not in allowed dimensions {allowed_dimensions}"
                if not isinstance(units, set):
                    return False, f"Unit options units must be a set, got {type(units)}"
                for unit in units:
                    if not isinstance(unit, Unit):
                        return False, f"Unit options unit must be a Unit, got {type(unit)}"

            # Get the value
            if "value" in x:
                value: RealUnitedScalar = x.get("value", initial_value)
            else:
                value: RealUnitedScalar = self._get_component_value_reference("value")

            # Check if the value is valid
            if not isinstance(value, RealUnitedScalar):
                return False, f"Value must be a RealUnitedScalar, got {type(value)}"
            if self._allowed_dimensions is not None and value.dimension not in self._allowed_dimensions:
                return False, f"Value dimension {value.dimension} not in allowed dimensions {self._allowed_dimensions}"
        
            # Get the unit
            unit: Unit = value.unit
            if unit.dimension not in unit_options_dict:
                return False, f"Value dimension {unit.dimension} not in unit options {unit_options_dict}"
            unit_options: set[Unit] = unit_options_dict[unit.dimension]
            if unit not in unit_options:
                return False, f"Unit {unit} not in unit options {unit_options}"
   
            # Checks passed
            return True, "Verification method passed"

        super().__init__(
            {
                "value": initial_value,
                "unit_options": initial_display_unit_options
            },
            verification_method=verification_method,
            parent=parent,
            logger=logger
        )
        
        if value_hook is not None:
            self.connect(value_hook, to_key="value", initial_sync_mode=InitialSyncMode.USE_TARGET_VALUE)
        if display_unit_options_hook is not None:
            self.connect(display_unit_options_hook, to_key="unit_options", initial_sync_mode=InitialSyncMode.USE_TARGET_VALUE)

    ###########################################################################
    # Widget methods
    ###########################################################################

    def _initialize_widgets(self) -> None:
        """
        Create and configure all the user interface widgets.
        
        This method sets up the complete widget collection that users interact with:
        
        **Display Widgets (Read-only):**
        - Real United Scalar Label: Shows the complete formatted quantity (e.g., "100.000 km")
        - Value Label: Shows only the numeric portion (e.g., "100.000")
        
        **Interactive Widgets:**
        - Unit Combo Box: Dropdown for selecting from available units of the same dimension
        - Real United Scalar Line Edit: Text field for entering complete quantities (e.g., "50 m/s")
        - Value Line Edit: Text field for editing just the numeric value
        - Unit Line Edit: Text field for typing new units to extend available options
        
        The method also connects all the interactive widgets to their respective event handlers
        so that user changes are properly processed and validated.
        
        Note: This method is called automatically during controller initialization.
        Users typically don't need to call this directly.
        """

        # Show real united scalar and change display unit widgets
        self._real_united_scalar_label = GuardedLabel(self)
        self._value_label = GuardedLabel(self)
        self._unit_combobox = GuardedComboBox(self)
        self._unit_editable_combobox = GuardedEditableComboBox(self)

        # Edit real united scalar and edit value and edit unit widgets
        self._real_united_scalar_line_edit = GuardedLineEdit(self)
        self._value_line_edit = GuardedLineEdit(self)
        self._unit_line_edit = GuardedLineEdit(self)

        # Connect UI -> model
        self._unit_combobox.currentIndexChanged.connect(lambda _i: self._on_unit_combo_changed())
        self._unit_editable_combobox.userEditingFinished.connect(lambda text: self._on_unit_editable_combobox_text_edited(text))
        self._unit_editable_combobox.currentIndexChanged.connect(lambda _i: self._on_unit_editable_combobox_index_changed())
        self._real_united_scalar_line_edit.editingFinished.connect(self._on_real_united_scalar_edited)
        self._value_line_edit.editingFinished.connect(self._on_value_edited)
        self._unit_line_edit.editingFinished.connect(self._on_unit_edited)

    def _disable_widgets(self) -> None:
        """
        Disable all widgets.
        """

        self._real_united_scalar_label.setText("")
        self._value_label.setText("")
        self._unit_combobox.clear()
        self._unit_editable_combobox.clear()
        self._unit_line_edit.setText("")
        self._real_united_scalar_line_edit.setText("")
        self._value_line_edit.setText("")

        self._real_united_scalar_label.setEnabled(False)
        self._value_label.setEnabled(False)
        self._unit_combobox.setEnabled(False)
        self._unit_editable_combobox.setEnabled(False)
        self._unit_line_edit.setEnabled(False)
        self._real_united_scalar_line_edit.setEnabled(False)
        self._value_line_edit.setEnabled(False)

    def _enable_widgets(self, initial_component_values: dict[Literal["value", "unit_options"], Any]) -> None:
        """
        Enable all widgets.
        """
        self._real_united_scalar_label.setEnabled(True)
        self._value_label.setEnabled(True)
        self._unit_combobox.setEnabled(True)
        self._unit_editable_combobox.setEnabled(True)
        self._unit_line_edit.setEnabled(True)
        self._real_united_scalar_line_edit.setEnabled(True)
        self._value_line_edit.setEnabled(True)

    def _on_unit_combo_changed(self) -> None:
        """
        Handle when the user selects a different unit from the dropdown menu.
        
        This method is called automatically when the user clicks on the unit dropdown
        and selects a different unit. It performs unit conversion while preserving
        the physical quantity's actual value.
        
        **What happens:**
        1. The numeric value is automatically converted to the new unit
        2. All display widgets are updated to show the converted value
        3. The unit dropdown shows the newly selected unit
        
        **Example:**
        - Current value: "1.5 km"
        - User selects "m" from dropdown
        - Result: "1500.000 m" (same distance, different unit)
        
        **Validation:**
        - Only units from the same physical dimension can be selected
        - If somehow an incompatible unit is selected, the change is rejected
        - The display automatically reverts to the previous valid state
        
        **Technical Details:**
        The conversion preserves the canonical (base SI) value while only changing
        the display unit. This ensures mathematical accuracy and consistency.
        """

        if self.is_blocking_signals:
            return
               
        ################# Processing user input #################

        dict_to_set: dict[Literal["value", "unit_options"], Any] = {}

        # Get the new unit from the combo box

        new_unit: Optional[Unit] = self._unit_combobox.currentData()
        if new_unit is None:
            self.apply_component_values_to_widgets()
            return
        
        # Take care of the unit options
        new_unit_options: dict[Dimension, set[Unit]] = self._get_component_value_reference("unit_options").copy()
        if new_unit.dimension not in new_unit_options:
            # The new unit must have the same dimension as the current unit!
            self.apply_component_values_to_widgets()
            return
        if new_unit not in new_unit_options[new_unit.dimension]:
            new_unit_options[new_unit.dimension].add(new_unit)

        # Create the new value (Only change the display unit, not the canonical value)
        current_value: RealUnitedScalar = self._get_component_value_reference("value")
        new_value: RealUnitedScalar = RealUnitedScalar(current_value.canonical_value, current_value.dimension, display_unit=new_unit)

        ################# Verify the new value #################

        dict_to_set["unit_options"] = new_unit_options
        dict_to_set["value"] = new_value

        if self._verification_method is not None:
            success, message = self._verification_method(dict_to_set)
            log_bool(self, "verification_method", self._logger, success, message)
            if not success:
                self.apply_component_values_to_widgets()
                return
        
        ################# Updating the widgets and setting the component values #################

        self._update_component_values_and_widgets(dict_to_set)

        ################################################################

    def _on_real_united_scalar_edited(self) -> None:
        """
        Handle when the user edits the complete quantity in the main text field.
        
        This method is called when the user types a complete physical quantity
        (value + unit) in the "Real United Scalar edit" field and presses Enter
        or clicks outside the field.
        
        **What the user can type:**
        - Complete quantities: "50 m", "1.5 km/h", "120 V", "25.7 kg"
        - Just numbers: "100" (keeps the current unit)
        - Complex units: "9.8 m/s^2", "3.14 rad/s"
        
        **What happens:**
        1. The text is parsed to extract the numeric value and unit
        2. If the unit is new, it's automatically added to available options
        3. All other widgets are updated to reflect the new quantity
        4. The unit dropdown is updated with the new unit if applicable
        
        **Examples:**
        - Type "50 m" → Value becomes 50, unit becomes meters
        - Type "2.5 km" → Value becomes 2500, unit shown in dropdown as km
        - Type "100 mph" → Adds mph to speed unit options (if allowed)
        
        **Error Handling:**
        - Invalid formats (like "abc def") are rejected
        - Incompatible dimensions are rejected based on allowed_dimensions
        - On error, the field reverts to the last valid value
        
        **Power User Features:**
        - Supports scientific notation: "1.5e-3 m" = "0.0015 m"
        - Handles complex units: "kg*m/s^2" for force units
        - Automatically normalizes unit representations
        """

        if self.is_blocking_signals:
            return
        
        ################# Processing user input #################
     
        dict_to_set: dict[Literal["value", "unit_options"], Any] = {}

        # Get the new value from the line edit
        text: str = self._real_united_scalar_line_edit.text().strip()
        if not text:
            new_value: RealUnitedScalar = RealUnitedScalar(float("nan"), Unit.dimensionless_unit())
        else:
            try:
                new_value: RealUnitedScalar = RealUnitedScalar(text)
            except Exception:
                return
            
        new_unit: Unit = new_value.unit

        # Take care of the unit options
        new_unit_options: dict[Dimension, set[Unit]] = self._get_component_value_reference("unit_options").copy()
        if new_unit.dimension not in new_unit_options:
            new_unit_options[new_unit.dimension] = set()
        if new_unit not in new_unit_options[new_unit.dimension]:
            new_unit_options[new_unit.dimension].add(new_unit)

        ################# Verify the new value #################

        dict_to_set["value"] = new_value
        dict_to_set["unit_options"] = new_unit_options

        if self._verification_method is not None:
            success, message = self._verification_method(dict_to_set)
            log_bool(self, "verification_method", self._logger, success, message)
            if not success:
                self.apply_component_values_to_widgets()
                return

        ################# Updating the widgets and setting the component values #################

        self._update_component_values_and_widgets(dict_to_set)

        ################################################################

    def _on_value_edited(self) -> None:
        """
        Handle when the user edits only the numeric value while keeping the same unit.
        
        This method is called when the user types a new number in the "Value edit" 
        field and presses Enter or clicks outside the field. The unit remains unchanged.
        
        **What the user can type:**
        - Decimal numbers: "123.45", "0.001", "1000"
        - Scientific notation: "1.5e-3", "2.1E+6"
        - Negative values: "-273.15" (for temperatures, etc.)
        
        **What happens:**
        1. The number is parsed and validated
        2. The current unit is preserved exactly as it was
        3. All display widgets show the new value with the same unit
        4. The unit dropdown selection remains unchanged
        
        **Examples:**
        - Current: "100 km", User types "50" → Result: "50 km"
        - Current: "1.5 V", User types "3.3" → Result: "3.3 V"
        - Current: "25 kg", User types "0" → Result: "0 kg"
        
        **Use Cases:**
        - Adjusting measurements while keeping the same scale
        - Quick value updates without changing units
        - Data entry when the unit is predetermined
        
        **Error Handling:**
        - Non-numeric input (like "abc") is rejected
        - Invalid numbers cause the field to revert to the last valid value
        - Empty input sets the value to NaN (not-a-number)
        
        **Precision:**
        The entered value is stored with full floating-point precision,
        though the display format may round for readability.
        """

        if self.is_blocking_signals:
            return
        
        ################# Processing user input #################
     
        dict_to_set: dict[Literal["value", "unit_options"], Any] = {}

        # Get the new value from the line edit
        text: str = self._value_line_edit.text().strip()
        current_unit: Unit = self._unit_combobox.currentData()

        if not text:
            new_value: RealUnitedScalar = RealUnitedScalar(float("nan"), current_unit)
        else:
            try:
                new_value: RealUnitedScalar = RealUnitedScalar(text, current_unit)
            except Exception:
                self.apply_component_values_to_widgets()
                return

        ################# Verify the new value #################

        dict_to_set["value"] = new_value
        dict_to_set["unit_options"] = self._get_component_value_reference("unit_options")

        if self._verification_method is not None:
            success, message = self._verification_method(dict_to_set)
            log_bool(self, "verification_method", self._logger, success, message)
            if not success:
                self.apply_component_values_to_widgets()
                return

        ################# Updating the widgets and setting the component values #################

        self._update_component_values_and_widgets(dict_to_set)

        ################################################################

    def _on_unit_edited(self) -> None:
        """
        Handle when the user types a new unit in the unit text field.
        
        This method is called when the user types a unit symbol or name in the 
        "Unit edit" field and presses Enter or clicks outside the field. This is
        the most flexible way to add new units or change to units not in the dropdown.
        
        **What the user can type:**
        - Basic units: "m", "kg", "s", "V", "A"
        - Prefixed units: "km", "mg", "kV", "mA", "µm"
        - Complex units: "m/s", "kg/m^3", "W/m^2", "rad/s"
        - Alternative names: "meter", "volt", "gram"
        
        **What happens:**
        1. The unit text is parsed and validated
        2. If it's a new unit, it's added to the available unit options
        3. The current numeric value is preserved with the new unit
        4. All display widgets are updated
        5. The unit dropdown is updated to include the new unit
        
        **Examples:**
        - Current: "100 m", User types "cm" → Result: "100 cm" (NOT converted!)
        - Current: "5 kg", User types "lb" → Adds pounds to mass options
        - Current: "50 V", User types "mV" → Result: "50 mV" + adds mV to dropdown
        
        **Important Behavior:**
        Unlike the dropdown selector, typing a unit does NOT perform automatic
        conversion. It changes the unit while keeping the same numeric value.
        
        **Adding New Dimensions:**
        This method can introduce entirely new physical dimensions:
        - Type "Hz" to add frequency measurements
        - Type "°C" to add temperature (if supported)
        - Type "bit/s" to add data transfer rates
        
        **Error Handling:**
        - Unrecognized unit symbols are rejected
        - Dimensionally incompatible units may be rejected (if restrictions are set)
        - Invalid unit syntax causes reversion to the previous valid state
        
        **Power User Features:**
        - Supports full unit expression syntax from the united_system library
        - Can handle complex derived units and unit arithmetic
        - Automatically normalizes unit representations for consistency
        """

        if self.is_blocking_signals:
            return
        
        ################# Processing user input #################
     
        dict_to_set: dict[Literal["value", "unit_options"], Any] = {}

        # Get the new value from the line edit
        text: str = self._unit_line_edit.text().strip()
        try:
            new_unit: Unit = Unit(text)
        except Exception as e:
            self.apply_component_values_to_widgets()
            return
        
        # Take care of the unit options
        new_unit_options: dict[Dimension, set[Unit]] = self._get_component_value_reference("unit_options").copy()
        if new_unit.dimension not in new_unit_options:
            new_unit_options[new_unit.dimension] = set()
        if new_unit not in new_unit_options[new_unit.dimension]:
            new_unit_options[new_unit.dimension].add(new_unit)

        # Create the new value
        current_float_value: float = float(self._value_line_edit.text().strip())
        new_value: RealUnitedScalar = RealUnitedScalar(current_float_value, new_unit)

        ################# Verify the new value #################

        dict_to_set["value"] = new_value
        dict_to_set["unit_options"] = new_unit_options

        if self._verification_method is not None:
            success, message = self._verification_method(dict_to_set)
            log_bool(self, "verification_method", self._logger, success, message)
            if not success:
                self.apply_component_values_to_widgets()
                return

        ################# Updating the widgets and setting the component values #################

        self.__internal_apply_component_values_to_widgets(dict_to_set)
        self._set_component_values(dict_to_set, notify_binding_system=True)

        ################################################################
        
    def _on_unit_editable_combobox_text_edited(self, text: str) -> None:
        """
        Handle when the user types a new unit in the unit text field.
        """

        if self.is_blocking_signals:
            return
               
        ################# Processing user input #################

        dict_to_set: dict[Literal["value", "unit_options"], Any] = {}

        # Get the new unit from the combo box

        log_msg(self, "_on_unit_editable_combobox_text_edited", self._logger, f"text: {text}")

        try:
            new_unit: Unit = Unit(text)
        except Exception:
            log_bool(self, "_on_unit_editable_combobox_text_edited", self._logger, False, "Invalid unit")
            self.apply_component_values_to_widgets()
            return
        
        # Take care of the unit options
        new_unit_options: dict[Dimension, set[Unit]] = self._get_component_value_reference("unit_options").copy()
        if new_unit.dimension not in new_unit_options:
            # The new unit must have the same dimension as the current unit!
            self.apply_component_values_to_widgets()
            return
        if new_unit not in new_unit_options[new_unit.dimension]:
            new_unit_options[new_unit.dimension].add(new_unit)

        # Create the new value (Only change the display unit, not the canonical value)
        current_value: RealUnitedScalar = self._get_component_value_reference("value")
        new_value: RealUnitedScalar = RealUnitedScalar(current_value.canonical_value, current_value.dimension, display_unit=new_unit)

        ################# Verify the new value #################

        dict_to_set["unit_options"] = new_unit_options
        dict_to_set["value"] = new_value

        if self._verification_method is not None:
            success, message = self._verification_method(dict_to_set)
            log_bool(self, "verification_method", self._logger, success, message)
            if not success:
                self.apply_component_values_to_widgets()
                return
        
        ################# Updating the widgets and setting the component values #################

        self._update_component_values_and_widgets(dict_to_set)
    
    def _on_unit_editable_combobox_index_changed(self) -> None:
        """
        Handle when the user selects a new unit in the unit dropdown.
        """

        if self.is_blocking_signals:
            return
               
        ################# Processing user input #################

        dict_to_set: dict[Literal["value", "unit_options"], Any] = {}

        # Get the new unit from the combo box

        new_unit: Optional[Unit] = self._unit_editable_combobox.currentData()
        if new_unit is None:
            self.apply_component_values_to_widgets()
            return
        
        # Take care of the unit options
        new_unit_options: dict[Dimension, set[Unit]] = self._get_component_value_reference("unit_options").copy()
        if new_unit.dimension not in new_unit_options:
            # The new unit must have the same dimension as the current unit!
            self.apply_component_values_to_widgets()
            return
        if new_unit not in new_unit_options[new_unit.dimension]:
            new_unit_options[new_unit.dimension].add(new_unit)

        # Create the new value (Only change the display unit, not the canonical value)
        current_value: RealUnitedScalar = self._get_component_value_reference("value")
        new_value: RealUnitedScalar = RealUnitedScalar(current_value.canonical_value, current_value.dimension, display_unit=new_unit)

        ################# Verify the new value #################

        dict_to_set["unit_options"] = new_unit_options
        dict_to_set["value"] = new_value

        if self._verification_method is not None:
            success, message = self._verification_method(dict_to_set)
            log_bool(self, "verification_method", self._logger, success, message)
            if not success:
                self.apply_component_values_to_widgets()
                return
        
        ################# Updating the widgets and setting the component values #################

        self._update_component_values_and_widgets(dict_to_set)

    def _fill_widgets_from_component_values(self, component_values: dict[Literal["value", "unit_options"], Any]) -> None:
        """
        Synchronize all widget displays with the current internal state.
        
        This method is called automatically whenever the underlying data changes,
        either through user interaction or programmatic updates via observables.
        It ensures that all visible widgets show consistent, up-to-date information.
        
        **What gets updated:**
        - Display labels show the current formatted quantity
        - Input fields reflect the current values
        - Unit dropdown is populated with available units for the current dimension
        - Unit dropdown selection matches the current unit
        
        **When this is called:**
        - After successful user edits
        - When connected observable values change
        - When validation fails and the display needs to revert
        - During initialization to show initial values
        
        **Internal Use:**
        This is an internal method. Users don't typically call this directly,
        but it's essential for maintaining UI consistency.

        **This method should be called while the signals are blocked.**
        """

        value: RealUnitedScalar = component_values["value"]
        available_units: dict[Dimension, set[Unit]] = component_values["unit_options"]

        log_msg(self, "_fill_widgets_from_component_values", self._logger, f"value: {value}")
        log_msg(self, "_fill_widgets_from_component_values", self._logger, f"available_units: {available_units}")

        float_value: float = value.value()
        selected_unit: Unit = value.unit
        unit_options: set[Unit] = available_units[selected_unit.dimension]

        # Real united scalar label and line edit
        self._real_united_scalar_label.setText(self._value_formatter(value))
        self._real_united_scalar_line_edit.setText(self._value_formatter(value))

        # Value label and line edit
        self._value_label.setText(f"{float_value:.3f}")
        self._value_line_edit.setText(f"{float_value:.3f}")

        # Unit line edit
        self._unit_line_edit.setText(self._unit_formatter(selected_unit))

        # Unit combobox
        self._unit_combobox.clear()
        for unit in sorted(unit_options, key=lambda u: self._unit_formatter(u)):
            self._unit_combobox.addItem(self._unit_formatter(unit), userData=unit)
        self._unit_combobox.setCurrentIndex(self._unit_combobox.findData(selected_unit))

        # Unit editable combobox
        self._unit_editable_combobox.clear()
        for unit in sorted(unit_options, key=lambda u: self._unit_formatter(u)):
            self._unit_editable_combobox.addItem(self._unit_formatter(unit), userData=unit)
        self._unit_editable_combobox.setCurrentIndex(self._unit_editable_combobox.findData(selected_unit))

    ###########################################################################
    # Disposal
    ###########################################################################

    def dispose_before_children(self) -> None:
        try:
            self._unit_combobox.currentIndexChanged.disconnect()
        except Exception:
            pass

    ###########################################################################
    # Public accessors
    ###########################################################################

    @property
    def value(self) -> RealUnitedScalar:
        """Get the current value."""
        return self.get_value("value")
    
    @value.setter
    def value(self, value: RealUnitedScalar) -> None:
        """Set the current value."""
        self._update_component_values_and_widgets({"value": value})

    @property
    def hook_value(self) -> HookLike[RealUnitedScalar]:
        """
        Get a hook for two-way binding to the current physical quantity value.
        
        This hook allows external code to read the current value and be notified
        when it changes, or to programmatically set new values that will be
        reflected in the UI.
        
        Returns:
            A hook that provides access to the current RealUnitedScalar value
            
        Example Usage:
            ```python
            controller = RealUnitedScalarController(...)
            
            # Read current value
            current_value = controller.hook_value.value
            print(f"Current: {current_value}")  # e.g., "100.000 km"
            
            # Connect to another observable
            other_observable.single_value_hook.connect_to(controller.hook_value)
            
            # Set new value programmatically
            controller.hook_value.value = RealUnitedScalar(50, Unit("m"))
            ```
        """
        return self.get_hook("value")
    
    @property
    def hook_unit_options(self) -> HookLike[dict[Dimension, set[Unit]]]:
        """
        Get a hook for two-way binding to the available unit options.
        
        This hook provides access to the dictionary that defines which units
        are available in the dropdown for each physical dimension. External
        code can read the current options or modify them programmatically.
        
        Returns:
            A hook that provides access to the unit options dictionary
            
        Example Usage:
            ```python
            controller = RealUnitedScalarController(...)
            
            # Read current unit options
            options = controller.hook_unit_options.value
            print(f"Length units: {options[Dimension.LENGTH]}")
            
            # Add new units programmatically
            new_options = options.copy()
            new_options[Dimension.LENGTH].add(Unit("ft"))
            controller.hook_unit_options.value = new_options
            ```
        """
        return self.get_hook("unit_options")

    @property
    def widget_real_united_scalar_label(self) -> GuardedLabel:
        """
        Get the main display label showing the complete formatted quantity.
        
        This read-only label displays the full physical quantity in a user-friendly
        format, such as "100.000 km" or "1.500 V". The formatting can be customized
        via the formatter parameter in the constructor.
        
        Returns:
            GuardedLabel widget displaying the complete quantity
            
        Use this when you need to place the main value display in a custom layout.
        """
        return self._real_united_scalar_label

    @property
    def widget_display_unit_combobox(self) -> GuardedComboBox:
        """
        Get the dropdown menu for selecting units of the same dimension.
        
        This combo box contains all available units that are compatible with
        the current value's physical dimension. Selecting a different unit
        automatically converts the displayed value while preserving the
        actual physical quantity.
        
        Returns:
            GuardedComboBox widget for unit selection
            
        Use this when you want to embed the unit selector in a custom layout
        or need to programmatically control its appearance.
        """
        return self._unit_combobox
    
    @property
    def widget_unit_editable_combobox(self) -> GuardedEditableComboBox:
        """
        Get the editable combo box for selecting units.
        """
        return self._unit_editable_combobox
    
    @property
    def widget_value_label(self) -> GuardedLabel:
        """
        Get the numeric-only display label showing just the value portion.
        
        This read-only label displays only the numeric part of the quantity,
        such as "100.000" or "1.500". It's useful when you want to show
        the number separately from the unit.
        
        Returns:
            GuardedLabel widget displaying only the numeric value
            
        Use this for compact displays or when units are shown elsewhere.
        """
        return self._value_label
    
    @property
    def widget_real_united_scalar_line_edit(self) -> GuardedLineEdit:
        """
        Get the text field for editing complete physical quantities.
        
        This editable text field allows users to type complete quantities
        like "50 m/s" or "1.5 kV". It supports the full syntax of the
        united_system library for units.
        
        Returns:
            GuardedLineEdit widget for editing complete quantities
            
        This is the most flexible input method as it allows users to
        enter both new values and new units in a single field.
        """
        return self._real_united_scalar_line_edit
    
    @property
    def widget_value_line_edit(self) -> GuardedLineEdit:
        """
        Get the text field for editing only the numeric value.
        
        This editable text field allows users to type just numbers
        while keeping the current unit unchanged. It accepts decimal
        numbers, scientific notation, and negative values.
        
        Returns:
            GuardedLineEdit widget for editing numeric values only
            
        Use this when you want users to adjust values quickly without
        changing units, or when the unit should remain fixed.
        """
        return self._value_line_edit
    
    @property
    def widget_unit_line_edit(self) -> GuardedLineEdit:
        """
        Get the text field for typing new units or changing units.
        
        This editable text field allows users to type unit symbols
        or names to change the current unit or add new units to the
        available options. Unlike the dropdown, this preserves the
        numeric value when changing units.
        
        Returns:
            GuardedLineEdit widget for editing units
            
        Use this for power users who want to type units directly
        or when you need to support units not in the dropdown.
        """
        return self._unit_line_edit
    
    ###########################################################################
    # Debugging
    ###########################################################################

    def all_widgets_as_frame(self) -> QFrame:
        """
        Create a comprehensive demo frame containing all available widgets.
        
        This method creates a complete demonstration layout that showcases
        every widget and feature of the controller. It's primarily intended
        for testing, debugging, and educational purposes.
        
        **What's included:**
        - Real United Scalar Label: Shows the formatted complete quantity
        - Value Label: Shows only the numeric portion  
        - Unit Selector: Dropdown for choosing compatible units
        - Real United Scalar Edit: Text field for complete quantity input
        - Value Edit: Text field for numeric-only input
        - Unit Edit: Text field for typing new units
        - Observable Status: Live display of internal state
        
        **Layout:**
        All widgets are organized in labeled groups within a vertical layout,
        making it easy to understand what each widget does and test all
        the different interaction methods.
        
        Returns:
            QFrame containing all widgets in an organized demo layout
            
        Example Usage:
            ```python
            controller = RealUnitedScalarController(...)
            demo_frame = controller.all_widgets_as_frame()
            
            # Add to your application window
            main_layout.addWidget(demo_frame)
            ```
            
        **Use Cases:**
        - Quick testing of controller functionality
        - Educational demonstrations of the widget system
        - Debugging and development
        - Feature exploration for new users
        
        Note: This creates a fully functional interface - all widgets
        are live and connected to the controller's data model.
        """
        frame = QFrame()
        layout = QVBoxLayout()
        frame.setLayout(layout)

        # Real United Scalar Label
        real_united_scalar_group = QGroupBox("Real United Scalar label")
        real_united_scalar_layout = QVBoxLayout()
        real_united_scalar_layout.addWidget(self._real_united_scalar_label)
        real_united_scalar_group.setLayout(real_united_scalar_layout)
        layout.addWidget(real_united_scalar_group)

        # Value Label
        value_label_group = QGroupBox("Value label")
        value_label_layout = QVBoxLayout()
        value_label_layout.addWidget(self._value_label)
        value_label_group.setLayout(value_label_layout)
        layout.addWidget(value_label_group)

        # Unit Selection from options
        unit_group = QGroupBox("Unit selector")
        unit_layout = QVBoxLayout()
        unit_layout.addWidget(self._unit_combobox)
        unit_group.setLayout(unit_layout)
        layout.addWidget(unit_group)

        # Unit Selection from editable combo box
        unit_editable_group = QGroupBox("Unit selector (editable)")
        unit_editable_layout = QVBoxLayout()
        unit_editable_layout.addWidget(self._unit_editable_combobox)
        unit_editable_group.setLayout(unit_editable_layout)
        layout.addWidget(unit_editable_group)

        # Real United Scalar Input
        real_united_scalar_input_group = QGroupBox("Real United Scalar edit")
        real_united_scalar_input_layout = QVBoxLayout()
        real_united_scalar_input_layout.addWidget(self._real_united_scalar_line_edit)
        real_united_scalar_input_group.setLayout(real_united_scalar_input_layout)
        layout.addWidget(real_united_scalar_input_group)

        # Value Input
        value_group = QGroupBox("Value edit")
        value_layout = QVBoxLayout()
        value_layout.addWidget(self._value_line_edit)
        value_group.setLayout(value_layout)
        layout.addWidget(value_group)

        # Unit Input
        unit_options_group = QGroupBox("Unit edit")
        unit_options_layout = QVBoxLayout()
        unit_options_layout.addWidget(self._unit_line_edit)
        unit_options_group.setLayout(unit_options_layout)
        layout.addWidget(unit_options_group)

        # Observables

        value_observable: ObservableSingleValueLike[RealUnitedScalar] = ObservableSingleValue[RealUnitedScalar](self.hook_value)
        unit_options_observable: ObservableDictLike[Dimension, set[Unit]] = ObservableDict[Dimension, set[Unit]](self.hook_unit_options)

        display_value_controller: DisplayValueController[RealUnitedScalar] = DisplayValueController[RealUnitedScalar](value_observable)
        display_unit_options_controller: DisplayValueController[dict[Dimension, set[Unit]]] = DisplayValueController[dict[Dimension, set[Unit]]](unit_options_observable.hook_value)

        observables_group = QGroupBox("Observables")
        observables_layout = QVBoxLayout()
        observables_layout.addWidget(display_value_controller.widget_label)
        observables_layout.addWidget(display_unit_options_controller.widget_label)
        observables_group.setLayout(observables_layout)
        layout.addWidget(observables_group)

        return frame
