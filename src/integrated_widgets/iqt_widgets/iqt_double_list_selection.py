from typing import Optional, Union, TypeVar, Generic, Callable, Any, Literal
from PySide6.QtWidgets import QWidget, QLayout, QVBoxLayout, QHBoxLayout, QLabel
from logging import Logger
from observables import HookLike, ObservableSetLike

from .iqt_base import IQtBaseWidget, LayoutStrategyForControllers
from integrated_widgets.widget_controllers.double_list_selection_controller import DoubleListSelectionController

T = TypeVar("T")


class DefaultLayoutStrategy(LayoutStrategyForControllers[DoubleListSelectionController[T]], Generic[T]):
    def __call__(self, parent: QWidget, controller: DoubleListSelectionController[T]) -> Union[QLayout, QWidget]:
        layout = QHBoxLayout(parent)
        
        # Available list
        available_layout = QVBoxLayout()
        available_layout.addWidget(QLabel("Available"))
        available_layout.addWidget(controller.widget_available_list)
        layout.addLayout(available_layout)
        
        # Buttons in the middle
        button_layout = QVBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(controller.widget_button_move_to_selected)
        button_layout.addWidget(controller.widget_button_remove_from_selected)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Selected list
        selected_layout = QVBoxLayout()
        selected_layout.addWidget(QLabel("Selected"))
        selected_layout.addWidget(controller.widget_selected_list)
        layout.addLayout(selected_layout)
        
        return layout


class IQtDoubleListSelection(IQtBaseWidget[Literal["selected_options", "available_options"], set[T], DoubleListSelectionController[T]], Generic[T]):
    """
    Available hooks:
        - "selected_options": set[T]
        - "available_options": set[T]
    """

    def __init__(
        self,
        selected_options: set[T] | HookLike[set[T]] | ObservableSetLike[T],
        available_options: set[T] | HookLike[set[T]] | ObservableSetLike[T],
        *,
        order_by_callable: Callable[[T], Any] = lambda x: str(x),
        layout_strategy: Optional[LayoutStrategyForControllers] = None,
        parent: Optional[QWidget] = None,
        logger: Optional[Logger] = None
    ) -> None:

        controller = DoubleListSelectionController(
            selected_options=selected_options,
            available_options=available_options,
            order_by_callable=order_by_callable,
            logger=logger
        )

        if layout_strategy is None:
            layout_strategy = DefaultLayoutStrategy()

        super().__init__(controller, layout_strategy, parent)

