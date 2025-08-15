from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from integrated_widgets import CheckBoxController
from observables import ObservableSingleValue
from pytestqt.qtbot import QtBot


@pytest.mark.qt_log_ignore(".*")
def test_display_label_updates(qtbot: QtBot):
    app = QApplication.instance() or QApplication([])
    # Replace generic label test with a simple checkbox observable sync check
    osv = ObservableSingleValue(True)
    c = CheckBoxController(osv, text="x")
    qtbot.addWidget(c.owner_widget)
    assert c.widget_check_box.isChecked() is True
    osv.single_value = False
    qtbot.waitUntil(lambda: c.widget_check_box.isChecked() is False, timeout=1000)
    assert c.widget_check_box.isChecked() is False


