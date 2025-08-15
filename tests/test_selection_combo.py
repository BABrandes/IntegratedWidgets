from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from pytestqt.qtbot import QtBot
from typing import TypeVar, Protocol

from observables import ObservableSelectionOption
from integrated_widgets import ComboBoxController

T = TypeVar("T")


class DummySelection(Protocol[T]):
    def __init__(self, options: set[T], selected: T) -> None: ...
    @property
    def selected_option(self) -> T: ...
    @selected_option.setter
    def selected_option(self, value: T) -> None: ...
    @property
    def available_options(self) -> set[T]: ...


class SimpleSelection:
    def __init__(self, options: set[T], selected: T) -> None:
        self._options = options
        self._selected = selected
    
    @property
    def selected_option(self) -> T:
        return self._selected
    
    @selected_option.setter
    def selected_option(self, value: T) -> None:
        if value in self._options:
            self._selected = value
    
    @property
    def available_options(self) -> set[T]:
        return self._options


@pytest.mark.qt_log_ignore(".*")
def test_selection_combo_updates_from_model(qtbot: QtBot):
    app = QApplication.instance() or QApplication([])
    sel = SimpleSelection({"A", "B"}, selected="A")
    c = ComboBoxController(
        "A",
        available_options_or_observable_or_hook=sel,
        parent=None
    )
    qtbot.addWidget(c._owner_widget)
    
    # Test initial state
    assert c.selected_option == "A"
    
    # Test selection change
    c.selected_option = "B"
    assert c.selected_option == "B"


@pytest.mark.qt_log_ignore(".*")
def test_selection_combo_updates_model_from_ui(qtbot: QtBot):
    app = QApplication.instance() or QApplication([])
    sel = SimpleSelection({"A", "B"}, selected="A")
    c = ComboBoxController(
        "A",
        available_options_or_observable_or_hook=sel,
        parent=None
    )
    qtbot.addWidget(c._owner_widget)
    
    # Test initial state
    assert c.selected_option == "A"
    
    # Test selection change
    c.selected_option = "B"
    assert c.selected_option == "B"


