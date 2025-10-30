from typing import Optional, Callable
from logging import Logger
from dataclasses import dataclass

from PySide6.QtWidgets import QWidget

from nexpy import Hook, XSingleValueProtocol
from nexpy import default as nexpy_default
from nexpy.core import NexusManager


from ..controllers.singleton.text_entry_controller import TextEntryController
from ..auxiliaries.default import default_debounce_ms
from .foundation.iqt_singleton_controller_widget_base import IQtSingletonControllerWidgetBase
from .foundation.layout_strategy_base import LayoutStrategyBase
from .foundation.layout_payload_base import LayoutPayloadBase


@dataclass(frozen=True)
class Controller_Payload(LayoutPayloadBase):
    """Payload for a text entry widget."""
    text_entry: QWidget


class IQtTextEntry(IQtSingletonControllerWidgetBase[str, Controller_Payload, TextEntryController]):
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
        layout_strategy: LayoutStrategyBase[Controller_Payload] = lambda payload, **_: payload.text_entry,
        debounce_ms: int|Callable[[], int] = default_debounce_ms,
        nexus_manager: NexusManager = nexpy_default.NEXUS_MANAGER,
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
        debounce_ms: int|Callable[[], int] = default_debounce_ms,
        nexus_manager: NexusManager = nexpy_default.NEXUS_MANAGER,
        parent : QWidget, optional
            The parent widget. Default is None.
        logger : Logger, optional
            Logger instance for debugging. Default is None.
        """

        controller = TextEntryController(
            value=value_or_hook_or_observable,
            validator=validator,
            strip_whitespace=strip_whitespace,
            debounce_ms=debounce_ms,
            nexus_manager=nexus_manager,
            logger=logger
        )

        payload = Controller_Payload(text_entry=controller.widget_text_entry)
        
        super().__init__(controller, payload, layout_strategy=layout_strategy, parent=parent, logger=logger)

    ###########################################################################
    # Accessors
    ###########################################################################

    @property
    def text(self) -> str:
        return self.value

    @text.setter
    def text(self, value: str) -> None:
        self.controller.value = value

    def change_text(self, value: str) -> None:
        self.controller.change_value(value)