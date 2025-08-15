from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from pytestqt.qtbot import QtBot

from observables import ObservableSingleValue
from integrated_widgets import CheckBoxController


@pytest.mark.qt_log_ignore(".*")
def test_check_box_sync(qtbot: QtBot):
    app = QApplication.instance() or QApplication([])
    osv = ObservableSingleValue(False)
    c = CheckBoxController(osv)
    qtbot.addWidget(c._owner_widget)
    
    # Test initial state
    assert c.value == False
    
    # Test checkbox click
    qtbot.mouseClick(c._check, Qt.MouseButton.LeftButton)
    assert c.value == True
    
    # Test programmatic change
    c.value = False
    assert c._check.isChecked() == False


