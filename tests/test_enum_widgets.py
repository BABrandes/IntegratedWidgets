from __future__ import annotations

from enum import Enum
import pytest
from PySide6.QtWidgets import QApplication

from integrated_widgets import ComboBoxController, RadioButtonsController
from observables import ObservableSingleValue, ObservableSelectionOption


class Color(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3


@pytest.mark.qt_log_ignore(".*")
def test_enum_combo_box(qtbot):
    app = QApplication.instance() or QApplication([])
    selection = ObservableSelectionOption(selected_option=Color.RED, options={Color.RED, Color.GREEN, Color.BLUE})
    c = ComboBoxController(selection)
    qtbot.addWidget(c.owner_widget)
    # Model -> UI
    selection.selected_option = Color.GREEN
    qtbot.waitUntil(lambda: c.combo.currentText() == "GREEN", timeout=1000)
    assert c.combo.currentText() == "GREEN"
    # UI -> Model
    idx_blue = c.combo.findText("BLUE")
    c.combo.setCurrentIndex(idx_blue)
    qtbot.waitUntil(lambda: selection.selected_option == Color.BLUE, timeout=1000)
    assert selection.selected_option == Color.BLUE


@pytest.mark.qt_log_ignore(".*")
def test_enum_radio_buttons(qtbot):
    app = QApplication.instance() or QApplication([])
    selection = ObservableSelectionOption(selected_option=Color.RED, options={Color.RED, Color.GREEN, Color.BLUE})
    c = RadioButtonsController(selection)
    qtbot.addWidget(c.owner_widget)
    # Model -> UI: ensure some radio is checked for GREEN
    selection.selected_option = Color.GREEN
    # find by property on any radio button
    def green_checked() -> bool:
        for btn in c.radio_buttons:
            if btn.property("value") == Color.GREEN and btn.isChecked():
                return True
        return False
    qtbot.waitUntil(green_checked, timeout=1000)
    assert green_checked()


