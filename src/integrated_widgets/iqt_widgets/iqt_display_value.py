from typing import Optional, Generic, TypeVar, Callable
from PySide6.QtWidgets import QWidget
from logging import Logger
from dataclasses import dataclass

from nexpy import Hook, XSingleValueProtocol
from nexpy.core import NexusManager
from nexpy import default as nexpy_default

from ..controllers.singleton.display_value_controller import DisplayValueController
from ..controlled_widgets.controlled_qlabel import ControlledQLabel
from .foundation.iqt_singleton_controller_widget_base import IQtSingletonControllerWidgetBase
from .foundation.layout_strategy_base import LayoutStrategyBase
from .foundation.layout_payload_base import LayoutPayloadBase
from ..auxiliaries.default import default_debounce_ms


T = TypeVar("T")

@dataclass(frozen=True)
class Controller_Payload(LayoutPayloadBase):
    """
    Payload for a display value widget.
    
    This payload contains the controller and the widgets extracted from it.
    """
    label: ControlledQLabel

class IQtDisplayValue(IQtSingletonControllerWidgetBase[T, Controller_Payload, DisplayValueController[T]], Generic[T]):
    """
    A read-only display widget for showing values with custom formatting.
    
    This widget provides a label for displaying values that automatically updates
    when the bound observable changes. Supports custom formatters to control how
    values are displayed. The display is read-only from the user's perspective.
    
    Available hooks:
        - "value": T - The value to display
    
    Properties:
        value: T - Get or set the displayed value (read/write)
    
    Key Features:
        - **Easy Connect**: Pass observables directly for automatic synchronization
        - **Custom Formatting**: Flexible formatters for any value type
        - **Simple Submit**: Use `submit(value)` instead of `submit_value("value", value)`
        - **Custom Layouts**: Optional layout strategies for flexible UI design
    
    Examples
    --------
    Basic usage with observable:
    
    >>> from nexpy import XValue
    >>> counter = XValue(0)
    >>> display = IQtDisplayValue(counter, formatter=lambda x: f"Count: {x}")
    >>> # Widget automatically updates when counter changes
    >>> counter.value = 10  # Display shows "Count: 10"
    
    Easy connect with custom formatting:
    
    >>> temperature = XValue(20.5)
    >>> display = IQtDisplayValue(
    ...     temperature,
    ...     formatter=lambda t: f"{t:.1f}°C"
    ... )
    
    Using simplified submit method:
    
    >>> display.submit(25.0)  # Clean API instead of submit_value("value", 25.0)
    >>> # Or use the property
    >>> display.value = 30.0
    
    Custom layout with label:
    
    >>> def labeled_layout(parent, payload):
    ...     widget = QWidget()
    ...     layout = QHBoxLayout(widget)
    ...     layout.addWidget(QLabel("Status:"))
    ...     layout.addWidget(payload.label)
    ...     return widget
    >>> display = IQtDisplayValue(
    ...     status_observable,
    ...     layout_strategy=labeled_layout
    ... )
    """

    def __init__(
        self,
        value: T | Hook[T] | XSingleValueProtocol[T],
        formatter: Optional[Callable[[T], str]] = None,
        layout_strategy: Optional[LayoutStrategyBase[Controller_Payload]] = lambda payload, **_: payload.label,
        debounce_ms: int|Callable[[], int] = default_debounce_ms,
        nexus_manager: NexusManager = nexpy_default.NEXUS_MANAGER,
        parent: Optional[QWidget] = None,
        logger: Optional[Logger] = None
        ) -> None:
        """
        Initialize the display value widget.
        
        Parameters
        ----------
        value : T | Hook[T] | XSingleValueProtocol[T]
            The initial value to display, or a hook/observable to bind to.
            **Easy Connect**: Pass an observable directly and the widget automatically
            syncs with it - changes to the observable update the display in real-time.
        formatter : Callable[[T], str], optional
            Function to format the value for display. Default is str(value).
            Examples: lambda x: f"{x:.2f}", lambda x: f"{x*100}%"
        layout_strategy : LayoutStrategyBase[Controller_Payload]
            Custom layout strategy for widget arrangement. Default is default layout
        debounce_ms: int|Callable[[], int] = default_debounce_ms,
        nexus_manager: NexusManager = nexpy_default.NEXUS_MANAGER,
        parent : QWidget, optional
            The parent widget. Default is None.
        logger : Logger, optional
            Logger instance for debugging. Default is None.
        
        Examples
        --------
        Easy connect to observable:
        
        >>> temperature = XValue(20.0)
        >>> widget = IQtDisplayValue(temperature, formatter=lambda t: f"{t}°C")
        
        Using simplified submit:
        
        >>> widget.submit(25.0)  # Instead of submit_value("value", 25.0)
        """

        controller = DisplayValueController(
            value=value,
            formatter=formatter,
            debounce_ms=debounce_ms,
            nexus_manager=nexus_manager,
            logger=logger)

        payload = Controller_Payload(label=controller.widget_label)
        
        super().__init__(controller, payload, layout_strategy=layout_strategy, parent=parent, logger=logger)