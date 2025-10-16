from typing import Optional, Union, Callable, Literal
from PySide6.QtWidgets import QWidget, QLayout, QVBoxLayout
from logging import Logger
from observables import HookLike, ObservableSingleValueLike

from .iqt_base import IQtBaseWidget, LayoutStrategyForControllers
from integrated_widgets.widget_controllers.integer_entry_controller import IntegerEntryController


class DefaultLayoutStrategy(LayoutStrategyForControllers[IntegerEntryController]):
    def __call__(self, parent: QWidget, controller: IntegerEntryController) -> Union[QLayout, QWidget]:
        layout = QVBoxLayout(parent)
        layout.addWidget(controller.widget_line_edit)
        return layout


class IQtIntegerEntry(IQtBaseWidget[Literal["value", "enabled"], int, IntegerEntryController]):
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
        layout_strategy: Optional[LayoutStrategyForControllers] = None,
        parent: Optional[QWidget] = None,
        logger: Optional[Logger] = None
    ) -> None:

        controller = IntegerEntryController(
            value_or_hook_or_observable=value_or_hook_or_observable,
            validator=validator,
            logger=logger
        )

        if layout_strategy is None:
            layout_strategy = DefaultLayoutStrategy()

        super().__init__(controller, layout_strategy, parent)

