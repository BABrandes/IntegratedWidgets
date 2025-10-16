from typing import Any, Optional, Generic, TypeVar, Callable, Union, Literal
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
    Available hooks:
        - "value": T
    """

    def __init__(
        self,
        value_or_hook_or_observable: T | HookLike[T] | ObservableSingleValueLike[T],
        formatter: Optional[Callable[[T], str]] = None,
        layout_strategy: Optional[Controller_LayoutStrategy] = None,
        parent: Optional[QWidget] = None,
        logger: Optional[Logger] = None
        ) -> None:

        controller = DisplayValueController(
            value_or_hook_or_observable=value_or_hook_or_observable,
            formatter=formatter,
            logger=logger)

        payload = Controller_Payload(label=controller.widget_label)
        super().__init__(controller, payload, layout_strategy, parent)

    @property
    def value(self) -> T:
        return self.get_value_of_hook("value")