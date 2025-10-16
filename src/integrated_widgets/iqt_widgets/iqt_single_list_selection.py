from typing import Optional, Union, TypeVar, Generic, Callable, Any, Literal
from PySide6.QtWidgets import QWidget, QLayout, QVBoxLayout
from logging import Logger
from observables import HookLike, ObservableSingleValueLike, ObservableSetLike, ObservableOptionalSelectionOptionLike

from .iqt_base import IQtBaseWidget, LayoutStrategy
from integrated_widgets.widget_controllers.single_list_selection_controller import SingleListSelectionController

T = TypeVar("T")


class DefaultLayoutStrategy(LayoutStrategy[SingleListSelectionController[T]], Generic[T]):
    def __call__(self, parent: QWidget, controller: SingleListSelectionController[T]) -> Union[QLayout, QWidget]:
        layout = QVBoxLayout(parent)
        layout.addWidget(controller.widget_list)
        return layout


class IQtSingleListSelection(IQtBaseWidget[Literal["selected_option", "available_options"], Optional[T] | set[T], SingleListSelectionController[T]], Generic[T]):
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
        layout_strategy: Optional[LayoutStrategy] = None,
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

        if layout_strategy is None:
            layout_strategy = DefaultLayoutStrategy()

        super().__init__(controller, layout_strategy, parent)
