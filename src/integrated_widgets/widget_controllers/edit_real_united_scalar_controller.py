from __future__ import annotations

from typing import Callable, Optional, overload

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget

from united_system import RealUnitedScalar, Unit, Dimension

from integrated_widgets.widget_controllers.base_controller import ObservableController
from integrated_widgets.util.observable_protocols import (
    ObservableSingleValueLike,
    ObservableSingleValue,
)
from integrated_widgets.guarded_widgets import GuardedLineEdit
from integrated_widgets.util.general import DEFAULT_FLOAT_FORMAT_VALUE


Observable = ObservableSingleValueLike[RealUnitedScalar] | ObservableSingleValue[RealUnitedScalar]


class EditRealUnitedScalarController(ObservableController[Observable]):
    @overload
    def __init__(
        self,
        observable: Observable,
        *,
        allowed_dimension: Optional[Dimension] = None,
        validator: Optional[Callable[[RealUnitedScalar], bool]] = None,
        formatter: Callable[[RealUnitedScalar], str] = DEFAULT_FLOAT_FORMAT_VALUE,
        parent: Optional[QWidget] = None,
    ) -> None: ...

    @overload
    def __init__(
        self,
        value: RealUnitedScalar,
        *,
        allowed_dimension: Optional[Dimension] = None,
        validator: Optional[Callable[[RealUnitedScalar], bool]] = None,
        formatter: Callable[[RealUnitedScalar], str] = DEFAULT_FLOAT_FORMAT_VALUE,
        parent: Optional[QWidget] = None,
    ) -> None: ...

    def __init__(  # type: ignore
        self,
        observable_or_value,
        *,
        allowed_dimension: Optional[Dimension] = None,
        validator: Optional[Callable[[RealUnitedScalar], bool]] = None,
        formatter: Callable[[RealUnitedScalar], str] = DEFAULT_FLOAT_FORMAT_VALUE,
        parent: Optional[QWidget] = None,
    ) -> None:
        if isinstance(observable_or_value, (ObservableSingleValueLike, ObservableSingleValue)):
            observable: Observable = observable_or_value
        elif isinstance(observable_or_value, RealUnitedScalar):
            observable = ObservableSingleValue(observable_or_value)
        else:
            raise TypeError(f"Invalid type for observable_or_value: {type(observable_or_value)}")

        self._allowed_dimension = allowed_dimension
        self._validator = validator
        self._formatter = formatter
        super().__init__(observable, parent=parent)

    ###########################################################################
    # Hooks
    ###########################################################################

    def initialize_widgets(self) -> None:
        self._value_edit = GuardedLineEdit(self.owner_widget)
        self._value_edit.setPlaceholderText("value")
        self._unit_edit = GuardedLineEdit(self.owner_widget)
        self._unit_edit.setPlaceholderText("unit (e.g., m, km, V)")
        # Connect UI -> model
        self._value_edit.editingFinished.connect(self._on_edited)
        self._unit_edit.editingFinished.connect(self._on_edited)

    def update_widgets_from_observable(self) -> None:
        try:
            value = self._observable.value
        except Exception:
            with self._internal_update():
                self._value_edit.setText("")
                self._unit_edit.setText("")
            return
        with self._internal_update():
            self._value_edit.setText(self._formatter(value))
            self._unit_edit.setText(str(value.unit))

    def update_observable_from_widgets(self) -> None:
        unit_text = self._unit_edit.text().strip()
        value_text = self._value_edit.text().strip()
        if not unit_text or not value_text:
            return
        # Parse unit
        try:
            desired_unit = Unit(unit_text)
        except Exception:
            cur = self._observable.value
            with self._internal_update():
                self._unit_edit.setText(str(cur.unit))
            return
        # Parse value
        try:
            desired_value = float(value_text)
        except Exception:
            cur = self._observable.value
            with self._internal_update():
                self._value_edit.setText(self._formatter(cur))
            return
        cur = self._observable.value
        # Enforce allowed dimension
        if self._allowed_dimension is not None and not desired_unit.compatible_to(self._allowed_dimension):
            with self._internal_update():
                self._unit_edit.setText(str(cur.unit))
            return
        # Skip if no change
        if str(desired_unit) == str(cur.unit) and abs(desired_value - cur.value()) < 1e-12:
            return
        # New candidate value
        new_value = RealUnitedScalar(desired_value, desired_unit)
        # Validate
        if self._validator is not None and not self._validator(new_value):
            with self._internal_update():
                self._value_edit.setText(self._formatter(cur))
                self._unit_edit.setText(str(cur.unit))
            return
        self._observable.set_value(new_value)

    ###########################################################################
    # Events / disposal
    ###########################################################################
    
    def _on_edited(self) -> None:
        if self.is_blocking_signals:
            return
        self.update_observable_from_widgets()

    def dispose_before_children(self) -> None:
        try:
            self._value_edit.editingFinished.disconnect()
        except Exception:
            pass
        try:
            self._unit_edit.editingFinished.disconnect()
        except Exception:
            pass

    ###########################################################################
    # Public accessors
    ###########################################################################
    @property
    def value_line_edit(self) -> GuardedLineEdit:
        return self._value_edit

    @property
    def unit_line_edit(self) -> GuardedLineEdit:
        return self._unit_edit


