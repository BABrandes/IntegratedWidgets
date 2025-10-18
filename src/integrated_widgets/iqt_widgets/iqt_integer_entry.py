from typing import Optional, Callable, Literal
from PySide6.QtWidgets import QWidget
from logging import Logger
from observables import Hook, ObservableSingleValueProtocol
from dataclasses import dataclass

from integrated_widgets.widget_controllers.integer_entry_controller import IntegerEntryController
from .core.iqt_controlled_layouted_widget import IQtControlledLayoutedWidget
from .core.layout_strategy_base import LayoutStrategyBase
from .core.layout_payload_base import LayoutPayloadBase


@dataclass(frozen=True)
class Controller_Payload(LayoutPayloadBase):
    """Payload for an integer entry widget."""
    line_edit: QWidget

class IQtIntegerEntry(IQtControlledLayoutedWidget[Literal["value", "enabled"], int, Controller_Payload, IntegerEntryController]):
    """
    An integer entry widget with validation and data binding.
    
    This widget provides a line edit for entering integer numbers with
    automatic validation and bidirectional synchronization with observables.
    Invalid inputs are rejected and the widget reverts to the last valid value.
    
    Available hooks:
        - "value": int - The integer value
        - "enabled": bool - Whether the widget is enabled for user interaction
    
    Properties:
        value: int - Get or set the integer value (read/write)
    """

    def __init__(
        self,
        value_or_hook_or_observable: int | Hook[int] | ObservableSingleValueProtocol[int],
        *,
        validator: Optional[Callable[[int], bool]] = None,
        layout_strategy: LayoutStrategyBase[Controller_Payload] = lambda payload, **_: payload.line_edit,
        parent: Optional[QWidget] = None,
        logger: Optional[Logger] = None
    ) -> None:
        """
        Initialize the integer entry widget.
        
        Parameters
        ----------
        value_or_hook_or_observable : int | Hook[int] | ObservableSingleValueProtocol[int]
            The initial value, or a hook/observable to bind to.
        validator : Callable[[int], bool], optional
            Validation function that returns True if the value is valid. Default is None (all values valid).
        layout_strategy : LayoutStrategyBase[Controller_Payload], optional
            Custom layout strategy for widget arrangement. Default is default layout.
        parent : QWidget, optional
            The parent widget. Default is None.
        logger : Logger, optional
            Logger instance for debugging. Default is None.
        """

        controller = IntegerEntryController(
            value_or_hook_or_observable=value_or_hook_or_observable,
            validator=validator,
            logger=logger
        )

        payload = Controller_Payload(line_edit=controller.widget_line_edit)
        
        super().__init__(controller, payload, layout_strategy, parent)

    ###########################################################################
    # Accessors
    ###########################################################################

    #--------------------------------------------------------------------------
    # Hooks
    #--------------------------------------------------------------------------
    
    @property
    def value_hook(self) -> Hook[int]:
        """
        Hook for the value.
        """
        hook: Hook[int] = self.get_hook("value") # type: ignore
        return hook

    #--------------------------------------------------------------------------
    # Properties
    #--------------------------------------------------------------------------

    @property
    def value(self) -> int:
        return self.get_value_of_hook("value")

    @value.setter
    def value(self, value: int) -> None:
        self.controller.value = value

    def change_value(self, value: int) -> None:
        self.controller.value = value

