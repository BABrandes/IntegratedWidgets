from typing import Optional, Union, TypeVar, Generic, Callable, Any, Literal
from PySide6.QtWidgets import QWidget, QLayout, QVBoxLayout
from logging import Logger
from observables import HookLike, ObservableSingleValueLike, ObservableSetLike, ObservableSelectionOptionLike

from .iqt_base import IQtBaseWidget, LayoutStrategy
from integrated_widgets.widget_controllers.radio_buttons_controller import RadioButtonsController

T = TypeVar("T")


class DefaultLayoutStrategy(LayoutStrategy[RadioButtonsController[T]], Generic[T]):
    def __call__(self, parent: QWidget, controller: RadioButtonsController[T]) -> Union[QLayout, QWidget]:
        layout = QVBoxLayout(parent)
        for button in controller.widget_radio_buttons:
            layout.addWidget(button)
        return layout


class IQtRadioButtons(IQtBaseWidget[Literal["selected_option", "available_options"], T | set[T], RadioButtonsController[T]], Generic[T]):
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
        sorter: Callable[[T], Any] = lambda item: str(item),
        layout_strategy: Optional[LayoutStrategy] = None,
        parent: Optional[QWidget] = None,
        logger: Optional[Logger] = None
    ) -> None:

        controller = RadioButtonsController(
            selected_option=selected_option,
            available_options=available_options,
            formatter=formatter,
            sorter=sorter,
            logger=logger
        )

        if layout_strategy is None:
            layout_strategy = DefaultLayoutStrategy()

        super().__init__(controller, layout_strategy, parent)
