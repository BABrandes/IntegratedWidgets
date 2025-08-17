from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from pytestqt.qtbot import QtBot

from integrated_widgets import IntegerEntryController


@pytest.mark.qt_log_ignore(".*")
def test_integer_entry_roundtrip(qtbot: QtBot):
    app = QApplication.instance() or QApplication([])
    c = IntegerEntryController(1)  # type: ignore
    qtbot.addWidget(c._owner_widget)
    
    # Test initial state
    assert c.single_value == 1
    
    # Test value change
    c.single_value = 42
    assert c.single_value == 42


@pytest.mark.qt_log_ignore(".*")
def test_integer_entry_public_api(qtbot: QtBot) -> None:
    app = QApplication.instance() or QApplication([])

    c = IntegerEntryController(7)  # type: ignore
    qtbot.addWidget(c._owner_widget)

    assert c.single_value == 7
    c.single_value = 9
    assert c.single_value == 9

    # Accessor exists
    _ = c.widget_line_edit
    # Focus on public API consistency
    c.single_value = 11
    assert c.single_value == 11


@pytest.mark.qt_log_ignore(".*")
def test_integer_entry_rejects_invalid_then_restores(qtbot: QtBot) -> None:
    app = QApplication.instance() or QApplication([])

    c = IntegerEntryController(5, validator=lambda v: v >= 0)  # type: ignore
    qtbot.addWidget(c._owner_widget)

    edit = c.widget_line_edit
    edit.setText("-3")
    edit.editingFinished.emit()  # type: ignore[attr-defined]

    assert c.single_value == 5
    assert edit.text() == "5"

    edit.setText("12")
    edit.editingFinished.emit()  # type: ignore[attr-defined]
    assert c.single_value == 12

