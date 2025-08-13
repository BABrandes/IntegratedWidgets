from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from integrated_widgets import IntegerEntryController
from observables import ObservableSingleValue


@pytest.mark.qt_log_ignore(".*")
def test_integer_entry_roundtrip(qtbot):
    app = QApplication.instance() or QApplication([])
    osv = ObservableSingleValue(1)
    c = IntegerEntryController(osv)
    qtbot.addWidget(c.owner_widget)
    assert c.line_edit.text() == "1"
    # Model -> UI
    osv.set_value(5)
    qtbot.waitUntil(lambda: c.line_edit.text() == "5", timeout=1000)
    assert c.line_edit.text() == "5"
    # UI -> Model
    c.line_edit.setText("7")
    c.line_edit.editingFinished.emit()
    qtbot.waitUntil(lambda: osv.value == 7, timeout=1000)
    assert osv.value == 7


