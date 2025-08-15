from __future__ import annotations

from PySide6.QtWidgets import QApplication

from integrated_widgets.widget_controllers.unit_combo_box_controller import UnitComboBoxController
from observables import ObservableSelectionOption
from united_system import Unit
from pytestqt.qtbot import QtBot

def test_unit_combo_accepts_valid_new_unit(qtbot: QtBot):
    app = QApplication.instance() or QApplication([])
    obs = ObservableSelectionOption(selected_option=Unit("V"), options={Unit("V")}, allow_none=False)
    c = UnitComboBoxController(obs)
    qtbot.addWidget(c.owner_widget)

    # Type a compatible unit
    c.widget_combobox.setCurrentText("mV")
    c.widget_combobox.lineEdit().editingFinished.emit()  # type: ignore[attr-defined]

    assert Unit("mV") in obs.available_options
    assert str(obs.selected_option) == "mV"

def test_unit_combo_rejects_invalid_unit(qtbot: QtBot):
    app = QApplication.instance() or QApplication([])
    obs = ObservableSelectionOption(selected_option=Unit("V"), options={Unit("V")}, allow_none=False)
    c = UnitComboBoxController(obs)
    qtbot.addWidget(c.owner_widget)

    # Try incompatible unit
    c.widget_combobox.setCurrentText("kg")
    c.widget_combobox.lineEdit().editingFinished.emit()  # type: ignore[attr-defined]

    # Should remain V
    assert str(obs.selected_option) == "V"

