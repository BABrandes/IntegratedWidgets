from __future__ import annotations

import sys
from typing import Any

from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel

from integrated_widgets import (
    DisplayRealUnitedScalarController,
    ComboBoxController,
    EditRealUnitedScalarController,
)
from observables import ObservableSingleValue
from united_system import RealUnitedScalar, Unit


def build_demo_window() -> QWidget:
    window = QWidget()
    layout = QVBoxLayout(window)
    layout.setContentsMargins(12, 12, 12, 12)
    layout.setSpacing(12)

    # RealUnitedScalar demo: value label + unit selector
    length = ObservableSingleValue(RealUnitedScalar(10, Unit("m")))
    layout.addWidget(QLabel("RealUnitedScalar display (value + unit):"))
    c_display = DisplayRealUnitedScalarController(length)
    layout.addWidget(c_display.owner_widget)
    layout.addWidget(QLabel("RealUnitedScalar edit (value + unit via text):"))
    c_edit = EditRealUnitedScalarController(length)
    layout.addWidget(c_edit.owner_widget)
    # Status label for current observable value
    status_length = QLabel()
    layout.addWidget(QLabel("Current RealUnitedScalar observable:"))
    layout.addWidget(status_length)

    def _update_length_label() -> None:
        val = length.value
        try:
            status_length.setText(f"{val.value():.3f} {val.unit} (canonical={val.canonical_value} {val.dimension.canonical_unit})")
        except Exception:
            status_length.setText(str(val))

    length.add_listeners(_update_length_label)
    _update_length_label()

    # Selection combo demo using ObservableSelectionOption if available
    try:
        from observables.examples.demo import ObservableSelectionOption  # type: ignore

        selection = ObservableSelectionOption(
            selected_option="A",
            options={"A", "B", "C"},
            allow_none=True,
        )
        layout.addWidget(QLabel("SelectionComboBox demo:"))
        c_combo = ComboBoxController(selection)
        layout.addWidget(c_combo.owner_widget)
        # Status label for current selection observable
        status_sel = QLabel()
        layout.addWidget(QLabel("Current Selection observable:"))
        layout.addWidget(status_sel)

        def _update_sel_label() -> None:
            try:
                status_sel.setText(f"selected={selection.selected_option} options={sorted(selection.options)}")
            except Exception as e:
                status_sel.setText(f"error: {e}")

        selection.add_listeners(_update_sel_label)
        _update_sel_label()
    except Exception as e:  # pragma: no cover - optional runtime feature
        layout.addWidget(QLabel(f"SelectionComboBox demo unavailable: {e}"))

    window.setLayout(layout)
    window.setWindowTitle("Integrated Widgets Demo")
    return window


def main(argv: list[str] | None = None) -> int:
    app = QApplication.instance() or QApplication(sys.argv if argv is None else argv)
    w = build_demo_window()
    w.resize(400, 160)
    w.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())


