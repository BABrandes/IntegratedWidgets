from __future__ import annotations

from integrated_widgets.util.base_controller import BaseController

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QCheckBox, QWidget

from ._enable_watcher import EnabledWatcher


class GuardedCheckBox(QCheckBox):
    enabledChanged = Signal(bool)

    def __init__(self, owner: BaseController, text: str = "") -> None:
        super().__init__(text, owner._owner_widget)
        self._owner = owner

        self._enabled_watcher = EnabledWatcher(self, parent=self)
        self._enabled_watcher.enabledChanged.connect(self.enabledChanged)
    # Programmatic setChecked allowed; controller commits via signals


