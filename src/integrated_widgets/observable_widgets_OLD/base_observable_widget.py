from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Signal
from typing import Callable, Optional
from ._observable_mixin import ObservableWithObservableMixin, O


class BaseWidget_With_Observable(QWidget, ObservableWithObservableMixin[O]):
    widget_changed = Signal()

    def __init__(self, observable: Optional[O], parent: QWidget | None = None):
        QWidget.__init__(self, parent)
        ObservableWithObservableMixin.__init__(self, observable)

    # Re-expose Qt-style API for clarity
    def connect_widget_listener(self, slot: Callable[[], None]) -> None:
        self.widget_changed.connect(slot)

    def disconnect_widget_listener(self, slot: Callable[[], None]) -> None:
        self.widget_changed.disconnect(slot)