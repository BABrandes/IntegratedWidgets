from typing import Optional, Literal, Any
from PySide6.QtWidgets import QWidget
from logging import Logger
from observables import HookLike, ObservableSingleValueLike
from dataclasses import dataclass

from integrated_widgets.widget_controllers.check_box_controller import CheckBoxController
from .core.iqt_controlled_layouted_widget import IQtControlledLayoutedWidget
from .core.layout_strategy_base import LayoutStrategyBase
from .core.layout_payload_base import LayoutPayloadBase

@dataclass(frozen=True)
class Controller_Payload(LayoutPayloadBase):
    """
    Payload for a checkbox widget.
    
    This payload contains the controller and the widgets extracted from it.
    """
    check_box: QWidget

class Controller_LayoutStrategy(LayoutStrategyBase[Controller_Payload]):
    """
    Layout strategy for a checkbox widget.
    
    This strategy extracts the widgets from the controller and returns them as a payload.
    """
    def __call__(self, payload: Controller_Payload, **layout_strategy_kwargs: Any) -> QWidget:
        return payload.check_box

class IQtCheckBox(IQtControlledLayoutedWidget[Literal["value", "enabled"], bool, Controller_Payload, CheckBoxController]):
    """
    A checkbox widget with bidirectional data binding to observables.
    
    This widget provides a standard Qt checkbox that automatically synchronizes
    with an observable value. Changes to the checkbox update the observable,
    and changes to the observable update the checkbox.
    
    Available hooks:
        - "value": bool - The checked state of the checkbox
        - "enabled": bool - Whether the checkbox is enabled for user interaction
    
    Properties:
        is_checked: bool - Get or set the checked state (read/write)
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
        """
        Initialize the checkbox widget.
        
        Parameters
        ----------
        value_or_hook_or_observable : bool | HookLike[bool] | ObservableSingleValueLike[bool]
            The initial checked state, or a hook/observable to bind to.
        text : str, optional
            The label text displayed next to the checkbox. Default is empty.
        layout_strategy : Controller_LayoutStrategy, optional
            Custom layout strategy for widget arrangement. If None, uses default layout.
        parent : QWidget, optional
            The parent widget. Default is None.
        logger : Logger, optional
            Logger instance for debugging. Default is None.
        """

        controller = CheckBoxController(
            value_or_hook_or_observable=value_or_hook_or_observable,
            text=text,
            logger=logger
        )

        payload = Controller_Payload(check_box=controller.widget_check_box)
        
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
    def is_checked_hook(self):
        """Hook for the checked state."""
        return self.controller.value_hook

    #--------------------------------------------------------------------------
    # Properties
    #--------------------------------------------------------------------------

    @property
    def is_checked(self) -> bool:
        return self.get_value_of_hook("value")

    @is_checked.setter
    def is_checked(self, value: bool) -> None:
        self.controller.value = value

    def change_is_checked(self, value: bool) -> None:
        self.controller.value = value

