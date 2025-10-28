from typing import Optional, Callable, Literal
from logging import Logger
from dataclasses import dataclass

from PySide6.QtWidgets import QWidget

from nexpy import Hook, XSingleValueProtocol
from nexpy.core import NexusManager
from nexpy import default as nexpy_default

from ..controllers.singleton.integer_entry_controller import IntegerEntryController
from ..auxiliaries.default import default_debounce_ms
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
        value: int | Hook[int] | XSingleValueProtocol[int],
        *,
        validator: Optional[Callable[[int], bool]] = None,
        layout_strategy: LayoutStrategyBase[Controller_Payload] = lambda payload, **_: payload.line_edit,
        debounce_ms: int|Callable[[], int] = default_debounce_ms,
        nexus_manager: NexusManager = nexpy_default.NEXUS_MANAGER,
        parent: Optional[QWidget] = None,
        logger: Optional[Logger] = None
    ) -> None:
        """
        Initialize the integer entry widget.
        
        Parameters
        ----------
        value : int | Hook[int] | XSingleValueProtocol[int]
            The initial value, or a hook/observable to bind to.
        validator : Callable[[int], bool], optional
            Validation function that returns True if the value is valid. Default is None (all values valid).
        layout_strategy : LayoutStrategyBase[Controller_Payload], optional
            Custom layout strategy for widget arrangement. Default is default layout.
        debounce_ms: int|Callable[[], int] = default_debounce_ms,
        nexus_manager: NexusManager = nexpy_default.NEXUS_MANAGER,
        parent : QWidget, optional
            The parent widget. Default is None.
        logger : Logger, optional
            Logger instance for debugging. Default is None.
        """

        controller = IntegerEntryController(
            value=value,
            validator=validator,
            debounce_ms=debounce_ms,
            nexus_manager=nexus_manager,
            logger=logger
        )

        payload = Controller_Payload(line_edit=controller.widget_line_edit)
        
        super().__init__(controller, payload, layout_strategy, parent=parent, logger=logger)

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
        hook: Hook[int] = self.get_hook_by_key("value")
        return hook

    #--------------------------------------------------------------------------
    # Properties
    #--------------------------------------------------------------------------

    @property
    def value(self) -> int:
        return self.get_hook_value_by_key("value")

    @value.setter
    def value(self, value: int) -> None:
        self.controller.value = value

    def change_value(self, value: int) -> None:
        self.controller.value = value

