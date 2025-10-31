from __future__ import annotations

from typing import Optional, Any
from logging import Logger
from PySide6.QtWidgets import QSlider, QWidget
from PySide6.QtCore import Qt
from integrated_widgets.controllers.core.base_controller import BaseController
from .base_controlled_widget import BaseControlledWidget


class ControlledSlider(BaseControlledWidget, QSlider):
    def __init__(self, controller: BaseController[Any, Any], parent_of_widget: Optional[QWidget] = None, orientation: Optional[Qt.Orientation] = None, logger: Optional[Logger] = None) -> None:  # orientation optional for convenience
        if orientation is None:
            BaseControlledWidget.__init__(self, controller, logger)
            QSlider.__init__(self, parent_of_widget)
        else:
            BaseControlledWidget.__init__(self, controller, logger)
            QSlider.__init__(self, orientation, parent_of_widget)

    # Programmatic setValue allowed; controller manages commit

    def __str__(self) -> str:
        value = self.value()
        min_val = self.minimum()
        max_val = self.maximum()
        return f"{self.__class__.__name__}(value={value}, range={min_val}-{max_val})"

    def __repr__(self) -> str:
        value = self.value()
        min_val = self.minimum()
        max_val = self.maximum()
        return f"{self.__class__.__name__}(value={value}, range={min_val}-{max_val}, id={hex(id(self))})"

