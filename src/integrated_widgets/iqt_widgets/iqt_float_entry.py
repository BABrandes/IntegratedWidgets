from typing import Optional, Callable, Literal
from logging import Logger
from dataclasses import dataclass

from PySide6.QtWidgets import QWidget

from nexpy import Hook, XSingleValueProtocol
from nexpy.core import NexusManager
from nexpy import default as nexpy_default

from ..controllers.singleton.float_entry_controller import FloatEntryController
from ..auxiliaries.default import default_debounce_ms
from .core.iqt_controlled_layouted_widget import IQtControlledLayoutedWidget
from .core.layout_strategy_base import LayoutStrategyBase
from .core.layout_payload_base import LayoutPayloadBase


@dataclass(frozen=True)
class Controller_Payload(LayoutPayloadBase):
    """Payload for a float entry widget."""
    line_edit: QWidget


class IQtFloatEntry(IQtControlledLayoutedWidget[Literal["value", "enabled"], float, Controller_Payload, FloatEntryController]):
    """
    A floating-point number entry widget with validation and data binding.
    
    This widget provides a line edit for entering floating-point numbers with
    automatic validation and bidirectional synchronization with observables.
    Invalid inputs are rejected and the widget reverts to the last valid value.
    
    Available hooks:
        - "value": float - The numeric value
        - "enabled": bool - Whether the widget is enabled for user interaction
    
    Properties:
        value: float - Get or set the numeric value (read/write)
    """

    def __init__(
        self,
        value: float | Hook[float] | XSingleValueProtocol[float],
        *,
        validator: Optional[Callable[[float], bool]] = None,
        layout_strategy: LayoutStrategyBase[Controller_Payload] = lambda payload, **_: payload.line_edit,
        debounce_ms: int|Callable[[], int] = default_debounce_ms,
        nexus_manager: NexusManager = nexpy_default.NEXUS_MANAGER,
        parent: Optional[QWidget] = None,
        logger: Optional[Logger] = None
    ) -> None:
        """
        Initialize the float entry widget.
        
        Parameters
        ----------
        value : float | Hook[float] | XSingleValueProtocol[float]
            The initial value, or a hook/observable to bind to.
        validator : Callable[[float], bool], optional
            Validation function that returns True if the value is valid. Default is None (all values valid).
        layout_strategy : LayoutStrategyBase[Controller_Payload], optional
            Custom layout strategy for widget arrangement. Default is default layout.
        parent : QWidget, optional
            The parent widget. Default is None.
        logger : Logger, optional
            Logger instance for debugging. Default is None.
        """

        controller = FloatEntryController(
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
    def value_hook(self) -> Hook[float]:
        """
        Hook for the value.
        """
        hook: Hook[float] = self.get_hook_by_key("value")
        return hook

    #--------------------------------------------------------------------------
    # Properties
    #--------------------------------------------------------------------------

    @property
    def value(self) -> float:
        return self.get_hook_value_by_key("value")

    @value.setter
    def value(self, value: float) -> None:
        self.controller.value = value

    def change_value(self, value: float) -> None:
        self.controller.value = value
