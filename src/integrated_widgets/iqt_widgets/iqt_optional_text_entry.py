from typing import Optional, Callable, Literal
from PySide6.QtWidgets import QWidget
from logging import Logger
from observables import HookLike, ObservableSingleValueLike
from dataclasses import dataclass

from .iqt_controlled_layouted_widget import IQtControlledLayoutedWidget, LayoutStrategy
from integrated_widgets.widget_controllers.optional_text_entry_controller import OptionalTextEntryController
from .layout_payload import BaseLayoutPayload


@dataclass(frozen=True)
class Controller_Payload(BaseLayoutPayload):
    """Payload for an optional text entry widget."""
    line_edit: QWidget


class Controller_LayoutStrategy(LayoutStrategy[Controller_Payload]):
    """Default layout strategy for optional text entry widget."""
    def __call__(self, parent: QWidget, payload: Controller_Payload) -> QWidget:
        return payload.line_edit


class IQtOptionalTextEntry(IQtControlledLayoutedWidget[Literal["value", "enabled"], Optional[str], Controller_Payload, OptionalTextEntryController]):
    """
    Available hooks:
        - "value": Optional[str]
        - "enabled": bool
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
