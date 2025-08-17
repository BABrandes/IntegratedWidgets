from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from integrated_widgets import UnitComboBoxController
from united_system import Unit
from pytestqt.qtbot import QtBot


def test_unit_combo_accepts_valid_new_unit(qtbot: QtBot):
    app = QApplication.instance() or QApplication([])
    c = UnitComboBoxController(Unit("V"), available_units={Unit("V")})
    qtbot.addWidget(c._owner_widget)

    # Type a compatible unit
    with c._internal_update():
        c.widget_combobox.setEditText("mV")
    c.widget_combobox.lineEdit().editingFinished.emit() # type: ignore
    
    # Should accept mV as it's compatible with V
    assert Unit("mV") in c.available_units
    assert c.selected_unit == Unit("mV")


def test_unit_combo_rejects_invalid_unit(qtbot: QtBot):
    app = QApplication.instance() or QApplication([])
    c = UnitComboBoxController(Unit("V"), available_units={Unit("V")})
    qtbot.addWidget(c._owner_widget)

    # Try incompatible unit
    original_unit = c.selected_unit
    with c._internal_update():
        c.widget_combobox.setEditText("kg")
    c.widget_combobox.lineEdit().editingFinished.emit() # type: ignore
    
    # Should reject kg as it's incompatible with V (voltage)
    # The unit should remain the same
    assert c.selected_unit == original_unit
    assert Unit("kg") not in c.available_units

