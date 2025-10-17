from typing import Optional, Literal, Any, TypeVar, Generic
import math
from PySide6.QtWidgets import QWidget, QVBoxLayout
from logging import Logger
from observables import HookLike, ObservableSingleValueLike
from united_system import RealUnitedScalar
from dataclasses import dataclass

from integrated_widgets.widget_controllers.range_slider_controller import RangeSliderController
from integrated_widgets.util.base_single_hook_controller import HookWithOwnerLike
from integrated_widgets.util.base_controller import DEFAULT_DEBOUNCE_MS
from .core.iqt_controlled_layouted_widget import IQtControlledLayoutedWidget
from .core.layout_strategy_base import LayoutStrategyBase
from .core.layout_payload_base import LayoutPayloadBase


T = TypeVar("T", bound=float|RealUnitedScalar)

@dataclass(frozen=True)
class Controller_Payload(LayoutPayloadBase):
    """Payload for range slider widget."""
    range_slider: QWidget
    range_lower_value: QWidget
    range_upper_value: QWidget
    span_lower_value: QWidget
    span_upper_value: QWidget
    span_size_value: QWidget
    span_center_value: QWidget


class Controller_LayoutStrategy(LayoutStrategyBase[Controller_Payload]):
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
    RangeSliderController[T]
], Generic[T]):
    """
    A two-handle range slider with value displays and debounced updates.
    
    This widget provides a range slider with two handles for selecting a span
    within a range. Includes value displays for range bounds and span values
    (lower, upper, size, center). Supports both plain floats and united scalars
    from united_system. Debounced slider updates prevent excessive updates
    during dragging. Bidirectionally synchronizes with observables.
    
    Available hooks:
        Primary (input):
        - "number_of_ticks": int - Number of discrete positions on the slider
        - "span_lower_relative_value": float - Lower span position (0.0-1.0)
        - "span_upper_relative_value": float - Upper span position (0.0-1.0)
        - "minimum_span_size_relative_value": float - Minimum span size (0.0-1.0)
        - "range_lower_value": float | RealUnitedScalar - Range minimum value
        - "range_upper_value": float | RealUnitedScalar - Range maximum value
        
        Secondary (computed, read-only):
        - "span_lower_value": float | RealUnitedScalar - Computed lower span value
        - "span_upper_value": float | RealUnitedScalar - Computed upper span value
        - "span_size_value": float | RealUnitedScalar - Computed span size
        - "span_center_value": float | RealUnitedScalar - Computed span center
        - "value_type": RangeValueType - Type of values (float or united)
        - "value_unit": Optional[Unit] - Unit if using RealUnitedScalar
    
    Note: The widget includes 7 sub-widgets accessible via the payload for custom layouts.
    """

    def __init__(
        self,
        number_of_ticks: int | ObservableSingleValueLike[int] | HookLike[int] = 100,
        span_lower_relative_value: float | ObservableSingleValueLike[float] | HookLike[float] = 0.0,
        span_upper_relative_value: float | ObservableSingleValueLike[float] | HookLike[float] = 1.0,
        minimum_span_size_relative_value: float | ObservableSingleValueLike[float] | HookLike[float] = 0.0,
        range_lower_value: T | ObservableSingleValueLike[T] | HookLike[T] = math.nan,
        range_upper_value: T | ObservableSingleValueLike[T] | HookLike[T] = math.nan,
        *,
        debounce_of_range_slider_changes_ms: int = DEFAULT_DEBOUNCE_MS,
        layout_strategy: Optional[Controller_LayoutStrategy] = None,
        parent: Optional[QWidget] = None,
        logger: Optional[Logger] = None
    ) -> None:
        """
        Initialize the range slider widget.
        
        Parameters
        ----------
        number_of_ticks : int | ObservableSingleValueLike[int] | HookLike[int], optional
            Number of discrete tick positions. Default is 100.
        span_lower_relative_value : float | ObservableSingleValueLike[float] | HookLike[float], optional
            Lower span position (0.0 to 1.0). Default is 0.0.
        span_upper_relative_value : float | ObservableSingleValueLike[float] | HookLike[float], optional
            Upper span position (0.0 to 1.0). Default is 1.0.
        minimum_span_size_relative_value : float | ObservableSingleValueLike[float] | HookLike[float], optional
            Minimum span size (0.0 to 1.0). Default is 0.0 (no minimum).
        range_lower_value : float | RealUnitedScalar | ObservableSingleValueLike[...] | HookLike[...], optional
            Range minimum value. Default is math.nan.
        range_upper_value : float | RealUnitedScalar | ObservableSingleValueLike[...] | HookLike[...], optional
            Range maximum value. Default is math.nan.
        debounce_of_range_slider_changes_ms : int, optional
            Debounce delay in milliseconds for slider changes. Default is DEFAULT_DEBOUNCE_MS.
        layout_strategy : Controller_LayoutStrategy, optional
            Custom layout strategy for widget arrangement. If None, uses default vertical layout.
        parent : QWidget, optional
            The parent widget. Default is None.
        logger : Logger, optional
            Logger instance for debugging. Default is None.
        """

        controller = RangeSliderController[T](
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

    ###########################################################################
    # Accessors
    ###########################################################################

    #--------------------------------------------------------------------------
    # Properties
    #--------------------------------------------------------------------------

    @property
    def span_lower_relative_value(self) -> float:
        return self.controller.span_lower_relative_value
    
    @property
    def span_upper_relative_value(self) -> float:
        return self.controller.span_upper_relative_value

    #--------------------------------------------------------------------------
    # Methods
    #--------------------------------------------------------------------------
    
    def change_relative_selected_range_values(self, lower: float, upper: float) -> None:
        self.controller.set_relative_selected_range_values(lower, upper)

    #--------------------------------------------------------------------------
    # Hooks
    #--------------------------------------------------------------------------

    @property
    def number_of_ticks_hook(self) -> HookWithOwnerLike[int]:
        """
        Number of discrete positions on the slider.
        """
        return self.controller.number_of_ticks_hook
    
    @property
    def span_lower_relative_value_hook(self) -> HookWithOwnerLike[float]:
        """
        Relative value of the lower bound of the selected span (0.0 to 1.0).
        Must be smaller or equal the lower relative lower span value.
        """
        return self.controller.span_lower_relative_value_hook
    
    @property
    def span_upper_relative_value_hook(self) -> HookWithOwnerLike[float]:
        """
        Relative value of the lower bound of the selected span (0.0 to 1.0).
        Must be greater or equal the lower relative lower span value.
        """
        return self.controller.span_upper_relative_value_hook
    
    @property
    def minimum_span_size_relative_value_hook(self) -> HookWithOwnerLike[float]:
        """
        Relative value of the minimum size of the selected span (0.0 to 1.0).
        It must be smaller than or equal the current span size.
        """
        return self.controller.minimum_span_size_relative_value_hook
    
    @property
    def range_lower_value_hook(self) -> HookWithOwnerLike[T]:
        """
        Physical/real lower bound of the full range. Must be smaller than the upper range value.
        """
        return self.controller.range_lower_value_hook
    
    @property
    def range_upper_value_hook(self) -> HookWithOwnerLike[T]:
        """
        Physical/real upper bound of the full range. Must be greater than the lower range value.

        **Does not accept values**
        """
        return self.controller.range_upper_value_hook
    
    @property
    def span_lower_value_hook(self) -> HookWithOwnerLike[T]:
        """
        Physical/real value at the lower bound of the selected span.

        **Does not accept values**
        """
        return self.controller.span_lower_value_hook
    
    @property
    def span_upper_value_hook(self) -> HookWithOwnerLike[T]:
        """
        Physical/real value at the upper bound of the selected span.

        **Does not accept values**
        """
        return self.controller.span_upper_value_hook

    @property
    def span_size_value_hook(self) -> HookWithOwnerLike[T]:
        """
        Physical/real size of the selected span.

        **Does not accept values**
        """
        return self.controller.span_size_value_hook
    
    @property
    def span_center_value_hook(self) -> HookWithOwnerLike[T]:
        """
        Physical/real center of the selected span.

        **Does not accept values**
        """
        return self.controller.span_center_value_hook

    #--------------------------------------------------------------------------