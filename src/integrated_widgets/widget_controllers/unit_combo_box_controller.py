from __future__ import annotations

"""UnitComboBoxController

Controller that binds an editable combo box to a unit selection observable or
to a provided Unit/Dimension. It validates user-typed units against the
configured dimension, adds valid new units to the observable's options, and
reverts invalid edits.
"""

from typing import Optional, overload

from PySide6.QtWidgets import QWidget

from integrated_widgets.widget_controllers.base_controller import ObservableController
from integrated_widgets.util.observable_protocols import (
    ObservableSelectionOptionLike,
    ObservableSelectionOption,
)
from integrated_widgets.guarded_widgets import GuardedEditableComboBox

from united_system import Unit, Dimension


Model = ObservableSelectionOptionLike[Unit] | ObservableSelectionOption[Unit]


class UnitComboBoxController(ObservableController[Model]):

    @overload
    def __init__(self, observable: Model, *, parent: Optional[QWidget] = None) -> None: ...

    @overload
    def __init__(self, unit: Unit, *, parent: Optional[QWidget] = None) -> None: ...

    @overload
    def __init__(self, dimension: Dimension, *, parent: Optional[QWidget] = None) -> None: ...

    def __init__(self, observable_or_unit, *, parent: Optional[QWidget] = None, dimension: Optional[Dimension] = None) -> None:  # type: ignore[override]
        # Resolve model and dimension
        if isinstance(observable_or_unit, (ObservableSelectionOptionLike, ObservableSelectionOption)):
            model: Model = observable_or_unit
            dim: Optional[Dimension] = dimension
            # Try to infer dimension from selection/options
            if dim is None:
                try:
                    cur = model.selected_option  # type: ignore[attr-defined]
                    if cur is not None:
                        dim = cur.dimension  # type: ignore[attr-defined]
                except Exception:
                    pass
            if dim is None:
                try:
                    any_unit = next(iter(model.options))  # type: ignore[attr-defined]
                    dim = any_unit.dimension  # type: ignore[attr-defined]
                except Exception:
                    pass
            self._dimension = dim
            super().__init__(model, parent=parent)
        elif isinstance(observable_or_unit, Unit):
            u: Unit = observable_or_unit
            self._dimension = u.dimension
            super().__init__(ObservableSelectionOption(selected_option=u, options={u}, allow_none=False), parent=parent)
        elif isinstance(observable_or_unit, Dimension):
            d: Dimension = observable_or_unit
            self._dimension = d
            canonical = d.canonical_unit
            super().__init__(ObservableSelectionOption(selected_option=canonical, options={canonical}, allow_none=False), parent=parent)
        else:
            raise TypeError("UnitComboBoxController expects an observable, Unit or Dimension")

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
            selected = self._observable.selected_option  # type: ignore[attr-defined]
        except Exception:
            selected = None
        self._combo.blockSignals(True)
        try:
            with self._internal_update():
                self._combo.clear()
                for u in sorted(options, key=lambda x: str(x)):
                    self._combo.addItem(str(u), userData=u)
                # select
                if selected is not None:
                    for i in range(self._combo.count()):
                        if self._combo.itemData(i) == selected:
                            self._combo.setCurrentIndex(i)
                            break
                    self._combo.setEditText(str(selected))
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
        if self._dimension is None:
            return
        raw = self._combo.currentText().strip()
        if raw == "":
            self.update_widgets_from_observable()
            return
        try:
            u = Unit(raw)
            if not u.compatible_to(self._dimension):
                raise ValueError("unit incompatible with dimension")
        except Exception:
            # revert
            self.update_widgets_from_observable()
            return
        # Add if new and select
        try:
            options: set[Unit] = set(self._observable.options)  # type: ignore[attr-defined]
            if u not in options:
                options.add(u)
                self._observable.options = options  # type: ignore[attr-defined]
            self._observable.selected_option = u  # type: ignore[attr-defined]
            self.update_widgets_from_observable()
        except Exception:
            pass

    @property
    def combo(self) -> GuardedEditableComboBox:
        return self._combo


