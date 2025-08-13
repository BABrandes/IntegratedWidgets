from PySide6.QtWidgets import QWidget, QRadioButton, QVBoxLayout
from python.common.serialization.serializable_enum import JSON_HDF5_SerializableEnum
from .base_observable_widget import BaseWidget_With_Observable
from enum import Enum
from typing import Callable, TypeVar

from observables import ObservableEnum

E = TypeVar("E", bound=Enum|JSON_HDF5_SerializableEnum)

class ObsQEnumRadioButton(BaseWidget_With_Observable[ObservableEnum[E]]):
    def __init__(self, initial_enum_value_or_observable: E|ObservableEnum[E], format_function: Callable[[E], str] = lambda x: x.value, parent: QWidget | None = None):

        if isinstance(initial_enum_value_or_observable, Enum):
            enum_options: set[E] = set(initial_enum_value_or_observable.__class__)
            observable: ObservableEnum[E] = ObservableEnum(enum_value=initial_enum_value_or_observable, enum_options=enum_options)
        elif isinstance(initial_enum_value_or_observable, ObservableEnum):
            enum_options = initial_enum_value_or_observable.enum_options
        else:
            raise ValueError(f"Invalid observable: {initial_enum_value_or_observable}")
        
        super().__init__(observable, parent)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self._radio_buttons: dict[E, QRadioButton] = {}
        for enum_value in self.observable.enum_options:
            radio_button = QRadioButton(format_function(enum_value), self)
            radio_button.setChecked(enum_value == self.observable.enum_value)
            def _toggled(selected: bool, ev: E):
                if selected:
                    self.observable.set_enum_value(ev)
            radio_button.toggled.connect(lambda checked, ev=enum_value: _toggled(checked, ev))
            self._radio_buttons[enum_value] = radio_button
            layout.addWidget(radio_button)

        self.construction_finished()

    def update_widget(self):

        for enum_value, radio_button in self._radio_buttons.items():
            radio_button.setEnabled(True)
            radio_button.setChecked(enum_value == self.observable.enum_value)

    def update_observable(self):
        """
        The observable is updated in calls directly from the radio button toggled signal.
        """
        pass