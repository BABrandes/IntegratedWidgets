from typing import Any, Optional, Generic, TypeVar, Callable, Union, Literal
from PySide6.QtWidgets import QWidget, QLayout, QGroupBox, QVBoxLayout
from logging import Logger
from observables import HookLike, ObservableSingleValueLike

from .iqt_base import IQtBaseWidget, LayoutStrategyForControllers
from integrated_widgets.widget_controllers.display_value_controller import DisplayValueController

T = TypeVar("T")

class DefaultLayoutStrategy(LayoutStrategyForControllers[DisplayValueController[T]], Generic[T]):
    def __call__(self,parent: QWidget, controller: DisplayValueController[T]) -> Union[QLayout, QWidget]:
        layout = QVBoxLayout(parent)
        layout.addWidget(controller.widget_label)
        return layout

class IQtDisplayValue(IQtBaseWidget[Literal["value"], T, DisplayValueController[T]], Generic[T]):
    """
    Available hooks:
        - "value": T
    """

    def __init__(
        self,
        value_or_hook_or_observable: T | HookLike[T] | ObservableSingleValueLike[T],
        formatter: Optional[Callable[[T], str]] = None,
        layout_strategy: Optional[LayoutStrategyForControllers] = None,
        parent: Optional[QWidget] = None,
        logger: Optional[Logger] = None
        ) -> None:

        _controller = DisplayValueController(
            value_or_hook_or_observable=value_or_hook_or_observable,
            formatter=formatter,
            logger=logger)

        if layout_strategy is None:
            layout_strategy = DefaultLayoutStrategy()

        super().__init__(
            _controller, 
            layout_strategy, parent)