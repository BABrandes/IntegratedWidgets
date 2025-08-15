from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from pytestqt.qtbot import QtBot

from observables import ObservableSingleValue
from integrated_widgets import IntegerEntryController


@pytest.mark.qt_log_ignore(".*")
def test_integer_entry_roundtrip(qtbot: QtBot):
    app = QApplication.instance() or QApplication([])
    osv = ObservableSingleValue(1)
    c = IntegerEntryController(osv)
    qtbot.addWidget(c._owner_widget)
    
    # Test initial state
    assert c.value == 1
    
    # Test value change
    c.value = 42
    assert c.value == 42


