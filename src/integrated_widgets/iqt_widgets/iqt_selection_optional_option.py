from typing import Optional, Union, TypeVar, Generic, Callable, Literal
from PySide6.QtWidgets import QWidget, QLayout, QVBoxLayout
from logging import Logger
from observables import HookLike, ObservableSingleValueLike, ObservableSetLike, ObservableOptionalSelectionOptionLike

from .iqt_base import IQtBaseWidget, LayoutStrategyForControllers
from integrated_widgets.widget_controllers.selection_optional_option_controller import SelectionOptionalOptionController

T = TypeVar("T")


class DefaultLayoutStrategy(LayoutStrategyForControllers[SelectionOptionalOptionController[T]], Generic[T]):
    def __call__(self, parent: QWidget, controller: SelectionOptionalOptionController[T]) -> Union[QLayout, QWidget]:
        layout = QVBoxLayout(parent)
        layout.addWidget(controller.widget_combobox)
        return layout


class IQtSelectionOptionalOption(IQtBaseWidget[Literal["selected_option", "available_options"], Optional[T] | set[T], SelectionOptionalOptionController[T]], Generic[T]):
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
        formatter: Callable[[T], str] = lambda item: str(item),
        none_option_text: str = "-",
        layout_strategy: Optional[LayoutStrategyForControllers] = None,
        parent: Optional[QWidget] = None,
        logger: Optional[Logger] = None
    ) -> None:

        controller = SelectionOptionalOptionController(
            selected_option=selected_option,
            available_options=available_options,
            formatter=formatter,
            none_option_text=none_option_text,
            logger=logger
        )

        if layout_strategy is None:
            layout_strategy = DefaultLayoutStrategy()

        super().__init__(controller, layout_strategy, parent)
