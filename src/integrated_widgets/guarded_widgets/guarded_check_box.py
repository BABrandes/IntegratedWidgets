from __future__ import annotations

from integrated_widgets.widget_controllers.base_controller import BaseObservableController

from PySide6.QtWidgets import QCheckBox, QWidget


class GuardedCheckBox(QCheckBox):
    def __init__(self, owner: BaseObservableController, text: str = "") -> None:
        super().__init__(text, owner._owner_widget)
        self._owner = owner
    # Programmatic setChecked allowed; controller commits via signals


