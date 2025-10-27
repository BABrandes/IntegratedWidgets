from typing import Optional, Callable, Literal
from PySide6.QtWidgets import QWidget
from logging import Logger
from nexpy import Hook
from nexpy.x_objects.single_value_like.protocols import XSingleValueProtocol
from dataclasses import dataclass

from integrated_widgets.controllers.singleton.optional_text_entry_controller import OptionalTextEntryController
from .core.iqt_controlled_layouted_widget import IQtControlledLayoutedWidget
from .core.layout_strategy_base import LayoutStrategyBase
from .core.layout_payload_base import LayoutPayloadBase


@dataclass(frozen=True)
class Controller_Payload(LayoutPayloadBase):
    """Payload for an optional text entry widget."""
    line_edit: QWidget


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
        value: Optional[str] | Hook[Optional[str]] | XSingleValueProtocol[Optional[str]],
        *,
        validator: Optional[Callable[[Optional[str]], bool]] = None,
        none_value: str = "",
        strip_whitespace: bool = True,
        layout_strategy: LayoutStrategyBase[Controller_Payload] = lambda payload, **_: payload.line_edit,
        parent: Optional[QWidget] = None,
        logger: Optional[Logger] = None
    ) -> None:
        """
        Initialize the optional text entry widget.
        
        Parameters
        ----------
        value : Optional[str] | Hook[Optional[str]] | XSingleValueProtocol[Optional[str]]
            The initial text value (can be None), or a hook/observable to bind to.
        validator : Callable[[Optional[str]], bool], optional
            Validation function that returns True if the value is valid. Default is None (all values valid).
        none_value : str, optional
            The string representation of None (what's shown when value is None). Default is empty string.
        strip_whitespace : bool, optional
            If True, automatically trim leading/trailing whitespace. Default is True.
        layout_strategy : LayoutStrategyBase[Controller_Payload], optional
            Custom layout strategy for widget arrangement. Default is default layout.
        parent : QWidget, optional
            The parent widget. Default is None.
        logger : Logger, optional
            Logger instance for debugging. Default is None.
        """

        controller = OptionalTextEntryController(
            value=value,
            validator=validator,
            none_value=none_value,
            strip_whitespace=strip_whitespace,
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
    def text_hook(self) -> Hook[Optional[str]]:
        """Hook for the optional text value."""
        hook: Hook[Optional[str]] = self.get_hook_by_key("value")
        return hook

    #--------------------------------------------------------------------------
    # Properties
    #--------------------------------------------------------------------------

    @property
    def text(self) -> Optional[str]:
        return self.get_hook_value_by_key("value")

    @text.setter
    def text(self, value: Optional[str]) -> None:
        self.controller.value = value

    def change_text(self, value: Optional[str]) -> None:
        self.controller.value = value