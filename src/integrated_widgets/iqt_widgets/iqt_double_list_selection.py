from typing import Optional, TypeVar, Generic, Callable, Any, Literal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout
from logging import Logger
from observables import HookLike, ObservableSetLike
from dataclasses import dataclass

from .iqt_controlled_layouted_widget import IQtControlledLayoutedWidget, LayoutStrategy
from integrated_widgets.widget_controllers.double_list_selection_controller import DoubleListSelectionController
from .layout_payload import BaseLayoutPayload

T = TypeVar("T")


@dataclass(frozen=True)
class Controller_Payload(BaseLayoutPayload):
    """Payload for double list selection widget."""
    available_list: QWidget
    selected_list: QWidget
    button_move_to_selected: QWidget
    button_remove_from_selected: QWidget


class Controller_LayoutStrategy(LayoutStrategy[Controller_Payload], Generic[T]):
    """Default layout strategy for double list selection widget."""
    def __call__(self, parent: QWidget, payload: Controller_Payload) -> QWidget:
        widget = QWidget()
        layout = QHBoxLayout(widget)

        # Available list
        available_layout = QVBoxLayout()
        available_layout.addWidget(QLabel("Available"))
        available_layout.addWidget(payload.available_list)
        layout.addLayout(available_layout)
        
        # Buttons in the middle
        button_layout = QVBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(payload.button_move_to_selected)
        button_layout.addWidget(payload.button_remove_from_selected)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Selected list
        selected_layout = QVBoxLayout()
        selected_layout.addWidget(QLabel("Selected"))
        selected_layout.addWidget(payload.selected_list)
        layout.addLayout(selected_layout)
        
        return widget


class IQtDoubleListSelection(IQtControlledLayoutedWidget[Literal["selected_options", "available_options"], set[T], Controller_Payload, DoubleListSelectionController[T]], Generic[T]):
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
        layout_strategy: Optional[Controller_LayoutStrategy[T]] = None,
        parent: Optional[QWidget] = None,
        logger: Optional[Logger] = None
    ) -> None:

        controller = DoubleListSelectionController(
            selected_options=selected_options,
            available_options=available_options,
            order_by_callable=order_by_callable,
            logger=logger
        )

        payload = Controller_Payload(
            available_list=controller.widget_available_list,
            selected_list=controller.widget_selected_list,
            button_move_to_selected=controller.widget_button_move_to_selected,
            button_remove_from_selected=controller.widget_button_remove_from_selected
        )
        
        if layout_strategy is None:
            layout_strategy = Controller_LayoutStrategy()

        super().__init__(controller, payload, layout_strategy, parent)

