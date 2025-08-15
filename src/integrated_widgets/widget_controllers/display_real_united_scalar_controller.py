from __future__ import annotations

from typing import Callable, Optional, overload

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget

from united_system import RealUnitedScalar, Unit

from integrated_widgets.widget_controllers.base_controller import ObservableController
from integrated_widgets.util.observable_protocols import ObservableSingleValueLike
from observables import ObservableSingleValue
from integrated_widgets.guarded_widgets import GuardedLabel, GuardedComboBox
from integrated_widgets.util.general import DEFAULT_FLOAT_FORMAT_VALUE

Observable = ObservableSingleValueLike[RealUnitedScalar] | ObservableSingleValue[RealUnitedScalar]

class DisplayRealUnitedScalarController(ObservableController[Observable]):
    
    @overload
    def __init__(
        self,
        observable: Observable,
        unit_options: Optional[list[Unit]] = None,
        formatter: Callable[[RealUnitedScalar], str] = DEFAULT_FLOAT_FORMAT_VALUE,
        *,
        parent: Optional[QWidget] = None,
    ) -> None: ...

    @overload
    def __init__(
        self,
        value: RealUnitedScalar,
        unit_options: Optional[list[Unit]] = None,
        formatter: Callable[[RealUnitedScalar], str] = DEFAULT_FLOAT_FORMAT_VALUE,
        *,
        parent: Optional[QWidget] = None,
    ) -> None: ...

    def __init__(  # type: ignore
        self,
        observable_or_value,
        unit_options: Optional[list[Unit]] = None,
        formatter: Callable[[RealUnitedScalar], str] = DEFAULT_FLOAT_FORMAT_VALUE,
        *,
        parent: Optional[QWidget] = None,
    ) -> None:
        
        if isinstance(observable_or_value, (ObservableSingleValueLike, ObservableSingleValue)):
            observable: Observable = observable_or_value
        elif isinstance(observable_or_value, RealUnitedScalar):
            observable: Observable = ObservableSingleValue(observable_or_value)
        else:
            raise TypeError(f"Invalid type for observable_or_value: {type(observable_or_value)}")
        self._formatter = formatter
        self._unit_options_input = unit_options
        super().__init__(observable, parent=parent)

    ###########################################################################
    # Hooks
    ###########################################################################

    def initialize_widgets(self) -> None:
        self._label = GuardedLabel(self.owner_widget)
        self._label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self._combo = GuardedComboBox(self.owner_widget)
        self._combo.currentIndexChanged.connect(lambda _i: self._on_unit_changed())

    def update_widgets_from_observable(self) -> None:
        try:
            value = self._observable.single_value
        except Exception:
            with self._internal_update():
                self._label.setText("")
                self._combo.clear()
            return
        # Label
        with self._internal_update():
            self._label.setText(self._formatter(value))
        # Units
        units = self._unit_options_input or self._unit_options_for(value)
        self._rebuild_units(units)
        self._select_unit(value.unit)

    def update_observable_from_widgets(self) -> None:
        idx = self._combo.currentIndex()
        if idx < 0:
            return
        new_unit = self._combo.itemData(idx)
        if new_unit is None:
            return
        current = self._observable.single_value
        if current.unit == new_unit:
            return
        new_value: RealUnitedScalar = RealUnitedScalar(current.canonical_value, current.dimension, display_unit=new_unit)
        self._observable.single_value = new_value

    ###########################################################################
    # Internal
    ###########################################################################

    def _on_unit_changed(self) -> None:
        if self.is_blocking_signals:
            return
        self.update_observable_from_widgets()

    def _unit_options_for(self, value: RealUnitedScalar) -> list[Unit]:
        canonical = value.dimension.canonical_unit
        units: list[Unit] = [canonical]
        try:
            km = Unit("km")
            if km.compatible_to(value.dimension) and km != canonical:
                units.append(km)
        except Exception:
            pass
        if value.unit not in units:
            units.append(value.unit)
        return units

    def _rebuild_units(self, units: list[Unit]) -> None:
        self._combo.blockSignals(True)
        try:
            with self._internal_update():
                self._combo.clear()
            for unit in units:
                with self._internal_update():
                    self._combo.addItem(str(unit), userData=unit)
        finally:
            self._combo.blockSignals(False)

    def _select_unit(self, unit: Unit) -> None:
        self._combo.blockSignals(True)
        try:
            for i in range(self._combo.count()):
                if self._combo.itemData(i) == unit:
                    with self._internal_update():
                        self._combo.setCurrentIndex(i)
                    return
            with self._internal_update():
                self._combo.setCurrentIndex(-1)
        finally:
            self._combo.blockSignals(False)

    ###########################################################################
    # Public accessors
    ###########################################################################

    @property
    def widget_value_label(self) -> GuardedLabel:
        return self._label

    @property
    def widget_unit_combo(self) -> GuardedComboBox:
        return self._combo

    def dispose_before_children(self) -> None:
        try:
            self._combo.currentIndexChanged.disconnect()
        except Exception:
            pass


