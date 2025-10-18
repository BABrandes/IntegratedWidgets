from typing import Optional, Callable, Literal, Any
from PySide6.QtWidgets import QWidget
from logging import Logger
from observables import HookLike, ObservableSingleValueLike
from dataclasses import dataclass

from integrated_widgets.widget_controllers.optional_text_entry_controller import OptionalTextEntryController
from .core.iqt_controlled_layouted_widget import IQtControlledLayoutedWidget
from .core.layout_strategy_base import LayoutStrategyBase
from .core.layout_payload_base import LayoutPayloadBase


@dataclass(frozen=True)
class Controller_Payload(LayoutPayloadBase):
    """Payload for an optional text entry widget."""
    line_edit: QWidget


class Controller_LayoutStrategy(LayoutStrategyBase[Controller_Payload]):
    """Default layout strategy for optional text entry widget."""
    def layout(self, payload: Controller_Payload, **layout_strategy_kwargs: Any) -> QWidget:
        return payload.line_edit


class IQtOptionalTextEntry(IQtControlledLayoutedWidget[Literal["value", "enabled"], Optional[str], Controller_Payload, OptionalTextEntryController]):
    """
    An optional text entry widget with validation and data binding.
    
    This widget provides a line edit for entering text that can be None/empty.
    It includes a clear button and supports custom representations of None values.
    Bidirectionally synchronizes with observables.
    
    Available hooks:
        - "value": Optional[str] - The text value (can be None)
        - "enabled": bool - Whether the widget is enabled for user interaction
    
    Properties:
        value: Optional[str] - Get or set the text value (read/write, can be None)
    """

    def __init__(
        self,
        value_or_hook_or_observable: Optional[str] | HookLike[Optional[str]] | ObservableSingleValueLike[Optional[str]],
        *,
        validator: Optional[Callable[[Optional[str]], bool]] = None,
        none_value: str = "",
        strip_whitespace: bool = True,
        layout_strategy: Optional[Controller_LayoutStrategy] = None,
        parent: Optional[QWidget] = None,
        logger: Optional[Logger] = None
    ) -> None:
        """
        Initialize the optional text entry widget.
        
        Parameters
        ----------
        value_or_hook_or_observable : Optional[str] | HookLike[Optional[str]] | ObservableSingleValueLike[Optional[str]]
            The initial text value (can be None), or a hook/observable to bind to.
        validator : Callable[[Optional[str]], bool], optional
            Validation function that returns True if the value is valid. Default is None (all values valid).
        none_value : str, optional
            The string representation of None (what's shown when value is None). Default is empty string.
        strip_whitespace : bool, optional
            If True, automatically trim leading/trailing whitespace. Default is True.
        layout_strategy : Controller_LayoutStrategy, optional
            Custom layout strategy for widget arrangement. If None, uses default layout.
        parent : QWidget, optional
            The parent widget. Default is None.
        logger : Logger, optional
            Logger instance for debugging. Default is None.
        """

        controller = OptionalTextEntryController(
            value_or_hook_or_observable=value_or_hook_or_observable,
            validator=validator,
            none_value=none_value,
            strip_whitespace=strip_whitespace,
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
    def text_hook(self):
        """Hook for the optional text value."""
        return self.controller.value_hook

    #--------------------------------------------------------------------------
    # Properties
    #--------------------------------------------------------------------------

    @property
    def text(self) -> Optional[str]:
        return self.get_value_of_hook("value")

    @text.setter
    def text(self, value: Optional[str]) -> None:
        self.controller.value = value

    def change_text(self, value: Optional[str]) -> None:
        self.controller.value = value