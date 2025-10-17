from typing import Optional, Callable, Literal
from PySide6.QtWidgets import QWidget
from logging import Logger
from observables import HookLike, ObservableSingleValueLike
from dataclasses import dataclass

from observables.core import HookWithOwnerLike

from .iqt_controlled_layouted_widget import IQtControlledLayoutedWidget, LayoutStrategy
from integrated_widgets.widget_controllers.float_entry_controller import FloatEntryController
from .layout_payload import BaseLayoutPayload


@dataclass(frozen=True)
class Controller_Payload(BaseLayoutPayload):
    """Payload for a float entry widget."""
    line_edit: QWidget


class Controller_LayoutStrategy(LayoutStrategy[Controller_Payload]):
    """Default layout strategy for float entry widget."""
    def __call__(self, parent: QWidget, payload: Controller_Payload) -> QWidget:
        return payload.line_edit


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
        value_or_hook_or_observable: float | HookLike[float] | ObservableSingleValueLike[float],
        *,
        validator: Optional[Callable[[float], bool]] = None,
        layout_strategy: Optional[Controller_LayoutStrategy] = None,
        parent: Optional[QWidget] = None,
        logger: Optional[Logger] = None
    ) -> None:
        """
        Initialize the float entry widget.
        
        Parameters
        ----------
        value_or_hook_or_observable : float | HookLike[float] | ObservableSingleValueLike[float]
            The initial value, or a hook/observable to bind to.
        validator : Callable[[float], bool], optional
            Validation function that returns True if the value is valid. Default is None (all values valid).
        layout_strategy : Controller_LayoutStrategy, optional
            Custom layout strategy for widget arrangement. If None, uses default layout.
        parent : QWidget, optional
            The parent widget. Default is None.
        logger : Logger, optional
            Logger instance for debugging. Default is None.
        """

        controller = FloatEntryController(
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
    def value_hook(self) -> HookWithOwnerLike[float]:
        """
        Hook for the value.
        """
        return self.controller.value_hook

    #--------------------------------------------------------------------------
    # Properties
    #--------------------------------------------------------------------------

    @property
    def value(self) -> float:
        return self.get_value_of_hook("value")

    @value.setter
    def value(self, value: float) -> None:
        self.controller.value = value

    def change_value(self, value: float) -> None:
        self.controller.value = value
