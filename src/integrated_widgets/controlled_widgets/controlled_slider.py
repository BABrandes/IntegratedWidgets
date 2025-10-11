from __future__ import annotations

from typing import Optional
from logging import Logger
from PySide6.QtWidgets import QSlider, QWidget
from integrated_widgets.util.base_controller import BaseController
from .base_controlled_widget import BaseControlledWidget


class ControlledSlider(BaseControlledWidget, QSlider):
    def __init__(self, controller: BaseController, parent_of_widget: Optional[QWidget] = None, orientation=None, logger: Optional[Logger] = None) -> None:  # orientation optional for convenience
        if orientation is None:
            BaseControlledWidget.__init__(self, controller, logger)
            QSlider.__init__(self, parent_of_widget)
        else:
            BaseControlledWidget.__init__(self, controller, logger)
            QSlider.__init__(self, orientation, parent_of_widget)

    # Programmatic setValue allowed; controller manages commit


