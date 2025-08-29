from __future__ import annotations

from typing import Optional

from PySide6.QtWidgets import QLineEdit, QWidget
from logging import Logger

from integrated_widgets.widget_controllers.base_controller import BaseWidgetController

class GuardedLineEdit(QLineEdit):
    def __init__(self, owner: BaseWidgetController, logger: Optional[Logger] = None) -> None:
        super().__init__(owner._owner_widget)
        self._owner = owner
        self._logger = logger
    # Programmatic setText allowed; controller commits via editingFinished


