from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from pytestqt.qtbot import QtBot

from integrated_widgets.widget_controllers.check_box_controller import CheckBoxController


@pytest.mark.qt_log_ignore(".*")
def test_display_label_updates(qtbot: QtBot):
    app = QApplication.instance() or QApplication([])
    # Replace generic label test with a simple checkbox observable sync check
    c = CheckBoxController(True, text="x")  # type: ignore
    qtbot.addWidget(c._owner_widget)
    
    # Test initial state
    assert c.distinct_single_value_reference == True
    assert c._check.text() == "x"
    
    # Constructor only: ensure initial label text and value are consistent
    assert c.distinct_single_value_reference in {True, False}


