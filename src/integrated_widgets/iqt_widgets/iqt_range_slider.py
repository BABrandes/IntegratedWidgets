from typing import Optional, Union, Literal, Any
import math
from PySide6.QtWidgets import QWidget, QLayout, QVBoxLayout
from logging import Logger
from observables import HookLike, ObservableSingleValueLike
from united_system import RealUnitedScalar

from .iqt_base import IQtBaseWidget, LayoutStrategyForControllers
from integrated_widgets.widget_controllers.range_slider_controller import RangeSliderController
from integrated_widgets.util.base_controller import DEFAULT_DEBOUNCE_MS


class DefaultLayoutStrategy(LayoutStrategyForControllers[RangeSliderController]):
    def __call__(self, parent: QWidget, controller: RangeSliderController) -> Union[QLayout, QWidget]:
        layout = QVBoxLayout(parent)
        layout.addWidget(controller.widget_range_slider)
        return layout


class IQtRangeSlider(IQtBaseWidget[
    Literal[
        "number_of_ticks",
        "span_lower_relative_value", 
        "span_upper_relative_value",
        "minimum_span_size_relative_value",
        "range_lower_value",
        "range_upper_value",
        "span_lower_value",
        "span_upper_value",
        "span_size_value",
        "span_center_value",
        "value_type",
        "value_unit"
    ],
    Any,
    RangeSliderController
]):
    """
    Available hooks:
        Primary:
        - "number_of_ticks": int
        - "span_lower_relative_value": float
        - "span_upper_relative_value": float
        - "minimum_span_size_relative_value": float
        - "range_lower_value": float | RealUnitedScalar
        - "range_upper_value": float | RealUnitedScalar
        
        Secondary (computed):
        - "span_lower_value": float | RealUnitedScalar
        - "span_upper_value": float | RealUnitedScalar
        - "span_size_value": float | RealUnitedScalar
        - "span_center_value": float | RealUnitedScalar
        - "value_type": RangeValueType
        - "value_unit": Optional[Unit]
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
        layout_strategy: Optional[LayoutStrategyForControllers] = None,
        parent: Optional[QWidget] = None,
        logger: Optional[Logger] = None
    ) -> None:

        controller = RangeSliderController(
            number_of_ticks=number_of_ticks,
            span_lower_relative_value=span_lower_relative_value,
            span_upper_relative_value=span_upper_relative_value,
            minimum_span_size_relative_value=minimum_span_size_relative_value,
            range_lower_value=range_lower_value,
            range_upper_value=range_upper_value,
            debounce_of_range_slider_changes_ms=debounce_of_range_slider_changes_ms,
            logger=logger
        )

        if layout_strategy is None:
            layout_strategy = DefaultLayoutStrategy()

        super().__init__(controller, layout_strategy, parent)
