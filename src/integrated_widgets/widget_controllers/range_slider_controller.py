# Standard library imports
from __future__ import annotations
from typing import Generic, Optional, TypeVar, Any, Mapping, Literal
from PySide6.QtWidgets import QWidget
from enum import Enum
from logging import Logger
import math

# BAB imports
from ..util.base_complex_hook_controller import BaseComplexHookController
from observables import InitialSyncMode, HookLike, ObservableSingleValueLike, OwnedHookLike
from united_system import RealUnitedScalar, Unit

# Local imports
from ..guarded_widgets.guarded_range_slider import GuardedRangeSlider
from ..guarded_widgets.guarded_label import GuardedLabel
from ..guarded_widgets.guarded_line_edit import GuardedLineEdit
from ..guarded_widgets.blankable_widget import BlankableWidget

PrimaryHookKeyType = Literal[
    "full_range_lower_value",
    "full_range_upper_value",
    "number_of_ticks",
    "minimum_number_of_ticks",
    "selected_lower_range_tick_position",
    "selected_upper_range_tick_position",
    "unit"
]
SecondaryHookKeyType = Literal[
    "selected_range_lower_tick_value",
    "selected_range_upper_tick_value",
    "selected_range_lower_tick_relative_value",
    "selected_range_upper_tick_relative_value",
    "selected_range_size",
    "minimum_range_size",
    "center_of_range_value",
    "step_size",
    "range_value_type"
]

T = TypeVar("T", bound=float | RealUnitedScalar)

class RangeValueType(Enum):
    REAL_UNITED_SCALAR = "real_united_scalar"
    FLOAT = "float"

class RangeSliderController(BaseComplexHookController[PrimaryHookKeyType, SecondaryHookKeyType, Any, Any, "RangeSliderController"], Generic[T]):

    def __init__(
        self,
        full_range_lower_value: T | ObservableSingleValueLike[T] | HookLike[T],
        full_range_upper_value: T | ObservableSingleValueLike[T] | HookLike[T],
        number_of_ticks: int | ObservableSingleValueLike[int] | HookLike[int] = 100,
        minimum_number_of_ticks: int | ObservableSingleValueLike[int] | HookLike[int] = 1,
        selected_lower_range_tick_position: int | ObservableSingleValueLike[int] | HookLike[int] = 0,
        selected_upper_range_tick_position: int | ObservableSingleValueLike[int] | HookLike[int] = 100,
        unit: Optional[Unit] | ObservableSingleValueLike[Optional[Unit]] | HookLike[Optional[Unit]] = None,
        logger: Optional[Logger] = None,
        parent: Optional[QWidget] = None,
    ) -> None:

        # full_range_lower_value
        if isinstance(full_range_lower_value, ObservableSingleValueLike):
            initial_full_range_lower_value: T = full_range_lower_value.value # type: ignore
            full_range_lower_value_hook: Optional[HookLike[T]] = full_range_lower_value.value # type: ignore
        elif isinstance(full_range_lower_value, HookLike):
            initial_full_range_lower_value: T = full_range_lower_value.value # type: ignore
            full_range_lower_value_hook: Optional[HookLike[T]] = full_range_lower_value
        else:
            # full_range_lower_value is of type T
            initial_full_range_lower_value: T = full_range_lower_value
            full_range_lower_value_hook = None

        # full_range_upper_value
        if isinstance(full_range_upper_value, ObservableSingleValueLike):
            initial_full_range_upper_value: T = full_range_upper_value.value # type: ignore
            full_range_upper_value_hook: Optional[HookLike[T]] = full_range_upper_value.value # type: ignore
        elif isinstance(full_range_upper_value, HookLike):
            initial_full_range_upper_value: T = full_range_upper_value.value # type: ignore
            full_range_upper_value_hook: Optional[HookLike[T]] = full_range_upper_value
        else:
            # full_range_upper_value is of type T
            initial_full_range_upper_value: T = full_range_upper_value
            full_range_upper_value_hook = None

        # number_of_ticks
        if isinstance(number_of_ticks, int):
            initial_number_of_ticks: int = number_of_ticks
            number_of_ticks_hook: Optional[HookLike[int]] = None
        elif isinstance(number_of_ticks, ObservableSingleValueLike):
            initial_number_of_ticks  = number_of_ticks.value # type: ignore
            number_of_ticks_hook = number_of_ticks.value # type: ignore
        elif isinstance(number_of_ticks, HookLike):
            initial_number_of_ticks  = number_of_ticks.value # type: ignore
            number_of_ticks_hook = number_of_ticks
        else:
            raise ValueError(f"Invalid number_of_ticks: {number_of_ticks}")
        
        # minimum_number_of_ticks
        if isinstance(minimum_number_of_ticks, int):
            initial_minimum_number_of_ticks: int = minimum_number_of_ticks
            minimum_number_of_ticks_hook: Optional[HookLike[int]] = None
        elif isinstance(minimum_number_of_ticks, ObservableSingleValueLike):
            initial_minimum_number_of_ticks = minimum_number_of_ticks.value # type: ignore
            minimum_number_of_ticks_hook = minimum_number_of_ticks.value # type: ignore
        elif isinstance(minimum_number_of_ticks, HookLike):
            initial_minimum_number_of_ticks = minimum_number_of_ticks.value # type: ignore
            minimum_number_of_ticks_hook = minimum_number_of_ticks
        else:
            raise ValueError(f"Invalid minimum_number_of_ticks: {minimum_number_of_ticks}")
        
        # selected_lower_range_tick_position
        if isinstance(selected_lower_range_tick_position, int):
            initial_selected_lower_range_tick_position: int = selected_lower_range_tick_position
            selected_lower_range_tick_position_hook: Optional[HookLike[int]] = None
        elif isinstance(selected_lower_range_tick_position, ObservableSingleValueLike):
            initial_selected_lower_range_tick_position = selected_lower_range_tick_position.value # type: ignore
            selected_lower_range_tick_position_hook = selected_lower_range_tick_position.value # type: ignore
        elif isinstance(selected_lower_range_tick_position, HookLike):
            initial_selected_lower_range_tick_position = selected_lower_range_tick_position.value # type: ignore
            selected_lower_range_tick_position_hook = selected_lower_range_tick_position
        else:
            raise ValueError(f"Invalid selected_lower_range_tick_position: {selected_lower_range_tick_position}")
        
        # selected_upper_range_tick_position
        if isinstance(selected_upper_range_tick_position, int):
            initial_selected_upper_range_tick_position: int = selected_upper_range_tick_position
            selected_upper_range_tick_position_hook: Optional[HookLike[int]] = None
        elif isinstance(selected_upper_range_tick_position, ObservableSingleValueLike):
            initial_selected_upper_range_tick_position = selected_upper_range_tick_position.value # type: ignore
            selected_upper_range_tick_position_hook = selected_upper_range_tick_position.value # type: ignore
        elif isinstance(selected_upper_range_tick_position, HookLike):
            initial_selected_upper_range_tick_position = selected_upper_range_tick_position.value # type: ignore
            selected_upper_range_tick_position_hook = selected_upper_range_tick_position
        else:
            raise ValueError(f"Invalid selected_upper_range_tick_position: {selected_upper_range_tick_position}")
        
        # unit
        if unit is None:
            initial_unit: Optional[Unit] = None
            unit_hook: Optional[HookLike[Optional[Unit]]] = None
        elif isinstance(unit, Unit):
            initial_unit = unit
            unit_hook = None
        elif isinstance(unit, ObservableSingleValueLike):
            initial_unit = unit.value # type: ignore
            unit_hook = unit.value # type: ignore
        elif isinstance(unit, HookLike):
            initial_unit = unit.value # type: ignore
            unit_hook = unit
        else:
            raise ValueError(f"Invalid unit: {unit}")

        super().__init__(
            {
                "full_range_lower_value": initial_full_range_lower_value,
                "full_range_upper_value": initial_full_range_upper_value,
                "number_of_ticks": initial_number_of_ticks,
                "minimum_number_of_ticks": initial_minimum_number_of_ticks,
                "selected_lower_range_tick_position": initial_selected_lower_range_tick_position,
                "selected_upper_range_tick_position": initial_selected_upper_range_tick_position,
                "unit": initial_unit,
            },
            verification_method=self.__verification_method,
            secondary_hook_callbacks={
                "selected_range_lower_tick_value": self._compute_selected_range_lower_tick_value,
                "selected_range_upper_tick_value": self._compute_selected_range_upper_tick_value,
                "selected_range_lower_tick_relative_value": self._compute_selected_range_lower_tick_relative_value,
                "selected_range_upper_tick_relative_value": self._compute_selected_range_upper_tick_relative_value,
                "selected_range_size": self._compute_selected_range_size,
                "minimum_range_size": self._compute_minimum_range_size,
                "center_of_range_value": self._compute_center_of_range_value,
                "step_size": self._compute_step_size_value,
                "range_value_type": self._compute_range_value_type,
            },
            logger=logger,
            parent=parent
        )

        self.connect_hook(full_range_lower_value_hook, "full_range_lower_value", initial_sync_mode=InitialSyncMode.USE_TARGET_VALUE) if full_range_lower_value_hook is not None else None
        self.connect_hook(full_range_upper_value_hook, "full_range_upper_value", initial_sync_mode=InitialSyncMode.USE_TARGET_VALUE) if full_range_upper_value_hook is not None else None
        self.connect_hook(number_of_ticks_hook, "number_of_ticks", initial_sync_mode=InitialSyncMode.USE_TARGET_VALUE) if number_of_ticks_hook is not None else None
        self.connect_hook(minimum_number_of_ticks_hook, "minimum_number_of_ticks", initial_sync_mode=InitialSyncMode.USE_TARGET_VALUE) if minimum_number_of_ticks_hook is not None else None
        self.connect_hook(selected_lower_range_tick_position_hook, "selected_lower_range_tick_position", initial_sync_mode=InitialSyncMode.USE_TARGET_VALUE) if selected_lower_range_tick_position_hook is not None else None
        self.connect_hook(selected_upper_range_tick_position_hook, "selected_upper_range_tick_position", initial_sync_mode=InitialSyncMode.USE_TARGET_VALUE) if selected_upper_range_tick_position_hook is not None else None
        self.connect_hook(unit_hook, "unit", initial_sync_mode=InitialSyncMode.USE_TARGET_VALUE) if unit_hook is not None else None

    ###########################################################################
    # NaN Detection Helper Method
    ###########################################################################

    def _is_nan_or_inf(self, value: Any) -> bool:
        """Check if a value is NaN or infinite."""
        if isinstance(value, float):
            return math.isnan(value) or math.isinf(value)
        elif isinstance(value, RealUnitedScalar):
            return value.is_nan() or value.is_infinite()
        return False

    ###########################################################################
    # Verification Method
    ###########################################################################

    def __verification_method(self, component_values: Mapping[PrimaryHookKeyType, Any]) -> tuple[bool, str]:
        
        full_range_lower_value: T = component_values["full_range_lower_value"]
        full_range_upper_value: T = component_values["full_range_upper_value"]
        number_of_ticks: int = component_values["number_of_ticks"]
        minimum_number_of_ticks: int = component_values["minimum_number_of_ticks"]
        selected_lower_range_tick_position: int = component_values["selected_lower_range_tick_position"]
        selected_upper_range_tick_position: int = component_values["selected_upper_range_tick_position"]
        unit: Optional[Unit] = component_values["unit"]

        # Check the value type of the full range values
        value_type: RangeValueType = self._compute_range_value_type(component_values)
        match value_type:
            case RangeValueType.REAL_UNITED_SCALAR:
                if not isinstance(full_range_lower_value, RealUnitedScalar):
                    return False, f"full_range_lower_value must be a RealUnitedScalar"
                if not isinstance(full_range_upper_value, RealUnitedScalar):
                    return False, f"full_range_upper_value must be a RealUnitedScalar"
                if unit is None:
                    return False, f"unit must be provided for RealUnitedScalar values"
                if unit.dimension != full_range_lower_value.unit.dimension or unit.dimension != full_range_upper_value.unit.dimension:
                    return False, f"unit must have the same dimension as full_range_lower_value and full_range_upper_value"
                # Allow NaN values by checking for NaN before comparison
                if not (full_range_lower_value.is_nan() or full_range_upper_value.is_nan()):
                    if full_range_lower_value > full_range_upper_value:
                        return False, f"full_range_lower_value must be less or equal to full_range_upper_value"
            case RangeValueType.FLOAT:
                if not isinstance(full_range_lower_value, float):
                    return False, f"full_range_lower_value must be a float"
                if not isinstance(full_range_upper_value, float):
                    return False, f"full_range_upper_value must be a float"
                if unit is not None:
                    return False, f"unit must be None for float values"
                # Allow NaN values by checking for NaN before comparison
                if not (math.isnan(full_range_lower_value) or math.isnan(full_range_upper_value)):
                    if full_range_lower_value > full_range_upper_value:
                        return False, f"full_range_lower_value must be less or equal to full_range_upper_value"
            case _:
                return False, f"Invalid range value type: {value_type}"
            
        # Check the integer values
        if number_of_ticks <= 0:
            return False, f"number_of_ticks must be greater than 0"
        if minimum_number_of_ticks <= 0 or minimum_number_of_ticks > number_of_ticks:
            return False, f"minimum_number_of_ticks must be greater than 0 and less than or equal to number_of_ticks"
        if selected_lower_range_tick_position < 0 or selected_lower_range_tick_position > selected_upper_range_tick_position or selected_lower_range_tick_position >= number_of_ticks:
            return False, f"selected_lower_range_tick_position must be greater than or equal to 0 and less than or equal to selected_upper_range_tick_position and less than number_of_ticks"
        if selected_upper_range_tick_position <= selected_lower_range_tick_position or selected_upper_range_tick_position >= number_of_ticks:
            return False, f"selected_upper_range_tick_position must be greater than selected_lower_range_tick_position and less than number_of_ticks"
        if minimum_number_of_ticks > (selected_upper_range_tick_position - selected_lower_range_tick_position):
            return False, f"minimum_number_of_ticks must be less than or equal to the difference between selected_upper_range_tick_position and selected_lower_range_tick_position"
        
        return True, "Verification successful"
            
    ###########################################################################
    # Emitter Hook Methods
    ###########################################################################

    @staticmethod
    def _compute_selected_range_lower_tick_value(x: Mapping[PrimaryHookKeyType|SecondaryHookKeyType, Any] | Mapping[PrimaryHookKeyType, Any]) -> T:

        full_range_lower_value = x["full_range_lower_value"]
        full_range_upper_value = x["full_range_upper_value"]
        number_of_ticks: int = x["number_of_ticks"]
        minimum_number_of_ticks: int = x["minimum_number_of_ticks"]
        selected_lower_range_tick_position: int = x["selected_lower_range_tick_position"]
        selected_upper_range_tick_position: int = x["selected_upper_range_tick_position"]
        unit: Optional[Unit] = x["unit"]
        
        selected_range_lower_value = full_range_lower_value + (selected_lower_range_tick_position / number_of_ticks) * (full_range_upper_value - full_range_lower_value)
        if unit is not None:
            assert isinstance(selected_range_lower_value, RealUnitedScalar)
            selected_range_lower_value = selected_range_lower_value.scalar_in_unit(unit)
        else:
            assert isinstance(selected_range_lower_value, float)
        return selected_range_lower_value # type: ignore
    
    @staticmethod
    def _compute_selected_range_upper_tick_value(x: Mapping[PrimaryHookKeyType|SecondaryHookKeyType, Any] | Mapping[PrimaryHookKeyType, Any]) -> T:
        
        full_range_lower_value = x["full_range_lower_value"]
        full_range_upper_value = x["full_range_upper_value"]
        number_of_ticks: int = x["number_of_ticks"]
        minimum_number_of_ticks: int = x["minimum_number_of_ticks"]
        selected_lower_range_tick_position: int = x["selected_lower_range_tick_position"]
        selected_upper_range_tick_position: int = x["selected_upper_range_tick_position"]
        unit: Optional[Unit] = x["unit"]

        selected_range_upper_value = full_range_lower_value + (selected_upper_range_tick_position / number_of_ticks) * (full_range_upper_value - full_range_lower_value)
        if unit is not None:
            assert isinstance(selected_range_upper_value, RealUnitedScalar)
            selected_range_upper_value = selected_range_upper_value.scalar_in_unit(unit)
        else:
            assert isinstance(selected_range_upper_value, float)
        return selected_range_upper_value # type: ignore
    
    @staticmethod
    def _compute_selected_range_lower_tick_relative_value(x: Mapping[PrimaryHookKeyType|SecondaryHookKeyType, Any] | Mapping[PrimaryHookKeyType, Any]) -> T:

        selected_lower_range_tick_position: int = x["selected_lower_range_tick_position"]
        number_of_ticks: int = x["number_of_ticks"]
        
        selected_range_lower_relative_value = selected_lower_range_tick_position / number_of_ticks
        return selected_range_lower_relative_value # type: ignore
    
    @staticmethod
    def _compute_selected_range_upper_tick_relative_value(x: Mapping[PrimaryHookKeyType|SecondaryHookKeyType, Any] | Mapping[PrimaryHookKeyType, Any]) -> T:
        
        selected_upper_range_tick_position: int = x["selected_upper_range_tick_position"]
        number_of_ticks: int = x["number_of_ticks"]

        selected_range_upper_relative_value = selected_upper_range_tick_position / number_of_ticks
        return selected_range_upper_relative_value # type: ignore
    
    @staticmethod
    def _compute_selected_range_size(x: Mapping[PrimaryHookKeyType|SecondaryHookKeyType, Any] | Mapping[PrimaryHookKeyType, Any]) -> T:

        full_range_lower_value = x["full_range_lower_value"]
        full_range_upper_value = x["full_range_upper_value"]
        selected_lower_range_tick_position: int = x["selected_lower_range_tick_position"]
        selected_upper_range_tick_position: int = x["selected_upper_range_tick_position"]
        number_of_ticks: int = x["number_of_ticks"]
        
        selected_range_size = (full_range_upper_value - full_range_lower_value) * (selected_upper_range_tick_position - selected_lower_range_tick_position) / number_of_ticks
        return selected_range_size # type: ignore
    
    @staticmethod
    def _compute_minimum_range_size(x: Mapping[PrimaryHookKeyType|SecondaryHookKeyType, Any] | Mapping[PrimaryHookKeyType, Any]) -> T:
        
        full_range_lower_value = x["full_range_lower_value"]
        full_range_upper_value = x["full_range_upper_value"]
        number_of_ticks: int = x["number_of_ticks"]
        minimum_number_of_ticks: int = x["minimum_number_of_ticks"]
        unit: Optional[Unit] = x["unit"]
        
        minimum_range_size = minimum_number_of_ticks * (full_range_upper_value - full_range_lower_value) / number_of_ticks
        if unit is not None:
            assert isinstance(minimum_range_size, RealUnitedScalar)
            minimum_range_size = minimum_range_size.scalar_in_unit(unit)
        else:
            assert isinstance(minimum_range_size, float)
        return minimum_range_size # type: ignore
    
    @staticmethod
    def _compute_center_of_range_value(x: Mapping[PrimaryHookKeyType|SecondaryHookKeyType, Any] | Mapping[PrimaryHookKeyType, Any]) -> T:
        
        full_range_lower_value = x["full_range_lower_value"]
        full_range_upper_value = x["full_range_upper_value"]
        number_of_ticks: int = x["number_of_ticks"]
        selected_lower_range_tick_position: int = x["selected_lower_range_tick_position"]
        selected_upper_range_tick_position: int = x["selected_upper_range_tick_position"]
        unit: Optional[Unit] = x["unit"]
        
        center_of_range_value = full_range_lower_value + (selected_lower_range_tick_position + selected_upper_range_tick_position) / 2 / number_of_ticks * (full_range_upper_value - full_range_lower_value)    
        if unit is not None:
            assert isinstance(center_of_range_value, RealUnitedScalar)
            center_of_range_value = center_of_range_value.scalar_in_unit(unit)
        else:
            assert isinstance(center_of_range_value, float)
        return center_of_range_value # type: ignore
    
    @staticmethod
    def _compute_step_size_value(x: Mapping[PrimaryHookKeyType|SecondaryHookKeyType, Any] | Mapping[PrimaryHookKeyType, Any]) -> T:
        
        full_range_lower_value = x["full_range_lower_value"]
        full_range_upper_value = x["full_range_upper_value"]
        number_of_ticks: int = x["number_of_ticks"]
        unit: Optional[Unit] = x["unit"]
        
        step_size = (full_range_upper_value - full_range_lower_value) / number_of_ticks
        if unit is not None:
            assert isinstance(step_size, RealUnitedScalar)
            step_size = step_size.scalar_in_unit(unit)
        else:
            assert isinstance(step_size, float)
        return step_size # type: ignore
    
    @staticmethod
    def _compute_range_value_type(x: Mapping[PrimaryHookKeyType|SecondaryHookKeyType, Any] | Mapping[PrimaryHookKeyType, Any]) -> RangeValueType:
        
        full_range_lower_value = x["full_range_lower_value"]

        if isinstance(full_range_lower_value, RealUnitedScalar):
            return RangeValueType.REAL_UNITED_SCALAR
        elif isinstance(full_range_lower_value, float):
            return RangeValueType.FLOAT
        else:
            raise ValueError(f"Invalid full_range_lower_value: {full_range_lower_value}")

    ###########################################################################
    # Widgets
    ###########################################################################

    def _initialize_widgets(self) -> None:
        """Initialize the widgets."""

        number_of_ticks: int = self.get_value_of_hook("number_of_ticks")

        self._widget_range = GuardedRangeSlider(self._owner_widget)
        self._widget_range.setTickRange(0, number_of_ticks - 1)
        
        self._widget_range.rangeChanged.connect(self._on_range_changed)
        
        # Wrap the range slider in a BlankableWidget for NaN handling
        self._blankable_widget_range = BlankableWidget(self._widget_range, self._owner_widget)

    def _on_range_changed(self, lower_range_position_tick_position: int, upper_range_position_tick_position: int) -> None:
        """
        Handle range slider change.
        
        This method is called when the range slider is changed. It receives the integer values of the lower and upper range.

        Then the following values are computed:
        - selected_lower_range_tick_position
        - selected_upper_range_tick_position

        Then the component values are updated.
        """

        if self.is_blocking_signals:
            return
        
        dict_to_set: dict[PrimaryHookKeyType, Any] = {
            "selected_lower_range_tick_position": lower_range_position_tick_position,
            "selected_upper_range_tick_position": upper_range_position_tick_position
        }

        self._submit_values_on_widget_changed(dict_to_set)

    def _on_text_edit_selected_range_lower_float_value_changed(self) -> None:
        """Handle text edit selected range lower float value changed."""

        if self.is_blocking_signals:
            return
        
        text_edit_value: str = self._widget_text_edit_selected_range_lower_float_value.text()
        try:
            float_value: float = float(text_edit_value)
        except ValueError:
            self.invalidate_widgets()
            return
        
        component_values: dict[PrimaryHookKeyType|SecondaryHookKeyType, Any] = self.get_dict_of_values()

        full_range_lower_value: RealUnitedScalar | float = component_values["full_range_lower_value"]
        full_range_upper_value: RealUnitedScalar | float = component_values["full_range_upper_value"]
        number_of_ticks: int = component_values["number_of_ticks"]
        value_type: RangeValueType = self._compute_range_value_type(component_values)
        
        match value_type:
            case RangeValueType.REAL_UNITED_SCALAR:
                unit: Unit = component_values["unit"]
                assert isinstance(full_range_lower_value, RealUnitedScalar)
                assert isinstance(full_range_upper_value, RealUnitedScalar)
                upper_value_in_unit: float = full_range_upper_value.value_in_unit(unit)
                lower_value_in_unit: float = full_range_lower_value.value_in_unit(unit)
                selected_lower_range_tick_position: int = max(0, min(number_of_ticks - 1, int((float_value - lower_value_in_unit) / (upper_value_in_unit - lower_value_in_unit) * number_of_ticks)))
            case RangeValueType.FLOAT:
                assert isinstance(full_range_lower_value, float)
                assert isinstance(full_range_upper_value, float)
                selected_lower_range_tick_position = max(0, min(number_of_ticks - 1, int((float_value - full_range_lower_value) / (full_range_upper_value - full_range_lower_value) * number_of_ticks)))
            case _:
                raise ValueError(f"Invalid range value type: {value_type}")
        
        # Get current upper tick position to ensure we don't exceed it
        current_upper_tick_position: int = component_values["selected_upper_range_tick_position"]
        selected_lower_range_tick_position = min(selected_lower_range_tick_position, current_upper_tick_position)
            
        dict_to_set: dict[PrimaryHookKeyType, Any] = {"selected_lower_range_tick_position": selected_lower_range_tick_position}
            
        self._submit_values_on_widget_changed(dict_to_set)

    def _on_text_edit_selected_range_upper_float_value_changed(self) -> None:
        """Handle text edit selected range upper float value changed."""

        if self.is_blocking_signals:
            return
        
        text_edit_value: str = self._widget_text_edit_selected_range_upper_float_value.text()
        try:
            float_value: float = float(text_edit_value)
        except ValueError:
            self.invalidate_widgets()
            return
        
        component_values: dict[PrimaryHookKeyType|SecondaryHookKeyType, Any] = self.get_dict_of_values()
        
        full_range_lower_value: RealUnitedScalar | float = self.get_value_of_hook("full_range_lower_value")
        full_range_upper_value: RealUnitedScalar | float = self.get_value_of_hook("full_range_upper_value")
        number_of_ticks: int = component_values["number_of_ticks"]
        value_type: RangeValueType = self._compute_range_value_type(component_values)
        
        match value_type:
            case RangeValueType.REAL_UNITED_SCALAR:
                unit: Unit = self.get_value_of_hook("unit") # type: ignore
                assert isinstance(full_range_lower_value, RealUnitedScalar)
                assert isinstance(full_range_upper_value, RealUnitedScalar)
                upper_value_in_unit: float = full_range_upper_value.value_in_unit(unit)
                lower_value_in_unit: float = full_range_lower_value.value_in_unit(unit)
                selected_upper_range_tick_position: int = max(0, min(number_of_ticks - 1, int((float_value - lower_value_in_unit) / (upper_value_in_unit - lower_value_in_unit) * number_of_ticks)))
            case RangeValueType.FLOAT:
                assert isinstance(full_range_lower_value, float)
                assert isinstance(full_range_upper_value, float)
                selected_upper_range_tick_position = max(0, min(number_of_ticks - 1, int((float_value - full_range_lower_value) / (full_range_upper_value - full_range_lower_value) * number_of_ticks)))
            case _:
                raise ValueError(f"Invalid range value type: {value_type}")
        
        # Get current lower tick position to ensure we don't go below it
        current_lower_tick_position: int = self.get_value_of_hook("selected_lower_range_tick_position") # type: ignore
        selected_upper_range_tick_position = max(selected_upper_range_tick_position, current_lower_tick_position)
        
        dict_to_set: dict[PrimaryHookKeyType, Any] = {"selected_upper_range_tick_position": selected_upper_range_tick_position}

        self._submit_values_on_widget_changed(dict_to_set)

    def _invalidate_widgets_impl(self) -> None:
        """Update the widgets from the component values."""

        values_as_reference_dict: dict[PrimaryHookKeyType|SecondaryHookKeyType, Any] = self.get_dict_of_value_references()

        # Get values as reference
        full_range_lower_value = self.get_value_of_hook("full_range_lower_value")
        full_range_upper_value = self.get_value_of_hook("full_range_upper_value")
        selected_lower_range_tick_position: int = self.get_value_of_hook("selected_lower_range_tick_position")
        selected_upper_range_tick_position: int = self.get_value_of_hook("selected_upper_range_tick_position")
        unit: Optional[Unit] = self.get_value_of_hook("unit")

        # Check for NaN or infinite values in the range bounds
        has_nan_values = (self._is_nan_or_inf(full_range_lower_value) or 
                         self._is_nan_or_inf(full_range_upper_value))
        
        # Blank or unblank all widgets based on NaN detection
        blankable_widgets = [
            "_blankable_widget_range",
            "_blankable_widget_label_full_range_lower_value",
            "_blankable_widget_label_full_range_upper_value", 
            "_blankable_widget_label_full_range_lower_float_value",
            "_blankable_widget_label_full_range_upper_float_value",
            "_blankable_widget_label_selected_range_lower_value",
            "_blankable_widget_label_selected_range_upper_value",
            "_blankable_widget_label_selected_range_lower_float_value",
            "_blankable_widget_label_selected_range_upper_float_value",
            "_blankable_widget_label_selected_range_size_value",
            "_blankable_widget_label_selected_range_size_float_value",
            "_blankable_widget_label_center_of_selected_range_value",
            "_blankable_widget_label_center_of_selected_range_float_value",
            "_blankable_widget_label_unit",
            "_blankable_widget_text_edit_selected_range_lower_value",
            "_blankable_widget_text_edit_selected_range_upper_value"
        ]
        
        for widget_attr in blankable_widgets:
            if hasattr(self, widget_attr):
                blankable_widget = getattr(self, widget_attr)
                if has_nan_values:
                    blankable_widget.blank()
                else:
                    blankable_widget.unblank()

        # Compute emitted values
        selected_range_lower_value = self._compute_selected_range_lower_tick_value(values_as_reference_dict)
        selected_range_upper_value = self._compute_selected_range_upper_tick_value(values_as_reference_dict)
        selected_range_size = self._compute_selected_range_size(values_as_reference_dict)
        center_of_range = self._compute_center_of_range_value(values_as_reference_dict)
        range_value_type = self._compute_range_value_type(values_as_reference_dict)

        # Set range slider range
        self._widget_range.setTickValue(selected_lower_range_tick_position, selected_upper_range_tick_position)

        # Fill other, optional, widgets
        match range_value_type:
            case RangeValueType.REAL_UNITED_SCALAR:
                assert isinstance(full_range_lower_value, RealUnitedScalar)
                assert isinstance(full_range_upper_value, RealUnitedScalar)
                assert isinstance(selected_range_lower_value, RealUnitedScalar)
                assert isinstance(selected_range_upper_value, RealUnitedScalar)
                assert isinstance(selected_range_size, RealUnitedScalar)
                assert isinstance(center_of_range, RealUnitedScalar)
                assert unit is not None

                if hasattr(self, "_widget_label_full_range_lower_value"):
                    self._widget_label_full_range_lower_value.setText(full_range_lower_value.format(unit=unit))
                if hasattr(self, "_widget_label_full_range_upper_value"):
                    self._widget_label_full_range_upper_value.setText(full_range_upper_value.format(unit=unit))
                if hasattr(self, "_widget_label_full_range_lower_float_value"):
                    self._widget_label_full_range_lower_float_value.setText(f"{full_range_upper_value.value_in_unit(unit):.2f}")
                if hasattr(self, "_widget_label_full_range_upper_float_value"):
                    self._widget_label_full_range_upper_float_value.setText(f"{full_range_upper_value.value_in_unit(unit):.2f}")
                if hasattr(self, "_widget_label_selected_range_lower_value"):
                    self._widget_label_selected_range_lower_value.setText(selected_range_lower_value.format(unit=unit))
                if hasattr(self, "_widget_label_selected_range_upper_value"):
                    self._widget_label_selected_range_upper_value.setText(selected_range_upper_value.format(unit=unit))
                if hasattr(self, "_widget_label_selected_range_lower_float_value"):
                    self._widget_label_selected_range_lower_float_value.setText(f"{selected_range_lower_value.value_in_unit(unit):.2f}")
                if hasattr(self, "_widget_label_selected_range_upper_float_value"):
                    self._widget_label_selected_range_upper_float_value.setText(f"{selected_range_upper_value.value_in_unit(unit):.2f}")
                if hasattr(self, "_widget_label_selected_range_size_value"):
                    self._widget_label_selected_range_size_value.setText(selected_range_size.format(unit=unit))
                if hasattr(self, "_widget_label_center_of_selected_range_value"):
                    self._widget_label_center_of_selected_range_value.setText(center_of_range.format(unit=unit))
                if hasattr(self, "_widget_label_center_of_selected_range_float_value"):
                    self._widget_label_center_of_selected_range_float_value.setText(f"{center_of_range.value_in_unit(unit):.2f}")
                if hasattr(self, "_widget_text_edit_selected_range_lower_float_value"):
                    self._widget_text_edit_selected_range_lower_float_value.setText(f"{selected_range_lower_value.value_in_unit(unit):.2f}")
                if hasattr(self, "_widget_text_edit_selected_range_upper_float_value"):
                    self._widget_text_edit_selected_range_upper_float_value.setText(f"{selected_range_upper_value.value_in_unit(unit):.2f}")

            case RangeValueType.FLOAT:
                assert isinstance(full_range_lower_value, float)
                assert isinstance(full_range_upper_value, float)
                assert isinstance(selected_range_lower_value, float)
                assert isinstance(selected_range_upper_value, float)
                assert isinstance(selected_range_size, float)
                assert isinstance(center_of_range, float)

                if hasattr(self, "_widget_label_full_range_lower_value"):
                    self._widget_label_full_range_lower_value.setText(f"{full_range_lower_value:.2f}")
                if hasattr(self, "_widget_label_full_range_upper_value"):
                    self._widget_label_full_range_upper_value.setText(f"{full_range_upper_value:.2f}")
                if hasattr(self, "_widget_label_full_range_lower_float_value"):
                    self._widget_label_full_range_lower_float_value.setText(f"{full_range_upper_value:.2f}")
                if hasattr(self, "_widget_label_full_range_upper_float_value"):
                    self._widget_label_full_range_upper_float_value.setText(f"{full_range_upper_value:.2f}")
                if hasattr(self, "_widget_label_selected_range_lower_value"):
                    self._widget_label_selected_range_lower_value.setText(f"{selected_range_lower_value:.2f}")
                if hasattr(self, "_widget_label_selected_range_upper_value"):
                    self._widget_label_selected_range_upper_value.setText(f"{selected_range_upper_value:.2f}")
                if hasattr(self, "_widget_label_selected_range_lower_float_value"):
                    self._widget_label_selected_range_lower_float_value.setText(f"{selected_range_lower_value:.2f}")
                if hasattr(self, "_widget_label_selected_range_upper_float_value"):
                    self._widget_label_selected_range_upper_float_value.setText(f"{selected_range_upper_value:.2f}")
                if hasattr(self, "_widget_label_selected_range_size_value"):
                    self._widget_label_selected_range_size_value.setText(f"{selected_range_size:.2f}")
                if hasattr(self, "_widget_label_center_of_selected_range_value"):
                    self._widget_label_center_of_selected_range_value.setText(f"{center_of_range:.2f}")
                if hasattr(self, "_widget_label_center_of_selected_range_float_value"):
                    self._widget_label_center_of_selected_range_float_value.setText(f"{center_of_range:.2f}")
                if hasattr(self, "_widget_text_edit_selected_range_lower_float_value"):
                    self._widget_text_edit_selected_range_lower_float_value.setText(f"{selected_range_lower_value:.2f}")
                if hasattr(self, "_widget_text_edit_selected_range_upper_float_value"):
                    self._widget_text_edit_selected_range_upper_float_value.setText(f"{selected_range_upper_value:.2f}")

            case _:
                raise ValueError(f"Invalid range value type: {range_value_type}")      

    ###########################################################################
    # Getters and Setters
    ###########################################################################

    @property
    def full_range_lower_value_hook(self) -> OwnedHookLike[T]:
        return self.get_hook("full_range_lower_value")
    
    @property
    def full_range_upper_value_hook(self) -> OwnedHookLike[T]:
        return self.get_hook("full_range_upper_value")
    
    @property
    def number_of_ticks_hook(self) -> OwnedHookLike[int]:
        return self.get_hook("number_of_ticks")
    
    @property
    def minimum_number_of_ticks_hook(self) -> OwnedHookLike[int]:
        return self.get_hook("minimum_number_of_ticks")
    
    @property
    def selected_lower_range_tick_position_hook(self) -> OwnedHookLike[int]:
        return self.get_hook("selected_lower_range_tick_position")
    
    @property
    def selected_upper_range_tick_position_hook(self) -> OwnedHookLike[int]:
        return self.get_hook("selected_upper_range_tick_position")
    
    @property
    def unit_hook(self) -> OwnedHookLike[Optional[Unit]]:
        return self.get_hook("unit")
    
    @property
    def selected_range_lower_tick_value_hook(self) -> OwnedHookLike[T]:
        return self.get_hook("selected_range_lower_tick_value")
    
    @property
    def selected_range_upper_tick_value_hook(self) -> OwnedHookLike[T]:
        return self.get_hook("selected_range_upper_tick_value")

    @property
    def selected_range_lower_tick_relative_value_hook(self) -> OwnedHookLike[T]:
        return self.get_hook("selected_range_lower_tick_relative_value")
    
    @property
    def selected_range_upper_tick_relative_value_hook(self) -> OwnedHookLike[T]:
        return self.get_hook("selected_range_upper_tick_relative_value")
    
    @property
    def selected_range_size_hook(self) -> OwnedHookLike[T]:
        return self.get_hook("selected_range_size")
    
    @property
    def minimum_range_size_hook(self) -> OwnedHookLike[T]:
        return self.get_hook("minimum_range_size")
    
    @property
    def center_of_range_value_hook(self) -> OwnedHookLike[T]:
        return self.get_hook("center_of_range_value")
    
    @property
    def step_size_hook(self) -> OwnedHookLike[T]:
        return self.get_hook("step_size")
    
    @property
    def range_value_type_hook(self) -> OwnedHookLike[RangeValueType]:
        return self.get_hook("range_value_type")

    ###########################################################################
    # Convenience setter methods
    ###########################################################################

    def set_full_range_values(
            self,
            full_range_lower_value: T,
            full_range_upper_value: T) -> None:
        """
        Set the full range values.

        Args:
            full_range_lower_value: The lower value of the full range.
            full_range_upper_value: The upper value of the full range.
        """
        success, msg = self.submit_values({
            "full_range_lower_value": full_range_lower_value,
            "full_range_upper_value": full_range_upper_value
            })

        if not success:
            raise ValueError(f"Failed to set full range values: {msg}")

    def set_relative_selected_range_values(
            self,
            selected_range_lower_relative_float_value: float,
            selected_range_upper_relative_float_value: float) -> None:
        """
        Set the relative selected range values.

        Args:
            selected_range_lower_relative_float_value: The relative lower value of the selected range.
            selected_range_upper_relative_float_value: The relative upper value of the selected range.
        """

        number_of_ticks: int = self.get_value_of_hook("number_of_ticks")

        selected_lower_range_tick_position: int = int(selected_range_lower_relative_float_value * number_of_ticks)
        selected_upper_range_tick_position: int = int(selected_range_upper_relative_float_value * number_of_ticks)

        success, msg = self.submit_values({
            "selected_lower_range_tick_position": selected_lower_range_tick_position,
            "selected_upper_range_tick_position": selected_upper_range_tick_position,
            })

        if not success:
            raise ValueError(f"Failed to set relative selected range values: {msg}")

    def set_number_of_ticks(self, number_of_ticks: int, keep_relative_selected_range: bool = False) -> None:
        """
        Set the number of ticks.

        Args:
            number_of_ticks: The number of ticks.
            keep_relative_selected_range: Whether to keep the relative selected range values.
        """

        raise NotImplementedError("Not implemented yet.")
    
    ###########################################################################
    # Value accessors and setters
    ###########################################################################

    @property
    def full_range_lower_value(self) -> T:
        return self.get_value_of_hook("full_range_lower_value")
    
    @full_range_lower_value.setter
    def full_range_lower_value(self, value: T) -> None:
        self.submit_value("full_range_lower_value", value)

    @property
    def full_range_upper_value(self) -> T:
        return self.get_value_of_hook("full_range_upper_value")
    
    @full_range_upper_value.setter
    def full_range_upper_value(self, value: T) -> None:
        self.submit_value("full_range_upper_value", value)

    @property
    def selected_range_relative_lower_value(self) -> float:
        return self.get_value_of_hook("selected_range_lower_tick_relative_value")
    
    @property
    def selected_range_relative_lower_value_hook(self) -> OwnedHookLike[float]:
        return self.get_hook("selected_range_lower_tick_relative_value")
    
    @property
    def selected_range_relative_upper_value(self) -> float:
        return self.get_value_of_hook("selected_range_upper_tick_relative_value")

    @property
    def selected_range_relative_upper_value_hook(self) -> OwnedHookLike[float]:
        return self.get_hook("selected_range_upper_tick_relative_value")
    
    @property
    def selected_range_upper_value(self) -> T:
        return self.get_value_of_hook("selected_range_upper_tick_value")
    
    @property
    def selected_range_upper_value_hook(self) -> HookLike[T]:
        return self.get_hook("selected_range_upper_tick_value")
    
    @property
    def selected_range_lower_value(self) -> T:
        return self.get_value_of_hook("selected_range_lower_tick_value")
    
    @property
    def selected_range_lower_value_hook(self) -> HookLike[T]:
        return self.get_hook("selected_range_lower_tick_value")
    
    @property
    def selected_range_size_value(self) -> T:
        return self.get_value_of_hook("selected_range_size")
    
    @property
    def center_of_range_value(self) -> T:
        return self.get_value_of_hook("center_of_range_value")
    
    @property
    def step_size(self) -> T:
        return self.get_value_of_hook("step_size")

    @property
    def range_value_type(self) -> RangeValueType:
        return self.get_value_of_hook("range_value_type")

    ###########################################################################
    # Widgets accessors
    ###########################################################################

    @property
    def widget_range_slider(self) -> BlankableWidget[GuardedRangeSlider]:
        if not hasattr(self, "_blankable_widget_range"):
            # This should not happen as it's initialized in _initialize_widgets
            raise RuntimeError("Range slider not properly initialized")
        return self._blankable_widget_range
    

    @property
    def widget_label_full_range_lower_value(self) -> BlankableWidget[GuardedLabel]:
        if not hasattr(self, "_blankable_widget_label_full_range_lower_value"):
            self._widget_label_full_range_lower_value = GuardedLabel(self)
            self._blankable_widget_label_full_range_lower_value = BlankableWidget(self._widget_label_full_range_lower_value, self._owner_widget)
        self.invalidate_widgets()
        return self._blankable_widget_label_full_range_lower_value
    
    @property
    def widget_label_full_range_upper_value(self) -> BlankableWidget[GuardedLabel]:
        if not hasattr(self, "_blankable_widget_label_full_range_upper_value"):
            self._widget_label_full_range_upper_value = GuardedLabel(self)
            self._blankable_widget_label_full_range_upper_value = BlankableWidget(self._widget_label_full_range_upper_value, self._owner_widget)
        self.invalidate_widgets()
        return self._blankable_widget_label_full_range_upper_value
    
    @property
    def widget_label_full_range_lower_float_value(self) -> BlankableWidget[GuardedLabel]:
        if not hasattr(self, "_blankable_widget_label_full_range_lower_float_value"):
            self._widget_label_full_range_lower_float_value = GuardedLabel(self)
            self._blankable_widget_label_full_range_lower_float_value = BlankableWidget(self._widget_label_full_range_lower_float_value, self._owner_widget)
        self.invalidate_widgets()
        return self._blankable_widget_label_full_range_lower_float_value
    
    @property
    def widget_label_full_range_upper_float_value(self) -> BlankableWidget[GuardedLabel]:
        if not hasattr(self, "_blankable_widget_label_full_range_upper_float_value"):
            self._widget_label_full_range_upper_float_value = GuardedLabel(self)
            self._blankable_widget_label_full_range_upper_float_value = BlankableWidget(self._widget_label_full_range_upper_float_value, self._owner_widget)
        self.invalidate_widgets()
        return self._blankable_widget_label_full_range_upper_float_value
    
    @property
    def widget_label_selected_range_lower_value(self) -> BlankableWidget[GuardedLabel]:
        if not hasattr(self, "_blankable_widget_label_selected_range_lower_value"):
            self._widget_label_selected_range_lower_value = GuardedLabel(self)
            self._blankable_widget_label_selected_range_lower_value = BlankableWidget(self._widget_label_selected_range_lower_value, self._owner_widget)
        self.invalidate_widgets()
        return self._blankable_widget_label_selected_range_lower_value
    
    @property
    def widget_label_selected_range_upper_value(self) -> BlankableWidget[GuardedLabel]:
        if not hasattr(self, "_blankable_widget_label_selected_range_upper_value"):
            self._widget_label_selected_range_upper_value = GuardedLabel(self)
            self._blankable_widget_label_selected_range_upper_value = BlankableWidget(self._widget_label_selected_range_upper_value, self._owner_widget)
        self.invalidate_widgets()
        return self._blankable_widget_label_selected_range_upper_value

    @property
    def widget_label_selected_range_lower_float_value(self) -> BlankableWidget[GuardedLabel]:
        if not hasattr(self, "_blankable_widget_label_selected_range_lower_float_value"):
            self._widget_label_selected_range_lower_float_value = GuardedLabel(self)
            self._blankable_widget_label_selected_range_lower_float_value = BlankableWidget(self._widget_label_selected_range_lower_float_value, self._owner_widget)
        self.invalidate_widgets()
        return self._blankable_widget_label_selected_range_lower_float_value
    
    @property
    def widget_label_selected_range_upper_float_value(self) -> BlankableWidget[GuardedLabel]:
        if not hasattr(self, "_blankable_widget_label_selected_range_upper_float_value"):
            self._widget_label_selected_range_upper_float_value = GuardedLabel(self)
            self._blankable_widget_label_selected_range_upper_float_value = BlankableWidget(self._widget_label_selected_range_upper_float_value, self._owner_widget)
        self.invalidate_widgets()
        return self._blankable_widget_label_selected_range_upper_float_value
    
    @property
    def widget_label_selected_range_size_value(self) -> BlankableWidget[GuardedLabel]:
        if not hasattr(self, "_blankable_widget_label_selected_range_size_value"):
            self._widget_label_selected_range_size_value = GuardedLabel(self)
            self._blankable_widget_label_selected_range_size_value = BlankableWidget(self._widget_label_selected_range_size_value, self._owner_widget)
        self.invalidate_widgets()
        return self._blankable_widget_label_selected_range_size_value
    
    @property
    def widget_label_selected_range_size_float_value(self) -> BlankableWidget[GuardedLabel]:
        if not hasattr(self, "_blankable_widget_label_selected_range_size_float_value"):
            self._widget_label_selected_range_size_float_value = GuardedLabel(self)
            self._blankable_widget_label_selected_range_size_float_value = BlankableWidget(self._widget_label_selected_range_size_float_value, self._owner_widget)
        self.invalidate_widgets()
        return self._blankable_widget_label_selected_range_size_float_value
    
    @property
    def widget_label_center_of_selected_range_value(self) -> BlankableWidget[GuardedLabel]:
        if not hasattr(self, "_blankable_widget_label_center_of_selected_range_value"):
            self._widget_label_center_of_selected_range_value = GuardedLabel(self)
            self._blankable_widget_label_center_of_selected_range_value = BlankableWidget(self._widget_label_center_of_selected_range_value, self._owner_widget)
        self.invalidate_widgets()
        return self._blankable_widget_label_center_of_selected_range_value
    
    @property
    def widget_label_center_of_selected_range_float_value(self) -> BlankableWidget[GuardedLabel]:
        if not hasattr(self, "_blankable_widget_label_center_of_selected_range_float_value"):
            self._widget_label_center_of_selected_range_float_value = GuardedLabel(self)
            self._blankable_widget_label_center_of_selected_range_float_value = BlankableWidget(self._widget_label_center_of_selected_range_float_value, self._owner_widget)
        self.invalidate_widgets()
        return self._blankable_widget_label_center_of_selected_range_float_value
    
    @property
    def widget_label_unit(self) -> BlankableWidget[GuardedLabel]:
        if not hasattr(self, "_blankable_widget_label_unit"):
            self._widget_label_unit = GuardedLabel(self)
            self._blankable_widget_label_unit = BlankableWidget(self._widget_label_unit, self._owner_widget)
        self.invalidate_widgets()
        return self._blankable_widget_label_unit
    
    @property
    def widget_text_edit_selected_range_lower_value(self) -> BlankableWidget[GuardedLineEdit]:
        if not hasattr(self, "_blankable_widget_text_edit_selected_range_lower_value"):
            self._widget_text_edit_selected_range_lower_float_value = GuardedLineEdit(self)
            self._widget_text_edit_selected_range_lower_float_value.editingFinished.connect(self._on_text_edit_selected_range_lower_float_value_changed)
            self._blankable_widget_text_edit_selected_range_lower_value = BlankableWidget(self._widget_text_edit_selected_range_lower_float_value, self._owner_widget)
        self.invalidate_widgets()
        return self._blankable_widget_text_edit_selected_range_lower_value
    
    @property
    def widget_text_edit_selected_range_upper_value(self) -> BlankableWidget[GuardedLineEdit]:
        if not hasattr(self, "_blankable_widget_text_edit_selected_range_upper_value"):
            self._widget_text_edit_selected_range_upper_float_value = GuardedLineEdit(self)
            self._widget_text_edit_selected_range_upper_float_value.editingFinished.connect(self._on_text_edit_selected_range_upper_float_value_changed)
            self._blankable_widget_text_edit_selected_range_upper_value = BlankableWidget(self._widget_text_edit_selected_range_upper_float_value, self._owner_widget)
        self.invalidate_widgets()
        return self._blankable_widget_text_edit_selected_range_upper_value