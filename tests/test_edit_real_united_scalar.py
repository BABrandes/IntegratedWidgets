from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from pytestqt.qtbot import QtBot

from united_system import RealUnitedScalar, Unit
from integrated_widgets import EditRealUnitedScalarController


@pytest.mark.qt_log_ignore(".*")
def test_edit_real_united_scalar_constructs_and_sets(qtbot: QtBot):
    app = QApplication.instance() or QApplication([])
    c = EditRealUnitedScalarController(RealUnitedScalar(10, Unit("m")))  # type: ignore
    qtbot.addWidget(c._owner_widget)
    
    # Test initial state
    assert c.single_value == RealUnitedScalar(10, Unit("m"))
    
    # Test unit change
    c.single_value = RealUnitedScalar(10, Unit("km"))
    assert c.single_value == RealUnitedScalar(10, Unit("km"))


@pytest.mark.qt_log_ignore(".*")
def test_edit_real_united_scalar_combined_parsing_and_dimension_guard(qtbot: QtBot) -> None:
    app = QApplication.instance() or QApplication([])

    length = Unit("m").dimension
    c = EditRealUnitedScalarController(RealUnitedScalar(10, Unit("m")), allowed_dimension=length)  # type: ignore
    qtbot.addWidget(c._owner_widget)

    combined = c.widget_value_with_unit_line_edit
    combined.setText("10 kg")
    combined.editingFinished.emit()  # type: ignore[attr-defined]
    assert str(c.single_value.unit) == "m"

    combined.setText("12 km")
    combined.editingFinished.emit()  # type: ignore[attr-defined]
    assert str(c.single_value.unit) == "km"
    assert abs(c.single_value.value() - 12.0) < 1e-9

