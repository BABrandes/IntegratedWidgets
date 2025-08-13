from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from integrated_widgets import CheckBoxController
from observables import ObservableSingleValue


@pytest.mark.qt_log_ignore(".*")
def test_check_box_sync(qtbot):
    app = QApplication.instance() or QApplication([])
    osv = ObservableSingleValue(False)
    c = CheckBoxController(osv)
    qtbot.addWidget(c.owner_widget)
    cb = c.check_box
    assert not cb.isChecked()
    osv.set_value(True)
    qtbot.waitUntil(lambda: cb.isChecked(), timeout=1000)
    assert cb.isChecked()
    # UI -> observable
    cb.setChecked(False)
    cb.stateChanged.emit(cb.checkState())
    qtbot.waitUntil(lambda: osv.value is False, timeout=1000)
    assert osv.value is False


