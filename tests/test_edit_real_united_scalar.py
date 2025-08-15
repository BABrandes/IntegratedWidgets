from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from pytestqt.qtbot import QtBot

from observables import ObservableSingleValue
from united_system import RealUnitedScalar, Unit
from integrated_widgets import EditRealUnitedScalarController


@pytest.mark.qt_log_ignore(".*")
def test_edit_real_united_scalar_change_unit(qtbot: QtBot):
    app = QApplication.instance() or QApplication([])
    osv = ObservableSingleValue(RealUnitedScalar(10, Unit("m")))
    c = EditRealUnitedScalarController(osv)
    qtbot.addWidget(c._owner_widget)
    
    # Test initial state
    assert c.value == RealUnitedScalar(10, Unit("m"))
    
    # Test unit change
    c.value = RealUnitedScalar(10, Unit("km"))
    assert c.value == RealUnitedScalar(10, Unit("km"))


