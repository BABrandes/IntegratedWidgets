from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from integrated_widgets import CheckBoxController
from observables import ObservableSingleValue
from pytestqt.qtbot import QtBot

@pytest.mark.qt_log_ignore(".*")
def test_check_box_sync(qtbot: QtBot):
    app = QApplication.instance() or QApplication([])
    osv = ObservableSingleValue(False)
    c = CheckBoxController(osv)
    qtbot.addWidget(c.owner_widget)
    cb = c.widget_check_box
    assert not cb.isChecked()
    osv.single_value = True
    qtbot.waitUntil(lambda: cb.isChecked(), timeout=1000)
    assert cb.isChecked()
    # UI -> observable
    cb.setChecked(False)
    cb.stateChanged.emit(cb.checkState())
    qtbot.waitUntil(lambda: osv.single_value is False, timeout=1000)
    assert osv.single_value is False


