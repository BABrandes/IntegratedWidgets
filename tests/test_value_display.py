from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Generic, List, Protocol, TypeVar

import pytest
from PySide6.QtWidgets import QApplication

from integrated_widgets.widgets import UnitValueDisplay


T = TypeVar("T")


class DummyObservable(Generic[T]):
    def __init__(self, value: T) -> None:
        self.value = value
        self._subscribers: List[Callable[[T], Any]] = []

    def subscribe(self, callback: Callable[[T], Any]) -> None:
        self._subscribers.append(callback)

    def set(self, value: T) -> None:
        self.value = value
        for cb in list(self._subscribers):
            cb(value)


@dataclass
class DummyUnited:
    magnitude: float
    units: str


@pytest.mark.qt_log_ignore(".*")
def test_unit_value_display_updates(qtbot):
    app = QApplication.instance() or QApplication([])
    obs = DummyObservable(DummyUnited(10, "m"))
    widget = UnitValueDisplay(obs)
    qtbot.addWidget(widget)

    assert widget.text() == "10 m"

    obs.set(DummyUnited(20, "m"))
    qtbot.waitUntil(lambda: widget.text() == "20 m", timeout=1000)
    assert widget.text() == "20 m"


