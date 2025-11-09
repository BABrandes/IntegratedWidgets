from typing import Optional, Literal, Any, TypeVar, Generic, Callable
import math
from logging import Logger
from dataclasses import dataclass

from PySide6.QtWidgets import QWidget, QVBoxLayout

from nexpy import Hook, XSingleValueProtocol
from nexpy.core import NexusManager
from nexpy import default as nexpy_default

from united_system import RealUnitedScalar, Unit

from integrated_widgets.controlled_widgets import ControlledRangeSlider, ControlledQLabel

from ..controllers.composite.range_slider_controller import RangeSliderController, RangeValueType
from ..auxiliaries.default import default_debounce_ms
from .foundation.iqt_composite_controller_widget_base import IQtCompositeControllerWidgetBase
from .foundation.layout_strategy_base import LayoutStrategyBase
from .foundation.layout_payload_base import LayoutPayloadBase


T = TypeVar("T", bound=float|RealUnitedScalar)

@dataclass(frozen=True)
class Controller_Payload(LayoutPayloadBase):
    """Payload for range slider widget."""
    range_slider: ControlledRangeSlider
    range_lower_value: ControlledQLabel
    range_upper_value: ControlledQLabel
    span_lower_value: ControlledQLabel
    span_upper_value: ControlledQLabel
    span_size_value: ControlledQLabel
    span_center_value: ControlledQLabel


def layout_strategy(payload: Controller_Payload, **_: Any) -> QWidget:
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


class IQtRangeSlider(IQtCompositeControllerWidgetBase[
    Literal[
        "number_of_ticks",
        "span_relative_values_tuple",
        "minimum_span_size_relative_value",
        "range_values_tuple",
        "span_values_tuple",
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
        - "span_relative_values_tuple": tuple[float, float] - (lower, upper) span positions (0.0-1.0)
        - "minimum_span_size_relative_value": float - Minimum span size (0.0-1.0)
        - "range_values_tuple": tuple[float | RealUnitedScalar, float | RealUnitedScalar] - (lower, upper) range bounds
        
        Secondary (computed, read-only):
        - "span_values_tuple": tuple[float | RealUnitedScalar, float | RealUnitedScalar] - Computed (lower, upper) span values
        - "span_size_value": float | RealUnitedScalar - Computed span size
        - "span_center_value": float | RealUnitedScalar - Computed span center
        - "value_type": RangeValueType - Type of values (float or united)
        - "value_unit": Optional[Unit] - Unit if using RealUnitedScalar
    
    Note: The widget includes 7 sub-widgets accessible via the payload for custom layouts.
    """

    def __init__(
        self,
        number_of_ticks: int | XSingleValueProtocol[int] | Hook[int] = 100,
        span_relative_value_tuple: tuple[float, float] | XSingleValueProtocol[tuple[float, float]] | Hook[tuple[float, float]] = (0.0, 1.0),
        minimum_span_size_relative_value: float | XSingleValueProtocol[float] | Hook[float] = 0.0,
        range_values_tuple: tuple[T, T] | XSingleValueProtocol[tuple[T, T]] | Hook[tuple[T, T]] = (math.nan, math.nan),
        *,
        debounce_ms: int|Callable[[], int] = default_debounce_ms,
        nexus_manager: NexusManager = nexpy_default.NEXUS_MANAGER,
        layout_strategy: LayoutStrategyBase[Controller_Payload] = layout_strategy,
        parent: Optional[QWidget] = None,
        logger: Optional[Logger] = None
    ) -> None:
        """
        Initialize the range slider widget.
        
        Parameters
        ----------
        number_of_ticks : int | XSingleValueProtocol[int] | Hook[int], optional
            Number of discrete tick positions. Default is 100.
        span_relative_value_tuple : tuple[float, float] | XSingleValueProtocol[tuple[float, float]] | Hook[tuple[float, float]], optional
            Tuple containing the lower and upper span positions (0.0 to 1.0). Default is (0.0, 1.0).
        minimum_span_size_relative_value : float | XSingleValueProtocol[float] | Hook[float], optional
            Minimum span size (0.0 to 1.0). Default is 0.0 (no minimum).
        range_values_tuple : tuple[float | RealUnitedScalar, float | RealUnitedScalar] | XSingleValueProtocol[...] | Hook[...], optional
            Tuple containing the lower and upper range bounds. Default is (math.nan, math.nan).
        debounce_ms : int, optional
            Debounce delay in milliseconds for slider changes. Default is DEFAULT_DEBOUNCE_MS.
        layout_strategy : LayoutStrategyBase[Controller_Payload]
            Custom layout strategy for widget arrangement. If None, uses default vertical layout.
        parent : QWidget, optional
            The parent widget. Default is None.
        logger : Logger, optional
            Logger instance for debugging. Default is None.
        """

        controller = RangeSliderController[T](
            number_of_ticks=number_of_ticks,
            span_relative_value_tuple=span_relative_value_tuple,
            minimum_span_size_relative_value=minimum_span_size_relative_value,
            range_values_tuple=range_values_tuple,
            debounce_ms=debounce_ms,
            nexus_manager=nexus_manager,
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
        
        super().__init__(controller, payload, layout_strategy=layout_strategy, parent=parent, logger=logger)

    def __str__(self) -> str:
        lower, upper = self.span_relative_values_tuple
        return f"{self.__class__.__name__}(span={lower:.2f}-{upper:.2f})"

    def __repr__(self) -> str:
        lower, upper = self.span_relative_values_tuple
        return f"{self.__class__.__name__}(span={lower:.2f}-{upper:.2f}, id={hex(id(self))})"

    ###########################################################################
    # Accessors
    ###########################################################################

    #--------------------------------------------------------------------------
    # Properties
    #--------------------------------------------------------------------------

    @property
    def span_relative_values_tuple(self) -> tuple[float, float]:
        return self.controller.span_relative_values_tuple

    @property
    def span_lower_relative_value(self) -> float:
        return self.span_relative_values_tuple[0]
    
    @property
    def span_upper_relative_value(self) -> float:
        return self.span_relative_values_tuple[1]

    @property
    def range_values_tuple(self) -> tuple[T, T]:
        return self.controller.range_values_tuple

    @property
    def span_values_tuple(self) -> tuple[T, T]:
        return self.controller.span_values_tuple

    @property
    def span_lower_value(self) -> T:
        return self.span_values_tuple[0]

    @property
    def span_upper_value(self) -> T:
        return self.span_values_tuple[1]

    #--------------------------------------------------------------------------
    # Methods
    #--------------------------------------------------------------------------
    
    def change_span_relative_values(self, lower: float, upper: float, *, debounce_ms: Optional[int] = None, raise_submission_error_flag: bool = True) -> tuple[bool, str]:
        """
        Change the selected span relative values (0.0 to 1.0).

        Args:
            lower: The relative lower bound of the span (0.0 to 1.0).
            upper: The relative upper bound of the span (0.0 to 1.0).
        """
        success, msg = self.controller.change_span_relative_values(span_lower_relative_value=lower, span_upper_relative_value=upper, debounce_ms=debounce_ms, raise_submission_error_flag=False)
        if not success and raise_submission_error_flag:
            raise ValueError(f"Failed to change span relative values: {msg}")
        return success, msg

    def change_full_range_values(self, lower: T, upper: T, *, debounce_ms: Optional[int] = None, raise_submission_error_flag: bool = True) -> tuple[bool, str]:
        """
        Change the full range values.

        Args:
            lower: The lower value of the full range.
            upper: The upper value of the full range.
        """
        success, msg = self.controller.change_full_range_values(full_range_lower_value=lower, full_range_upper_value=upper, debounce_ms=debounce_ms, raise_submission_error_flag=False)
        if not success and raise_submission_error_flag:
            raise ValueError(f"Failed to change full range values: {msg}")
        return success, msg

    #--------------------------------------------------------------------------
    # Hooks
    #--------------------------------------------------------------------------

    @property
    def number_of_ticks_hook(self) -> Hook[int]:
        """
        Number of discrete positions on the slider.
        """
        hook: Hook[int] = self.get_hook_by_key("number_of_ticks") # type: ignore
        return hook
    
    @property
    def span_relative_values_tuple_hook(self) -> Hook[tuple[float, float]]:
        """
        Tuple of (lower, upper) relative values of the selected span (0.0 to 1.0).
        Lower value must be less than upper value.
        """
        hook: Hook[tuple[float, float]] = self.get_hook_by_key("span_relative_values_tuple") # type: ignore
        return hook
    
    @property
    def minimum_span_size_relative_value_hook(self) -> Hook[float]:
        """
        Relative value of the minimum size of the selected span (0.0 to 1.0).
        It must be smaller than or equal the current span size.
        """
        hook: Hook[float] = self.get_hook_by_key("minimum_span_size_relative_value") # type: ignore
        return hook
    
    @property
    def range_values_tuple_hook(self) -> Hook[tuple[T, T]]:
        """
        Tuple of (lower, upper) physical/real bounds of the full range.
        Lower value must be less than upper value.
        """
        hook: Hook[tuple[T, T]] = self.get_hook_by_key("range_values_tuple") # type: ignore
        return hook
    
    @property
    def span_values_tuple_hook(self) -> Hook[tuple[T, T]]:
        """
        Tuple of (lower, upper) physical/real values at the span positions.
    
        **Does not accept values**
        """
        hook: Hook[tuple[T, T]] = self.get_hook_by_key("span_values_tuple") # type: ignore
        return hook
    
    @property
    def span_size_value_hook(self) -> Hook[T]:
        """
        Physical/real size of the selected span.

        **Does not accept values**
        """
        hook: Hook[T] = self.get_hook_by_key("span_size_value") # type: ignore
        return hook
    
    @property
    def span_center_value_hook(self) -> Hook[T]:
        """
        Physical/real center of the selected span.

        **Does not accept values**
        """
        hook: Hook[T] = self.get_hook_by_key("span_center_value") # type: ignore
        return hook

    @property
    def value_type_hook(self) -> Hook[RangeValueType]:
        """
        Type of the values (float or RealUnitedScalar).
    
        **Does not accept values**
        """
        hook: Hook[RangeValueType] = self.get_hook_by_key("value_type") # type: ignore
        return hook

    @property
    def value_unit_hook(self) -> Hook[Optional[Unit]]:
        """
        Unit of the values.
        """
        hook: Hook[Optional[Unit]] = self.get_hook_by_key("value_unit") # type: ignore
        return hook

    #--------------------------------------------------------------------------