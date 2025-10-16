from typing import Optional, Literal, Any
import math
from PySide6.QtWidgets import QWidget, QVBoxLayout
from logging import Logger
from observables import HookLike, ObservableSingleValueLike
from united_system import RealUnitedScalar
from dataclasses import dataclass

from .iqt_controlled_layouted_widget import IQtControlledLayoutedWidget, LayoutStrategy
from integrated_widgets.widget_controllers.range_slider_controller import RangeSliderController
from integrated_widgets.util.base_controller import DEFAULT_DEBOUNCE_MS
from .layout_payload import BaseLayoutPayload


@dataclass(frozen=True)
class Controller_Payload(BaseLayoutPayload):
    """Payload for range slider widget."""
    range_slider: QWidget
    range_lower_value: QWidget
    range_upper_value: QWidget
    span_lower_value: QWidget
    span_upper_value: QWidget
    span_size_value: QWidget
    span_center_value: QWidget


class Controller_LayoutStrategy(LayoutStrategy[Controller_Payload]):
    """Default layout strategy for range slider widget."""
    def __call__(self, parent: QWidget, payload: Controller_Payload) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(payload.range_slider)
        layout.addWidget(payload.range_lower_value)
        layout.addWidget(payload.range_upper_value)
        layout.addWidget(payload.span_lower_value)
        layout.addWidget(payload.span_upper_value)
        layout.addWidget(payload.span_size_value)
        layout.addWidget(payload.span_center_value)
        return widget


class IQtRangeSlider(IQtControlledLayoutedWidget[
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
    Controller_Payload,
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
        layout_strategy: Optional[Controller_LayoutStrategy] = None,
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

        payload = Controller_Payload(
            range_slider=controller.widget_range_slider,
            range_lower_value=controller.widget_range_lower_value,
            range_upper_value=controller.widget_range_upper_value,
            span_lower_value=controller.widget_span_lower_value,
            span_upper_value=controller.widget_span_upper_value,
            span_size_value=controller.widget_span_size_value,
            span_center_value=controller.widget_span_center_value
        )
        
        if layout_strategy is None:
            layout_strategy = Controller_LayoutStrategy()

        super().__init__(controller, payload, layout_strategy, parent)
