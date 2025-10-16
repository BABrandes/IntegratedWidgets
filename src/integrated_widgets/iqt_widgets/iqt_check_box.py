from typing import Optional, Union, Literal
from PySide6.QtWidgets import QWidget, QLayout, QVBoxLayout
from logging import Logger
from observables import HookLike, ObservableSingleValueLike

from .iqt_base import IQtBaseWidget, LayoutStrategyForControllers
from integrated_widgets.widget_controllers.check_box_controller import CheckBoxController


class DefaultLayoutStrategy(LayoutStrategyForControllers[CheckBoxController]):
    def __call__(self, parent: QWidget, controller: CheckBoxController) -> Union[QLayout, QWidget]:
        layout = QVBoxLayout(parent)
        layout.addWidget(controller.widget_check_box)
        return layout

class IQtCheckBox(IQtBaseWidget[Literal["value", "enabled"], bool, CheckBoxController]):
    """
    Available hooks:
        - "value": bool
        - "enabled": bool
    """

    def __init__(
        self,
        value_or_hook_or_observable: bool | HookLike[bool] | ObservableSingleValueLike[bool],
        *,
        text: str = "",
        layout_strategy: Optional[LayoutStrategyForControllers] = None,
        parent: Optional[QWidget] = None,
        logger: Optional[Logger] = None
    ) -> None:

        controller = CheckBoxController(
            value_or_hook_or_observable=value_or_hook_or_observable,
            text=text,
            logger=logger
        )

        if layout_strategy is None:
            layout_strategy = DefaultLayoutStrategy()

        super().__init__(controller, layout_strategy, parent)

