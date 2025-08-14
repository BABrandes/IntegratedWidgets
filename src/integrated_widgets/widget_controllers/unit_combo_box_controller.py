from __future__ import annotations

"""UnitComboBoxController

Controller that binds an editable combo box to a unit selection observable or
to a provided Unit/Dimension. It validates user-typed units against the
configured dimension, adds valid new units to the observable's options, and
reverts invalid edits.
"""

from typing import Callable, Optional, overload

from PySide6.QtWidgets import QWidget

from integrated_widgets.widget_controllers.base_controller import ObservableController
from integrated_widgets.util.observable_protocols import ObservableSelectionOptionLike, ObservableSelectionOption
from integrated_widgets.guarded_widgets import GuardedEditableComboBox

from united_system import Unit, Dimension

Model = ObservableSelectionOptionLike[Unit] | ObservableSelectionOption[Unit]

class UnitComboBoxController(ObservableController[Model]):

    @overload
    def __init__(
        self,
        observable: Model,
        *,
        formatter: Callable[[Unit], str] = lambda u: u.format_string(as_fraction=True),
        adding_unit_options_allowed: bool = True,
        parent: Optional[QWidget] = None,
    ) -> None: ...

    @overload
    def __init__(
        self,
        unit: Unit,
        *,
        formatter: Callable[[Unit], str] = lambda u: u.format_string(as_fraction=True),
        adding_unit_options_allowed: bool = True,
        parent: Optional[QWidget] = None,
    ) -> None: ...

    @overload
    def __init__(
        self,
        dimension: Dimension,
        *,
        formatter: Callable[[Unit], str] = lambda u: u.format_string(as_fraction=True),
        adding_unit_options_allowed: bool = True,
        parent: Optional[QWidget] = None,
    ) -> None: ...  # type: ignore[override]

    @overload
    def __init__(
        self,
        no_unit: None = None,
        *,
        formatter: Callable[[Unit], str] = lambda u: u.format_string(as_fraction=True),
        adding_unit_options_allowed: bool = True,
        parent: Optional[QWidget] = None,
    ) -> None: ...  # type: ignore[override]

    def __init__(  # type: ignore[override]
        self,
        observable_or_unit: Model | Unit | Dimension | None,
        *,
        formatter: Callable[[Unit], str] = lambda u: u.format_string(as_fraction=True),
        adding_unit_options_allowed: bool = True,
        parent: Optional[QWidget] = None,
    ) -> None:  # type: ignore[override]

        self._formatter = formatter
        self._adding_unit_options_allowed = adding_unit_options_allowed

        # Resolve model and dimension
        if observable_or_unit is None:
            super().__init__(ObservableSelectionOption(selected_option=None, options=set(), allow_none=True), parent=parent)
        elif isinstance(observable_or_unit, ObservableSelectionOption):
            super().__init__(observable_or_unit, parent=parent)
        elif isinstance(observable_or_unit, ObservableSelectionOptionLike):
            super().__init__(observable_or_unit, parent=parent)
        elif isinstance(observable_or_unit, Unit):
            unit: Unit = observable_or_unit
            super().__init__(ObservableSelectionOption(selected_option=unit, options={unit}, allow_none=False), parent=parent)
        elif isinstance(observable_or_unit, Dimension):
            canonical_unit: Unit = observable_or_unit.canonical_unit
            super().__init__(ObservableSelectionOption(selected_option=canonical_unit, options={canonical_unit}, allow_none=False), parent=parent)
        else:
            raise TypeError("UnitComboBoxController expects an observable, Unit or Dimension")
        
    ###########################################################################
    # Hooks
    ###########################################################################

    def initialize_widgets(self) -> None:
        self._combo = GuardedEditableComboBox(self.owner_widget)
        self._combo.currentIndexChanged.connect(lambda _i: self._on_index_changed())
        self._combo.lineEdit().editingFinished.connect(self._on_edit_finished)  # type: ignore[union-attr]

    def update_widgets_from_observable(self) -> None:
        # Rebuild from model
        options: set[Unit]
        try:
            options = set(self._observable.options)  # type: ignore[attr-defined]
        except Exception:
            options = set()
        try:
            selected: Optional[Unit] = self._observable.selected_option
        except Exception:
            selected = None
        self._combo.blockSignals(True)
        try:
            with self._internal_update():
                self._combo.clear()
                for unit_option in sorted(options, key=lambda x: str(x)):
                    self._combo.addItem(str(unit_option), userData=unit_option)
                # select
                if selected is not None:
                    for i in range(self._combo.count()):
                        if self._combo.itemData(i) == selected:
                            self._combo.setCurrentIndex(i)
                            break
                    formatted_selected_text: str = self._formatter(selected)
                    self._combo.setEditText(formatted_selected_text)
        finally:
            self._combo.blockSignals(False)

    def update_observable_from_widgets(self) -> None:
        idx = self._combo.currentIndex()
        if idx < 0:
            return
        u = self._combo.itemData(idx)
        try:
            self._observable.selected_option = u  # type: ignore[attr-defined]
        except Exception:
            pass

    def _on_index_changed(self) -> None:
        if self.is_blocking_signals:
            return
        self.update_observable_from_widgets()

    def _on_edit_finished(self) -> None:    
        if self.is_blocking_signals:
            return

        current_text: str = self._combo.currentText().strip()
        if current_text == "":
            self.update_widgets_from_observable()
            return
        try:
            parsed_unit: Unit = Unit(current_text)

            selected_unit: Optional[Unit] = self._observable.selected_option
            if selected_unit is not None:
                if not parsed_unit.compatible_to(selected_unit.dimension):
                    raise ValueError("unit incompatible with dimension")
                if parsed_unit not in self._observable.options:
                    if not self._adding_unit_options_allowed:
                        raise ValueError("unit not in options and adding unit options is not allowed")
                    self._observable.options.add(parsed_unit)
        except Exception:
            # revert
            self.update_widgets_from_observable()
            return
        # Add if new and select
        try:
            options_set: set[Unit] = set(self._observable.options)  # type: ignore[attr-defined]
            if parsed_unit not in options_set:
                options_set.add(parsed_unit)
                self._observable.options = options_set  # type: ignore[attr-defined]
            self._observable.selected_option = parsed_unit  # type: ignore[attr-defined]
            self.update_widgets_from_observable()
        except Exception:
            pass

    ###########################################################################
    # Properties
    ###########################################################################

    @property
    def widget_combobox(self) -> GuardedEditableComboBox:
        return self._combo
    
    @property
    def adding_unit_options_allowed(self) -> bool:
        return self._adding_unit_options_allowed
    
    @adding_unit_options_allowed.setter
    def adding_unit_options_allowed(self, value: bool) -> None:
        self._adding_unit_options_allowed = value


