from __future__ import annotations

# Standard library imports
from typing import Callable, Optional, Any, Mapping, Literal, AbstractSet
from logging import Logger
import weakref

# BAB imports
from united_system import RealUnitedScalar, Unit, Dimension
from nexpy import XDictProtocol, Hook
from nexpy.x_objects.single_value_like.protocols import XSingleValueProtocol
from nexpy import UpdateFunctionValues
from nexpy.core import NexusManager
from nexpy import default as nexpy_default

# Local imports
from ..core.base_composite_controller import BaseCompositeController
from ...controlled_widgets.controlled_qlabel import ControlledQLabel
from ...controlled_widgets.controlled_combobox import ControlledComboBox
from ...controlled_widgets.controlled_line_edit import ControlledLineEdit
from ...controlled_widgets.controlled_editable_combobox import ControlledEditableComboBox
from ...auxiliaries.resources import log_msg, DEFAULT_FLOAT_FORMAT_VALUE

class RealUnitedScalarController(BaseCompositeController[Literal["scalar_value", "unit_options", "unit", "float_value"], Literal["dimension", "selectable_units"], RealUnitedScalar|Mapping[Dimension, AbstractSet[Unit]]|Unit|float, Dimension|AbstractSet[Unit]]):
    """
    A comprehensive widget controller for displaying and editing physical quantities with units.
    
    This controller provides a complete user interface for working with RealUnitedScalar values,
    which represent physical quantities like "100.5 km", "23.7 kg", or "120 V". Users can:
    
    - **View** the quantity in multiple formats (full display, numeric value only, unit only)
    - **Edit** the complete quantity as text (e.g., "50 m/s")
    - **Edit** just the numeric value while keeping the same unit
    - **Change** the unit from a dropdown of compatible units (with automatic value conversion)
    - **Type** new units to extend available options
    
    ## Architecture: Granular Hook-Based Design
    
    The controller uses a granular hook architecture with four primary hooks:
    
    **Primary Hooks** (user-modifiable):
    - `scalar_value` (RealUnitedScalar): The complete physical quantity
    - `unit_options` (Mapping[Dimension, AbstractSet[Unit]]): Available units for each dimension
    - `unit` (Unit): The current display unit
    - `float_value` (float): The numeric value in the current unit
    
    **Secondary Hooks** (derived automatically):
    - `dimension` (Dimension): Derived from the current unit
    - `selectable_units` (AbstractSet[Unit]): Units available for the current dimension
    
    This granular design enables:
    - Independent unit changes without recreating the entire RealUnitedScalar
    - Proper widget invalidation even when canonical values are unchanged
    - Fine-grained control over each aspect of the physical quantity
    - Automatic synchronization between related values
    
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
        value: RealUnitedScalar | Hook[RealUnitedScalar] | XSingleValueProtocol[RealUnitedScalar] = RealUnitedScalar.nan(Dimension.dimensionless_dimension()),
        display_unit_options: Optional[Mapping[Dimension, AbstractSet[Unit]]] | Hook[Mapping[Dimension, AbstractSet[Unit]]] | XDictProtocol[Dimension, AbstractSet[Unit]] = None,
        value_formatter: Callable[[RealUnitedScalar], str] = DEFAULT_FLOAT_FORMAT_VALUE,
        unit_formatter: Callable[[Unit], str] = lambda u: u.format_string(as_fraction=True),
        unit_options_sorter: Callable[[AbstractSet[Unit]], list[Unit]] = lambda u: sorted(u, key=lambda x: x.format_string(as_fraction=True)),
        *,
        allowed_dimensions: Optional[AbstractSet[Dimension]] = None,
        debounce_ms: int|Callable[[], int],
        nexus_manager: NexusManager = nexpy_default.NEXUS_MANAGER,
        logger: Optional[Logger] = None,
    ) -> None:
        """
        Create a new RealUnitedScalarController for displaying and editing physical quantities.
        
        This constructor sets up all widgets, establishes the granular hook system (scalar_value,
        unit_options, unit, float_value), and connects them to the underlying data model. The
        controller can work with static values or connect to observable data sources for real-time
        updates.
        
        Args:
            value_or_hook_or_observable: The initial physical quantity to display. Can be:
                - A RealUnitedScalar object (e.g., `RealUnitedScalar(100, Unit("km"))`)
                - An XSingleValueProtocol[RealUnitedScalar] that provides RealUnitedScalar values
                - A Hook that provides RealUnitedScalar values
                - Default: NaN with dimensionless dimension
                
            display_unit_options: Available units for the dropdown selector. Can be:
                - A dictionary mapping dimensions to sets of units
                  Example: `{length_dim: {Unit("m"), Unit("km"), Unit("cm")}}`
                - An XDictProtocol[Dimension, AbstractSet[Unit]] for dynamic unit options
                - A Hook providing the dictionary
                - None to use only the initial value's unit
                
            value_formatter: Function to format the RealUnitedScalar for display labels.
                Default shows values like "100.000 km" with 3 decimal places.
                Signature: `(RealUnitedScalar) -> str`
                
            unit_formatter: Function to format units for display.
                Default uses `Unit.format_string(as_fraction=True)`.
                Signature: `(Unit) -> str`
                
            unit_options_sorter: Function to sort units in the dropdown.
                Default sorts alphabetically by formatted unit symbol.
                Signature: `(AbstractSet[Unit]) -> list[Unit]`
                
            allowed_dimensions: Optional restriction on which physical dimensions
                are permitted. If provided, only units from these dimensions can be used.
                Example: `{length_dim, time_dim}` to allow only length and time.
                None (default) allows all dimensions.
                
            logger: Optional logger instance for debugging and diagnostics.
                
        Example Usage:
            ```python
            from united_system import RealUnitedScalar, Unit
            from nexpy import XValue
            
            # Simple static value
            controller = RealUnitedScalarController(
                value_or_hook_or_observable=RealUnitedScalar(100, Unit("km"))
            )
            
            # With custom unit options
            length_dim = Unit("m").dimension
            time_dim = Unit("s").dimension
            unit_options = {
                length_dim: {Unit("m"), Unit("km"), Unit("cm"), Unit("mm")},
                time_dim: {Unit("s"), Unit("min"), Unit("h")}
            }
            controller = RealUnitedScalarController(
                value=RealUnitedScalar(5, Unit("km")),
                display_unit_options=unit_options
            )
            
            # Connected to observable data for automatic synchronization
            x_value = XValue(RealUnitedScalar(50, Unit("m")))
            controller = RealUnitedScalarController(
                value=x_value
            )
            
            # Access individual hooks
            controller.unit = Unit("km")  # Change just the unit
            controller.float_value = 42.5  # Change just the numeric value
            print(controller.dimension)  # Access derived dimension hook
            ```
        """
        
        self._value_formatter = value_formatter
        self._unit_formatter = unit_formatter
        self._unit_options_sorter = unit_options_sorter

        ###########################################################################
        # Determine the initial values and external hooks
        ###########################################################################

        # --------------------- scalar_value ---------------------

        if isinstance(value, RealUnitedScalar):
            scalar_value_provided_value: RealUnitedScalar = value
            scalar_value_provided_hook: Optional[Hook[RealUnitedScalar]] = None

        elif isinstance(value, Hook):
            # It's a hook
            scalar_value_provided_value = value.value # type: ignore
            scalar_value_provided_hook = value # type: ignore

        elif isinstance(value, XSingleValueProtocol): # type: ignore
            # It's an XValue
            scalar_value_provided_value = value.value # type: ignore
            scalar_value_provided_hook= value.value_hook # type: ignore

        else:
            # It's an invalid type
            raise ValueError(f"Invalid scalar value: {value}")

        # Initialize allowed dimensions
        if allowed_dimensions is not None:
            self._allowed_dimensions: AbstractSet[Dimension] = allowed_dimensions
        else :
            self._allowed_dimensions = {scalar_value_provided_value.dimension}

        # --------------------- unit_options ---------------------

        if display_unit_options is None:
            unit_options_provided_value: Mapping[Dimension, AbstractSet[Unit]] = {scalar_value_provided_value.dimension: {scalar_value_provided_value.unit}}
            unit_options_provided_hook: Optional[Hook[Mapping[Dimension, AbstractSet[Unit]]]] = None

        elif isinstance(display_unit_options, dict):
            # It's a dict
            unit_options_provided_value = display_unit_options
            unit_options_provided_hook = None

        elif isinstance(display_unit_options, Hook):
            # It's a hook
            unit_options_provided_value = display_unit_options.value # type: ignore
            unit_options_provided_hook = display_unit_options # type: ignore

        elif isinstance(display_unit_options, XDictProtocol): # type: ignore
            # It's an XDict - the value will be a dict
            unit_options_provided_value = display_unit_options.dict
            unit_options_provided_hook = display_unit_options.dict_hook

        else:
            # It's an invalid type
            raise ValueError(f"Invalid unit options: {display_unit_options}")

        ###########################################################################
        # Initialize the base controller
        ###########################################################################

        #---------------------------------------------------- initial_hook_values ----------------------------------------------------

        #Step 1: Set the initial component values
        initial_hook_values: Mapping[Literal["scalar_value", "unit_options", "unit", "float_value"], RealUnitedScalar | Mapping[Dimension, AbstractSet[Unit]] | Unit | float] = { # type: ignore
            "scalar_value": scalar_value_provided_value,
            "unit_options": unit_options_provided_value,
            "unit": scalar_value_provided_value.unit,
            "float_value": scalar_value_provided_value.value()
        }

        #---------------------------------------------------- validate_complete_primary_values_callback ----------------------------------------------------

        def verification_method(x: Mapping[Literal["scalar_value", "unit_options", "unit", "float_value"], RealUnitedScalar | Mapping[Dimension, AbstractSet[Unit]] | Unit | float], _self: Optional[RealUnitedScalarController]) -> tuple[bool, str]:

            scalar_value: RealUnitedScalar = x["scalar_value"] # type: ignore
            unit_options: Mapping[Dimension, AbstractSet[Unit]] = x["unit_options"] # type: ignore
            unit: Unit = x["unit"] # type: ignore
            float_value: float = x["float_value"] # type: ignore

            if not scalar_value.dimension in unit_options:
                return False, f"Dimension {scalar_value.dimension} not in unit options {unit_options}"

            available_unit_options: AbstractSet[Unit] = unit_options[scalar_value.dimension]

            # Check that the dimension is in the allowed dimensions
            if _self is not None and scalar_value.dimension not in _self._allowed_dimensions:
                return False, f"Dimension {scalar_value.dimension} not in allowed dimensions {_self._allowed_dimensions}"

            # Check that the unit is in the available unit options
            if not unit in available_unit_options:
                return False, f"Unit {unit} not in available unit options {available_unit_options}"

            # Check that the scalar value is the same as the float value
            if scalar_value.value() != float_value:
                return False, f"Scalar value {scalar_value} does not match float value {float_value}"

            # Check that the scalar unit is the same as the unit
            if scalar_value.unit != unit:
                return False, f"Scalar unit {scalar_value.unit} does not match unit {unit}"

            # Checks passed
            return True, "Verification method passed"

        # Step 3: Set the secondary hook callbacks
        def dimension_callback(x: Mapping[Literal["scalar_value", "unit_options", "unit", "float_value"], RealUnitedScalar | Mapping[Dimension, AbstractSet[Unit]] | Unit | float]) -> Dimension:
            unit: Unit = x["unit"] # type: ignore
            return unit.dimension
        def selectable_units_callback(x: Mapping[Literal["scalar_value", "unit_options", "unit", "float_value"], RealUnitedScalar | Mapping[Dimension, AbstractSet[Unit]] | Unit | float]) -> AbstractSet[Unit]:
            unit: Unit = x["unit"] # type: ignore
            unit_options: Mapping[Dimension, AbstractSet[Unit]] = x["unit_options"] # type: ignore
            if unit.dimension not in unit_options:
                raise ValueError(f"Dimension ' {unit.dimension} ' not in unit options ' {unit_options} '")

            return unit_options[unit.dimension]


        #---------------------------------------------------- compute_missing_primary_values_callback ----------------------------------------------------
        
        def compute_missing_primary_values_callback(
            _: Any,
            values: UpdateFunctionValues[Literal["scalar_value", "unit_options", "unit", "float_value"], RealUnitedScalar | Mapping[Dimension, AbstractSet[Unit]] | Unit | float]
            ) -> Mapping[Literal["scalar_value", "unit_options", "unit", "float_value"], RealUnitedScalar | Mapping[Dimension, AbstractSet[Unit]] | Unit | float]:
            """
            Provides missing values to be updated in the controller.

            Must also check if the provided values are valid by itself, and if not, return False!

            Args:
                self_ref: The weak reference to the controller
                values: The UpdateFunctionValues object containing current and submitted values

            Returns:
                A dictionary of the values to be updated

            Raises:
                ValueError: If the combination of changed values is invalid

            """
            current_values = values.current
            changed_values = values.submitted

            added_values: Mapping[Literal["scalar_value", "unit_options", "unit", "float_value"], RealUnitedScalar | Mapping[Dimension, AbstractSet[Unit]] | Unit | float] = {}
            match "scalar_value" in changed_values, "unit_options" in changed_values, "unit" in changed_values, "float_value" in changed_values:
                case True, True, True, True:
                    pass

                case True, True, True, False:
                    scalar_value: RealUnitedScalar = changed_values["scalar_value"] # type: ignore
                    added_values["float_value"] = scalar_value.value()

                case True, True, False, True:
                    scalar_value = changed_values["scalar_value"] # type: ignore
                    added_values["unit"] = scalar_value.unit

                case True, True, False, False:
                    scalar_value: RealUnitedScalar = changed_values["scalar_value"] # type: ignore
                    added_values["unit"] = scalar_value.unit
                    added_values["float_value"] = scalar_value.value()

                case True, False, True, True:
                    unit: Unit = changed_values["unit"] # type: ignore
                    new_unit_options: dict[Dimension, set[Unit]] = current_values["unit_options"].copy() # type: ignore
                    if unit.dimension not in new_unit_options:
                        new_unit_options[unit.dimension] = {unit}
                    else:
                        new_unit_options[unit.dimension] = new_unit_options[unit.dimension] | {unit}
                    added_values["unit_options"] = new_unit_options # type: ignore

                case True, False, True, False:
                    scalar_value = changed_values["scalar_value"] # type: ignore
                    unit: Unit = changed_values["unit"] # type: ignore
                    new_unit_options: dict[Dimension, set[Unit]] = current_values["unit_options"].copy() # type: ignore
                    if unit.dimension not in new_unit_options:
                        new_unit_options[unit.dimension] = {unit}
                    else:
                        new_unit_options[unit.dimension] = new_unit_options[unit.dimension] | {unit}
                    added_values["unit_options"] = new_unit_options # type: ignore
                    added_values["float_value"] = scalar_value.value()

                case True, False, False, True:
                    scalar_value = changed_values["scalar_value"] # type: ignore
                    unit = scalar_value.unit
                    new_unit_options: dict[Dimension, set[Unit]] = current_values["unit_options"].copy() # type: ignore
                    if unit.dimension not in new_unit_options:
                        new_unit_options[unit.dimension] = {unit}
                    else:
                        new_unit_options[unit.dimension] = new_unit_options[unit.dimension] | {unit}
                    added_values["unit_options"] = new_unit_options # type: ignore
                    added_values["unit"] = unit

                case True, False, False, False:
                    scalar_value = changed_values["scalar_value"] # type: ignore
                    unit = scalar_value.unit
                    new_unit_options: dict[Dimension, set[Unit]] = current_values["unit_options"].copy() # type: ignore
                    if unit.dimension not in new_unit_options:
                        new_unit_options[unit.dimension] = {unit}
                    else:
                        new_unit_options[unit.dimension] = new_unit_options[unit.dimension] | {unit}
                    added_values["unit_options"] = new_unit_options # type: ignore
                    added_values["unit"] = unit
                    added_values["float_value"] = scalar_value.value()

                case False, True, True, True:
                    unit: Unit = changed_values["unit"] # type: ignore
                    float_value: float = changed_values["float_value"] # type: ignore
                    scalar_value = RealUnitedScalar(float_value, unit)
                    added_values["scalar_value"] = scalar_value

                case False, True, True, False:
                    scalar_value = current_values["scalar_value"] # type: ignore
                    added_values["float_value"] = scalar_value.value()

                case False, True, False, True:
                    unit: Unit = changed_values["unit"] # type: ignore
                    float_value: float = changed_values["float_value"] # type: ignore
                    scalar_value = RealUnitedScalar(float_value, unit)
                    added_values["scalar_value"] = scalar_value

                case False, True, False, False:
                    pass

                case False, False, True, True:
                    unit: Unit = changed_values["unit"] # type: ignore
                    float_value: float = changed_values["float_value"] # type: ignore
                    new_unit_options: dict[Dimension, set[Unit]] = current_values["unit_options"].copy() # type: ignore
                    if unit.dimension not in new_unit_options:
                        new_unit_options[unit.dimension] = {unit}
                    else:
                        new_unit_options[unit.dimension] = new_unit_options[unit.dimension] | {unit}
                    scalar_value = RealUnitedScalar(float_value, unit)
                    added_values["unit_options"] = new_unit_options # type: ignore
                    added_values["scalar_value"] = scalar_value

                case False, False, True, False:
                    unit: Unit = changed_values["unit"] # type: ignore
                    float_value: float = current_values["float_value"] # type: ignore
                    new_unit_options: dict[Dimension, set[Unit]] = current_values["unit_options"].copy() # type: ignore
                    if unit.dimension not in new_unit_options:
                        new_unit_options[unit.dimension] = {unit}
                    else:
                        new_unit_options[unit.dimension] = new_unit_options[unit.dimension] | {unit}
                    scalar_value = RealUnitedScalar(float_value, unit)
                    added_values["unit_options"] = new_unit_options # type: ignore
                    added_values["scalar_value"] = scalar_value
                    added_values["float_value"] = float_value

                case False, False, False, True:
                    # Only the float value changed -> new scalar value is needed
                    unit: Unit = current_values["unit"] # type: ignore
                    float_value = changed_values["float_value"] # type: ignore
                    scalar_value = RealUnitedScalar(float_value, unit)
                    added_values["scalar_value"] = scalar_value

                case False, False, False, False:
                    raise ValueError(f"Invalid combination of changed values: {changed_values}")

                case _: # type: ignore
                    raise ValueError(f"Invalid combination of changed values: {changed_values}")

            return added_values

        #---------------------------------------------------- initialize BaseCompositeController ----------------------------------------------------
        
        self_weak_ref = weakref.ref(self)
        BaseCompositeController.__init__( # type: ignore
            initial_hook_values=initial_hook_values,
            validate_complete_primary_values_callback= lambda x, self_weak_ref=self_weak_ref: verification_method(x, self_weak_ref()), # type: ignore
            compute_secondary_values_callback={
                "dimension": dimension_callback,
                "selectable_units": selectable_units_callback,
            },
            compute_missing_primary_values_callback=compute_missing_primary_values_callback,
            debounce_ms=debounce_ms,
            logger=logger 
        )

        ###########################################################################
        # Join external hooks
        ###########################################################################

        if scalar_value_provided_hook is not None:
            self.join_by_key(scalar_value_provided_hook, "scalar_value", initial_sync_mode="use_target_value") # type: ignore
        if unit_options_provided_hook is not None:
            self.join_by_key(unit_options_provided_hook, "unit_options", initial_sync_mode="use_target_value") # type: ignore

        ###########################################################################
        # Initialization completed successfully
        ###########################################################################

    ###########################################################################
    # Widget methods
    ###########################################################################

    def _initialize_widgets_impl(self) -> None:
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
        self._real_united_scalar_label = ControlledQLabel(self)
        self._value_label = ControlledQLabel(self)
        self._unit_combobox = ControlledComboBox(self)
        self._unit_editable_combobox = ControlledEditableComboBox(self)

        # Edit real united scalar and edit value and edit unit widgets
        self._real_united_scalar_line_edit = ControlledLineEdit(self)
        self._value_line_edit = ControlledLineEdit(self)
        self._unit_line_edit = ControlledLineEdit(self)

        # Connect UI -> model
        self._unit_combobox.currentIndexChanged.connect(lambda _i: self._on_unit_combo_changed()) # type: ignore
        self._unit_editable_combobox.editingFinished.connect(lambda text: self._on_unit_editable_combobox_text_edited(text)) # type: ignore
        self._unit_editable_combobox.currentIndexChanged.connect(lambda _i: self._on_unit_editable_combobox_index_changed()) # type: ignore
        self._real_united_scalar_line_edit.editingFinished.connect(self._on_real_united_scalar_edited)
        self._value_line_edit.editingFinished.connect(self._on_value_edited)
        self._unit_line_edit.editingFinished.connect(self._on_unit_edited)

    def _on_unit_combo_changed(self) -> None:
        """
        Handle when the user selects a different unit from the dropdown menu.
        
        This method is called automatically when the user clicks on the unit dropdown
        and selects a different unit. It submits only the new unit value, which triggers
        automatic recalculation of the float_value and scalar_value through the hook system.
        
        **What happens:**
        1. The new unit is extracted from the dropdown's currentData
        2. The unit is submitted via `submit_value_debounced("unit", new_unit)`
        3. The hook system's `add_values_to_be_updated_callback` automatically:
           - Recalculates the float_value for the new unit (unit conversion)
           - Reconstructs the scalar_value with the new unit
           - Triggers widget invalidation
        
        **Example:**
        - Current: unit="km", float_value=1.5, scalar_value="1.5 km"
        - User selects "m" from dropdown
        - System automatically updates: unit="m", float_value=1500, scalar_value="1500 m"
        
        **Validation:**
        - Only units from the same physical dimension can be selected
        - If an invalid unit is selected, widgets are invalidated to revert to last valid state
        
        **Technical Details:**
        Unlike traditional approaches that would recreate the entire RealUnitedScalar,
        this granular approach only updates the unit hook, allowing the system to detect
        the change and properly invalidate widgets even when the canonical value is unchanged.
        """

        if self.is_blocking_signals:
            return
               
        ################# Processing user input #################

        # Get the new unit from the combo box

        new_unit: Optional[Unit] = self._unit_combobox.currentData()
        if new_unit is None or not isinstance(new_unit, Unit): # type: ignore
            self.invalidate_widgets()
            return
        
        self.submit_value("unit", new_unit)

        ################################################################

    def _on_real_united_scalar_edited(self) -> None:
        """
        Handle when the user edits the complete quantity in the main text field.
        
        This method is called when the user types a complete physical quantity
        (value + unit) in the "Real United Scalar edit" field and presses Enter
        or clicks outside the field.
        
        **What the user can type:**
        - Complete quantities: "50 m", "1.5 km/h", "120 V", "25.7 kg"
        - Complex units: "9.8 m/s^2", "3.14 rad/s"
        - Scientific notation: "1.5e-3 m", "2.1E+6 Hz"
        
        **What happens:**
        1. The text is parsed into a RealUnitedScalar using `RealUnitedScalar(text)`
        2. The complete scalar_value is submitted via `submit_value_debounced("scalar_value", ...)`
        3. The hook system's `add_values_to_be_updated_callback` automatically:
           - Extracts and updates the unit
           - Extracts and updates the float_value  
           - Adds the unit to unit_options if it's new
           - Triggers widget invalidation
        
        **Examples:**
        - Type "50 m" → scalar_value="50 m", unit=Unit("m"), float_value=50
        - Type "2.5 km" → scalar_value="2.5 km", unit=Unit("km"), float_value=2.5
        - Type "100 mph" → Adds mph to available units (if dimension is allowed)
        
        **Error Handling:**
        - Invalid formats (like "abc def") trigger widget invalidation to revert
        - Parse errors are caught and logged
        - Empty input triggers invalidation
        
        **Power User Features:**
        - Supports full `united_system` parsing syntax
        - Handles complex units: "kg*m/s^2" for force
        - Automatically normalizes unit representations
        - Units are automatically added to unit_options if compatible
        """

        if self.is_blocking_signals:
            return
        
        ################# Processing user input #################

        # Get the new unit from the combo box

        text_input: str = self._real_united_scalar_line_edit.text()
        if not text_input:
            self.invalidate_widgets()
            return

        try:
            new_scalar_value: RealUnitedScalar = RealUnitedScalar(text_input)
        except Exception:
            self.invalidate_widgets()
            return
        self.submit_value("scalar_value", new_scalar_value)

        ################################################################

    def _on_value_edited(self) -> None:
        """
        Handle when the user edits only the numeric value while keeping the same unit.
        
        This method is called when the user types a new number in the "Value edit" 
        field and presses Enter or clicks outside the field. Only the float_value is updated.
        
        **What the user can type:**
        - Decimal numbers: "123.45", "0.001", "1000"
        - Scientific notation: "1.5e-3", "2.1E+6"
        - Negative values: "-273.15" (for temperatures, etc.)
        
        **What happens:**
        1. The text is parsed to a float using `float(text)`
        2. The float_value is submitted via `submit_value_debounced("float_value", ...)`
        3. The hook system's `add_values_to_be_updated_callback` automatically:
           - Reconstructs the scalar_value using the new float_value and current unit
           - Keeps the unit unchanged
           - Triggers widget invalidation
        
        **Examples:**
        - Current: unit="km", float_value=100
        - User types "50" → float_value=50, scalar_value="50 km", unit stays "km"
        - User types "3.3" → float_value=3.3, scalar_value="3.3 km"
        
        **Use Cases:**
        - Adjusting measurements while keeping the same scale
        - Quick value updates without changing units
        - Data entry when the unit is predetermined
        
        **Error Handling:**
        - Non-numeric input (like "abc") triggers widget invalidation to revert
        - Parse errors are caught and logged
        - Empty input triggers invalidation
        
        **Precision:**
        The entered value is stored with full floating-point precision,
        though the display format may round for readability.
        """

        if self.is_blocking_signals:
            return
        
        ################# Processing user input #################

        # Get the new value from the line edit
        text: str = self._value_line_edit.text().strip()

        if not text:
            self.invalidate_widgets()
            return
        
        try:
            new_float_value: float = float(text)
        except Exception:
            self.invalidate_widgets()
            return

        self.submit_value("float_value", new_float_value)

        ################################################################

    def _on_unit_edited(self) -> None:
        """
        Handle when the user types a new unit in the unit text field.
        
        This method is called when the user types a unit symbol or name in the 
        "Unit edit" field and presses Enter or clicks outside the field. This provides
        a way to change units by typing, which keeps the numeric value constant (no conversion).
        
        **What the user can type:**
        - Basic units: "m", "kg", "s", "V", "A"
        - Prefixed units: "km", "mg", "kV", "mA", "µm"
        - Complex units: "m/s", "kg/m^3", "W/m^2", "rad/s"
        
        **What happens:**
        1. The text is parsed into a Unit using `Unit(text)`
        2. The unit is submitted via `submit_value_debounced("unit", new_unit)`
        3. The hook system's `add_values_to_be_updated_callback` automatically:
           - Adds the unit to unit_options if it's new
           - Updates the scalar_value with the new unit (keeping float_value constant)
           - Triggers widget invalidation
        
        **Examples:**
        - Current: unit="m", float_value=100
        - User types "cm" → unit="cm", float_value=100, scalar_value="100 cm"
        - Note: This does NOT convert 100m to 10000cm! It changes to 100cm.
        
        **Important Behavior:**
        Unlike the dropdown selector (which converts values), typing a unit keeps
        the numeric value constant. This is useful for:
        - Correcting the unit after entering a value
        - Switching units without conversion
        - Adding new units to the dropdown
        
        **Error Handling:**
        - Unrecognized unit symbols trigger widget invalidation
        - Parse errors are caught and logged
        - Empty input triggers invalidation
        
        **Power User Features:**
        - Supports full `united_system` unit parsing syntax
        - Can handle complex derived units: "kg*m/s^2"
        - New units are automatically added to unit_options
        - Automatically normalizes unit representations
        """

        if self.is_blocking_signals:
            return
        
        ################# Processing user input #################

        text: str = self._unit_line_edit.text().strip()
        if not text:
            self.invalidate_widgets()
            return
        
        try:
            new_unit: Unit = Unit(text)
        except Exception:
            self.invalidate_widgets()
            return
        self.submit_value("unit", new_unit)

        ################################################################
    
    def _on_unit_editable_combobox_index_changed(self) -> None:
        """
        Handle when the user selects a new unit in the unit dropdown.
        """

        if self.is_blocking_signals:
            return
               
        ################# Processing user input #################

        # Get the new unit from the combo box

        new_unit: Optional[Unit] = self._unit_editable_combobox.currentData()
        if new_unit is None or not isinstance(new_unit, Unit): # type: ignore
            self.invalidate_widgets()
            return

        self.submit_value("unit", new_unit)

    def _on_unit_editable_combobox_text_edited(self, text: str) -> None:
        """
        Handle when the user edits the unit in the editable combo box.
        """

        if self.is_blocking_signals:
            return

        ################# Processing user input #################

        try:
            new_unit: Unit = Unit(text)
        except Exception:
            self.invalidate_widgets()
            return

        if new_unit is None or not isinstance(new_unit, Unit): # type: ignore
            raise RuntimeError(f"Invalid unit: {new_unit}")

        self.submit_value("unit", new_unit)

        ################################################################

    def _invalidate_widgets_impl(self) -> None:
        """
        Synchronize all widget displays with the current internal state from the hook system.
        
        This method is called automatically whenever any hook value changes (scalar_value,
        unit_options, unit, or float_value). It retrieves the current values from each hook
        and updates all widgets to reflect the current state.
        
        **What gets retrieved:**
        - `scalar_value` - The complete RealUnitedScalar for display labels
        - `unit_options` - Dict of available units by dimension
        - `unit` - The current display unit for the dropdowns
        - `float_value` - The numeric value for value-only displays
        
        **What gets updated:**
        - Real United Scalar Label: Shows formatted scalar_value
        - Value Label: Shows formatted float_value
        - Unit Line Edit: Shows formatted unit
        - Unit ComboBoxes: Populated with units for the current dimension, selection set to unit
        
        **When this is called:**
        - After successful user edits (after hook values are updated)
        - When connected observable values change externally
        - When validation fails and the display needs to revert
        - During initialization to show initial values
        - When unit changes (even if canonical value is unchanged)
        
        **Important:**
        This method is called with signals blocked (`is_blocking_signals=True`) to prevent
        widget change events from triggering additional hook updates, avoiding infinite loops.
        
        **Internal Use:**
        This is an internal method called by the base controller's invalidation system.
        Users don't call this directly.
        """

        scalar_value: RealUnitedScalar = self.value_by_key  ("scalar_value") # type: ignore
        unit_options: dict[Dimension, AbstractSet[Unit]] = self.value_by_key("unit_options") # type: ignore
        unit: Unit = self.value_by_key("unit") # type: ignore
        float_value: float = self.value_by_key("float_value") # type: ignore
        log_msg(self, "_invalidate_widgets", self._logger, f"value: {scalar_value}")
        log_msg(self, "_invalidate_widgets", self._logger, f"available_units: {unit_options}")

        # Real united scalar label and line edit
        formatted_value = self._value_formatter(scalar_value)
        self._real_united_scalar_label.setText(formatted_value)
        self._real_united_scalar_line_edit.setText(formatted_value)

        # Value label and line edit
        self._value_label.setText(f"{float_value:.3f}")
        self._value_line_edit.setText(f"{float_value:.3f}")

        # Unit line edit
        self._unit_line_edit.setText(self._unit_formatter(unit))

        # Unit combobox
        self._unit_combobox.clear()
        for _unit in sorted(unit_options[scalar_value.dimension], key=lambda u: self._unit_formatter(u)):
            self._unit_combobox.addItem(self._unit_formatter(_unit), userData=_unit) # type: ignore
        index = self._unit_combobox.findData(unit)
        self._unit_combobox.setCurrentIndex(index)

        # Unit editable combobox
        self._unit_editable_combobox.clear()
        for _unit in sorted(unit_options[scalar_value.dimension], key=lambda _u: self._unit_formatter(_u)):
            self._unit_editable_combobox.addItem(self._unit_formatter(_unit), userData=_unit) # type: ignore
        self._unit_editable_combobox.setCurrentIndex(self._unit_editable_combobox.findData(unit))

    ###########################################################################
    # Disposal
    ###########################################################################

    def dispose_before_children(self) -> None:
        try:
            self._unit_combobox.currentIndexChanged.disconnect()
        except Exception:
            pass

    ###########################################################################
    # Public API - values
    ###########################################################################

    # ---------------------------------------------------- value ----------------------------------------------------

    @property
    def value(self) -> RealUnitedScalar:
        """
        Get the current complete physical quantity (scalar_value).
        
        Returns the RealUnitedScalar that combines the numeric value, unit,
        and dimension into a single object.
        
        Example:
            ```python
            controller = RealUnitedScalarController(RealUnitedScalar(100, Unit("km")))
            print(controller.value)  # "100.000 km"
            print(controller.value.canonical_value)  # 100000.0 (in base SI units - meters)
            ```
        """
        return self.get_value_of_hook("scalar_value") # type: ignore
    
    @value.setter
    def value(self, value: RealUnitedScalar) -> None:
        """
        Set the current complete physical quantity (scalar_value).
        
        Updates the scalar_value, which automatically triggers updates to
        unit, float_value, and dimension hooks through the callback system.
        
        Example:
            ```python
            controller.value = RealUnitedScalar(50, Unit("m"))
            # Automatically updates: unit=Unit("m"), float_value=50
            ```
        """
        self.submit_value("scalar_value", value)

    def change_value(self, value: RealUnitedScalar) -> None:
        """
        Change the current complete physical quantity (scalar_value).
        
        Alias for the value setter. Updates the scalar_value and triggers
        automatic synchronization of related hooks.
        """
        self.submit_value("scalar_value", value)

    @property
    def value_hook(self) -> Hook[RealUnitedScalar]:
        """
        Get a hook for two-way binding to the complete physical quantity (scalar_value).
        
        This hook allows external observables to read and modify the scalar_value,
        with automatic bidirectional synchronization.
        
        Returns:
            Hook[RealUnitedScalar]: Hook providing access to scalar_value
            
        Example Usage:
            ```python
            from nexpy import XValue
            
            controller = RealUnitedScalarController(...)
            
            # Read current value via hook
            current_value = controller.value_hook.value
            print(f"Current: {current_value}")  # e.g., "100.000 km"
            
            # Connect to another observable for bidirectional sync
            external_observable = XValue(RealUnitedScalar(50, Unit("m")))
            external_observable.hook.connect_to(controller.value_hook)
            
            # Now changes in either direction are synchronized
            controller.value = RealUnitedScalar(75, Unit("km"))
            print(external_observable.value)  # Also "75.000 km"
            ```
        """
        return self.get_hook("scalar_value") # type: ignore

    # ---------------------------------------------------- unit_options ----------------------------------------------------

    @property
    def unit_options(self) -> dict[Dimension, frozenset[Unit]]:
        """Get the current unit options."""
        return self.get_value_of_hook("unit_options") # type: ignore

    @unit_options.setter
    def unit_options(self, unit_options: Mapping[Dimension, AbstractSet[Unit]]) -> None:
        """Set the current unit options."""
        self.submit_value("unit_options", unit_options)

    def change_unit_options(self, unit_options: Mapping[Dimension, AbstractSet[Unit]]) -> None:
        """Change the current unit options."""
        self.submit_value("unit_options", unit_options)

    @property
    def unit_options_hook(self) -> Hook[Mapping[Dimension, AbstractSet[Unit]]]:
        """Get the hook for the current unit options."""
        return self.get_hook("unit_options") # type: ignore

    #---------------------------------------------------------------------------
    # Unit
    #---------------------------------------------------------------------------

    @property
    def unit(self) -> Unit:
        """Get the current unit."""
        return self.get_value_of_hook("unit") # type: ignore

    @unit.setter
    def unit(self, unit: Unit) -> None:
        """Set the current unit."""
        self.submit_value("unit", unit)

    def change_unit(self, unit: Unit) -> None:
        """Change the current unit."""
        self.submit_value("unit", unit)

    @property
    def unit_hook(self) -> Hook[Unit]:
        """Get the hook for the current unit."""
        return self.get_hook("unit") # type: ignore

    # ---------------------------------------------------- float_value ----------------------------------------------------

    @property
    def float_value(self) -> float:
        """Get the current float value."""
        return self.get_value_of_hook("float_value") # type: ignore

    @float_value.setter
    def float_value(self, float_value: float) -> None:
        """Set the current float value."""
        self.submit_value("float_value", float_value)

    def change_float_value(self, float_value: float) -> None:
        """Change the current float value."""
        self.submit_value("float_value", float_value)

    @property
    def float_value_hook(self) -> Hook[float]:
        """Get the hook for the current float value."""
        return self.get_hook("float_value") # type: ignore

    #---------------------------------------------------------------------------
    # Dimension
    #---------------------------------------------------------------------------

    @property
    def dimension(self) -> Dimension:
        """Get the current dimension."""
        return self.get_value_of_hook("dimension") # type: ignore

    @property
    def dimension_hook(self) -> Hook[Dimension]:
        """Get the hook for the current dimension."""
        return self.get_hook("dimension") # type: ignore

    # ---------------------------------------------------- selectable_units ----------------------------------------------------

    @property
    def selectable_units(self) -> frozenset[Unit]:
        """Get the current selectable units."""
        return self.get_value_of_hook("selectable_units") # type: ignore

    @property
    def selectable_units_hook(self) -> Hook[frozenset[Unit]]:
        """Get the hook for the current selectable units."""
        return self.get_hook("selectable_units") # type: ignore

    # ---------------------------------------------------- allowed_dimensions ----------------------------------------------------

    @property
    def allowed_dimensions(self) -> AbstractSet[Dimension]:
        """
        Get the set of allowed physical dimensions for this controller.
        
        This property returns the dimensions that are permitted for scalar values
        in this controller. Any attempt to set a scalar_value with a dimension
        not in this set will be rejected during validation.
        
        Returns:
            AbstractSet[Dimension]: Set of allowed dimensions
        
        Notes:
            - If `allowed_dimensions` was provided during initialization, returns that set
            - If not provided, defaults to a set containing only the initial value's dimension
            - This restriction is enforced in the verification method
            - Attempting to change to a unit from a disallowed dimension will fail validation
        
        Example:
            ```python
            from united_system import Unit
            
            length_dim = Unit("m").dimension
            time_dim = Unit("s").dimension
            
            controller = RealUnitedScalarController(
                value=RealUnitedScalar(100, Unit("km")),
                allowed_dimensions={length_dim}
            )
            
            print(controller.allowed_dimensions)  # {L} (length dimension)
            
            # This would work - both are length units
            controller.unit = Unit("cm")  
            
            # This would fail validation - time is not in allowed_dimensions
            controller.value = RealUnitedScalar(5, Unit("s"))  # ValidationError!
            ```
        """
        return self._allowed_dimensions

    ###########################################################################
    # Public API - widgets
    ###########################################################################

    @property
    def widget_real_united_scalar_label(self) -> ControlledQLabel:
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
    def widget_display_unit_combobox(self) -> ControlledComboBox:
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
    def widget_unit_editable_combobox(self) -> ControlledEditableComboBox:
        """
        Get the editable combo box for selecting units.
        """
        return self._unit_editable_combobox
    
    @property
    def widget_value_label(self) -> ControlledQLabel:
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
    def widget_real_united_scalar_line_edit(self) -> ControlledLineEdit:
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
    def widget_value_line_edit(self) -> ControlledLineEdit:
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
    def widget_unit_line_edit(self) -> ControlledLineEdit:
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