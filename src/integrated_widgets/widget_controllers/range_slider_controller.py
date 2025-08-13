from __future__ import annotations

from typing import Optional, Tuple

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget

from integrated_widgets.widget_controllers.base_controller import ObservableController
from integrated_widgets.util.observable_protocols import ObservableSingleValueLike, ObservableSingleValue
from integrated_widgets.guarded_widgets.guarded_range_slider import GuardedRangeSlider


Model = ObservableSingleValueLike[Tuple[int, int]] | ObservableSingleValue[Tuple[int, int]]


class RangeSliderController(ObservableController[Model]):

    def __init__(
        self,
        observable: Model,
        *,
        minimum: int = 0,
        maximum: int = 100,
        parent: Optional[QWidget] = None,
    ) -> None:
        self._min = minimum
        self._max = maximum
        super().__init__(observable, parent=parent)

    ###########################################################################
    # Hooks
    ###########################################################################

    def initialize_widgets(self) -> None:
        self._range = GuardedRangeSlider(self.owner_widget)
        self._range.min_slider.setRange(self._min, self._max)
        self._range.max_slider.setRange(self._min, self._max)
        self._range.min_slider.valueChanged.connect(self._on_changed)
        self._range.max_slider.valueChanged.connect(self._on_changed)

    def update_widgets_from_observable(self) -> None:
        lo, hi = self._observable.value
        with self._internal_update():
            self._range.min_slider.setValue(int(lo))
            self._range.max_slider.setValue(int(hi))

    def update_observable_from_widgets(self) -> None:
        lo = self._range.min_slider.value()
        hi = self._range.max_slider.value()
        if lo > hi:
            lo, hi = hi, lo
        self._observable.set_value((lo, hi))

    def _on_changed(self, *_args) -> None:
        if self.is_blocking_signals:
            return
        self.update_observable_from_widgets()

    @property
    def range_widget(self) -> GuardedRangeSlider:
        return self._range


