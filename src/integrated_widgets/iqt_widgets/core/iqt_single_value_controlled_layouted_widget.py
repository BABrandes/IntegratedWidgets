from typing import Generic, TypeVar, Optional, Any, Literal
from PySide6.QtWidgets import QWidget
from logging import Logger

from integrated_widgets.util.base_single_hook_controller import BaseSingleHookController
from .iqt_controlled_layouted_widget import IQtControlledLayoutedWidget
from .layout_payload_base import LayoutPayloadBase
from .layout_strategy_base import LayoutStrategyBase

T = TypeVar("T")

class IQtSingleValueControlledLayoutedWidget(IQtControlledLayoutedWidget[Literal["value"], T, LayoutPayloadBase, BaseSingleHookController[T, Any]], Generic[T]):

    def __init__(
        self,
        controller: BaseSingleHookController[T, Any],
        payload: LayoutPayloadBase,
        layout_strategy: Optional[LayoutStrategyBase[LayoutPayloadBase]] = None,
        parent: Optional[QWidget] = None,
        logger: Optional[Logger] = None
    ) -> None:
        super().__init__(controller, payload, layout_strategy, parent, logger)

    @property
    def value(self) -> T:
        return self.controller.value
    @value.setter
    def value(self, value: T) -> None:
        self.controller.value = value
    def change_value(self, value: T) -> None:
        self.controller.change_value(value)