from typing import Optional, Any
from logging import Logger
from integrated_widgets.util.base_controller import BaseController

class BaseControlledWidget():
    def __init__(self, controller: BaseController[Any, Any, Any], logger: Optional[Logger] = None) -> None:
        self._controller = controller
        self._logger = logger
        self._internal_widget_update = False

    @property
    def controller(self) -> BaseController[Any, Any, Any]:
        return self._controller

    @property
    def logger(self) -> Optional[Logger]:
        return self._logger