from PySide6.QtWidgets import QWidget, QLabel
from typing import Any, Callable
from .base_observable_widget import BaseWidget_With_Observable

from observables import ObservableSingleValue

class ObsQLabel(BaseWidget_With_Observable[ObservableSingleValue[Any]]):
    def __init__(self, initial_value_or_observable: Any|ObservableSingleValue[Any], format_function: Callable[[Any], str] = lambda x: str(x), parent: QWidget | None = None):

        if isinstance(initial_value_or_observable, ObservableSingleValue):
            obs = initial_value_or_observable
        else:
            obs = ObservableSingleValue(initial_value_or_observable)

        super().__init__(obs, parent)

        self._format_function = format_function

        self._label = QLabel(self._format_function(self.observable.value))

        self.construction_finished()

    def update_observable(self):
        # Label does not push to observable; keep display synced from observable only
        pass

    def update_widget(self):
        self._label.setText(self._format_function(self.observable.value))