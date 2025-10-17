from typing import Optional, Generic, TypeVar, Callable, Literal
from PySide6.QtWidgets import QWidget
from logging import Logger
from observables import HookLike, ObservableSingleValueLike
from dataclasses import dataclass

from .iqt_controlled_layouted_widget import IQtControlledLayoutedWidget, LayoutStrategy
from integrated_widgets.widget_controllers.display_value_controller import DisplayValueController
from .layout_payload import BaseLayoutPayload

T = TypeVar("T")

@dataclass(frozen=True)
class Controller_Payload(BaseLayoutPayload):
    """
    Payload for a display value widget.
    
    This payload contains the controller and the widgets extracted from it.
    """
    label: QWidget

class Controller_LayoutStrategy(LayoutStrategy[Controller_Payload]):
    def __call__(self,parent: QWidget, payload: Controller_Payload) -> QWidget:
        return payload.label

class IQtDisplayValue(IQtControlledLayoutedWidget[Literal["value"], T, Controller_Payload, DisplayValueController[T]], Generic[T]):
    """
    A read-only display widget for showing values with custom formatting.
    
    This widget provides a label for displaying values that automatically updates
    when the bound observable changes. Supports custom formatters to control how
    values are displayed. The display is read-only from the user's perspective.
    
    Available hooks:
        - "value": T - The value to display
    
    Properties:
        value: T - Get or set the displayed value (read/write)
    """

    def __init__(
        self,
        value_or_hook_or_observable: T | HookLike[T] | ObservableSingleValueLike[T],
        formatter: Optional[Callable[[T], str]] = None,
        layout_strategy: Optional[Controller_LayoutStrategy] = None,
        parent: Optional[QWidget] = None,
        logger: Optional[Logger] = None
        ) -> None:
        """
        Initialize the display value widget.
        
        Parameters
        ----------
        value_or_hook_or_observable : T | HookLike[T] | ObservableSingleValueLike[T]
            The initial value to display, or a hook/observable to bind to.
        formatter : Callable[[T], str], optional
            Function to format the value for display. Default is str(value).
        layout_strategy : Controller_LayoutStrategy, optional
            Custom layout strategy for widget arrangement. If None, uses default layout.
        parent : QWidget, optional
            The parent widget. Default is None.
        logger : Logger, optional
            Logger instance for debugging. Default is None.
        """

        controller = DisplayValueController(
            value_or_hook_or_observable=value_or_hook_or_observable,
            formatter=formatter,
            logger=logger)

        payload = Controller_Payload(label=controller.widget_label)
        
        if layout_strategy is None:
            layout_strategy = Controller_LayoutStrategy()
        
        super().__init__(controller, payload, layout_strategy, parent)

    ###########################################################################
    # Accessors
    ###########################################################################

    #--------------------------------------------------------------------------
    # Hooks
    #--------------------------------------------------------------------------
    
    @property
    def value_hook(self):
        """Hook for the displayed value."""
        return self.controller.value_hook

    #--------------------------------------------------------------------------
    # Properties
    #--------------------------------------------------------------------------

    @property
    def value(self) -> T:
        return self.get_value_of_hook("value")

    @value.setter
    def value(self, value: T) -> None:
        self.controller.value = value

    def change_value(self, value: T) -> None:
        self.controller.value = value