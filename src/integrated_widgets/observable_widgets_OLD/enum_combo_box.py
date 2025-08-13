from typing import Any, Callable, Generic, TypeVar
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QWidget
from .base_observable_widget import BaseWidget_With_Observable
from enum import Enum
from python.common.serialization.serializable_enum import JSON_HDF5_SerializableEnum

from observables import ObservableEnum

E = TypeVar("E", bound=Enum|JSON_HDF5_SerializableEnum)

counter_for_debug: int = 0

class ObsQEnumComboBox(BaseWidget_With_Observable[ObservableEnum[E]], Generic[E]):
    def __init__(
            self,
            initial_enum_value_or_observable: E|ObservableEnum[E],
            available_enum_values: set[E]|None = None,
            format_function: Callable[[E], str] = lambda x: x.value,
            sort_function: Callable[[set[E]], list[E]] = lambda items: sorted(items, key=lambda x: str(x)),
            parent: QWidget | None = None,
    ) -> None:

        if isinstance(initial_enum_value_or_observable, Enum):
            if available_enum_values is None:
                enum_options: set[E] = set(initial_enum_value_or_observable.__class__)
            else:
                enum_options: set[E] = available_enum_values
            observable: ObservableEnum[E] = ObservableEnum(enum_value=initial_enum_value_or_observable, enum_options=enum_options)
        elif isinstance(initial_enum_value_or_observable, ObservableEnum):
            enum_options = initial_enum_value_or_observable.enum_options
        else:
            raise ValueError(f"Invalid observable: {initial_enum_value_or_observable}")
        
        super().__init__(observable, parent)

        self._format_function: Callable[[E], str] = format_function
        self._sort_function: Callable[[set[E]], list[E]] = sort_function

        self._combobox: QComboBox = QComboBox(self)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._combobox)
        self.setLayout(layout)

        # Connect UI -> Observable
        self._combobox.currentIndexChanged.connect(lambda _idx: self._internal_update_observable())

        self.construction_finished()

    def update_observable(self) -> None:
        index = self._combobox.currentIndex()
        if index != -1:
            data = self._combobox.itemData(index)
            if data != self.observable.enum_value:
                self.observable.set_enum_value(data)
        elif index == -1 and self.observable:
            self.observable.set_enum_value(None)
        else:
            raise ValueError(f"Index {index} is not valid.")
        
    def _reconstruct_options(self) -> None:
        self._combobox.blockSignals(True)
        self._combobox.clear()
        
        # Add None option first if can_be_none is True
        if self.observable.is_none_enum_value_allowed:
            self._combobox.addItem("", None)
        
        # Add all other options
        if self._sort_function is None:
            for option in self.observable.enum_options:
                self._combobox.addItem(self._format_function(option), option)
        else:
            for option in self._sort_function(self.observable.enum_options):
                self._combobox.addItem(self._format_function(option), option)
        
        self._combobox.blockSignals(False)

    def update_widget(self) -> None:

        self._combobox.setEnabled(True)

        # Step 1: Check if the observable available items are the same as the combobox items

        # Step 1a: Check the length of the observable options and the combobox items
        expected_count = len(self.observable.enum_options)
        if self.observable.is_none_enum_value_allowed:
            expected_count += 1  # Add 1 for the None option
        
        if expected_count != self._combobox.count():
            self._reconstruct_options()

        # Step 1b: Loop over the observable options and the combobox items and check if they are the same
        for option in self.observable.enum_options:
            if self._find_data(option) == -1:
                self._reconstruct_options()
                break

        # Step 2: Select the right item from the observable options
        if self.observable.enum_value is None:
            if self.observable.is_none_enum_value_allowed:
                self._combobox.setCurrentIndex(0)  # Select the None option
            else:
                # This shouldn't happen, but handle gracefully
                if self._combobox.count() > 0:
                    self._combobox.setCurrentIndex(0)
        else:
            index_of_selection: int = self._find_data(self.observable.enum_value)
            if index_of_selection == -1:
                # Current selection is not in available options, need to choose a new one
                if self.observable.is_none_enum_value_allowed:
                    self._combobox.setCurrentIndex(0)
                    if self.observable.enum_value is not None:
                        self.observable.set_enum_value(None)
                elif self._combobox.count() > 0:
                    self._combobox.setCurrentIndex(0)
                    fallback_option = self._combobox.itemData(0)
                    if fallback_option is not None and self.observable.enum_value != fallback_option:
                        self.observable.set_enum_value(fallback_option)
                else:
                    self._combobox.setCurrentIndex(-1)
            else:
                self._combobox.setCurrentIndex(index_of_selection)

    def _find_data(self, item_data: Any) -> int:
        for i in range(self._combobox.count()):
            if self._combobox.itemData(i) == item_data:
                return i
        return -1
    
    def select_enum(self, enum_value: E) -> None:
        index_of_selection: int = self._find_data(enum_value)
        if index_of_selection != -1:
            self._combobox.setCurrentIndex(index_of_selection)
        else:
            raise ValueError(f"Enum value {enum_value} not found in combobox")