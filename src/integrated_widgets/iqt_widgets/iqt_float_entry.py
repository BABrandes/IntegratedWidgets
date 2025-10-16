from typing import Optional, Union, Callable, Literal
from PySide6.QtWidgets import QWidget, QLayout, QVBoxLayout
from logging import Logger
from observables import HookLike, ObservableSingleValueLike

from .iqt_base import IQtBaseWidget, LayoutStrategyForControllers
from integrated_widgets.widget_controllers.float_entry_controller import FloatEntryController


class DefaultLayoutStrategy(LayoutStrategyForControllers[FloatEntryController]):
    def __call__(self, parent: QWidget, controller: FloatEntryController) -> Union[QLayout, QWidget]:
        layout = QVBoxLayout(parent)
        layout.addWidget(controller.widget_line_edit)
        return layout


class IQtFloatEntry(IQtBaseWidget[Literal["value", "enabled"], float, FloatEntryController]):
    """
    Available hooks:
        - "value": float
        - "enabled": bool
    """

    def __init__(
        self,
        value_or_hook_or_observable: float | HookLike[float] | ObservableSingleValueLike[float],
        *,
        validator: Optional[Callable[[float], bool]] = None,
        layout_strategy: Optional[LayoutStrategyForControllers] = None,
        parent: Optional[QWidget] = None,
        logger: Optional[Logger] = None
    ) -> None:

        controller = FloatEntryController(
            value_or_hook_or_observable=value_or_hook_or_observable,
            validator=validator,
            logger=logger
        )

        if layout_strategy is None:
            layout_strategy = DefaultLayoutStrategy()

        super().__init__(controller, layout_strategy, parent)

