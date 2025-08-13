from PySide6.QtWidgets import QWidget, QLabel, QLineEdit, QHBoxLayout
from typing import Callable, Generic, TypeVar
from .base_observable_widget import BaseWidget_With_Observable
from python.common.utils import str_to_float
from pandas import Timestamp

from united_system import RealUnitedScalar, HasUnit, SCALAR_TYPE, is_scalar
from observables import ObservableSingleValue

T = TypeVar("T", bound=SCALAR_TYPE)

class ObsQUnitedValueEntry(BaseWidget_With_Observable[ObservableSingleValue[T]], Generic[T]):
    
    def __init__(self, observable: T|ObservableSingleValue[T], format_function: Callable[[T], str] = lambda x: x.format(max_decimals=2, no_unit=True) if isinstance(x, RealUnitedScalar) else str(x), parent: QWidget | None = None):

        # Step 1: Initialize the observable
        if isinstance(observable, ObservableSingleValue):
            self._observable: ObservableSingleValue[T] = observable
        elif is_scalar(observable):
            self._observable: ObservableSingleValue[T] = ObservableSingleValue(observable)
        else:
            raise ValueError(f"Invalid observable type: {type(observable)}")

        super().__init__(self._observable, parent)

        self._format_function = format_function
        self._entry_scalar_type: type[T] = type(self._observable.value)

        self._entry = QLineEdit("")
        self._unit_label = QLabel("")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._entry)
        layout.addWidget(self._unit_label)

        # Update the observable when the enter key is pressed or the focus is lost
        self._entry.returnPressed.connect(self.update_observable)
        self._entry.editingFinished.connect(self.update_observable)

        self.construction_finished()

    def update_observable(self):

        current_value: T = self._observable.value
        try:
            if self._entry_scalar_type == RealUnitedScalar:
                assert isinstance(current_value, RealUnitedScalar)
                float_value: float = str_to_float(self._entry.text())
                new_value: T = RealUnitedScalar(float_value, current_value.unit)  # type: ignore[assignment]
            elif self._entry_scalar_type == int:
                assert isinstance(current_value, int)
                int_value: int = round(str_to_float(self._entry.text()))
                new_value: T = int(int_value)  # type: ignore[assignment]
            elif self._entry_scalar_type == float:
                float_value: float = str_to_float(self._entry.text())
                new_value: T = float(float_value)  # type: ignore[assignment]
            elif self._entry_scalar_type == str:
                new_value: T = self._entry.text()  # type: ignore[assignment]
            elif self._entry_scalar_type == bool:
                new_value: T = bool(self._entry.text())  # type: ignore[assignment]
            elif self._entry_scalar_type == Timestamp:
                new_value: T = Timestamp(self._entry.text())  # type: ignore[assignment]
            else:
                raise ValueError(f"Invalid scalar type: {self._entry_scalar_type}")

            self._observable.set_value(new_value)
        except ValueError:
            self.force_update_widget_from_observable()
            return

    def update_widget_non_empty(self):
        self._entry.setEnabled(True)
        self._unit_label.setEnabled(True)
        self._entry.setText(self._format_function(self._observable.value))
        if isinstance(self._observable.value, HasUnit):
            self._unit_label.setText(self._observable.value.unit.format_string(as_fraction=True))
        else:
            self._unit_label.setText("")

    def update_widget_empty(self) -> None:
        self._entry.setEnabled(False)
        self._unit_label.setEnabled(False)
        self._entry.clear()
        self._unit_label.clear()

    @property
    def entry(self) -> QLineEdit:
        return self._entry
    
    @property
    def unit_label(self) -> QLabel:
        return self._unit_label