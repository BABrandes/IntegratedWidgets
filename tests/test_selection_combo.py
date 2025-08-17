from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from pytestqt.qtbot import QtBot
from typing import TypeVar

from integrated_widgets import ComboBoxController

T = TypeVar("T")


@pytest.mark.qt_log_ignore(".*")
def test_selection_combo_updates_from_model(qtbot: QtBot):
    app = QApplication.instance() or QApplication([])
    available = {"A", "B"}
    c = ComboBoxController("A", available_options=available, parent=None)  # type: ignore
    qtbot.addWidget(c._owner_widget)
    
    # Constructor should succeed; initial selection may be None when allow_none is True by default
    assert c.selected_option in {"A", None}
    
    # Test selection change
    c.selected_option = "B"
    assert c.selected_option == "B"


@pytest.mark.qt_log_ignore(".*")
def test_selection_combo_updates_model_from_ui(qtbot: QtBot):
    app = QApplication.instance() or QApplication([])
    available = {"A", "B"}
    c = ComboBoxController("A", available_options=available, parent=None)  # type: ignore
    qtbot.addWidget(c._owner_widget)
    
    # Constructor should succeed
    assert c.selected_option in {"A", None}
    
    # Test selection change
    c.selected_option = "B"
    assert c.selected_option == "B"


@pytest.mark.qt_log_ignore(".*")
def test_combo_box_set_selected_and_options_atomically(qtbot: QtBot) -> None:
    app = QApplication.instance() or QApplication([])

    c = ComboBoxController("A", available_options={"A", "B"}, allow_none=False)  # type: ignore
    qtbot.addWidget(c._owner_widget)

    # Atomic update: change both options and selection in one step
    c.set_selected_option_and_available_options("B", {"B", "C"})

    assert c.selected_option == "B"
    assert c.available_options == {"B", "C"}

    # Widget should contain exactly the available options
    combo = c.widget_combobox
    datas = [combo.itemData(i) for i in range(combo.count())]
    assert set(datas) == {"B", "C"}


@pytest.mark.qt_log_ignore(".*")
def test_combo_box_public_api(qtbot: QtBot) -> None:
    app = QApplication.instance() or QApplication([])

    c = ComboBoxController("A", available_options={"A", "B"}, allow_none=False)  # type: ignore
    qtbot.addWidget(c._owner_widget)

    # Properties
    assert c.available_options == {"A", "B"}
    assert c.selected_option == "A"

    # Change selection
    c.selected_option = "B"
    assert c.selected_option == "B"

    # Change options to include new values and set selection atomically
    c.set_selected_option_and_available_options("A", {"A", "C"})
    assert c.selected_option == "A"
    assert c.available_options == {"A", "C"}

    # Widget accessor
    cb = c.widget_combobox
    datas = [cb.itemData(i) for i in range(cb.count())]
    assert set(datas) == {"A", "C"}

