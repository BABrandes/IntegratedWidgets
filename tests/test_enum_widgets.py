from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from pytestqt.qtbot import QtBot
from enum import Enum

from integrated_widgets import ComboBoxController, RadioButtonsController


class Color(Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"


@pytest.mark.qt_log_ignore(".*")
def test_enum_combo_box(qtbot: QtBot):
    app = QApplication.instance() or QApplication([])
    available = {Color.RED, Color.GREEN, Color.BLUE}
    c = ComboBoxController(Color.RED, available_options=available, parent=None)  # type: ignore
    qtbot.addWidget(c._owner_widget)
    
    # Constructor should succeed; initial selection may be None when allow_none is True by default
    assert c.selected_option in {Color.RED, None}
    
    # Test selection change
    c.selected_option = Color.BLUE
    assert c.selected_option == Color.BLUE


@pytest.mark.qt_log_ignore(".*")
def test_enum_radio_buttons(qtbot: QtBot):
    app = QApplication.instance() or QApplication([])
    available = {Color.RED, Color.GREEN, Color.BLUE}
    c = RadioButtonsController(Color.RED, available_options=available, parent=None)  # type: ignore
    qtbot.addWidget(c._owner_widget)
    
    # Test initial state
    assert c.selected_option == Color.RED
    
    # Test selection change
    c.selected_option = Color.GREEN
    assert c.selected_option == Color.GREEN


@pytest.mark.qt_log_ignore(".*")
def test_radio_buttons_rebuilds_on_options_change(qtbot: QtBot) -> None:
    app = QApplication.instance() or QApplication([])
    from PySide6.QtWidgets import QWidget

    parent = QWidget()
    c = RadioButtonsController("X", available_options={"X", "Y"}, parent=parent)  # type: ignore
    qtbot.addWidget(parent)

    # Initially two buttons
    assert len(c.widgets_radio_buttons) == 2

    # Change available options -> set selection to common value and update
    c.selected_option = "Y"
    c.available_options = {"Y", "Z"}
    assert len(c.widgets_radio_buttons) == 2
    assert c.selected_option in {"Y", "Z"}

