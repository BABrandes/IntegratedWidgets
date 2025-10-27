from typing import Optional, Callable, Literal
from PySide6.QtWidgets import QWidget
from logging import Logger
from nexpy import Hook
from nexpy.x_objects.single_value_like.protocols import XSingleValueProtocol
from nexpy.core import WritableHookProtocol
from dataclasses import dataclass

from integrated_widgets.controllers.singleton.text_entry_controller import TextEntryController
from .core.iqt_controlled_layouted_widget import IQtControlledLayoutedWidget
from .core.layout_strategy_base import LayoutStrategyBase
from .core.layout_payload_base import LayoutPayloadBase


@dataclass(frozen=True)
class Controller_Payload(LayoutPayloadBase):
    """Payload for a text entry widget."""
    line_edit: QWidget


class IQtTextEntry(IQtControlledLayoutedWidget[Literal["value"], str, Controller_Payload, TextEntryController]):
    """
    A text entry widget with validation and data binding.
    
    This widget provides a line edit for entering text with optional validation
    and bidirectional synchronization with observables. Supports automatic
    whitespace trimming and custom validation functions.
    
    Available hooks:
        - "value": str - The text value
        - "enabled": bool - Whether the widget is enabled for user interaction
    
    Properties:
        text: str - Get or set the text value (read/write)
    """

    def __init__(
        self,
        value_or_hook_or_observable: str | Hook[str] | XSingleValueProtocol[str],
        *,
        validator: Optional[Callable[[str], bool]] = None,
        strip_whitespace: bool = True,
        layout_strategy: LayoutStrategyBase[Controller_Payload] = lambda payload, **_: payload.line_edit,
        parent: Optional[QWidget] = None,
        logger: Optional[Logger] = None
    ) -> None:
        """
        Initialize the text entry widget.
        
        Parameters
        ----------
        value_or_hook_or_observable : str | Hook[str] | XSingleValueProtocol[str]
            The initial text value, or a hook/observable to bind to.
        validator : Callable[[str], bool], optional
            Validation function that returns True if the text is valid. Default is None (all text valid).
        strip_whitespace : bool, optional
            If True, automatically trim leading/trailing whitespace. Default is True.
        layout_strategy : LayoutStrategyBase[Controller_Payload]
            Custom layout strategy for widget arrangement. Default is default layout.
        parent : QWidget, optional
            The parent widget. Default is None.
        logger : Logger, optional
            Logger instance for debugging. Default is None.
        """

        controller = TextEntryController(
            value=value_or_hook_or_observable,
            validator=validator,
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
    def value_hook(self) -> Hook[str]:
        """Hook for the text value."""
        hook: Hook[str] = self.get_hook_by_key("value") # type: ignore
        return hook

    #--------------------------------------------------------------------------
    # Properties
    #--------------------------------------------------------------------------

    @property
    def text(self) -> str:
        return self.get_hook_value_by_key("value") # type: ignore

    @text.setter
    def text(self, value: str) -> None:
        hook: Hook[str] = self.get_hook_by_key("value") # type: ignore
        if isinstance(hook, WritableHookProtocol):
            hook.change_value(value)
        else:
            raise ValueError(f"Hook {hook} is not writable")

    def change_text(self, value: str) -> None:
        hook: Hook[str] = self.get_hook_by_key("value") # type: ignore
        if isinstance(hook, WritableHookProtocol):
            hook.change_value(value)
        else:
            raise ValueError(f"Hook {hook} is not writable")