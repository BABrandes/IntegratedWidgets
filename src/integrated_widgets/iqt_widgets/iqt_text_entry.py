from typing import Optional, Callable, Literal
from PySide6.QtWidgets import QWidget
from logging import Logger
from observables import HookLike, ObservableSingleValueLike
from dataclasses import dataclass

from integrated_widgets.widget_controllers.text_entry_controller import TextEntryController
from .core.iqt_controlled_layouted_widget import IQtControlledLayoutedWidget, LayoutStrategy
from .core.layout_payload import BaseLayoutPayload


@dataclass(frozen=True)
class Controller_Payload(BaseLayoutPayload):
    """Payload for a text entry widget."""
    line_edit: QWidget


class Controller_LayoutStrategy(LayoutStrategy[Controller_Payload]):
    """Default layout strategy for text entry widget."""
    def __call__(self, parent: QWidget, payload: Controller_Payload) -> QWidget:
        return payload.line_edit


class IQtTextEntry(IQtControlledLayoutedWidget[Literal["value", "enabled"], str, Controller_Payload, TextEntryController]):
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
        value_or_hook_or_observable: str | HookLike[str] | ObservableSingleValueLike[str],
        *,
        validator: Optional[Callable[[str], bool]] = None,
        strip_whitespace: bool = True,
        layout_strategy: Optional[Controller_LayoutStrategy] = None,
        parent: Optional[QWidget] = None,
        logger: Optional[Logger] = None
    ) -> None:
        """
        Initialize the text entry widget.
        
        Parameters
        ----------
        value_or_hook_or_observable : str | HookLike[str] | ObservableSingleValueLike[str]
            The initial text value, or a hook/observable to bind to.
        validator : Callable[[str], bool], optional
            Validation function that returns True if the text is valid. Default is None (all text valid).
        strip_whitespace : bool, optional
            If True, automatically trim leading/trailing whitespace. Default is True.
        layout_strategy : Controller_LayoutStrategy, optional
            Custom layout strategy for widget arrangement. If None, uses default layout.
        parent : QWidget, optional
            The parent widget. Default is None.
        logger : Logger, optional
            Logger instance for debugging. Default is None.
        """

        controller = TextEntryController(
            value_or_hook_or_observable=value_or_hook_or_observable,
            validator=validator,
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
    def value_hook(self):
        """Hook for the text value."""
        return self.controller.value_hook

    #--------------------------------------------------------------------------
    # Properties
    #--------------------------------------------------------------------------

    @property
    def text(self) -> str:
        return self.get_value_of_hook("value") # type: ignore

    @text.setter
    def text(self, value: str) -> None:
        self.controller.value = value

    def change_text(self, value: str) -> None:
        self.controller.value = value