from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from pytestqt.qtbot import QtBot
from enum import Enum

from observables import ObservableSelectionOption
from integrated_widgets import ComboBoxController, RadioButtonsController


class Color(Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"


@pytest.mark.qt_log_ignore(".*")
def test_enum_combo_box(qtbot: QtBot):
    app = QApplication.instance() or QApplication([])
    selection = ObservableSelectionOption(selected_option=Color.RED, options={Color.RED, Color.GREEN, Color.BLUE})
    
    c = ComboBoxController(
        Color.RED,
        available_options_or_observable_or_hook=selection,
        parent=None
    )
    qtbot.addWidget(c._owner_widget)
    
    # Test initial state
    assert c.selected_option == Color.RED
    
    # Test selection change
    c.selected_option = Color.BLUE
    assert c.selected_option == Color.BLUE


@pytest.mark.qt_log_ignore(".*")
def test_enum_radio_buttons(qtbot: QtBot):
    app = QApplication.instance() or QApplication([])
    selection = ObservableSelectionOption(selected_option=Color.RED, options={Color.RED, Color.GREEN, Color.BLUE})
    
    c = RadioButtonsController(
        Color.RED,
        available_options=selection,
        parent=None
    )
    qtbot.addWidget(c._owner_widget)
    
    # Test initial state
    assert c.selected_option == Color.RED
    
    # Test selection change
    c.selected_option = Color.GREEN
    assert c.selected_option == Color.GREEN


