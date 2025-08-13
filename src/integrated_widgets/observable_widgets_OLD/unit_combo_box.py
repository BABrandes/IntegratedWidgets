from typing import Callable, Optional
from PySide6.QtWidgets import QComboBox, QHBoxLayout
from python.gui.gui_utils import find_data
from united_system import Unit, Dimension
from .base_observable_widget import BaseWidget_With_Observable

from observables import ObservableSelectionOption

UNIT_COMBO_BOX_WIDTH: int = 90

PREPROGRAMMED_UNIT_OPTIONS: dict[Dimension, list[Unit]] = {
    Unit("mV/s").dimension: [Unit("mV/s"), Unit("V/s"), Unit("kV/s")],
    Unit("V").dimension: [Unit("V"), Unit("mV"), Unit("kV")],
}

class ObsQUnitComboBox(BaseWidget_With_Observable[ObservableSelectionOption[Unit]]):
    """
    A QFrame encapsulating a QComboBox bound to an ObservableSelectionOption.
    """

    def __init__(
        self,
        initial_unit_or_dimension_or_observable: Optional[Unit|Dimension|ObservableSelectionOption[Unit]],
        format_function: Callable[[Unit], str] = lambda x: x.format_string(as_fraction=True),
        parent=None,
    ) -> None:
        """
        Args:
            initial_unit_or_dimension: The initial unit or dimension to set the unit combo box to.
            format_function: The function to use to format the unit.
            parent: The parent widget.
        """
        
        self._format_function = format_function

        if initial_unit_or_dimension_or_observable is None:
            initial_unit_or_dimension_or_observable = ObservableSelectionOption(selected_option=None, options=set(), allow_none=True)
        elif isinstance(initial_unit_or_dimension_or_observable, Unit):
            if initial_unit_or_dimension_or_observable.dimension in PREPROGRAMMED_UNIT_OPTIONS:
                unit_options: set[Unit] = set(PREPROGRAMMED_UNIT_OPTIONS[initial_unit_or_dimension_or_observable.dimension])
            else:
                unit_options: set[Unit] = {initial_unit_or_dimension_or_observable}
            unit_observable: ObservableSelectionOption[Unit] = ObservableSelectionOption(selected_option=initial_unit_or_dimension_or_observable, options=unit_options, allow_none=True)
        elif isinstance(initial_unit_or_dimension_or_observable, Dimension):
            if initial_unit_or_dimension_or_observable in PREPROGRAMMED_UNIT_OPTIONS:
                unit_options: set[Unit] = set(PREPROGRAMMED_UNIT_OPTIONS[initial_unit_or_dimension_or_observable])
            else:
                unit_options: set[Unit] = {initial_unit_or_dimension_or_observable.canonical_unit}
            # Prefer canonical unit if available; otherwise pick a deterministic first by string sort
            preferred_unit = initial_unit_or_dimension_or_observable.canonical_unit
            if preferred_unit in unit_options:
                initial_selection: Unit = preferred_unit
            else:
                initial_selection = sorted(unit_options, key=lambda u: str(u))[0]
            unit_observable: ObservableSelectionOption[Unit] = ObservableSelectionOption(selected_option=initial_selection, options=unit_options, allow_none=True)
        elif isinstance(initial_unit_or_dimension_or_observable, ObservableSelectionOption):
            unit_observable: ObservableSelectionOption[Unit] = initial_unit_or_dimension_or_observable
        else:
            raise ValueError(f"Invalid initial unit or dimension: {initial_unit_or_dimension_or_observable}")
        
        super().__init__(unit_observable, parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self._combobox = QComboBox(self)
        layout.addWidget(self._combobox)
        self._combobox.setFixedWidth(UNIT_COMBO_BOX_WIDTH)

        # Connect UI -> Observable
        self._combobox.currentIndexChanged.connect(lambda _idx: self._internal_update_observable())

        self.construction_finished()

    def update_widget(self) -> None:
        self._refresh()

    def _refresh(self) -> None:
        self._combobox.blockSignals(True)
        if self.observable is None:
            self._combobox.clear()
            self._combobox.setCurrentIndex(-1)
        else:
            current_options = set(self.observable.options)
            current_selection = self.observable.selected_option
            for i in range(self._combobox.count() - 1, -1, -1):
                item_data = self._combobox.itemData(i)
                if item_data is not None and item_data not in current_options:
                    self._combobox.removeItem(i)
            if self.observable.is_none_selection_allowed and (self._combobox.count() == 0 or self._combobox.itemData(0) is not None):
                self._combobox.insertItem(0, '', None)
            existing_items = {self._combobox.itemData(i) for i in range(self._combobox.count())}
            current_options_alphabetically_sorted = sorted(current_options, key=lambda x: self._format_function(x))
            for idx, opt in enumerate(current_options_alphabetically_sorted):
                if opt not in existing_items:
                    insert_index = idx + (1 if self.observable.is_none_selection_allowed else 0)
                    self._combobox.insertItem(insert_index, self._format_function(opt), opt)
            existing_items = {self._combobox.itemData(i) for i in range(self._combobox.count())}
            if current_selection is None and self.observable.is_none_selection_allowed:
                self._combobox.setCurrentIndex(0)
            else:
                if current_selection not in current_options:
                    raise ValueError(f"Selection {current_selection} is not in options {current_options}: Should not happen")
                if current_selection not in existing_items:
                    raise ValueError(f"Selection {current_selection} is not in existing items {existing_items}: Should not happen")
                idx = find_data(self._combobox, current_selection)
                if idx != -1:
                    self._combobox.setCurrentIndex(idx)
                elif self.observable.is_none_selection_allowed:
                    self._combobox.setCurrentIndex(0)
                    self.observable.set_selected_option(None)
                else:
                    self._combobox.setCurrentIndex(1 if self.observable.is_none_selection_allowed else 0)
                    self.observable.set_selected_option(self._combobox.itemData(self._combobox.currentIndex()))
        self._combobox.blockSignals(False)

    @property
    def unit(self) -> Optional[Unit]:
        return self.observable.selected_option
    
    @property
    def unit_not_none(self) -> Unit:
        if self.observable is None:
            raise ValueError("An empty unit combo box has no unit")
        return self.observable.selected_option_not_none

    def set_unit(self, unit_or_dimension: Unit|Dimension, replace_none_if_neccessary: bool=True) -> None:
        """
        This method is used to set the unit or dimension of the unit combo box and replace the observable if necessary.

        If replace_none_if_neccessary is True, the observable will be set to the new dimension.
        If replace_none_if_neccessary is False, the observable will not be set to the new dimension and an error will be raised.
        """

        # Get the dimension and initial unit
        if isinstance(unit_or_dimension, Unit):
            dimension = unit_or_dimension.dimension
            initial_unit = unit_or_dimension
        elif isinstance(unit_or_dimension, Dimension):
            dimension = unit_or_dimension
            initial_unit = unit_or_dimension.canonical_unit
        else:
            raise ValueError(f"Invalid unit or dimension: {unit_or_dimension}")

        # Get the unit options
        if dimension in PREPROGRAMMED_UNIT_OPTIONS:
            unit_options: set[Unit] = set(PREPROGRAMMED_UNIT_OPTIONS[dimension])
        else:
            unit_options: set[Unit] = {dimension.canonical_unit}
        
        # Add the initial unit to the options if it is not in the options
        if initial_unit not in unit_options:
            unit_options.add(initial_unit)

        # Create or change the new observable
        if self._observable is None:
            if replace_none_if_neccessary:
                self.set_or_replace_observable(ObservableSelectionOption(selected_option=initial_unit, options=unit_options, allow_none=False))
            else:
                raise ValueError("Cannot set new dimension for a unit combo box without an observable")
        else:
            self._observable.set_options(unit_options)
            self._observable.set_selected_option(initial_unit)