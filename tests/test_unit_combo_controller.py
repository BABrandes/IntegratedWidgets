from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from integrated_widgets import UnitComboBoxController
from observables import ObservableSelectionOption
from united_system import Unit
from pytestqt.qtbot import QtBot


@pytest.mark.skip("UnitComboBoxController is missing required abstract methods")
def test_unit_combo_accepts_valid_new_unit(qtbot: QtBot):
    app = QApplication.instance() or QApplication([])
    obs = ObservableSelectionOption(selected_option=Unit("V"), options={Unit("V")}, allow_none=False)
    c = UnitComboBoxController(obs)
    qtbot.addWidget(c._owner_widget)

    # Type a compatible unit
    c.widget_combobox.setCurrentText("mV")
    c.widget_combobox.lineEdit().editingFinished.emit()  # type: ignore[attr-defined]

    assert Unit("mV") in obs.available_options
    assert str(obs.selected_option) == "mV"


@pytest.mark.skip("UnitComboBoxController is missing required abstract methods")
def test_unit_combo_rejects_invalid_unit(qtbot: QtBot):
    app = QApplication.instance() or QApplication([])
    obs = ObservableSelectionOption(selected_option=Unit("V"), options={Unit("V")}, allow_none=False)
    c = UnitComboBoxController(obs)
    qtbot.addWidget(c._owner_widget)

    # Try incompatible unit
    c.widget_combobox.setCurrentText("kg")
    c.widget_combobox.lineEdit().editingFinished.emit()  # type: ignore[attr-defined]

    # Should remain V
    assert str(obs.selected_option) == "V"

