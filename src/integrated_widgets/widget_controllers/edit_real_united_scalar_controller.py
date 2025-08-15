from __future__ import annotations

from typing import Callable, Optional, overload

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget

from united_system import RealUnitedScalar, Unit, Dimension

from integrated_widgets.widget_controllers.base_controller import ObservableController
from integrated_widgets.util.observable_protocols import ObservableSingleValueLike
from observables import ObservableSingleValue
from integrated_widgets.guarded_widgets import GuardedLineEdit, GuardedLabel
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
        # Display label for the full RealUnitedScalar (e.g., "10.000 m")
        self._display_label = GuardedLabel(self.owner_widget)
        with self._internal_update():
            self._display_label.setText("")
        # Separate edits for value and unit
        self._value_edit = GuardedLineEdit(self.owner_widget)
        self._value_edit.setPlaceholderText("value (e.g., 10)")
        self._unit_edit = GuardedLineEdit(self.owner_widget)
        self._unit_edit.setPlaceholderText("unit (e.g., m, km, V)")
        # Combined entry that accepts strings like "10 m"
        self._combined_edit = GuardedLineEdit(self.owner_widget)
        self._combined_edit.setPlaceholderText("value with unit (e.g., 10 m)")
        # Connect UI -> model
        self._value_edit.editingFinished.connect(self._on_edited)
        self._unit_edit.editingFinished.connect(self._on_edited)
        self._combined_edit.editingFinished.connect(self._on_combined_edited)

    def update_widgets_from_observable(self) -> None:
        try:
            value = self._observable.single_value
        except Exception:
            with self._internal_update():
                self._value_edit.setText("")
                self._unit_edit.setText("")
            return
        # Update discrete widgets
        with self._internal_update():
            # Value field shows only the numeric part
            self._value_edit.setText(f"{value.value():.3f}")
            # Unit field shows unit symbol
            self._unit_edit.setText(str(value.unit))
            # Display label shows the fully formatted value (using provided formatter)
            self._display_label.setText(self._formatter(value))
            # Combined text mirrors the formatted label for convenience
            self._combined_edit.setText(f"{value.value():.3f} {value.unit}")

    def update_observable_from_widgets(self) -> None:
        # Discrete fields only: parse value and unit separately
        unit_text = self._unit_edit.text().strip()
        value_text = self._value_edit.text().strip()
        if not unit_text or not value_text:
            return
        try:
            desired_unit = Unit(unit_text)
        except Exception:
            cur = self._observable.single_value
            with self._internal_update():
                self._unit_edit.setText(str(cur.unit))
            return
        try:
            desired_value = float(value_text)
        except Exception:
            cur = self._observable.single_value
            with self._internal_update():
                self._value_edit.setText(f"{cur.value():.3f}")
            return
        new_value = RealUnitedScalar(desired_value, desired_unit)
        cur = self._observable.single_value
        # Enforce allowed dimension
        if self._allowed_dimension is not None and not new_value.unit.compatible_to(self._allowed_dimension):
            with self._internal_update():
                self._combined_edit.setText(f"{cur.value():.3f} {cur.unit}")
                self._unit_edit.setText(str(cur.unit))
            return
        # Skip if no change (compare numeric value in current unit and symbol)
        if str(new_value.unit) == str(cur.unit) and abs(new_value.value() - cur.value()) < 1e-12:
            return
        # Validate
        if self._validator is not None and not self._validator(new_value):
            with self._internal_update():
                self._value_edit.setText(f"{cur.value():.3f}")
                self._unit_edit.setText(str(cur.unit))
                self._combined_edit.setText(f"{cur.value():.3f} {cur.unit}")
            return
        self._observable.single_value = new_value

    def _on_combined_edited(self) -> None:
        if self.is_blocking_signals:
            return
        text = self._combined_edit.text().strip()
        if not text:
            return
        try:
            new_value = RealUnitedScalar(text)
        except Exception:
            # Revert combined field on parse error
            cur = self._observable.single_value
            with self._internal_update():
                self._combined_edit.setText(f"{cur.value():.3f} {cur.unit}")
            return
        cur = self._observable.single_value
        if self._allowed_dimension is not None and not new_value.unit.compatible_to(self._allowed_dimension):
            with self._internal_update():
                self._combined_edit.setText(f"{cur.value():.3f} {cur.unit}")
            return
        if self._validator is not None and not self._validator(new_value):
            with self._internal_update():
                self._combined_edit.setText(f"{cur.value():.3f} {cur.unit}")
            return
        if str(new_value.unit) == str(cur.unit) and abs(new_value.value() - cur.value()) < 1e-12:
            return
        self._observable.single_value = new_value

    ###########################################################################
    # Events / disposal
    ###########################################################################
    
    def _on_edited(self) -> None:
        if self.is_blocking_signals:
            return
        self.update_observable_from_widgets()

        # No separate handler needed for the combined entry; parsing handled in update_observable_from_widgets

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
    def widget_value_line_edit(self) -> GuardedLineEdit:
        return self._value_edit

    @property
    def widget_unit_line_edit(self) -> GuardedLineEdit:
        return self._unit_edit

    @property
    def widget_display_label(self) -> GuardedLabel:
        return self._display_label

    @property
    def widget_value_with_unit_line_edit(self) -> GuardedLineEdit:
        return self._combined_edit


