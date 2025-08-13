from __future__ import annotations

from typing import Any, Callable, List, Optional, Set

import pytest
from PySide6.QtWidgets import QApplication

from integrated_widgets import ComboBoxController


class DummySelection:
    def __init__(self, options: Set[str], selected: Optional[str] = None, allow_none: bool = True) -> None:
        self._options = set(options)
        self._selected = selected
        self._listeners: List[Callable[[], Any]] = []
        self._allow_none = allow_none

    @property
    def options(self) -> Set[str]:
        return set(self._options)

    @options.setter
    def options(self, value: Set[str]) -> None:
        self._options = set(value)
        self._emit()

    @property
    def selected_option(self) -> Optional[str]:
        return self._selected

    @selected_option.setter
    def selected_option(self, value: Optional[str]) -> None:
        self._selected = value
        self._emit()

    @property
    def is_none_selection_allowed(self) -> bool:
        return self._allow_none

    def add_listeners(self, callback: Callable[[], Any]) -> Any:
        self._listeners.append(callback)
        return callback

    def remove_listeners(self, callback: Callable[[], Any]) -> Any:
        if callback in self._listeners:
            self._listeners.remove(callback)
        return callback

    def _emit(self) -> None:
        for cb in list(self._listeners):
            cb()


@pytest.mark.qt_log_ignore(".*")
def test_selection_combo_updates_from_model(qtbot):
    app = QApplication.instance() or QApplication([])
    sel = DummySelection({"A", "B"}, selected="A")
    c = ComboBoxController(sel)  # uses SelectionOption-like protocol
    qtbot.addWidget(c.owner_widget)

    # Initial sync
    assert c.combo.count() == 2
    assert c.combo.currentText() == "A"

    # Change model
    sel.selected_option = "B"
    qtbot.waitUntil(lambda: c.combo.currentText() == "B", timeout=1000)
    assert c.combo.currentText() == "B"


@pytest.mark.qt_log_ignore(".*")
def test_selection_combo_updates_model_from_ui(qtbot):
    app = QApplication.instance() or QApplication([])
    sel = DummySelection({"A", "B"}, selected="A")
    c = ComboBoxController(sel)
    qtbot.addWidget(c.owner_widget)

    # Change UI selection
    index_b = c.combo.findText("B")
    c.combo.setCurrentIndex(index_b)
    qtbot.waitUntil(lambda: sel.selected_option == "B", timeout=1000)
    assert sel.selected_option == "B"


