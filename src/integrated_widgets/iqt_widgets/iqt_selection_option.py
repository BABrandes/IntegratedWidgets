from typing import Optional, TypeVar, Generic, Callable, Literal
from PySide6.QtWidgets import QWidget
from logging import Logger
from observables import HookLike, ObservableSingleValueLike, ObservableSetLike, ObservableSelectionOptionLike
from dataclasses import dataclass

from .iqt_controlled_layouted_widget import IQtControlledLayoutedWidget, LayoutStrategy
from integrated_widgets.widget_controllers.selection_option_controller import SelectionOptionController
from .layout_payload import BaseLayoutPayload

T = TypeVar("T")


@dataclass(frozen=True)
class Controller_Payload(BaseLayoutPayload):
    """Payload for a selection option widget."""
    combobox: QWidget


class Controller_LayoutStrategy(LayoutStrategy[Controller_Payload], Generic[T]):
    """Default layout strategy for selection option widget."""
    def __call__(self, parent: QWidget, payload: Controller_Payload) -> QWidget:
        return payload.combobox


class IQtSelectionOption(IQtControlledLayoutedWidget[Literal["selected_option", "available_options"], T | set[T], Controller_Payload, SelectionOptionController[T]], Generic[T]):
    """
    Available hooks:
        - "selected_option": T
        - "available_options": set[T]
    """

    def __init__(
        self,
        selected_option: T | HookLike[T] | ObservableSingleValueLike[T] | ObservableSelectionOptionLike[T],
        available_options: set[T] | HookLike[set[T]] | ObservableSetLike[T] | None,
        *,
        formatter: Callable[[T], str] = lambda item: str(item),
        layout_strategy: Optional[Controller_LayoutStrategy[T]] = None,
        parent: Optional[QWidget] = None,
        logger: Optional[Logger] = None
    ) -> None:

        controller = SelectionOptionController(
            selected_option=selected_option,
            available_options=available_options,
            formatter=formatter,
            logger=logger
        )

        payload = Controller_Payload(combobox=controller.widget_combobox)
        
        if layout_strategy is None:
            layout_strategy = Controller_LayoutStrategy()

        super().__init__(controller, payload, layout_strategy, parent)
