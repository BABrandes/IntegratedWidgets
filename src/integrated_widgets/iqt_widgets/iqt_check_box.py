from typing import Optional, Callable
from PySide6.QtWidgets import QWidget
from logging import Logger
from dataclasses import dataclass

from nexpy import Hook
from nexpy.x_objects.single_value_like.protocols import XSingleValueProtocol
from nexpy.core import NexusManager
from nexpy import default as nexpy_default

from ..controllers.singleton.check_box_controller import CheckBoxController
from .foundation.iqt_singleton_controller_widget_base import IQtSingletonControllerWidgetBase
from .foundation.layout_strategy_base import LayoutStrategyBase
from .foundation.layout_payload_base import LayoutPayloadBase
from ..auxiliaries.default import default_debounce_ms

@dataclass(frozen=True)
class Controller_Payload(LayoutPayloadBase):
    """
    Payload for a checkbox widget.
    
    This payload contains the controller and the widgets extracted from it.
    """
    check_box: QWidget

class IQtCheckBox(IQtSingletonControllerWidgetBase[bool, Controller_Payload, CheckBoxController]):
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
        value: bool | Hook[bool] | XSingleValueProtocol[bool],
        *,
        text: str = "",
        layout_strategy: LayoutStrategyBase[Controller_Payload] = lambda payload, **_: payload.check_box,
        debounce_ms: int|Callable[[], int] = default_debounce_ms,
        nexus_manager: NexusManager = nexpy_default.NEXUS_MANAGER,
        parent: Optional[QWidget] = None,
        logger: Optional[Logger] = None
    ) -> None:
        """
        Initialize the checkbox widget.
        
        Parameters
        ----------
        value : bool | Hook[bool] | XSingleValueProtocol[bool]
            The initial checked state, or a hook/observable to bind to.
        text : str, optional
            The label text displayed next to the checkbox. Default is empty.
        layout_strategy : LayoutStrategyBase[Controller_Payload]
            Custom layout strategy for widget arrangement.
        parent : QWidget, optional
            The parent widget. Default is None.
        logger : Logger, optional
            Logger instance for debugging. Default is None.
        """

        controller = CheckBoxController(
            value=value,
            text=text,
            debounce_ms=debounce_ms,
            nexus_manager=nexus_manager,
            logger=logger
        )

        payload = Controller_Payload(check_box=controller.widget_check_box)

        super().__init__(controller, payload, layout_strategy=layout_strategy, parent=parent, logger=logger)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(checked={self.value})"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(checked={self.value!r}, id={hex(id(self))})"

    ###########################################################################
    # Accessors
    ###########################################################################

    #--------------------------------------------------------------------------
    # Hooks
    #--------------------------------------------------------------------------
    
    @property
    def is_checked_hook(self) -> Hook[bool]:
        """Hook for the checked state."""
        hook: Hook[bool] = self.hook
        return hook

    #--------------------------------------------------------------------------
    # Properties
    #--------------------------------------------------------------------------

    @property
    def is_checked(self) -> bool:
        return self.value

    @is_checked.setter
    def is_checked(self, value: bool) -> None:
        self.controller.value = value

    def change_is_checked(self, value: bool) -> None:
        self.controller.value = value

