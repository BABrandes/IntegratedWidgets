from PySide6.QtWidgets import QWidget, QCheckBox, QHBoxLayout
from .base_observable_widget import BaseWidget_With_Observable
from typing import Optional

from observables import ObservableSingleValue

class ObsQCheckBox(BaseWidget_With_Observable[ObservableSingleValue[bool]]):
    def __init__(self, initial_value_or_observable: bool|ObservableSingleValue[bool], label: str = "", parent: QWidget | None = None):

        if isinstance(initial_value_or_observable, bool):
            observable = ObservableSingleValue(initial_value_or_observable)
        else:
            observable = initial_value_or_observable
        super().__init__(observable, parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self._checkbox: QCheckBox = QCheckBox(label, self)
        layout.addWidget(self._checkbox)

        self._checkbox.stateChanged.connect(lambda _: self._internal_update_observable())

        self.construction_finished()

    def update_widget(self):
        self._checkbox.setChecked(self.observable.value)
        self._checkbox.setEnabled(True)

    def update_observable(self) -> None:
        self.observable.set_value(self._checkbox.isChecked())

    def is_checked(self) -> bool:
        return self.observable.value
    
    def set_checked(self, value: bool) -> None:
        if self._checkbox.isChecked() == value or self.observable.value == value:
            return
        self._checkbox.setChecked(value)

    def set_enabled(self, value: bool) -> None:
        self._checkbox.setEnabled(value)

    # Optional convenience property
    @property
    def checked(self) -> bool:
        return self.is_checked()

    @checked.setter
    def checked(self, value: bool) -> None:
        self.set_checked(value)
