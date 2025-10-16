from typing import Optional, TypeVar, Generic, Callable, Any, Literal
from PySide6.QtWidgets import QWidget
from logging import Logger
from observables import HookLike, ObservableSingleValueLike, ObservableSetLike, ObservableOptionalSelectionOptionLike
from dataclasses import dataclass

from .iqt_controlled_layouted_widget import IQtControlledLayoutedWidget, LayoutStrategy
from integrated_widgets.widget_controllers.single_list_selection_controller import SingleListSelectionController
from .layout_payload import BaseLayoutPayload

T = TypeVar("T")


@dataclass(frozen=True)
class Controller_Payload(BaseLayoutPayload):
    """Payload for a single list selection widget."""
    list_widget: QWidget


class Controller_LayoutStrategy(LayoutStrategy[Controller_Payload], Generic[T]):
    """Default layout strategy for single list selection widget."""
    def __call__(self, parent: QWidget, payload: Controller_Payload) -> QWidget:
        return payload.list_widget


class IQtSingleListSelection(IQtControlledLayoutedWidget[Literal["selected_option", "available_options"], Optional[T] | set[T], Controller_Payload, SingleListSelectionController[T]], Generic[T]):
    """
    Available hooks:
        - "selected_option": Optional[T]
        - "available_options": set[T]
    """

    def __init__(
        self,
        selected_option: Optional[T] | HookLike[Optional[T]] | ObservableSingleValueLike[Optional[T]] | ObservableOptionalSelectionOptionLike[T],
        available_options: set[T] | HookLike[set[T]] | ObservableSetLike[T] | None,
        *,
        order_by_callable: Callable[[T], Any] = lambda x: str(x),
        formatter: Callable[[T], str] = str,
        allow_deselection: bool = True,
        layout_strategy: Optional[Controller_LayoutStrategy[T]] = None,
        parent: Optional[QWidget] = None,
        logger: Optional[Logger] = None
    ) -> None:

        controller = SingleListSelectionController(
            selected_option=selected_option,
            available_options=available_options,
            order_by_callable=order_by_callable,
            formatter=formatter,
            allow_deselection=allow_deselection,
            logger=logger
        )

        payload = Controller_Payload(list_widget=controller.widget_list)
        
        if layout_strategy is None:
            layout_strategy = Controller_LayoutStrategy()

        super().__init__(controller, payload, layout_strategy, parent)
