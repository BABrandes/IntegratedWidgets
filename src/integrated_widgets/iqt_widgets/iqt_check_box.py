from typing import Optional, Literal
from PySide6.QtWidgets import QWidget
from logging import Logger
from observables import HookLike, ObservableSingleValueLike
from dataclasses import dataclass

from .iqt_controlled_layouted_widget import IQtControlledLayoutedWidget, LayoutStrategy
from integrated_widgets.widget_controllers.check_box_controller import CheckBoxController
from .layout_payload import BaseLayoutPayload

@dataclass(frozen=True)
class Controller_Payload(BaseLayoutPayload):
    """
    Payload for a checkbox widget.
    
    This payload contains the controller and the widgets extracted from it.
    """
    check_box: QWidget

class Controller_LayoutStrategy(LayoutStrategy[Controller_Payload]):
    """
    Layout strategy for a checkbox widget.
    
    This strategy extracts the widgets from the controller and returns them as a payload.
    """
    def __call__(self, parent: QWidget, payload: Controller_Payload) -> QWidget:
        return payload.check_box

class IQtCheckBox(IQtControlledLayoutedWidget[Literal["value", "enabled"], bool, Controller_Payload, CheckBoxController]):
    """
    Available hooks:
        - "value": bool
        - "enabled": bool
    """

    def __init__(
        self,
        value_or_hook_or_observable: bool | HookLike[bool] | ObservableSingleValueLike[bool],
        *,
        text: str = "",
        layout_strategy: Optional[Controller_LayoutStrategy] = None,
        parent: Optional[QWidget] = None,
        logger: Optional[Logger] = None
    ) -> None:

        controller = CheckBoxController(
            value_or_hook_or_observable=value_or_hook_or_observable,
            text=text,
            logger=logger
        )

        payload = Controller_Payload(check_box=controller.widget_check_box)
        super().__init__(controller, payload, layout_strategy, parent)

