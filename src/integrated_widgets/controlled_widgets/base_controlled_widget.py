from typing import Optional
from logging import Logger
from integrated_widgets.util.base_controller import BaseController

class BaseControlledWidget():
    def __init__(self, controller: BaseController, logger: Optional[Logger] = None) -> None:
        self._controller = controller
        self._logger = logger
        self._internal_widget_update = False

    @property
    def controller(self) -> BaseController:
        return self._controller

    @property
    def logger(self) -> Optional[Logger]:
        return self._logger