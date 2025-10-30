from typing import Generic, TypeVar, Any, Literal, Optional
from logging import Logger

from PySide6.QtWidgets import QWidget

from nexpy import Hook

from ...controllers.core.base_singleton_controller import BaseSingletonController
from .iqt_controller_widget_base import IQtControllerWidgetBase
from .layout_payload_base import LayoutPayloadBase
from .layout_strategy_base import LayoutStrategyBase

T = TypeVar("T")
P = TypeVar("P", bound=LayoutPayloadBase)
C = TypeVar("C", bound=BaseSingletonController[Any])


class IQtSingletonControllerWidgetBase(IQtControllerWidgetBase[Literal["value"], T, P, C], Generic[T, P, C]):

    def __init__(
        self,
        controller: C,
        payload: P,
        *,
        layout_strategy: Optional[LayoutStrategyBase[P]] = None,
        parent: Optional[QWidget] = None,
        logger: Optional[Logger] = None
        ) -> None:
        super().__init__(controller, payload, layout_strategy=layout_strategy, parent=parent, logger=logger)

    @property
    def hook(self) -> Hook[T]:
        return self.controller.value_hook

    @property
    def value(self) -> T:
        return self.controller.value

    @value.setter
    def value(self, value: T) -> None:
        self.controller.value = value

    def change_value(self, value: T) -> None:
        self.controller.change_value(value)