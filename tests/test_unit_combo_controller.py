from __future__ import annotations

from PySide6.QtWidgets import QApplication

from integrated_widgets.widget_controllers.unit_combo_box_controller import UnitComboBoxController
from integrated_widgets.util.observable_protocols import ObservableSelectionOption
from united_system import Unit


def test_unit_combo_accepts_valid_new_unit(qtbot):
    app = QApplication.instance() or QApplication([])
    obs = ObservableSelectionOption(selected_option=Unit("V"), options={Unit("V")}, allow_none=False)
    c = UnitComboBoxController(obs)
    qtbot.addWidget(c.owner_widget)

    # Type a compatible unit
    c.combo.setCurrentText("mV")
    c.combo.lineEdit().editingFinished.emit()  # type: ignore

    assert Unit("mV") in obs.options
    assert str(obs.selected_option) == "mV"


def test_unit_combo_rejects_invalid_unit(qtbot):
    app = QApplication.instance() or QApplication([])
    obs = ObservableSelectionOption(selected_option=Unit("V"), options={Unit("V")}, allow_none=False)
    c = UnitComboBoxController(obs)
    qtbot.addWidget(c.owner_widget)

    # Try incompatible unit
    c.combo.setCurrentText("kg")
    c.combo.lineEdit().editingFinished.emit()  # type: ignore

    # Should remain V
    assert str(obs.selected_option) == "V"

