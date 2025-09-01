# Standard library imports
from __future__ import annotations
from typing import Generic, Optional, TypeVar, cast, Any, Mapping, Literal
import math
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget
from enum import Enum
from logging import Logger

# BAB imports
from integrated_widgets.widget_controllers.base_controller import BaseWidgetController
from observables import ObservableTupleLike, Hook, InitialSyncMode, HookLike, ObservableSingleValueLike
from united_system import RealUnitedScalar, Unit

# Local imports
from ..guarded_widgets.guarded_range_slider import GuardedRangeSlider
from ..guarded_widgets.guarded_label import GuardedLabel
from ..guarded_widgets.guarded_line_edit import GuardedLineEdit
from ..util.resources import log_msg, log_bool

HookKeyType = Literal[
    "full_range_lower_value",
    "full_range_upper_value",
    "number_of_ticks",
    "minimum_number_of_ticks",
    "selected_lower_range_tick_position",
    "selected_upper_range_tick_position",
    "unit"
]
EmitterHookKeyType = Literal[
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

class RangeSliderController(BaseWidgetController[HookKeyType, EmitterHookKeyType], Generic[T]):

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
            full_range_lower_value_hook: Optional[HookLike[T]] = None

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
            full_range_upper_value_hook: Optional[HookLike[T]] = None

        # number_of_ticks
        if isinstance(number_of_ticks, int):
            initial_number_of_ticks: int = number_of_ticks
            number_of_ticks_hook: Optional[HookLike[int]] = None
        elif isinstance(number_of_ticks, ObservableSingleValueLike):
            initial_number_of_ticks: int = number_of_ticks.value # type: ignore
            number_of_ticks_hook: Optional[HookLike[int]] = number_of_ticks.value # type: ignore
        elif isinstance(number_of_ticks, HookLike):
            initial_number_of_ticks: int = number_of_ticks.value # type: ignore
            number_of_ticks_hook: Optional[HookLike[int]] = number_of_ticks
        else:
            raise ValueError(f"Invalid number_of_ticks: {number_of_ticks}")
        
        # minimum_number_of_ticks
        if isinstance(minimum_number_of_ticks, int):
            initial_minimum_number_of_ticks: int = minimum_number_of_ticks
            minimum_number_of_ticks_hook: Optional[HookLike[int]] = None
        elif isinstance(minimum_number_of_ticks, ObservableSingleValueLike):
            initial_minimum_number_of_ticks: int = minimum_number_of_ticks.value # type: ignore
            minimum_number_of_ticks_hook: Optional[HookLike[int]] = minimum_number_of_ticks.value # type: ignore
        elif isinstance(minimum_number_of_ticks, HookLike):
            initial_minimum_number_of_ticks: int = minimum_number_of_ticks.value # type: ignore
            minimum_number_of_ticks_hook: Optional[HookLike[int]] = minimum_number_of_ticks
        else:
            raise ValueError(f"Invalid minimum_number_of_ticks: {minimum_number_of_ticks}")
        
        # selected_lower_range_tick_position
        if isinstance(selected_lower_range_tick_position, int):
            initial_selected_lower_range_tick_position: int = selected_lower_range_tick_position
            selected_lower_range_tick_position_hook: Optional[HookLike[int]] = None
        elif isinstance(selected_lower_range_tick_position, ObservableSingleValueLike):
            initial_selected_lower_range_tick_position: int = selected_lower_range_tick_position.value # type: ignore
            selected_lower_range_tick_position_hook: Optional[HookLike[int]] = selected_lower_range_tick_position.value # type: ignore
        elif isinstance(selected_lower_range_tick_position, HookLike):
            initial_selected_lower_range_tick_position: int = selected_lower_range_tick_position.value # type: ignore
            selected_lower_range_tick_position_hook: Optional[HookLike[int]] = selected_lower_range_tick_position
        else:
            raise ValueError(f"Invalid selected_lower_range_tick_position: {selected_lower_range_tick_position}")
        
        # selected_upper_range_tick_position
        if isinstance(selected_upper_range_tick_position, int):
            initial_selected_upper_range_tick_position: int = selected_upper_range_tick_position
            selected_upper_range_tick_position_hook: Optional[HookLike[int]] = None
        elif isinstance(selected_upper_range_tick_position, ObservableSingleValueLike):
            initial_selected_upper_range_tick_position: int = selected_upper_range_tick_position.value # type: ignore
            selected_upper_range_tick_position_hook: Optional[HookLike[int]] = selected_upper_range_tick_position.value # type: ignore
        elif isinstance(selected_upper_range_tick_position, HookLike):
            initial_selected_upper_range_tick_position: int = selected_upper_range_tick_position.value # type: ignore
            selected_upper_range_tick_position_hook: Optional[HookLike[int]] = selected_upper_range_tick_position
        else:
            raise ValueError(f"Invalid selected_upper_range_tick_position: {selected_upper_range_tick_position}")
        
        # unit
        if unit is None:
            initial_unit: Optional[Unit] = None
            unit_hook: Optional[HookLike[Optional[Unit]]] = None
        elif isinstance(unit, Unit):
            initial_unit: Optional[Unit] = unit
            unit_hook: Optional[HookLike[Optional[Unit]]] = None
        elif isinstance(unit, ObservableSingleValueLike):
            initial_unit: Optional[Unit] = unit.value # type: ignore
            unit_hook: Optional[HookLike[Optional[Unit]]] = unit.value # type: ignore
        elif isinstance(unit, HookLike):
            initial_unit: Optional[Unit] = unit.value # type: ignore
            unit_hook: Optional[HookLike[Optional[Unit]]] = unit
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
            verification_method=self._verification_method,
            emitter_hook_callbacks={
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

        self.attach(full_range_lower_value_hook, "full_range_lower_value") if full_range_lower_value_hook is not None else None
        self.attach(full_range_upper_value_hook, "full_range_upper_value") if full_range_upper_value_hook is not None else None
        self.attach(number_of_ticks_hook, "number_of_ticks") if number_of_ticks_hook is not None else None
        self.attach(minimum_number_of_ticks_hook, "minimum_number_of_ticks") if minimum_number_of_ticks_hook is not None else None
        self.attach(selected_lower_range_tick_position_hook, "selected_lower_range_tick_position") if selected_lower_range_tick_position_hook is not None else None
        self.attach(selected_upper_range_tick_position_hook, "selected_upper_range_tick_position") if selected_upper_range_tick_position_hook is not None else None
        self.attach(unit_hook, "unit") if unit_hook is not None else None

    ###########################################################################
    # Verification Method
    ###########################################################################

    def _verification_method(self, component_values: Mapping[HookKeyType, Any]) -> tuple[bool, str]:
        
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
                if full_range_lower_value > full_range_upper_value:
                    return False, f"full_range_lower_value must be less or equal to full_range_upper_value"
            case RangeValueType.FLOAT:
                if not isinstance(full_range_lower_value, float):
                    return False, f"full_range_lower_value must be a float"
                if not isinstance(full_range_upper_value, float):
                    return False, f"full_range_upper_value must be a float"
                if unit is not None:
                    return False, f"unit must be None for float values"
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
    def _compute_selected_range_lower_tick_value(x: Mapping[HookKeyType, Any]) -> T:

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
    def _compute_selected_range_upper_tick_value(x: Mapping[HookKeyType, Any]) -> T:
        
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
    def _compute_selected_range_lower_tick_relative_value(x: Mapping[HookKeyType, Any]) -> T:

        selected_lower_range_tick_position: int = x["selected_lower_range_tick_position"]
        number_of_ticks: int = x["number_of_ticks"]
        
        selected_range_lower_relative_value = selected_lower_range_tick_position / number_of_ticks
        return selected_range_lower_relative_value # type: ignore
    
    @staticmethod
    def _compute_selected_range_upper_tick_relative_value(x: Mapping[HookKeyType, Any]) -> T:
        
        selected_upper_range_tick_position: int = x["selected_upper_range_tick_position"]
        number_of_ticks: int = x["number_of_ticks"]

        selected_range_upper_relative_value = selected_upper_range_tick_position / number_of_ticks
        return selected_range_upper_relative_value # type: ignore
    
    @staticmethod
    def _compute_selected_range_size(x: Mapping[HookKeyType, Any]) -> T:

        full_range_lower_value = x["full_range_lower_value"]
        full_range_upper_value = x["full_range_upper_value"]
        selected_lower_range_tick_position: int = x["selected_lower_range_tick_position"]
        selected_upper_range_tick_position: int = x["selected_upper_range_tick_position"]
        number_of_ticks: int = x["number_of_ticks"]
        
        selected_range_size = (full_range_upper_value - full_range_lower_value) * (selected_upper_range_tick_position - selected_lower_range_tick_position) / number_of_ticks
        return selected_range_size # type: ignore
    
    @staticmethod
    def _compute_minimum_range_size(x: Mapping[HookKeyType, Any]) -> T:
        
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
    def _compute_center_of_range_value(x: Mapping[HookKeyType, Any]) -> T:
        
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
    def _compute_step_size_value(x: Mapping[HookKeyType, Any]) -> T:
        
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
    def _compute_range_value_type(x: Mapping[HookKeyType, Any]) -> RangeValueType:
        
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

        number_of_ticks: int = self._component_values["number_of_ticks"]

        self._widget_range = GuardedRangeSlider(self._owner_widget)
        self._widget_range.setTickRange(0, number_of_ticks - 1)
        
        self._widget_range.rangeChanged.connect(self._on_range_changed)

    def _disable_widgets(self) -> None:
        """Disable the widgets."""

        self._widget_range.setShowHandles(False)
        self._widget_range.setEnabled(False)
        if hasattr(self, "_widget_label_full_range_lower_value"):
            self._widget_label_full_range_lower_value.setText("")
            self._widget_label_full_range_lower_value.setEnabled(False)
        if hasattr(self, "_widget_label_full_range_upper_value"):
            self._widget_label_full_range_upper_value.setText("")
            self._widget_label_full_range_upper_value.setEnabled(False)
        if hasattr(self, "_widget_label_full_range_lower_float_value"):
            self._widget_label_full_range_lower_float_value.setText("")
            self._widget_label_full_range_lower_float_value.setEnabled(False)
        if hasattr(self, "_widget_label_full_range_upper_float_value"):
            self._widget_label_full_range_upper_float_value.setText("")
            self._widget_label_full_range_upper_float_value.setEnabled(False)
        if hasattr(self, "_widget_label_unit"):
            self._widget_label_unit.setText("")
            self._widget_label_unit.setEnabled(False)
        if hasattr(self, "_widget_label_selected_range_lower_value"):
            self._widget_label_selected_range_lower_value.setText("")
            self._widget_label_selected_range_lower_value.setEnabled(False)
        if hasattr(self, "_widget_label_selected_range_upper_value"):
            self._widget_label_selected_range_upper_value.setText("")
            self._widget_label_selected_range_upper_value.setEnabled(False)
        if hasattr(self, "_widget_label_selected_range_size_value"):
            self._widget_label_selected_range_size_value.setText("")
            self._widget_label_selected_range_size_value.setEnabled(False)
        if hasattr(self, "_widget_label_selected_range_size_float_value"):
            self._widget_label_selected_range_size_float_value.setText("")
            self._widget_label_selected_range_size_float_value.setEnabled(False)
        if hasattr(self, "_widget_label_center_of_selected_range_value"):
            self._widget_label_center_of_selected_range_value.setText("")
            self._widget_label_center_of_selected_range_value.setEnabled(False)
        if hasattr(self, "_widget_text_edit_selected_range_lower_float_value"):
            self._widget_text_edit_selected_range_lower_float_value.setText("")
            self._widget_text_edit_selected_range_lower_float_value.setEnabled(False)
        if hasattr(self, "_widget_text_edit_selected_range_upper_float_value"):
            self._widget_text_edit_selected_range_upper_float_value.setText("")
            self._widget_text_edit_selected_range_upper_float_value.setEnabled(False)

    def _enable_widgets(self) -> None:
        """Enable the widgets."""
        
        self._widget_range.setEnabled(True)
        if hasattr(self, "_widget_label_full_range_lower_value"):
            self._widget_label_full_range_lower_value.setEnabled(True)
        if hasattr(self, "_widget_label_full_range_upper_value"):
            self._widget_label_full_range_upper_value.setEnabled(True)
        if hasattr(self, "_widget_label_full_range_lower_float_value"):
            self._widget_label_full_range_lower_float_value.setEnabled(True)
        if hasattr(self, "_widget_label_full_range_upper_float_value"):
            self._widget_label_full_range_upper_float_value.setEnabled(True)
        if hasattr(self, "_widget_label_unit"):
            self._widget_label_unit.setEnabled(True)
        if hasattr(self, "_widget_label_selected_range_lower_value"):
            self._widget_label_selected_range_lower_value.setEnabled(True)
        if hasattr(self, "_widget_label_selected_range_upper_value"):
            self._widget_label_selected_range_upper_value.setEnabled(True)
        if hasattr(self, "_widget_label_selected_range_size_value"):
            self._widget_label_selected_range_size_value.setEnabled(True)
        if hasattr(self, "_widget_label_selected_range_size_float_value"):
            self._widget_label_selected_range_size_float_value.setEnabled(True)
        if hasattr(self, "_widget_label_center_of_selected_range_value"):
            self._widget_label_center_of_selected_range_value.setEnabled(True)
        if hasattr(self, "_widget_text_edit_selected_range_lower_float_value"):
            self._widget_text_edit_selected_range_lower_float_value.setEnabled(True)
        if hasattr(self, "_widget_text_edit_selected_range_upper_float_value"):
            self._widget_text_edit_selected_range_upper_float_value.setEnabled(True)

        self._widget_range.setShowHandles(True)

        self.apply_component_values_to_widgets()

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
        
        dict_to_set: dict[HookKeyType, Any] = {
            "selected_lower_range_tick_position": lower_range_position_tick_position,
            "selected_upper_range_tick_position": upper_range_position_tick_position
        }

        self._update_component_values_and_widgets(dict_to_set)

    def _on_text_edit_selected_range_lower_float_value_changed(self) -> None:
        """Handle text edit selected range lower float value changed."""

        if self.is_blocking_signals:
            return
        
        text_edit_value: str = self._widget_text_edit_selected_range_lower_float_value.text()
        try:
            float_value: float = float(text_edit_value)
        except ValueError:
            self.apply_component_values_to_widgets()
            return

        full_range_lower_value: RealUnitedScalar | float = self._component_values["full_range_lower_value"]
        full_range_upper_value: RealUnitedScalar | float = self._component_values["full_range_upper_value"]
        number_of_ticks: int = self._component_values["number_of_ticks"]
        value_type: RangeValueType = self._compute_range_value_type(self._component_values)
        
        match value_type:
            case RangeValueType.REAL_UNITED_SCALAR:
                unit: Unit = self._component_values["unit"]
                assert isinstance(full_range_lower_value, RealUnitedScalar)
                assert isinstance(full_range_upper_value, RealUnitedScalar)
                upper_value_in_unit: float = full_range_upper_value.value_in_unit(unit)
                lower_value_in_unit: float = full_range_lower_value.value_in_unit(unit)
                selected_lower_range_tick_position: int = max(0, min(number_of_ticks - 1, int((float_value - lower_value_in_unit) / (upper_value_in_unit - lower_value_in_unit) * number_of_ticks)))
            case RangeValueType.FLOAT:
                assert isinstance(full_range_lower_value, float)
                assert isinstance(full_range_upper_value, float)
                selected_lower_range_tick_position: int = max(0, min(number_of_ticks - 1, int((float_value - full_range_lower_value) / (full_range_upper_value - full_range_lower_value) * number_of_ticks)))
            case _:
                raise ValueError(f"Invalid range value type: {value_type}")
        
        # Get current upper tick position to ensure we don't exceed it
        current_upper_tick_position: int = self._component_values["selected_upper_range_tick_position"]
        selected_lower_range_tick_position = min(selected_lower_range_tick_position, current_upper_tick_position)
            
        dict_to_set: dict[HookKeyType, Any] = {"selected_lower_range_tick_position": selected_lower_range_tick_position}
            
        self._update_component_values_and_widgets(dict_to_set)

    def _on_text_edit_selected_range_upper_float_value_changed(self) -> None:
        """Handle text edit selected range upper float value changed."""

        if self.is_blocking_signals:
            return
        
        text_edit_value: str = self._widget_text_edit_selected_range_upper_float_value.text()
        try:
            float_value: float = float(text_edit_value)
        except ValueError:
            self.apply_component_values_to_widgets()
            return
        
        full_range_lower_value: RealUnitedScalar | float = self._component_values["full_range_lower_value"]
        full_range_upper_value: RealUnitedScalar | float = self._component_values["full_range_upper_value"]
        number_of_ticks: int = self._component_values["number_of_ticks"]
        value_type: RangeValueType = self._compute_range_value_type(self._component_values)
        
        match value_type:
            case RangeValueType.REAL_UNITED_SCALAR:
                unit: Unit = self._component_values["unit"]
                assert isinstance(full_range_lower_value, RealUnitedScalar)
                assert isinstance(full_range_upper_value, RealUnitedScalar)
                upper_value_in_unit: float = full_range_upper_value.value_in_unit(unit)
                lower_value_in_unit: float = full_range_lower_value.value_in_unit(unit)
                selected_upper_range_tick_position: int = max(0, min(number_of_ticks - 1, int((float_value - lower_value_in_unit) / (upper_value_in_unit - lower_value_in_unit) * number_of_ticks)))
            case RangeValueType.FLOAT:
                assert isinstance(full_range_lower_value, float)
                assert isinstance(full_range_upper_value, float)
                selected_upper_range_tick_position: int = max(0, min(number_of_ticks - 1, int((float_value - full_range_lower_value) / (full_range_upper_value - full_range_lower_value) * number_of_ticks)))
            case _:
                raise ValueError(f"Invalid range value type: {value_type}")
        
        # Get current lower tick position to ensure we don't go below it
        current_lower_tick_position: int = self._component_values["selected_lower_range_tick_position"]
        selected_upper_range_tick_position = max(selected_upper_range_tick_position, current_lower_tick_position)
        
        dict_to_set: dict[HookKeyType, Any] = {"selected_upper_range_tick_position": selected_upper_range_tick_position}

        self._update_component_values_and_widgets(dict_to_set)

    def _fill_widgets_from_component_values(self, component_values: dict[HookKeyType, Any]) -> None:
        """Update the widgets from the component values."""

        # Get component values
        full_range_lower_value = component_values["full_range_lower_value"]
        full_range_upper_value = component_values["full_range_upper_value"]
        selected_lower_range_tick_position = component_values["selected_lower_range_tick_position"]
        selected_upper_range_tick_position = component_values["selected_upper_range_tick_position"]
        unit = component_values["unit"]

        # Compute emitted values
        selected_range_lower_value = self._compute_selected_range_lower_tick_value(component_values)
        selected_range_upper_value = self._compute_selected_range_upper_tick_value(component_values)
        selected_range_size = self._compute_selected_range_size(component_values)
        center_of_range = self._compute_center_of_range_value(component_values)
        range_value_type = self._compute_range_value_type(component_values)

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
    def hook_full_range_lower_value(self) -> HookLike[T]:
        return self._component_values["full_range_lower_value"]
    
    @property
    def hook_full_range_upper_value(self) -> HookLike[T]:
        return self._component_values["full_range_upper_value"]
    
    @property
    def hook_number_of_ticks(self) -> HookLike[int]:
        return self._component_values["number_of_ticks"]
    
    @property
    def hook_minimum_number_of_ticks(self) -> HookLike[int]:
        return self._component_values["minimum_number_of_ticks"]
    
    @property
    def hook_selected_lower_range_tick_position(self) -> HookLike[int]:
        return self._component_values["selected_lower_range_tick_position"]
    
    @property
    def hook_selected_upper_range_tick_position(self) -> HookLike[int]:
        return self._component_values["selected_upper_range_tick_position"]
    
    @property
    def hook_unit(self) -> HookLike[Optional[Unit]]:
        return self._component_values["unit"]
    
    @property
    def hook_selected_range_lower_tick_value(self) -> HookLike[T]:
        return self.get_hook("selected_range_lower_tick_value")
    
    @property
    def hook_selected_range_upper_tick_value(self) -> HookLike[T]:
        return self.get_hook("selected_range_upper_tick_value")

    @property
    def hook_selected_range_lower_tick_relative_value(self) -> HookLike[T]:
        return self.get_hook("selected_range_lower_tick_relative_value")
    
    @property
    def hook_selected_range_upper_tick_relative_value(self) -> HookLike[T]:
        return self.get_hook("selected_range_upper_tick_relative_value")
    
    @property
    def hook_selected_range_size(self) -> HookLike[T]:
        return self.get_hook("selected_range_size")
    
    @property
    def hook_minimum_range_size(self) -> HookLike[T]:
        return self.get_hook("minimum_range_size")
    
    @property
    def hook_center_of_range_value(self) -> HookLike[T]:
        return self.get_hook("center_of_range_value")
    
    @property
    def hook_step_size(self) -> HookLike[T]:
        return self.get_hook("step_size")
    
    @property
    def hook_range_value_type(self) -> HookLike[RangeValueType]:
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

        self._update_component_values_and_widgets({
            "full_range_lower_value": full_range_lower_value,
            "full_range_upper_value": full_range_upper_value
            })

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

        number_of_ticks: int = self._component_values["number_of_ticks"]

        selected_range_tick_position: int = int(selected_range_lower_relative_float_value * number_of_ticks)
        selected_range_tick_position: int = int(selected_range_upper_relative_float_value * number_of_ticks)

        self._update_component_values_and_widgets({
            "selected_lower_range_tick_position": selected_range_tick_position,
            "selected_upper_range_tick_position": selected_range_tick_position,
            })

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
        if self.is_disabled:
            raise ValueError("Controller is disabled")
        return self.get_value("full_range_lower_value")
    
    @full_range_lower_value.setter
    def full_range_lower_value(self, value: T) -> None:
        self._update_component_values_and_widgets({"full_range_lower_value": value})

    @property
    def full_range_lower_value_hook(self) -> HookLike[T]:
        return self.get_hook("full_range_lower_value")

    @property
    def full_range_upper_value(self) -> T:
        if self.is_disabled:
            raise ValueError("Controller is disabled")
        return self.get_value("full_range_upper_value")
    
    @full_range_upper_value.setter
    def full_range_upper_value(self, value: T) -> None:
        self._update_component_values_and_widgets({"full_range_upper_value": value})
    
    @property
    def full_range_upper_value_hook(self) -> HookLike[T]:
        return self.get_hook("full_range_upper_value")
    
    @property
    def selected_range_relative_lower_value(self) -> float:
        if self.is_disabled:
            raise ValueError("Controller is disabled")
        return self.get_value("selected_range_lower_tick_relative_value")
    
    @property
    def selected_range_relative_lower_value_hook(self) -> HookLike[float]:
        return self.get_hook("selected_range_lower_tick_relative_value")
    
    @property
    def selected_range_relative_upper_value(self) -> float:
        if self.is_disabled:
            raise ValueError("Controller is disabled")
        return self.get_value("selected_range_upper_tick_relative_value")

    @property
    def selected_range_relative_upper_value_hook(self) -> HookLike[float]:
        return self.get_hook("selected_range_upper_tick_relative_value")
    
    @property
    def selected_range_upper_value(self) -> T:
        if self.is_disabled:
            raise ValueError("Controller is disabled")
        return self.get_value("selected_range_upper_tick_value")
    
    @property
    def selected_range_upper_value_hook(self) -> HookLike[T]:
        return self.get_hook("selected_range_upper_tick_value")
    
    @property
    def selected_range_lower_value(self) -> T:
        if self.is_disabled:
            raise ValueError("Controller is disabled")
        return self.get_value("selected_range_lower_tick_value")
    
    @property
    def selected_range_lower_value_hook(self) -> HookLike[T]:
        return self.get_hook("selected_range_lower_tick_value")
    
    @property
    def selected_range_size_value(self) -> T:
        if self.is_disabled:
            raise ValueError("Controller is disabled")
        return self.get_value("selected_range_size")
    
    @property
    def selected_range_size_value_hook(self) -> HookLike[T]:
        return self.get_hook("selected_range_size")
    
    @property
    def center_of_range_value(self) -> T:
        if self.is_disabled:
            raise ValueError("Controller is disabled")
        return self.get_value("center_of_range_value")
    
    @property
    def center_of_range_value_hook(self) -> HookLike[T]:
        return self.get_hook("center_of_range_value")
    
    @property
    def step_size(self) -> T:
        if self.is_disabled:
            raise ValueError("Controller is disabled")
        return self.get_value("step_size")
    
    @property
    def step_size_hook(self) -> HookLike[T]:
        return self.get_hook("step_size")
    
    @property
    def range_value_type(self) -> RangeValueType:
        if self.is_disabled:
            raise ValueError("Controller is disabled")
        return self.get_value("range_value_type")

    ###########################################################################
    # Widgets accessors
    ###########################################################################

    @property
    def widget_range_slider(self) -> GuardedRangeSlider:
        return self._widget_range

    @property
    def widget_label_full_range_lower_value(self) -> GuardedLabel:
        if not hasattr(self, "_widget_label_full_range_lower_value"):
            self._widget_label_full_range_lower_value = GuardedLabel(self)
        self.apply_component_values_to_widgets()
        return self._widget_label_full_range_lower_value
    
    @property
    def widget_label_full_range_upper_value(self) -> GuardedLabel:
        if not hasattr(self, "_widget_label_full_range_upper_value"):
            self._widget_label_full_range_upper_value = GuardedLabel(self)
        self.apply_component_values_to_widgets()
        return self._widget_label_full_range_upper_value
    
    @property
    def widget_label_full_range_lower_float_value(self) -> GuardedLabel:
        if not hasattr(self, "_widget_label_full_range_lower_float_value"):
            self._widget_label_full_range_lower_float_value = GuardedLabel(self)
        self.apply_component_values_to_widgets()
        return self._widget_label_full_range_lower_float_value
    
    @property
    def widget_label_full_range_upper_float_value(self) -> GuardedLabel:
        if not hasattr(self, "_widget_label_full_range_upper_float_value"):
            self._widget_label_full_range_upper_float_value = GuardedLabel(self)
        self.apply_component_values_to_widgets()
        return self._widget_label_full_range_upper_float_value
    
    @property
    def widget_label_selected_range_lower_value(self) -> GuardedLabel:
        if not hasattr(self, "_widget_label_selected_range_lower_value"):
            self._widget_label_selected_range_lower_value = GuardedLabel(self)
        self.apply_component_values_to_widgets()
        return self._widget_label_selected_range_lower_value
    
    @property
    def widget_label_selected_range_upper_value(self) -> GuardedLabel:
        if not hasattr(self, "_widget_label_selected_range_upper_value"):
            self._widget_label_selected_range_upper_value = GuardedLabel(self)
        self.apply_component_values_to_widgets()
        return self._widget_label_selected_range_upper_value
    
    @property
    def widget_label_selected_range_size_value(self) -> GuardedLabel:
        if not hasattr(self, "_widget_label_selected_range_size_value"):
            self._widget_label_selected_range_size_value = GuardedLabel(self)
        self.apply_component_values_to_widgets()
        return self._widget_label_selected_range_size_value
    
    @property
    def widget_label_selected_range_size_float_value(self) -> GuardedLabel:
        if not hasattr(self, "_widget_label_selected_range_size_float_value"):
            self._widget_label_selected_range_size_float_value = GuardedLabel(self)
        self.apply_component_values_to_widgets()
        return self._widget_label_selected_range_size_float_value
    
    @property
    def widget_label_center_of_selected_range_value(self) -> GuardedLabel:
        if not hasattr(self, "_widget_label_center_of_selected_range_value"):
            self._widget_label_center_of_selected_range_value = GuardedLabel(self)
        self.apply_component_values_to_widgets()
        return self._widget_label_center_of_selected_range_value
    
    @property
    def widget_label_center_of_selected_range_float_value(self) -> GuardedLabel:
        if not hasattr(self, "_widget_label_center_of_selected_range_float_value"):
            self._widget_label_center_of_selected_range_float_value = GuardedLabel(self)
        self.apply_component_values_to_widgets()
        return self._widget_label_center_of_selected_range_float_value
    
    @property
    def widget_label_unit(self) -> GuardedLabel:
        if not hasattr(self, "_widget_label_unit"):
            self._widget_label_unit = GuardedLabel(self)
        self.apply_component_values_to_widgets()
        return self._widget_label_unit
    
    @property
    def widget_text_edit_selected_range_lower_value(self) -> GuardedLineEdit:
        if not hasattr(self, "_widget_text_edit_selected_range_lower_float_value"):
            self._widget_text_edit_selected_range_lower_float_value = GuardedLineEdit(self)
            self._widget_text_edit_selected_range_lower_float_value.editingFinished.connect(self._on_text_edit_selected_range_lower_float_value_changed)
        self.apply_component_values_to_widgets()
        return self._widget_text_edit_selected_range_lower_float_value
    
    @property
    def widget_text_edit_selected_range_upper_value(self) -> GuardedLineEdit:
        if not hasattr(self, "_widget_text_edit_selected_range_upper_float_value"):
            self._widget_text_edit_selected_range_upper_float_value = GuardedLineEdit(self)
            self._widget_text_edit_selected_range_upper_float_value.editingFinished.connect(self._on_text_edit_selected_range_upper_float_value_changed)
        self.apply_component_values_to_widgets()
        return self._widget_text_edit_selected_range_upper_float_value