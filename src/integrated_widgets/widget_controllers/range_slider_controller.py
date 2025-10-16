# Standard library imports
from __future__ import annotations
from typing import Optional, Any, Mapping, Literal
from PySide6.QtWidgets import QWidget
from enum import Enum
from logging import Logger
import math
import weakref

# BAB imports
from ..util.base_complex_hook_controller import BaseComplexHookController
from observables import ObservableSingleValueLike, HookLike
from observables.core import HookWithOwnerLike

from united_system import RealUnitedScalar, Unit, Dimension

# Local imports
from ..controlled_widgets.controlled_range_slider import ControlledRangeSlider
from ..controlled_widgets.blankable_widget import BlankableWidget
from ..util.resources import log_msg
from ..util.base_controller import DEFAULT_DEBOUNCE_MS

PrimaryHookKeyType = Literal[
    "number_of_ticks",
    "span_lower_relative_value",
    "span_upper_relative_value",
    "minimum_span_size_relative_value",
    "range_lower_value",
    "range_upper_value",
]
SecondaryHookKeyType = Literal[
    "span_lower_value",
    "span_upper_value",
    "span_size_value",
    "span_center_value",
    "value_type",
    "value_unit",
]

class RangeValueType(Enum):
    REAL_UNITED_SCALAR = "real_united_scalar"
    FLOAT = "float"

class RangeSliderController(BaseComplexHookController[PrimaryHookKeyType, SecondaryHookKeyType, Any, Any, "RangeSliderController"]):
    """
    A controller for a range slider widget.

    The range slider allows the user to select a span (subrange) from a full range of values
    using a two-handle slider interface.

    Architecture:
        The controller operates on TWO coordinate systems:
        
        1. **Tick-based coordinates** (discrete integer positions):
           - Used internally by the ControlledRangeSlider widget
           - Positions range from 0 to (number_of_ticks - 1)
           - Example: 100 ticks means positions 0, 1, 2, ..., 99
        
        2. **Relative coordinates** (normalized 0.0 to 1.0):
           - Primary API for this controller
           - Independent of the number of ticks
           - Always spans [0.0, 1.0] regardless of tick count
        
        The mapping between these systems:
        - Tick → Relative: relative = tick_position / (number_of_ticks - 1)
        - Relative → Tick: tick_position = round(relative * (number_of_ticks - 1))
        
        Example with 100 ticks:
        - Tick 0   → Relative 0.0
        - Tick 49  → Relative 0.495
        - Tick 50  → Relative 0.505
        - Tick 99  → Relative 1.0

    Primary Hooks (Core Functionality):
        - number_of_ticks: Number of discrete positions (must be ≥ 3)
        - span_lower_relative_value: Lower bound of selection (0.0 to 1.0)
        - span_upper_relative_value: Upper bound of selection (0.0 to 1.0)
        - minimum_span_size_relative_value: Minimum allowed span size (0.0 to 1.0)

    Secondary Hooks (Convenience - optional):
        - range_lower_value: Physical/real lower bound (float or RealUnitedScalar)
        - range_upper_value: Physical/real upper bound (float or RealUnitedScalar)
        
        When provided, these enable computed hooks:
        - span_lower_value: Physical value at lower span position
        - span_upper_value: Physical value at upper span position
        - span_size_value: Physical span size
        - span_center_value: Physical center of span
        - value_type: Type of values (FLOAT or REAL_UNITED_SCALAR)
        - value_unit: Unit of values (for RealUnitedScalar)

    Minimal Usage (no physical values):
        ```python
        controller = RangeSliderController(
            number_of_ticks=100,
            span_lower_relative_value=0.2,
            span_upper_relative_value=0.8,
            minimum_span_size_relative_value=0.1
        )
        # Access the slider widget
        layout.addWidget(controller.widget_range_slider)
        ```

    Full Usage (with physical values):
        ```python
        from united_system import RealUnitedScalar, Unit
        
        controller = RangeSliderController(
            number_of_ticks=100,
            span_lower_relative_value=0.2,
            span_upper_relative_value=0.8,
            minimum_span_size_relative_value=0.05,
            range_lower_value=RealUnitedScalar(0.0, Unit("m")),
            range_upper_value=RealUnitedScalar(100.0, Unit("m"))
        )
        
        # Now computed values are available
        print(controller.span_lower_value)  # 20.0 m
        print(controller.span_upper_value)  # 80.0 m
        print(controller.span_size_value)   # 60.0 m
        ```
    """

    def __init__(
        self,
        number_of_ticks: int | ObservableSingleValueLike[int] | HookLike[int] = 100,
        span_lower_relative_value: float | ObservableSingleValueLike[float] | HookLike[float] = 0.0,
        span_upper_relative_value: float | ObservableSingleValueLike[float] | HookLike[float] = 1.0,
        minimum_span_size_relative_value: float | ObservableSingleValueLike[float] | HookLike[float] = 0.0,
        range_lower_value: float | RealUnitedScalar | ObservableSingleValueLike[float | RealUnitedScalar] | HookLike[float | RealUnitedScalar] = math.nan,
        range_upper_value: float | RealUnitedScalar | ObservableSingleValueLike[float | RealUnitedScalar] | HookLike[float | RealUnitedScalar] = math.nan,
        *,
        debounce_of_range_slider_changes_ms: int = DEFAULT_DEBOUNCE_MS,
        logger: Optional[Logger] = None,
    ) -> None:

        self._debounce_of_range_slider_changes_ms = debounce_of_range_slider_changes_ms
        self._logger = logger

        #---------------- Core functionality values and hooks ----------------

        # number_of_ticks
        if isinstance(number_of_ticks, int):
            initial_number_of_ticks: int = number_of_ticks
            number_of_ticks_hook: Optional[HookLike[int]] = None
        elif isinstance(number_of_ticks, ObservableSingleValueLike):
            initial_number_of_ticks  = number_of_ticks.value # type: ignore
            number_of_ticks_hook = number_of_ticks.hook # type: ignore
        elif isinstance(number_of_ticks, HookLike):
            initial_number_of_ticks  = number_of_ticks.value # type: ignore
            number_of_ticks_hook = number_of_ticks
        else:
            raise ValueError(f"Invalid number_of_ticks: {number_of_ticks}")

        # span_lower_relative_value: Lower bound of the selected span (0.0 to 1.0)
        if isinstance(span_lower_relative_value, (float, int)):
            initial_span_lower_relative_value: float = span_lower_relative_value
            span_lower_relative_value_hook: Optional[HookLike[float]] = None
        elif isinstance(span_lower_relative_value, ObservableSingleValueLike):
            initial_span_lower_relative_value = span_lower_relative_value.value # type: ignore
            span_lower_relative_value_hook = span_lower_relative_value.hook # type: ignore
        elif isinstance(span_lower_relative_value, HookLike):
            initial_span_lower_relative_value = span_lower_relative_value.value # type: ignore
            span_lower_relative_value_hook = span_lower_relative_value
        else:
            raise ValueError(f"Invalid span_lower_relative_value: {span_lower_relative_value}")
        
        # span_upper_relative_value: Upper bound of the selected span (0.0 to 1.0)
        if isinstance(span_upper_relative_value, (float, int)):
            initial_span_upper_relative_value: float = span_upper_relative_value
            span_upper_relative_value_hook: Optional[HookLike[float]] = None
        elif isinstance(span_upper_relative_value, ObservableSingleValueLike):
            initial_span_upper_relative_value = span_upper_relative_value.value # type: ignore
            span_upper_relative_value_hook = span_upper_relative_value.hook # type: ignore
        elif isinstance(span_upper_relative_value, HookLike):
            initial_span_upper_relative_value = span_upper_relative_value.value # type: ignore
            span_upper_relative_value_hook = span_upper_relative_value
        else:
            raise ValueError(f"Invalid span_upper_relative_value: {span_upper_relative_value}")

        # minimum_span_size_relative_value: Minimum allowed span size (0.0 to 1.0)
        if isinstance(minimum_span_size_relative_value, (float, int)):
            initial_minimum_span_size_relative_value: float = minimum_span_size_relative_value
            minimum_span_size_relative_value_hook: Optional[HookLike[float]] = None
        elif isinstance(minimum_span_size_relative_value, ObservableSingleValueLike):
            initial_minimum_span_size_relative_value = minimum_span_size_relative_value.value # type: ignore
            minimum_span_size_relative_value_hook = minimum_span_size_relative_value.hook # type: ignore
        elif isinstance(minimum_span_size_relative_value, HookLike):
            initial_minimum_span_size_relative_value = minimum_span_size_relative_value.value # type: ignore
            minimum_span_size_relative_value_hook = minimum_span_size_relative_value
        else:
            raise ValueError(f"Invalid minimum_span_size_relative_value: {minimum_span_size_relative_value}")

        # ---------------- Convenience values and hooks (optional) ----------------

        # range_lower_value: Physical/real lower bound of the full range (optional)
        if isinstance(range_lower_value, ObservableSingleValueLike):
            initial_range_lower_value: float | RealUnitedScalar = range_lower_value.value # type: ignore
            range_lower_value_hook: Optional[HookLike[float | RealUnitedScalar]] = range_lower_value.hook # type: ignore
        elif isinstance(range_lower_value, HookLike):
            initial_range_lower_value: float | RealUnitedScalar = range_lower_value.value # type: ignore
            range_lower_value_hook: Optional[HookLike[float | RealUnitedScalar]] = range_lower_value
        else:
            # Direct value provided (float or RealUnitedScalar)
            initial_range_lower_value: float | RealUnitedScalar = range_lower_value
            range_lower_value_hook = None

        # range_upper_value: Physical/real upper bound of the full range (optional)
        if isinstance(range_upper_value, ObservableSingleValueLike):
            initial_range_upper_value: float | RealUnitedScalar = range_upper_value.value # type: ignore
            range_upper_value_hook: Optional[HookLike[float | RealUnitedScalar]] = range_upper_value.hook # type: ignore
        elif isinstance(range_upper_value, HookLike):
            initial_range_upper_value: float | RealUnitedScalar = range_upper_value.value # type: ignore
            range_upper_value_hook: Optional[HookLike[float | RealUnitedScalar]] = range_upper_value
        else:
            # Direct value provided (float or RealUnitedScalar)
            initial_range_upper_value: float | RealUnitedScalar = range_upper_value
            range_upper_value_hook = None

        # ---------------- Initialize the controller ----------------

        self_ref = weakref.ref(self)

        super().__init__(
            {
                "number_of_ticks": initial_number_of_ticks,
                "span_lower_relative_value": initial_span_lower_relative_value,
                "span_upper_relative_value": initial_span_upper_relative_value,
                "minimum_span_size_relative_value": initial_minimum_span_size_relative_value,
                "range_lower_value": initial_range_lower_value,
                "range_upper_value": initial_range_upper_value,
            },
            verification_method=self.__verification_method,
            secondary_hook_callbacks={
                "span_lower_value": lambda x: self_ref()._compute_span_lower_value_and_span_upper_value_and_span_size_value_and_span_center_value(x)[0], # type: ignore
                "span_upper_value": lambda x: self_ref()._compute_span_lower_value_and_span_upper_value_and_span_size_value_and_span_center_value(x)[1], # type: ignore
                "span_size_value": lambda x: self_ref()._compute_span_lower_value_and_span_upper_value_and_span_size_value_and_span_center_value(x)[2], # type: ignore
                "span_center_value": lambda x: self_ref()._compute_span_lower_value_and_span_upper_value_and_span_size_value_and_span_center_value(x)[3], # type: ignore
                "value_type": self._compute_value_type,
                "value_unit": self._compute_value_unit,
            },
            logger=logger,
        )

        # ---------------- Connect hooks, if provided ----------------

        self.connect_hook(number_of_ticks_hook, "number_of_ticks", initial_sync_mode="use_target_value") if number_of_ticks_hook is not None else None
        self.connect_hook(span_lower_relative_value_hook, "span_lower_relative_value", initial_sync_mode="use_target_value") if span_lower_relative_value_hook is not None else None
        self.connect_hook(span_upper_relative_value_hook, "span_upper_relative_value", initial_sync_mode="use_target_value") if span_upper_relative_value_hook is not None else None
        self.connect_hook(minimum_span_size_relative_value_hook, "minimum_span_size_relative_value", initial_sync_mode="use_target_value") if minimum_span_size_relative_value_hook is not None else None
        self.connect_hook(range_lower_value_hook, "range_lower_value", initial_sync_mode="use_target_value") if range_lower_value_hook is not None else None
        self.connect_hook(range_upper_value_hook, "range_upper_value", initial_sync_mode="use_target_value") if range_upper_value_hook is not None else None

    ###########################################################################
    # NaN Detection Helper Method
    ###########################################################################

    @staticmethod
    def _is_nan_or_inf(value: Any) -> bool:
        """Check if a value is NaN or infinite."""
        if isinstance(value, float):
            return math.isnan(value) or math.isinf(value)
        elif isinstance(value, RealUnitedScalar):
            return value.is_nan() or value.is_infinite()
        return False

    @staticmethod
    def _check_full_range_values_are_valid_for_compute(full_range_lower_value: float | RealUnitedScalar, full_range_upper_value: float | RealUnitedScalar) -> bool:

        if RangeSliderController._is_nan_or_inf(full_range_lower_value):
            return False
        if RangeSliderController._is_nan_or_inf(full_range_upper_value):
            return False
        if full_range_lower_value > full_range_upper_value:
            return False

        return True

    ###########################################################################
    # Verification Method
    ###########################################################################

    def __verification_method(self, component_values: Mapping[PrimaryHookKeyType, Any]) -> tuple[bool, str]:

        number_of_ticks: int = component_values["number_of_ticks"]
        span_lower_relative_value: float = component_values["span_lower_relative_value"]
        span_upper_relative_value: float = component_values["span_upper_relative_value"]
        minimum_span_size_relative_value: float = component_values["minimum_span_size_relative_value"]

        range_lower_value: float | RealUnitedScalar = component_values["range_lower_value"]
        range_upper_value: float | RealUnitedScalar = component_values["range_upper_value"]
        
        ###########################################################################
        # Core functionality
        ###########################################################################

        # Correct types:

        if not isinstance(number_of_ticks, int):
            return False, f"number_of_ticks must be an integer"
        if not isinstance(span_lower_relative_value, (float, int)):
            return False, f"span_lower_relative_value must be a float or an integer"
        if not isinstance(span_upper_relative_value, (float, int)):
            return False, f"span_upper_relative_value must be a float or an integer"
        if not isinstance(minimum_span_size_relative_value, (float, int)):
            return False, f"minimum_span_size_relative_value must be a float or an integer"

        # Check for NaN or infinite values:
        if self._is_nan_or_inf(span_lower_relative_value):
            return False, f"span_lower_relative_value must not be NaN or infinite"
        if self._is_nan_or_inf(span_upper_relative_value):
            return False, f"span_upper_relative_value must not be NaN or infinite"
        if self._is_nan_or_inf(minimum_span_size_relative_value):
            return False, f"minimum_span_size_relative_value must not be NaN or infinite"

        # Check for the correct values:
        if  number_of_ticks < 3:
            return False, f"number_of_ticks must be greater than or equal to 3"
        if span_lower_relative_value < 0.0 or span_lower_relative_value > 1.0:
            return False, f"span_lower_relative_value must be between 0.0 and 1.0"
        if span_upper_relative_value < 0.0 or span_upper_relative_value > 1.0:
            return False, f"span_upper_relative_value must be between 0.0 and 1.0"
        if span_lower_relative_value >= span_upper_relative_value:
            return False, f"span_lower_relative_value must be less than span_upper_relative_value"
        if minimum_span_size_relative_value > span_upper_relative_value - span_lower_relative_value:
            return False, f"minimum_span_size_relative_value must be smaller than or equal to the relative size of the range"

        ###########################################################################
        # Convenience functionality
        ###########################################################################

        # Correct types:

        if not isinstance(range_lower_value, (float, RealUnitedScalar)):
            return False, f"range_lower_value must be a float or RealUnitedScalar"
        if not isinstance(range_upper_value, (float, RealUnitedScalar)):
            return False, f"range_upper_value must be a float or RealUnitedScalar"
        type_of_range_lower_value: type[float | RealUnitedScalar] = type(range_lower_value)
        type_of_range_upper_value: type[float | RealUnitedScalar] = type(range_upper_value)
        if type_of_range_lower_value != type_of_range_upper_value:
            return False, f"range_lower_value and range_upper_value must be of the same type"

        # Correct dimensions:

        if isinstance(range_lower_value, RealUnitedScalar):
            assert isinstance(range_upper_value, RealUnitedScalar)
            dimension_of_range_lower_value: Dimension = range_lower_value.dimension
            dimension_of_range_upper_value: Dimension = range_upper_value.dimension
            if not dimension_of_range_lower_value == dimension_of_range_upper_value:
                return False, f"range_lower_value and range_upper_value must have the same dimension"
        
        # Check ordering (only if both values are valid, not NaN):
        if not self._is_nan_or_inf(range_lower_value) and not self._is_nan_or_inf(range_upper_value):
            if range_lower_value >= range_upper_value:
                return False, f"range_lower_value must be less than range_upper_value"

        ###########################################################################
        # Done!
        ###########################################################################

        return True, "Verification successful"
            
    ###########################################################################
    # Emitter Hook Methods
    ###########################################################################

    def _compute_span_lower_tick_position_and_span_upper_tick_position(self, x: Mapping[PrimaryHookKeyType|SecondaryHookKeyType, Any] | Mapping[PrimaryHookKeyType, Any]) -> Optional[tuple[int, int]]:

        log_msg(self, "_compute_span_lower_tick_position_and_span_upper_tick_position", self.logger, f"Computing span lower tick position and span upper tick position with x={x}")

        span_lower_relative_value: float = x["span_lower_relative_value"]
        span_upper_relative_value: float = x["span_upper_relative_value"]
        number_of_ticks: int = x["number_of_ticks"]
        
        lower_tick_position: int = int(span_lower_relative_value * number_of_ticks)
        upper_tick_position: int = int(span_upper_relative_value * number_of_ticks)
        return lower_tick_position, upper_tick_position

    def _compute_span_lower_value_and_span_upper_value_and_span_size_value_and_span_center_value(self, x: Mapping[PrimaryHookKeyType|SecondaryHookKeyType, Any] | Mapping[PrimaryHookKeyType, Any]) -> tuple[float | RealUnitedScalar, float | RealUnitedScalar, float | RealUnitedScalar, float | RealUnitedScalar]:

        log_msg(self, "_compute_span_lower_value_and_span_upper_value_and_span_size_value_and_span_center_value", self.logger, f"Computing span lower value and span upper value and span size value and span center value with x={x}")

        full_range_lower_value = x["range_lower_value"]
        full_range_upper_value = x["range_upper_value"]
        span_lower_relative_value: float = x["span_lower_relative_value"]
        span_upper_relative_value: float = x["span_upper_relative_value"]
        
        value_type: RangeValueType = self._compute_value_type(x)
        value_unit: Optional[Unit] = self._compute_value_unit(x)

        if RangeSliderController._check_full_range_values_are_valid_for_compute(full_range_lower_value, full_range_upper_value):

            match value_type:
                case RangeValueType.REAL_UNITED_SCALAR:
                    assert isinstance(full_range_lower_value, RealUnitedScalar)
                    assert isinstance(full_range_upper_value, RealUnitedScalar)
                    assert isinstance(value_unit, Unit)
                    full_range_value_span = full_range_upper_value - full_range_lower_value
                    lower_tick_value = full_range_lower_value + span_lower_relative_value * full_range_value_span
                    upper_tick_value = full_range_lower_value + span_upper_relative_value * full_range_value_span
                    lower_tick_value = lower_tick_value.scalar_in_unit(value_unit)
                    upper_tick_value = upper_tick_value.scalar_in_unit(value_unit)
                    return lower_tick_value, upper_tick_value, upper_tick_value - lower_tick_value, (lower_tick_value + upper_tick_value) / 2.0
                case RangeValueType.FLOAT:
                    full_range_value_span = full_range_upper_value - full_range_lower_value
                    lower_tick_value = full_range_lower_value + span_lower_relative_value * full_range_value_span
                    upper_tick_value = full_range_lower_value + span_upper_relative_value * full_range_value_span
                    return lower_tick_value, upper_tick_value, upper_tick_value - lower_tick_value, (lower_tick_value + upper_tick_value) / 2.0
                case _:
                    raise ValueError(f"Invalid range value type: {value_type}")

        else:
            match value_type:
                case RangeValueType.REAL_UNITED_SCALAR:
                    assert isinstance(full_range_lower_value, RealUnitedScalar)
                    assert isinstance(full_range_upper_value, RealUnitedScalar)
                    assert isinstance(value_unit, Unit)
                    return RealUnitedScalar.nan(value_unit), RealUnitedScalar.nan(value_unit), RealUnitedScalar.nan(value_unit), RealUnitedScalar.nan(value_unit)
                case RangeValueType.FLOAT:
                    return math.nan, math.nan, math.nan, math.nan
                case _:
                    raise ValueError(f"Invalid range value type: {value_type}")
    
    def _compute_value_type(self, x: Mapping[PrimaryHookKeyType|SecondaryHookKeyType, Any] | Mapping[PrimaryHookKeyType, Any]) -> RangeValueType:
        
        log_msg(self, "_compute_range_value_type", self.logger, f"Computing range value type with x={x}")

        full_range_lower_value = x["range_lower_value"]

        if isinstance(full_range_lower_value, RealUnitedScalar):
            return RangeValueType.REAL_UNITED_SCALAR
        elif isinstance(full_range_lower_value, float):
            return RangeValueType.FLOAT
        else:
            raise ValueError(f"Invalid full_range_lower_value: {full_range_lower_value}")

    def _compute_value_unit(self, x: Mapping[PrimaryHookKeyType|SecondaryHookKeyType, Any] | Mapping[PrimaryHookKeyType, Any]) -> Optional[Unit]:
        
        log_msg(self, "_compute_value_unit", self.logger, f"Computing value unit with x={x}")

        if isinstance(x["range_lower_value"], RealUnitedScalar):
            return x["range_lower_value"].unit
        elif isinstance(x["range_lower_value"], float):
            return None
        else:
            raise ValueError(f"Invalid range_lower_value: {x['range_lower_value']}")

    ###########################################################################
    # Widgets
    ###########################################################################

    def _initialize_widgets(self) -> None:
        """Initialize the widgets."""

        number_of_ticks: int = self.get_value_of_hook("number_of_ticks")

        self._widget_range = ControlledRangeSlider(self)
        self._widget_range.setTickRange(0, number_of_ticks - 1)
        
        self._widget_range.rangeChanged.connect(self._on_range_changed)
        
        # Wrap the range slider in a BlankableWidget for NaN handling
        self._blankable_widget_range = BlankableWidget(self._widget_range)

    def _on_range_changed(self, lower_range_position_tick_position: int, upper_range_position_tick_position: int) -> None:
        """
        Handle range slider change from the widget.
        
        This method is called when the user interacts with the ControlledRangeSlider widget.
        It receives tick positions (discrete integer values from 0 to number_of_ticks-1) and
        converts them to relative values (normalized float values from 0.0 to 1.0).
        
        Conversion formula:
            relative_value = tick_position / (number_of_ticks - 1)
        
        Example with 100 ticks:
            - Tick 0  → Relative 0.0   (minimum)
            - Tick 50 → Relative 0.505 (just past middle)
            - Tick 99 → Relative 1.0   (maximum)
        
        Args:
            lower_range_position_tick_position: Lower handle tick position [0, number_of_ticks-1]
            upper_range_position_tick_position: Upper handle tick position [0, number_of_ticks-1]
        """

        if self.is_blocking_signals:
            return
        
        number_of_ticks: int = self.get_value_of_hook("number_of_ticks")
        
        # Convert tick positions to relative values [0.0, 1.0]
        # Using (number_of_ticks - 1) ensures the full range maps correctly:
        # - Tick 0 → 0.0
        # - Tick (number_of_ticks - 1) → 1.0
        span_lower_relative_value: float = lower_range_position_tick_position / (number_of_ticks - 1)
        span_upper_relative_value: float = upper_range_position_tick_position / (number_of_ticks - 1)
        
        dict_to_set: dict[PrimaryHookKeyType, Any] = {
            "span_lower_relative_value": span_lower_relative_value,
            "span_upper_relative_value": span_upper_relative_value
        }

        self._submit_values_debounced(dict_to_set, debounce_ms=self._debounce_of_range_slider_changes_ms)

    def _invalidate_widgets_impl(self) -> None:
        """
        Update the range slider widget from the controller's relative values.
        
        This method converts relative values (0.0 to 1.0) back to tick positions
        (discrete integers from 0 to number_of_ticks-1) for the ControlledRangeSlider widget.
        
        Conversion formula:
            tick_position = round(relative_value * (number_of_ticks - 1))
        
        Example with 100 ticks:
            - Relative 0.0   → Tick 0  (minimum)
            - Relative 0.505 → Tick 50 (middle)
            - Relative 1.0   → Tick 99 (maximum)
        
        Note:
            Using round() instead of int() ensures better accuracy at boundaries,
            especially for relative value 1.0 which should map to tick (number_of_ticks - 1).
        """

        # Get values as reference
        number_of_ticks: int = self.get_value_of_hook("number_of_ticks")
        span_lower_relative_value: float = self.get_value_of_hook("span_lower_relative_value")
        span_upper_relative_value: float = self.get_value_of_hook("span_upper_relative_value")
        minimum_span_size_relative_value: float = self.get_value_of_hook("minimum_span_size_relative_value")

        # Convert relative values [0.0, 1.0] to tick positions [0, number_of_ticks-1]
        # Using round() to ensure:
        # - Relative 0.0 → Tick 0
        # - Relative 1.0 → Tick (number_of_ticks - 1)
        span_lower_tick_position: int = round(span_lower_relative_value * (number_of_ticks - 1))
        span_upper_tick_position: int = round(span_upper_relative_value * (number_of_ticks - 1))
        minimum_tick_gap: int = round(minimum_span_size_relative_value * (number_of_ticks - 1))

        # Set range slider range
        self._widget_range.setTickValue(span_lower_tick_position, span_upper_tick_position) 
        self._widget_range.setMinimumTickGap(minimum_tick_gap)

    ###########################################################################
    # Hook accessors
    ###########################################################################

    @property
    def number_of_ticks_hook(self) -> HookWithOwnerLike[int]:
        return self.get_hook("number_of_ticks")

    @property
    def span_lower_relative_value_hook(self) -> HookWithOwnerLike[float]:
        return self.get_hook("span_lower_relative_value")
    
    @property
    def span_upper_relative_value_hook(self) -> HookWithOwnerLike[float]:
        return self.get_hook("span_upper_relative_value")

    @property
    def minimum_span_size_relative_value_hook(self) -> HookWithOwnerLike[float]:
        return self.get_hook("minimum_span_size_relative_value")

    @property
    def range_lower_value_hook(self) -> HookWithOwnerLike[float | RealUnitedScalar]:
        return self.get_hook("range_lower_value")
    
    @property
    def range_upper_value_hook(self) -> HookWithOwnerLike[float | RealUnitedScalar]:
        return self.get_hook("range_upper_value")
    
    @property
    def span_lower_value_hook(self) -> HookWithOwnerLike[float | RealUnitedScalar]:
        return self.get_hook("span_lower_value")
    
    @property
    def span_upper_value_hook(self) -> HookWithOwnerLike[float | RealUnitedScalar]:
        return self.get_hook("span_upper_value")
    
    @property
    def span_size_value_hook(self) -> HookWithOwnerLike[float | RealUnitedScalar]:
        return self.get_hook("span_size_value")
    
    @property
    def span_center_value_hook(self) -> HookWithOwnerLike[float | RealUnitedScalar]:
        return self.get_hook("span_center_value")
    
    @property
    def value_unit_hook(self) -> HookWithOwnerLike[Optional[Unit]]:
        return self.get_hook("value_unit")

    @property
    def value_type_hook(self) -> HookWithOwnerLike[RangeValueType]:
        return self.get_hook("value_type")

    ###########################################################################
    # Value Getters
    ###########################################################################

    @property
    def number_of_ticks(self) -> int:
        return self.get_value_of_hook("number_of_ticks")

    @property
    def span_lower_relative_value(self) -> float:
        return self.get_value_of_hook("span_lower_relative_value")
    
    @property
    def span_upper_relative_value(self) -> float:
        return self.get_value_of_hook("span_upper_relative_value")

    @property
    def minimum_span_size_relative_value(self) -> float:
        return self.get_value_of_hook("minimum_span_size_relative_value")

    @property
    def range_lower_value(self) -> float | RealUnitedScalar:
        return self.get_value_of_hook("range_lower_value")
    
    @property
    def range_upper_value(self) -> float | RealUnitedScalar:
        return self.get_value_of_hook("range_upper_value")
    
    @property
    def span_lower_value(self) -> float | RealUnitedScalar:
        return self.get_value_of_hook("span_lower_value")
    
    @property
    def span_upper_value(self) -> float | RealUnitedScalar:
        return self.get_value_of_hook("span_upper_value")
    
    @property
    def span_size_value(self) -> float | RealUnitedScalar:
        return self.get_value_of_hook("span_size_value")
    
    @property
    def span_center_value(self) -> float | RealUnitedScalar:
        return self.get_value_of_hook("span_center_value")
    
    @property
    def value_unit(self) -> Optional[Unit]:
        return self.get_value_of_hook("value_unit")

    @property
    def value_type(self) -> RangeValueType:
        return self.get_value_of_hook("value_type")

    ###########################################################################
    # Convenience setter methods
    ###########################################################################

    def set_full_range_values(
            self,
            full_range_lower_value: float | RealUnitedScalar,
            full_range_upper_value: float | RealUnitedScalar) -> None:
        """
        Set the full range values.

        Args:
            full_range_lower_value: The lower value of the full range.
            full_range_upper_value: The upper value of the full range.
        """
        success, msg = self.submit_values({
            "range_lower_value": full_range_lower_value,
            "range_upper_value": full_range_upper_value
            })

        if not success:
            raise ValueError(f"Failed to set full range values: {msg}")

    def set_relative_selected_range_values(
            self,
            span_lower_relative_value: float,
            span_upper_relative_value: float) -> None:
        """
        Set the selected span as relative values (0.0 to 1.0).
        
        This is the primary method for programmatically adjusting the span selection.
        The values are normalized positions independent of the number of ticks.

        Args:
            span_lower_relative_value: The relative lower bound of the span (0.0 to 1.0).
                0.0 represents the minimum of the full range, 1.0 represents the maximum.
            span_upper_relative_value: The relative upper bound of the span (0.0 to 1.0).
                Must be greater than span_lower_relative_value (unless minimum_span_size is 0).
        
        Raises:
            ValueError: If the values are invalid (out of range, inverted, or violate minimum span size)
        
        Example:
            # Set span to middle 50%
            controller.set_relative_selected_range_values(0.25, 0.75)
        """

        success, msg = self.submit_values({
            "span_lower_relative_value": span_lower_relative_value,
            "span_upper_relative_value": span_upper_relative_value,
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
    # Widgets accessors
    ###########################################################################

    @property
    def widget_range_slider(self) -> BlankableWidget[ControlledRangeSlider]:
        if not hasattr(self, "_blankable_widget_range"):
            # This should not happen as it's initialized in _initialize_widgets
            raise RuntimeError("Range slider not properly initialized")
        return self._blankable_widget_range