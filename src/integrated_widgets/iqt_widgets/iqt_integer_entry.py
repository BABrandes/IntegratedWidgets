from typing import Optional, Callable, Literal
from PySide6.QtWidgets import QWidget
from logging import Logger
from observables import HookLike, ObservableSingleValueLike
from dataclasses import dataclass

from .iqt_controlled_layouted_widget import IQtControlledLayoutedWidget, LayoutStrategy
from integrated_widgets.widget_controllers.integer_entry_controller import IntegerEntryController
from .layout_payload import BaseLayoutPayload


@dataclass(frozen=True)
class Controller_Payload(BaseLayoutPayload):
    """Payload for an integer entry widget."""
    line_edit: QWidget


class Controller_LayoutStrategy(LayoutStrategy[Controller_Payload]):
    """Default layout strategy for integer entry widget."""
    def __call__(self, parent: QWidget, payload: Controller_Payload) -> QWidget:
        return payload.line_edit


class IQtIntegerEntry(IQtControlledLayoutedWidget[Literal["value", "enabled"], int, Controller_Payload, IntegerEntryController]):
    """
    Available hooks:
        - "value": int
        - "enabled": bool
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

        controller = IntegerEntryController(
            value_or_hook_or_observable=value_or_hook_or_observable,
            validator=validator,
            logger=logger
        )

        payload = Controller_Payload(line_edit=controller.widget_line_edit)
        
        if layout_strategy is None:
            layout_strategy = Controller_LayoutStrategy()

        super().__init__(controller, payload, layout_strategy, parent)

