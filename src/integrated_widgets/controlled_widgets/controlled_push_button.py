from PySide6.QtWidgets import QPushButton, QWidget
from typing import Optional, Any
from logging import Logger

from integrated_widgets.controllers.core.base_controller import BaseController

from .base_controlled_widget import BaseControlledWidget

class ControlledPushButton(BaseControlledWidget, QPushButton):
    """

    Signaling behavior:
    ------------------
    "userInputFinishedSignal" is emitted for the QPushButton "clicked" signal.
    """

    def __init__(self, controller: BaseController[Any, Any], text: str = "", parent_of_widget: Optional[QWidget] = None, logger: Optional[Logger] = None) -> None:
        BaseControlledWidget.__init__(self, controller, logger)
        QPushButton.__init__(self, text, parent_of_widget)

        self.clicked.connect(self._on_user_input_finished)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(text={self.text()!r})"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(text={self.text()!r}, id={hex(id(self))})"