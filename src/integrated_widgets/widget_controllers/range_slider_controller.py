from __future__ import annotations

from typing import Optional
import math

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget

from integrated_widgets.widget_controllers.base_controller import ObservableController
from integrated_widgets.util.observable_protocols import ObservableSingleValueLike, ObservableSingleValue
from integrated_widgets.guarded_widgets.guarded_range_slider import GuardedRangeSlider


Model = ObservableSelection = ObservableSingleValueLike[tuple[float, float]] | ObservableSingleValue[tuple[float, float]]


class RangeSliderController(ObservableController[Model]):

    def __init__(
        self,
        observable: Model,
        *,
        minimum: float = 0.0,
        maximum: float = 1.0,
        number_of_steps: int = 100,
        minimum_range: float = 0.2,
        parent: Optional[QWidget] = None,
    ) -> None:
        if not minimum < maximum:
            raise ValueError("minimum must be less than maximum")
        if number_of_steps <= 0:
            raise ValueError("number_of_steps must be positive")
        if minimum_range <= 0:
            raise ValueError("minimum_range must be positive")
        if minimum_range > maximum - minimum:
            raise ValueError("minimum_range must be less than maximum - minimum")

        self._number_of_steps = number_of_steps
        self._min_float_value = minimum
        self._max_float_value = maximum
        self._minimum_range = minimum_range
        self._min_integer_value = 0
        self._max_integer_value = self._number_of_steps

        super().__init__(observable, parent=parent)

    ###########################################################################
    # Hooks
    ###########################################################################

    def initialize_widgets(self) -> None:
        self._range = GuardedRangeSlider(self.owner_widget)
        self._range.setRange(self._min_integer_value, self._max_integer_value)
        # Compute integer gap from float minimum_range
        step_float = (self._max_float_value - self._min_float_value) / float(self._number_of_steps)
        int_gap = 0 if self._minimum_range <= 0 else int(math.ceil(self._minimum_range / step_float))
        int_gap = max(0, min(self._number_of_steps, int_gap))
        self._range.setAllowZeroRange(self._minimum_range <= 0)
        self._range.setMinimumGap(int_gap)
        self._range.setValue(self._min_integer_value, max(self._min_integer_value + int_gap, self._max_integer_value))
        self._range.rangeChanged.connect(self._on_changed)

    def update_widgets_from_observable(self) -> None:
        float_lo, float_hi = self._observable.value
        lo = self._get_slider_integer_value_from_float_value(float_lo)
        hi = self._get_slider_integer_value_from_float_value(float_hi)
        # Enforce minimum integer gap on UI side
        gap = 0 if self._minimum_range <= 0 else int(math.ceil(self._minimum_range / ((self._max_float_value - self._min_float_value) / float(self._number_of_steps))))
        if hi - lo < gap:
            hi = min(self._max_integer_value, lo + gap)
        with self._internal_update():
            self._range.setValue(lo, hi)

    def update_observable_from_widgets(self) -> None:
        lo, hi = self._range.getRange()
        float_lo = self._get_float_value_from_slider_integer_value(lo)
        float_hi = self._get_float_value_from_slider_integer_value(hi)

        self._observable.set_value((float_lo, float_hi))

    def _on_changed(self, *_args) -> None:
        if self.is_blocking_signals:
            return
        self.update_observable_from_widgets()

    ###########################################################################
    # Helpers
    ###########################################################################

    def _get_slider_integer_value_from_float_value(self, float_value: float) -> int:
        # Round to nearest integer tick
        return int(round((float_value - self._min_float_value) / (self._max_float_value - self._min_float_value) * self._number_of_steps))

    def _get_float_value_from_slider_integer_value(self, integer_value: int) -> float:
        return self._min_float_value + float(integer_value) * (self._max_float_value - self._min_float_value) / float(self._number_of_steps)

    ###########################################################################
    # Public access
    ###########################################################################

    @property
    def min_value(self) -> float:
        lo, _ = self._range.getRange()
        return self._get_float_value_from_slider_integer_value(lo)

    @property
    def max_value(self) -> float:
        _, hi = self._range.getRange()
        return self._get_float_value_from_slider_integer_value(hi)
    
    @property
    def minimum_range(self) -> float:
        return self._minimum_range
    
    @property
    def number_of_steps(self) -> int:
        return self._number_of_steps
    
    @property
    def step_size(self) -> float:
        return (self._max_float_value - self._min_float_value) / self._number_of_steps

    @property
    def widget_range_slider(self) -> GuardedRangeSlider:
        return self._range


