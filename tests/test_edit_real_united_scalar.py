from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication, QLabel, QLineEdit

from integrated_widgets import EditRealUnitedScalarController
from observables import ObservableSingleValue
from united_system import RealUnitedScalar, Unit


@pytest.mark.qt_log_ignore(".*")
def test_edit_real_united_scalar_change_unit(qtbot):
    app = QApplication.instance() or QApplication([])
    osv = ObservableSingleValue(RealUnitedScalar(10, Unit("m")))
    c = EditRealUnitedScalarController(osv)
    qtbot.addWidget(c.owner_widget)

    value_edit = c.value_line_edit
    unit_edit = c.unit_line_edit
    # Initial state
    assert value_edit.text().startswith("10.000")
    assert unit_edit.text() == "m"

    # Change unit to km (value stays the same display number)
    unit_edit.setText("km")
    unit_edit.editingFinished.emit()
    qtbot.waitUntil(lambda: unit_edit.text() == "km", timeout=1000)
    # Expect 10.000 km displayed (dimension changed display unit, value preserved as display number)
    assert value_edit.text().startswith("10.000")

    # Change value to 5 in km
    value_edit.setText("5")
    value_edit.editingFinished.emit()
    qtbot.waitUntil(lambda: value_edit.text().startswith("5"), timeout=1000)


