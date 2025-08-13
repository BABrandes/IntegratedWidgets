from PySide6.QtWidgets import QWidget
from .base_observable_widget import BaseWidget_With_Observable
from python.gui.custom_widgets.positive_integer_entry import CQ_PositiveIntegerEntry, CQ_PositiveIntegerEntry_Empty

from observables import ObservableSingleValue

class ObsQIntegerEntry(BaseWidget_With_Observable[ObservableSingleValue[int]]):
    def __init__(self, initial_value_or_observable: int | ObservableSingleValue[int], lower_bound: int, upper_bound: int, parent: QWidget | None = None):

        if isinstance(initial_value_or_observable, int):
            observable = ObservableSingleValue(initial_value_or_observable)
        else:
            observable = initial_value_or_observable

        super().__init__(observable, parent)
        
        self._lower_bound = lower_bound
        self._upper_bound = upper_bound
        self._entry: CQ_PositiveIntegerEntry | CQ_PositiveIntegerEntry_Empty = CQ_PositiveIntegerEntry(inital_valid_value=0, lower_bound=lower_bound, upper_bound=upper_bound, parent=self)
        self._entry.editingFinished.connect(self._internal_update_observable)

        self.construction_finished()

    def update_widget(self):
        if isinstance(self._entry, CQ_PositiveIntegerEntry):
            self._entry.set_int_value(self.observable.value)
        else:
            self._entry = CQ_PositiveIntegerEntry(inital_valid_value=self.observable.value, lower_bound=self._lower_bound, upper_bound=self._upper_bound, parent=self)

    def update_observable(self):
        if isinstance(self._entry, CQ_PositiveIntegerEntry):
            self.observable.set_value(self._entry.int_value)
        else:
            raise RuntimeError("Should not happen")