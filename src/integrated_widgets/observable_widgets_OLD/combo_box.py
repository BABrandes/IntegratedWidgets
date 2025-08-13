from typing import Any, Callable, Generic, Optional, TypeVar
from PySide6.QtWidgets import QComboBox, QHBoxLayout
from .base_observable_widget import BaseWidget_With_Observable

from observables import ObservableSelectionOption

T = TypeVar('T')

counter_for_debug: int = 0

class ObsQComboBox(BaseWidget_With_Observable[ObservableSelectionOption[T]], Generic[T]):
    """
    A QFrame encapsulating a QComboBox bound to an ObservableSelectionOption.

    The widget is disabled when the observable is None.

    The widget is enabled when the observable is not None.

    The widget is updated to reflect the current value of the observable when the observable is not None.

    The observable is updated to reflect the current value of the widget when the widget is changed.
    """
    def __init__(
        self,
        observable: ObservableSelectionOption[T],
        format_function: Callable[[T], str] = lambda x: str(x),
        sort_function: Callable[[set[T]], list[T]] = lambda items: sorted(items, key=lambda x: str(x)),
        parent=None, name_for_debug: str = "",
    ) -> None:
        
        super().__init__(observable, parent)

        self._format_function: Callable[[T], str] = format_function
        self._sort_function: Callable[[set[T]], list[T]] = sort_function
        self._combobox: QComboBox = QComboBox(self)
        self._name_for_debug: str = name_for_debug

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
            if data != self.observable.selected_option:
                self.observable.set_selected_option(data)
        elif index == -1 and self.observable.is_none_selection_allowed:
            self.observable.set_selected_option(None)
        else:
            raise ValueError(f"Index {index} is not valid.")
        
    def _reconstruct_options(self) -> None:
        self._combobox.blockSignals(True)
        self._combobox.clear()
        
        # Add None option first if can_be_none is True
        if self.observable.is_none_selection_allowed:
            self._combobox.addItem("", None)
        
        # Add all other options
        if self._sort_function is None:
            for option in self.observable.options:
                self._combobox.addItem(self._format_function(option), option)
        else:
            for option in self._sort_function(self.observable.options):
                self._combobox.addItem(self._format_function(option), option)
        
        self._combobox.blockSignals(False)

    def update_widget(self) -> None:

        self._combobox.setEnabled(True)

        # Step 1: Check if the observable available items are the same as the combobox items

        # Step 1a: Check the length of the observable options and the combobox items
        expected_count = len(self.observable.options)
        if self.observable.is_none_selection_allowed:
            expected_count += 1  # Add 1 for the None option
        
        if expected_count != self._combobox.count():
            self._reconstruct_options()

        # Step 1b: Loop over the observable options and the combobox items and check if they are the same
        for option in self.observable.options:
            if self._find_data(option) == -1:
                self._reconstruct_options()
                break

        # Step 2: Select the right item from the observable options
        if self.observable.selected_option is None:
            if self.observable.is_none_selection_allowed:
                self._combobox.setCurrentIndex(0)  # Select the None option
            else:
                # This shouldn't happen, but handle gracefully
                if self._combobox.count() > 0:
                    self._combobox.setCurrentIndex(0)
        else:
            index_of_selection: int = self._find_data(self.observable.selected_option)
            if index_of_selection == -1:
                # Current selection is not in available options, need to choose a new one
                if self.observable.is_none_selection_allowed:
                    self._combobox.setCurrentIndex(0)
                    if self.observable.selected_option is not None:
                        self.observable.set_selected_option(None)
                elif self._combobox.count() > 0:
                    self._combobox.setCurrentIndex(0)
                    fallback_option = self._combobox.itemData(0)
                    if fallback_option is not None and self.observable.selected_option != fallback_option:
                        self.observable.set_selected_option(fallback_option)
                else:
                    self._combobox.setCurrentIndex(-1)
            else:
                self._combobox.setCurrentIndex(index_of_selection)

        # Debug output
        if self._name_for_debug != "":
            print(f"DEBUG: {self._name_for_debug} - ComboBox items:")
            for i in range(self._combobox.count()):
                text = self._combobox.itemText(i)
                data = self._combobox.itemData(i)
                print(f"  Item {i}: text='{text}', data={data}")
            print(f"  Current index: {self._combobox.currentIndex()}")
            print(f"  Observable selection: {self.observable.selected_option}")
            print(f"  Can be none: {self.observable.is_none_selection_allowed}")
            print("")

    def _find_data(self, item_data: Any) -> int:
        for i in range(self._combobox.count()):
            if self._combobox.itemData(i) == item_data:
                return i
        return -1



