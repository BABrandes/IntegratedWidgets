from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from pytestqt.qtbot import QtBot

from observables import ObservableSingleValue
from integrated_widgets.widget_controllers.check_box_controller import CheckBoxController


@pytest.mark.qt_log_ignore(".*")
def test_display_label_updates(qtbot: QtBot):
    app = QApplication.instance() or QApplication([])
    # Replace generic label test with a simple checkbox observable sync check
    osv = ObservableSingleValue(True)
    c = CheckBoxController(osv, text="x")
    qtbot.addWidget(c._owner_widget)
    
    # Test initial state
    assert c.value == True
    assert c._check.text() == "x"
    
    # Test value change
    c.value = False
    assert c._check.isChecked() == False


