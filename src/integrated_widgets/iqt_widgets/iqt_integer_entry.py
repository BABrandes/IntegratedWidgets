from typing import Optional, Callable, Literal, Any
from PySide6.QtWidgets import QWidget
from logging import Logger
from observables import HookLike, ObservableSingleValueLike
from dataclasses import dataclass

from observables.core import HookWithOwnerLike

from integrated_widgets.widget_controllers.integer_entry_controller import IntegerEntryController
from .core.iqt_controlled_layouted_widget import IQtControlledLayoutedWidget
from .core.layout_strategy_base import LayoutStrategyBase
from .core.layout_payload_base import LayoutPayloadBase


@dataclass(frozen=True)
class Controller_Payload(LayoutPayloadBase):
    """Payload for an integer entry widget."""
    line_edit: QWidget


class Controller_LayoutStrategy(LayoutStrategyBase[Controller_Payload]):
    """Default layout strategy for integer entry widget."""
    def __call__(self, payload: Controller_Payload, **layout_strategy_kwargs: Any) -> QWidget:
        return payload.line_edit


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
        value_or_hook_or_observable: int | HookLike[int] | ObservableSingleValueLike[int],
        *,
        validator: Optional[Callable[[int], bool]] = None,
        layout_strategy: Optional[Controller_LayoutStrategy] = None,
        parent: Optional[QWidget] = None,
        logger: Optional[Logger] = None
    ) -> None:
        """
        Initialize the integer entry widget.
        
        Parameters
        ----------
        value_or_hook_or_observable : int | HookLike[int] | ObservableSingleValueLike[int]
            The initial value, or a hook/observable to bind to.
        validator : Callable[[int], bool], optional
            Validation function that returns True if the value is valid. Default is None (all values valid).
        layout_strategy : Controller_LayoutStrategy, optional
            Custom layout strategy for widget arrangement. If None, uses default layout.
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
    def value_hook(self) -> HookWithOwnerLike[int]:
        """
        Hook for the value.
        """
        return self.controller.value_hook

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

