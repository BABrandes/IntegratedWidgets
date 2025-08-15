from __future__ import annotations

from typing import Generic, Optional, TypeVar, cast, Any, Mapping
import math

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget

from integrated_widgets.widget_controllers.base_controller import BaseObservableController
from observables import ObservableTupleLike, Hook, SyncMode, CarriesDistinctTupleHook, HookLike, ObservableSingleValueLike, CarriesDistinctSingleValueHook
from integrated_widgets.guarded_widgets.guarded_range_slider import GuardedRangeSlider
from integrated_widgets.guarded_widgets.guarded_line_edit import GuardedLineEdit
from integrated_widgets.guarded_widgets.guarded_label import GuardedLabel
from united_system import RealUnitedScalar, Unit
from integrated_widgets.widget_controllers.edit_real_united_scalar_controller import EditRealUnitedScalarController

T = TypeVar("T", bound=float | RealUnitedScalar)

class RangeSliderController(BaseObservableController, Generic[T]):

    @classmethod
    def _mandatory_component_value_keys(cls) -> set[str]:
        """Get the mandatory component value keys for this controller."""
        return {"selected_range_values", "full_range_values", "minimum_range_value", "number_of_steps", "range_size", "center_of_range", "unit"}

    @staticmethod
    def _check_values_are_of_same_type(
        selected_range_values: tuple[T, T],
        full_range_values: tuple[T, T],
        minimum_range_value: T,
    ) -> bool:
        if isinstance(selected_range_values[0], RealUnitedScalar) and isinstance(selected_range_values[1], RealUnitedScalar) and isinstance(full_range_values[0], RealUnitedScalar) and isinstance(full_range_values[1], RealUnitedScalar) and isinstance(minimum_range_value, RealUnitedScalar):
            return True
        elif isinstance(selected_range_values[0], float) and isinstance(selected_range_values[1], float) and isinstance(full_range_values[0], float) and isinstance(full_range_values[1], float) and isinstance(minimum_range_value, float):
            return True
        else:
            return False
        
    @staticmethod
    def _check_values_are_valid(
        selected_range_values: tuple[T, T],
        full_range_values: tuple[T, T],
        minimum_range_value: T,
        number_of_steps: int,
    ) -> tuple[bool, str]:
        if len(selected_range_values) != 2:
            return False, "selected_range_values must have exactly two values"
        if len(full_range_values) != 2:
            return False, "full_range_values must have exactly two values"
        if not isinstance(minimum_range_value, (float, RealUnitedScalar)):
            return False, "minimum_range_value must be a float or RealUnitedScalar"
        if not selected_range_values[0] < selected_range_values[1]:
            return False, "selected_range_values[0] must be less than selected_range_values[1]"
        if number_of_steps <= 0:
            return False, "number_of_steps must be positive"
        if minimum_range_value <= 1:
            return False, "minimum_range_value must be positive"
        if minimum_range_value > full_range_values[1] - full_range_values[0]: # type: ignore
            return False, "minimum_range_value must be less than full_range_values[1] - full_range_values[0]"
        return True, "Values are valid"

    def __init__(
        self,
        selected_range_values: tuple[T, T] | ObservableTupleLike[T] | HookLike[tuple[T, T]],
        full_range_values: tuple[T, T] | ObservableTupleLike[T] | HookLike[tuple[T, T]],
        minimum_range_value: T | ObservableSingleValueLike[T] | HookLike[T],
        number_of_steps: int | ObservableSingleValueLike[int] | HookLike[int] = 100,
        parent: Optional[QWidget] = None,
    ) -> None:
        
        # Retrieve initial values and hooks of selected range values
        if isinstance(selected_range_values, tuple):
            initial_selected_range_values: tuple[T, T] = selected_range_values
            selected_range_values_hook: Optional[HookLike[tuple[T, T]]] = None
        elif isinstance(selected_range_values, ObservableTupleLike):
            initial_selected_range_values: tuple[T, T] = selected_range_values.tuple_value # type: ignore
            selected_range_values_hook: Optional[HookLike[tuple[T, T]]] = selected_range_values.tuple_value # type: ignore
        elif isinstance(selected_range_values, HookLike):
            initial_selected_range_values: tuple[T, T] = selected_range_values.value # type: ignore
            selected_range_values_hook: Optional[HookLike[tuple[T, T]]] = selected_range_values
        else:
            raise ValueError(f"Invalid selected_range_values: {selected_range_values}")

        # Retrieve initial values and hooks of full range values
        if isinstance(full_range_values, tuple):
            initial_full_range_values: tuple[T, T] = full_range_values
            full_range_values_hook: Optional[HookLike[tuple[T, T]]] = None
        elif isinstance(full_range_values, ObservableTupleLike):
            initial_full_range_values: tuple[T, T] = full_range_values.tuple_value # type: ignore
            full_range_values_hook: Optional[HookLike[tuple[T, T]]] = full_range_values.tuple_value # type: ignore
        elif isinstance(full_range_values, HookLike):
            initial_full_range_values: tuple[T, T] = full_range_values.value # type: ignore
            full_range_values_hook: Optional[HookLike[tuple[T, T]]] = full_range_values
        else:
            raise ValueError(f"Invalid full_range_values: {full_range_values}")

        # Retrieve initial values and hooks of minimum range value
        if isinstance(minimum_range_value, ObservableSingleValueLike):
            initial_minimum_range_value: T = minimum_range_value.value # type: ignore
            minimum_range_value_hook: Optional[HookLike[T]] = minimum_range_value.value # type: ignore
        elif isinstance(minimum_range_value, HookLike):
            initial_minimum_range_value: T = minimum_range_value.value # type: ignore
            minimum_range_value_hook: Optional[HookLike[T]] = minimum_range_value
        else:
            initial_minimum_range_value: T = minimum_range_value
            minimum_range_value_hook: Optional[HookLike[T]] = None

        # Retrieve initial values and hooks of number of steps
        if isinstance(number_of_steps, int):
            initial_number_of_steps: int = number_of_steps
            number_of_steps_hook: Optional[HookLike[int]] = None
        elif isinstance(number_of_steps, ObservableSingleValueLike):
            initial_number_of_steps: int = number_of_steps.value # type: ignore
            number_of_steps_hook: Optional[HookLike[int]] = number_of_steps.value # type: ignore
        elif isinstance(number_of_steps, HookLike):
            initial_number_of_steps: int = number_of_steps.value # type: ignore
            number_of_steps_hook: Optional[HookLike[int]] = number_of_steps
        else:
            raise ValueError(f"Invalid number_of_steps: {number_of_steps}")
        
        assert isinstance(initial_minimum_range_value, RealUnitedScalar) or isinstance(initial_minimum_range_value, float)
        if not self._check_values_are_of_same_type(initial_selected_range_values, initial_full_range_values, initial_minimum_range_value):
            raise ValueError("selected_range_values, full_range_values, and minimum_range_value must be of the same type")
        
        self._value_type: type[T] = type(initial_minimum_range_value)

        # Range size
        range_size = initial_full_range_values[1] - initial_full_range_values[0] # type: ignore

        # Center of range
        center_of_range = (initial_full_range_values[0] + initial_full_range_values[1]) / 2 # type: ignore

        # Unit
        if self._value_type is RealUnitedScalar:
            assert isinstance(initial_minimum_range_value, RealUnitedScalar)
            unit: Optional[Unit] = initial_minimum_range_value.unit
        else:
            unit: Optional[Unit] = None

        # Check that the range is valid
        is_valid, error_message = self._check_values_are_valid(initial_selected_range_values, initial_full_range_values, initial_minimum_range_value, initial_number_of_steps)
        if not is_valid:
            raise ValueError(error_message)

        def verification_method(x: Mapping[str, Any]) -> tuple[bool, str]:
            is_valid, error_message = self._check_values_are_valid(x["selected_range_values"], x["full_range_values"], x["minimum_range_value"], x["number_of_steps"])
            if not is_valid:
                return False, error_message    
            return True, "Verification method passed"
        
        if selected_range_values_hook is None:
            selected_range_values_hook = Hook(self, self._get_selected_range_values, self._set_selected_range_values)
        if full_range_values_hook is None:
            full_range_values_hook = Hook(self, self._get_full_range_values, self._set_full_range_values)
        if minimum_range_value_hook is None:
            minimum_range_value_hook = Hook(self, self._get_minimum_range_value, self._set_minimum_range_value)
        if number_of_steps_hook is None:
            number_of_steps_hook = Hook(self, self._get_number_of_steps, self._set_number_of_steps)
        range_size_hook: Optional[HookLike[T]] = Hook(self, self._get_range_size, None)
        center_of_range_hook: Optional[HookLike[T]] = Hook(self, self._get_center_of_range, None)
        unit_hook: Optional[HookLike[Optional[Unit]]] = Hook(self, self._get_unit, self._set_unit)

        super().__init__(
            component_values={ 
                "selected_range_values": initial_selected_range_values,
                "full_range_values": initial_full_range_values,
                "minimum_range_value": initial_minimum_range_value,
                "number_of_steps": initial_number_of_steps,
                "range_size": range_size,
                "center_of_range": center_of_range,
                "unit": unit
            },
            component_hooks={
                "selected_range_values": selected_range_values_hook,
                "full_range_values": full_range_values_hook,
                "minimum_range_value": minimum_range_value_hook,
                "number_of_steps": number_of_steps_hook,
                "range_size": range_size_hook,
                "center_of_range": center_of_range_hook,
                "unit": unit_hook
            },
            verification_method=verification_method,
            parent=parent
        )

        if selected_range_values_hook is not None:
            self.bind_selected_range_values_to(selected_range_values_hook)
        if full_range_values_hook is not None:
            self.bind_full_range_values_to(full_range_values_hook)
        if minimum_range_value_hook is not None:
            self.bind_minimum_range_value_to(minimum_range_value_hook)
        if number_of_steps_hook is not None:
            self.bind_number_of_steps_to(number_of_steps_hook)
        if unit_hook is not None:
            self.bind_unit_to(unit_hook)

    @property
    def value_type(self) -> type[T]:
        return self._value_type
    
    ###########################################################################
    # Internal getters and setters
    ###########################################################################

    def _get_selected_range_values(self) -> tuple[T, T]:
        return self._get_component_value("selected_range_values")
    
    def _set_selected_range_values(self, value: tuple[T, T]) -> None:
        self._set_component_value("selected_range_values", value)
    
    def _get_full_range_values(self) -> tuple[T, T]:
        return self._get_component_value("full_range_values")
    
    def _set_full_range_values(self, value: tuple[T, T]) -> None:
        self._set_component_value("full_range_values", value)
    
    def _get_minimum_range_value(self) -> T:
        return self._get_component_value("minimum_range_value")
    
    def _set_minimum_range_value(self, value: T) -> None:
        self._set_component_value("minimum_range_value", value)
    
    def _get_number_of_steps(self) -> int:
        return self._get_component_value("number_of_steps")
    
    def _set_number_of_steps(self, value: int) -> None:
        self._set_component_value("number_of_steps", value)     
    
    def _get_range_size(self) -> T:
        return self._get_component_value("range_size")
    
    def _get_center_of_range(self) -> T:
        return self._get_component_value("center_of_range")
    
    def _get_unit(self) -> Optional[Unit]:
        return self._get_component_value("unit")
    
    def _set_unit(self, value: Optional[Unit]) -> None:
        self._set_component_value("unit", value)
    
    ###########################################################################
    # Getters and Setters
    ###########################################################################

    @property
    def selected_range_values(self) -> tuple[T, T]:
        return self._get_selected_range_values()
    
    @selected_range_values.setter
    def selected_range_values(self, value: tuple[T, T]) -> None:
        self._set_selected_range_values(value)
        
    @property
    def full_range_values(self) -> tuple[T, T]:
        return self._get_full_range_values()
    
    @full_range_values.setter
    def full_range_values(self, value: tuple[T, T]) -> None:
        self._set_full_range_values(value)
        
    @property
    def minimum_range_value(self) -> T:
        return self._get_minimum_range_value()
    
    @minimum_range_value.setter
    def minimum_range_value(self, value: T) -> None:
        self._set_minimum_range_value(value)
        
    @property
    def number_of_steps(self) -> int:
        return self._get_number_of_steps()
    
    @number_of_steps.setter
    def number_of_steps(self, value: int) -> None:
        self._set_number_of_steps(value)

    @property
    def range_size(self) -> T:
        return self._get_range_size()
        
    @property
    def center_of_range(self) -> T:
        return self._get_center_of_range()
        
    @property
    def unit(self) -> Optional[Unit]:
        return self._get_unit()
    
    @unit.setter
    def unit(self, value: Optional[Unit]) -> None:
        self._set_unit(value)

    @property
    def selected_range_values_hook(self) -> HookLike[tuple[T, ...]]:
        return self._component_hooks["selected_range_values"]
    
    @property
    def full_range_values_hook(self) -> HookLike[tuple[T, ...]]:
        return self._component_hooks["full_range_values"]
    
    @property
    def minimum_range_value_hook(self) -> HookLike[T]:
        return self._component_hooks["minimum_range_value"]
    
    @property
    def number_of_steps_hook(self) -> HookLike[int]:
        return self._component_hooks["number_of_steps"]
    
    @property
    def range_size_hook(self) -> HookLike[T]:
        return self._component_hooks["range_size"]
    
    @property
    def center_of_range_hook(self) -> HookLike[T]:
        return self._component_hooks["center_of_range"]

    @property
    def unit_hook(self) -> HookLike[Optional[Unit]]:
        return self._component_hooks["unit"]

    ###########################################################################
    # Binding Methods
    ###########################################################################

    def bind_selected_range_values_to(self, observable_or_hook: ObservableTupleLike[T] | CarriesDistinctTupleHook[T] | HookLike[tuple[T, ...]], initial_sync_mode: SyncMode = SyncMode.UPDATE_SELF_FROM_OBSERVABLE) -> None:
        """Establish a bidirectional binding with another observable or hook."""
        if isinstance(observable_or_hook, CarriesDistinctTupleHook):
            observable_or_hook = observable_or_hook._get_tuple_hook()
        self.selected_range_values_hook.establish_binding(observable_or_hook, initial_sync_mode)

    def unbind_selected_range_values_from(self, observable_or_hook: ObservableTupleLike[T] | CarriesDistinctTupleHook[T] | HookLike[tuple[T, ...]]) -> None:
        """Remove the bidirectional binding with another observable."""
        if isinstance(observable_or_hook, CarriesDistinctTupleHook):
            observable_or_hook = observable_or_hook._get_tuple_hook()
        self.selected_range_values_hook.remove_binding(observable_or_hook)

    def bind_full_range_values_to(self, observable_or_hook: ObservableTupleLike[T] | CarriesDistinctTupleHook[T] | HookLike[tuple[T, ...]], initial_sync_mode: SyncMode = SyncMode.UPDATE_SELF_FROM_OBSERVABLE) -> None:
        """Establish a bidirectional binding with another observable or hook."""
        if isinstance(observable_or_hook, CarriesDistinctTupleHook):
            observable_or_hook = observable_or_hook._get_tuple_hook()
        self.full_range_values_hook.establish_binding(observable_or_hook, initial_sync_mode)
        
    def unbind_full_range_values_from(self, observable_or_hook: ObservableTupleLike[T] | CarriesDistinctTupleHook[T] | HookLike[tuple[T, ...]]) -> None:
        """Remove the bidirectional binding with another observable."""
        if isinstance(observable_or_hook, CarriesDistinctTupleHook):
            observable_or_hook = observable_or_hook._get_tuple_hook()
        self.full_range_values_hook.remove_binding(observable_or_hook)
        
    def bind_minimum_range_value_to(self, observable_or_hook: ObservableSingleValueLike[T] | CarriesDistinctSingleValueHook[T] | HookLike[T], initial_sync_mode: SyncMode = SyncMode.UPDATE_SELF_FROM_OBSERVABLE) -> None:
        """Establish a bidirectional binding with another observable or hook."""
        if isinstance(observable_or_hook, CarriesDistinctSingleValueHook):
            observable_or_hook = observable_or_hook._get_single_value_hook()
        self.minimum_range_value_hook.establish_binding(observable_or_hook, initial_sync_mode)
        
    def unbind_minimum_range_value_from(self, observable_or_hook: ObservableSingleValueLike[T] | CarriesDistinctSingleValueHook[T] | HookLike[T]) -> None:
        """Remove the bidirectional binding with another observable."""
        if isinstance(observable_or_hook, CarriesDistinctSingleValueHook):
            observable_or_hook = observable_or_hook._get_single_value_hook()
        self.minimum_range_value_hook.remove_binding(observable_or_hook)
        
    def bind_number_of_steps_to(self, observable_or_hook: ObservableSingleValueLike[int] | CarriesDistinctSingleValueHook[int] | HookLike[int], initial_sync_mode: SyncMode = SyncMode.UPDATE_SELF_FROM_OBSERVABLE) -> None:
        """Establish a bidirectional binding with another observable or hook."""
        if isinstance(observable_or_hook, CarriesDistinctSingleValueHook):
            observable_or_hook = observable_or_hook._get_single_value_hook()
        self.number_of_steps_hook.establish_binding(observable_or_hook, initial_sync_mode)
        
    def unbind_number_of_steps_from(self, observable_or_hook: ObservableSingleValueLike[int] | CarriesDistinctSingleValueHook[int] | HookLike[int]) -> None:
        """Remove the bidirectional binding with another observable."""
        if isinstance(observable_or_hook, CarriesDistinctSingleValueHook):
            observable_or_hook = observable_or_hook._get_single_value_hook()
        self.number_of_steps_hook.remove_binding(observable_or_hook)
        
    def bind_unit_to(self, observable_or_hook: ObservableSingleValueLike[Optional[Unit]] | CarriesDistinctSingleValueHook[Optional[Unit]] | HookLike[Optional[Unit]], initial_sync_mode: SyncMode = SyncMode.UPDATE_SELF_FROM_OBSERVABLE) -> None:
        """Establish a bidirectional binding with another observable or hook."""
        if isinstance(observable_or_hook, CarriesDistinctSingleValueHook):
            observable_or_hook = observable_or_hook._get_single_value_hook()
        self.unit_hook.establish_binding(observable_or_hook, initial_sync_mode)
        
    def unbind_unit_from(self, observable_or_hook: ObservableSingleValueLike[Optional[Unit]] | CarriesDistinctSingleValueHook[Optional[Unit]] | HookLike[Optional[Unit]]) -> None:
        """Remove the bidirectional binding with another observable."""
        if isinstance(observable_or_hook, CarriesDistinctSingleValueHook):
            observable_or_hook = observable_or_hook._get_single_value_hook()
        self.unit_hook.remove_binding(observable_or_hook)

    def bind_range_size_to(self, observable_or_hook: ObservableSingleValueLike[T] | CarriesDistinctSingleValueHook[T] | HookLike[T], initial_sync_mode: SyncMode = SyncMode.UPDATE_SELF_FROM_OBSERVABLE) -> None:
        """Establish a unidirectional binding with another observable or hook."""
        if isinstance(observable_or_hook, CarriesDistinctSingleValueHook):
            observable_or_hook = observable_or_hook._get_single_value_hook()
        self.range_size_hook.establish_binding(observable_or_hook, initial_sync_mode)
        
    def unbind_range_size_from(self, observable_or_hook: ObservableSingleValueLike[T] | CarriesDistinctSingleValueHook[T] | HookLike[T]) -> None:
        """Remove the unidirectional binding with another observable."""
        if isinstance(observable_or_hook, CarriesDistinctSingleValueHook):
            observable_or_hook = observable_or_hook._get_single_value_hook()
        self.range_size_hook.remove_binding(observable_or_hook)
        
    def bind_center_of_range_to(self, observable_or_hook: ObservableSingleValueLike[T] | CarriesDistinctSingleValueHook[T] | HookLike[T], initial_sync_mode: SyncMode = SyncMode.UPDATE_SELF_FROM_OBSERVABLE) -> None:
        """Establish a unidirectional binding with another observable or hook."""
        if isinstance(observable_or_hook, CarriesDistinctSingleValueHook):
            observable_or_hook = observable_or_hook._get_single_value_hook()
        self.center_of_range_hook.establish_binding(observable_or_hook, initial_sync_mode)
        
    def unbind_center_of_range_from(self, observable_or_hook: ObservableSingleValueLike[T] | CarriesDistinctSingleValueHook[T] | HookLike[T]) -> None:
        """Remove the unidirectional binding with another observable."""
        if isinstance(observable_or_hook, CarriesDistinctSingleValueHook):
            observable_or_hook = observable_or_hook._get_single_value_hook()
        self.center_of_range_hook.remove_binding(observable_or_hook)
           
    ###########################################################################
    # Widgets
    ###########################################################################

    def initialize_widgets(self) -> None:
        self._range = GuardedRangeSlider(self._owner_widget)
        self._range.setRange(0, self.number_of_steps)
        # Compute integer gap from float minimum_range
        step_float = (self.full_range_values[1] - self.full_range_values[0]) / self.number_of_steps
        int_gap = 0 if self.minimum_range_value <= 0 else int(math.ceil(self.minimum_range_value / step_float))
        int_gap = max(0, min(self.number_of_steps, int_gap))
        self._range.setAllowZeroRange(self.minimum_range_value <= 0)
        self._range.setMinimumGap(int_gap)
        self._range.setValue(0, max(int_gap, self.number_of_steps))
        self._range.rangeChanged.connect(self._on_changed)

    def update_widgets_from_component_values(self) -> None:
        """Update the widgets from the component values."""
        if not hasattr(self, '_range'):
            return
            
        selected_range = self.selected_range_values
        if len(selected_range) != 2:
            raise ValueError("selected range must have exactly two values")
        range_value_lo, range_value_hi = selected_range
        
        # Update unit if type changes
        if isinstance(range_value_lo, RealUnitedScalar) and isinstance(range_value_hi, RealUnitedScalar):
            # Store the unit and convert to canonical values for slider calculations
            new_unit = range_value_lo.unit
            if self.unit != new_unit:
                self.unit = new_unit
                print(f"DEBUG: Unit changed to: {self.unit}")
            range_value_lo = range_value_lo.canonical_value
            range_value_hi = range_value_hi.canonical_value
        elif isinstance(range_value_lo, float) and isinstance(range_value_hi, float):
            # Keep the existing unit if we have one (for display purposes)
            if self.unit is not None:
                print(f"DEBUG: Keeping existing unit: {self.unit}")
        else:
            raise ValueError("range_value_lo and range_value_hi must be of the same type")

        # Convert to slider integer values
        lower_range_int_value = self._get_slider_integer_value_from_float_value(range_value_lo)
        upper_range_int_value = self._get_slider_integer_value_from_float_value(range_value_hi)
        
        # Enforce minimum integer gap on UI side
        full_range = self.full_range_values[1] - self.full_range_values[0]
        gap = 0 if self.minimum_range_value <= 0 else int(math.ceil(self.minimum_range_value / (full_range / float(self.number_of_steps))))
        if upper_range_int_value - lower_range_int_value < gap:
            upper_range_int_value = min(self.number_of_steps, lower_range_int_value + gap)
        
        self._range.blockSignals(True)
        try:
            self._range.setValue(lower_range_int_value, upper_range_int_value)
            self._update_widget_min_value()
            self._update_widget_max_value()
            self._update_widget_unit()
            self._update_widget_lower_range_value_label()
            self._update_widget_upper_range_value_label()
        finally:
            self._range.blockSignals(False)

    def update_component_values_from_widgets(self) -> None:
        """Update the component values from the widgets."""
        lo, hi = self._range.getRange()
        float_lo = self._get_float_value_from_slider_integer_value(lo)
        float_hi = self._get_float_value_from_slider_integer_value(hi)

        self.selected_range_values = (float_lo, float_hi)

    def _on_changed(self, *_args) -> None:
        """Handle range slider change."""
        if self.is_blocking_signals:
            return
        self.update_component_values_from_widgets()

    ###########################################################################
    # Helpers
    ###########################################################################

    def _get_slider_integer_value_from_float_value(self, float_value: float) -> int:
        # Round to nearest integer tick
        min_val = self.full_range_values[0]
        max_val = self.full_range_values[1]
        return int(round((float_value - min_val) / (max_val - min_val) * self.number_of_steps))

    def _get_float_value_from_slider_integer_value(self, integer_value: int) -> float:
        min_val = self.full_range_values[0]
        max_val = self.full_range_values[1]
        return min_val + float(integer_value) * (max_val - min_val) / float(self.number_of_steps)

    ###########################################################################
    # Public access
    ###########################################################################

    def set_all_values_at_once(
            self,
            selected_range_values: tuple[T, T],
            full_range_values: tuple[T, T],
            minimum_range_value: T,
            number_of_steps: int) -> None:
        """
        Set the full range of the slider. This must be used if the range is changed from float to RealUnitedScalar or vice versa.

        Args:
            selected_range_values: The selected range values of the slider.
            full_range_values: The full range values of the slider.
            minimum_range_value: The minimum range value of the slider.
            number_of_steps: The number of steps of the slider.

        If any of the values are not provided, the current value of the corresponding property will be used.
        If the minimum range is not provided, the current minimum range will be used.
        If the lower range value is not provided, the current lower range value will be used.
        If the upper range value is not provided, the current upper range value will be used.

        The minimum range must be less than the full range.
        Raises:
            ValueError: If the minimum range is not less than the full range.
        """

        is_valid = self._check_values_are_of_same_type(selected_range_values, full_range_values, minimum_range_value)
        if not is_valid:
            raise ValueError("selected_range_values, full_range_values, and minimum_range_value must be of the same type")
        is_valid, error_message = self._check_values_are_valid(selected_range_values, full_range_values, minimum_range_value, number_of_steps)
        if not is_valid:
            raise ValueError(error_message)

        # Update the component values
        self._set_component_values_from_tuples(
            ("selected_range_values", selected_range_values),
            ("full_range_values", full_range_values),
            ("minimum_range_value", minimum_range_value),
            ("number_of_steps", number_of_steps),
            ("range_size", selected_range_values[1] - selected_range_values[0]), # type: ignore
            ("center_of_range", (selected_range_values[0] + selected_range_values[1]) / 2), # type: ignore
            ("unit", selected_range_values[0].unit if isinstance(selected_range_values[0], RealUnitedScalar) else None) # type: ignore
        )

        # Update the widgets
        self.update_widgets_from_component_values()

    ###########################################################################
    # Optional widgets
    ###########################################################################

    def _update_widget_min_value(self) -> None:
        print(f"DEBUG: _update_widget_min_value called")
        if not hasattr(self, "_widget_min_value_label"):
            print(f"DEBUG: _widget_min_value_label not found")
            return
        else:
            min_val = self.full_range_values[0]
            print(f"DEBUG: min_val = {min_val}, unit = {self.unit}")
            # Show the full slider range minimum (fixed value)
            # Always use the original min/max values but convert to current unit if needed
            if self.unit is not None:
                assert isinstance(min_val, RealUnitedScalar)
                float_value: float = min_val.value_in_unit(self.unit)
                print(f"DEBUG: converted to unit: {float_value}")
            else:
                assert isinstance(min_val, float)
                float_value: float = min_val
                print(f"DEBUG: using raw value: {float_value}")
            # Convert to float for string formatting
            self._widget_min_value_label.setText(f"{float_value:.2f}")
            print(f"DEBUG: set min label text to: {float_value:.2f}")

    def _update_widget_max_value(self) -> None:
        print(f"DEBUG: _update_widget_max_value called")
        if not hasattr(self, "_widget_max_value_label"):
            print(f"DEBUG: _widget_max_value_label not found")
            return
        else:
            max_val = self.full_range_values[1]
            print(f"DEBUG: max_val = {max_val}, unit = {self.unit}")
            # Show the full slider range maximum (fixed value)
            # Always use the original min/max values but convert to current unit if needed
            if self.unit is not None:
                assert isinstance(max_val, RealUnitedScalar)
                float_value: float = max_val.value_in_unit(self.unit)
                print(f"DEBUG: converted to unit: {float_value}")
            else:
                assert isinstance(max_val, float)
                float_value: float = max_val
                print(f"DEBUG: using raw value: {float_value}")
            # Convert to float for string formatting
            self._widget_max_value_label.setText(f"{float_value:.2f}")
            print(f"DEBUG: set max label text to: {float_value:.2f}")

    def _update_widget_unit(self) -> None:
        print(f"DEBUG: _update_widget_unit called")
        if not hasattr(self, "_widget_unit_label"):
            print(f"DEBUG: _widget_unit_label not found")
            return
        else:
            print(f"DEBUG: unit = {self.unit}")
            if self.unit is not None:
                unit_text = self.unit.format_string(as_fraction=True)
                self._widget_unit_label.setText(unit_text)
                print(f"DEBUG: set unit label text to: {unit_text}")
            else:
                self._widget_unit_label.setText("")
                print(f"DEBUG: set unit label text to empty")
            
            # Ensure the label is visible and has minimum size
            self._widget_unit_label.setVisible(True)
            self._widget_unit_label.setMinimumWidth(20)
            print(f"DEBUG: Unit label visible: {self._widget_unit_label.isVisible()}")
            print(f"DEBUG: Unit label text: '{self._widget_unit_label.text()}'")

    def _update_widget_lower_range_value_label(self) -> None:
        print(f"DEBUG: _update_widget_lower_range_value_label called")
        if not hasattr(self, "_widget_lower_range_value_label"):
            print(f"DEBUG: _widget_lower_range_value_label not found")
            return
        else:
            # Show the current lower range value (current slider position)
            current_min, _ = self._range.getRange()
            print(f"DEBUG: current_min from slider = {current_min}")
            float_value = self._get_float_value_from_slider_integer_value(current_min)
            print(f"DEBUG: converted to float = {float_value}")
            if self.unit is not None:
                assert isinstance(float_value, RealUnitedScalar)
                float_value = float_value.value_in_unit(self.unit)
                print(f"DEBUG: converted to unit = {float_value}")
            # Convert to float for string formatting
            self._widget_lower_range_value_label.setText(f"{float_value:.2f}")
            print(f"DEBUG: set lower range label text to: {float_value:.2f}")

    def _update_widget_upper_range_value_label(self) -> None:
        print(f"DEBUG: _update_widget_upper_range_value_label called")
        if not hasattr(self, "_widget_upper_range_value_label"):
            print(f"DEBUG: _widget_upper_range_value_label not found")
            return
        else:
            # Show the current upper range value (current slider position)
            _, current_max = self._range.getRange()
            print(f"DEBUG: current_max from slider = {current_max}")
            float_value = self._get_float_value_from_slider_integer_value(current_max)
            print(f"DEBUG: converted to float = {float_value}")
            if self.unit is not None:
                assert isinstance(float_value, RealUnitedScalar)
                float_value = float_value.value_in_unit(self.unit)
                print(f"DEBUG: converted to unit = {float_value}")
            # Convert to float for string formatting
            self._widget_upper_range_value_label.setText(f"{float_value:.2f}")
            print(f"DEBUG: set upper range label text to: {float_value:.2f}")

    def _update_widget_range_size(self) -> None:
        print(f"DEBUG: _update_widget_range_size called")
        if not hasattr(self, "_widget_range_size_label"):
            print(f"DEBUG: _widget_range_size_label not found")
            return
        else:
            range_size = self.range_size
            if self.unit is not None:
                assert isinstance(range_size, RealUnitedScalar)
                float_value: float = range_size.value_in_unit(self.unit)
                print(f"DEBUG: converted to unit = {float_value}")
            else:
                assert isinstance(range_size, float)
                float_value: float = range_size
            self._widget_range_size_label.setText(f"{float_value:.2f}")
            print(f"DEBUG: set range size label text to: {float_value:.2f}")

    def _update_widget_center_of_range(self) -> None:
        print(f"DEBUG: _update_widget_center_of_range called")
        if not hasattr(self, "_widget_center_of_range_label"):
            print(f"DEBUG: _widget_center_of_range_label not found")
            return
        else:
            center_of_range = self.center_of_range
            if self.unit is not None:
                assert isinstance(center_of_range, RealUnitedScalar)
                float_value: float = center_of_range.value_in_unit(self.unit)
                print(f"DEBUG: converted to unit = {float_value}")
            else:
                assert isinstance(center_of_range, float)
                float_value: float = center_of_range
            self._widget_center_of_range_label.setText(f"{float_value:.2f}")
            print(f"DEBUG: set center of range label text to: {float_value:.2f}")

    ###########################################################################
    # Public access to widgets
    ###########################################################################

    @property
    def widget_range_slider(self) -> GuardedRangeSlider:
        return self._range

    @property
    def widget_min_value_label(self) -> GuardedLabel:
        if not hasattr(self, "_widget_min_value_label"):
            self._widget_min_value_label = GuardedLabel(self)
        self._update_widget_min_value()
        return self._widget_min_value_label
    
    @property
    def widget_max_value_label(self) -> GuardedLabel:
        if not hasattr(self, "_widget_max_value_label"):
            self._widget_max_value_label = GuardedLabel(self)
        self._update_widget_max_value()
        return self._widget_max_value_label
    
    @property
    def widget_unit_label(self) -> GuardedLabel:
        print(f"DEBUG: widget_unit_label property accessed")
        if not hasattr(self, "_widget_unit_label"):
            print(f"DEBUG: creating new _widget_unit_label")
            self._widget_unit_label = GuardedLabel(self)
            print(f"DEBUG: created _widget_unit_label: {self._widget_unit_label}")
        else:
            print(f"DEBUG: using existing _widget_unit_label: {self._widget_unit_label}")
        self._update_widget_unit()
        return self._widget_unit_label
    
    @property
    def widget_lower_range_value_label(self) -> GuardedLabel:
        if not hasattr(self, "_widget_lower_range_value_label"):
            self._widget_lower_range_value_label = GuardedLabel(self)
        self._update_widget_lower_range_value_label()
        return self._widget_lower_range_value_label
    
    @property
    def widget_upper_range_value_label(self) -> GuardedLabel:
        if not hasattr(self, "_widget_upper_range_value_label"):
            self._widget_upper_range_value_label = GuardedLabel(self)
        self._update_widget_upper_range_value_label()
        return self._widget_upper_range_value_label
    
    @property
    def widget_range_size_label(self) -> GuardedLabel:
        if not hasattr(self, "_widget_range_size_label"):
            self._widget_range_size_label = GuardedLabel(self)
        self._update_widget_range_size()
        return self._widget_range_size_label
    
    @property
    def widget_center_of_range_label(self) -> GuardedLabel:
        if not hasattr(self, "_widget_center_of_range_label"):
            self._widget_center_of_range_label = GuardedLabel(self)
        self._update_widget_center_of_range()
        return self._widget_center_of_range_label