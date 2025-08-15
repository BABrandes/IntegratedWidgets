from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from integrated_widgets import IntegerEntryController
from observables import ObservableSingleValue
from pytestqt.qtbot import QtBot


@pytest.mark.qt_log_ignore(".*")
def test_integer_entry_roundtrip(qtbot: QtBot):
    app = QApplication.instance() or QApplication([])
    osv = ObservableSingleValue(1)
    c = IntegerEntryController(osv)
    qtbot.addWidget(c.owner_widget)
    assert c.widget_line_edit.text() == "1"
    # Model -> UI
    osv.single_value = 5
    qtbot.waitUntil(lambda: c.widget_line_edit.text() == "5", timeout=1000)
    assert c.widget_line_edit.text() == "5"
    # UI -> Model
    c.widget_line_edit.setText("7")
    c.widget_line_edit.editingFinished.emit()
    qtbot.waitUntil(lambda: osv.single_value == 7, timeout=1000)
    assert osv.single_value == 7


