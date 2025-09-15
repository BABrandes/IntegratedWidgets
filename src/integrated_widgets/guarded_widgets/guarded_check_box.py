from __future__ import annotations

from integrated_widgets.util.base_controller import BaseController

from PySide6.QtWidgets import QCheckBox, QWidget


class GuardedCheckBox(QCheckBox):
    def __init__(self, owner: BaseController, text: str = "") -> None:
        super().__init__(text, owner._owner_widget)
        self._owner = owner
    # Programmatic setChecked allowed; controller commits via signals


