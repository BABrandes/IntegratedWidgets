from __future__ import annotations

from typing import Optional

from PySide6.QtWidgets import QLineEdit, QWidget
from integrated_widgets.widget_controllers.base_controller import BaseObservableController

class GuardedLineEdit(QLineEdit):
    def __init__(self, owner: BaseObservableController) -> None:
        super().__init__(owner._owner_widget)
        self._owner = owner
    # Programmatic setText allowed; controller commits via editingFinished


