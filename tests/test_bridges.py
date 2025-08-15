from __future__ import annotations

from typing import Any, Callable, Generic, TypeVar

import pytest
from PySide6.QtCore import QCoreApplication

from integrated_widgets.util.bridges import ObservableQtBridge


T = TypeVar("T")


class DummyObservable(Generic[T]):
    def __init__(self, value: T) -> None:
        self.value = value
        self._subscribers: list[Callable[[T], Any]] = []

    def subscribe(self, callback: Callable[[T], Any]) -> None:
        self._subscribers.append(callback)

    def set(self, value: T) -> None:
        self.value = value
        for cb in list(self._subscribers):
            cb(value)


@pytest.mark.qt_log_ignore(".*")
def test_bridge_emits_in_qt_thread(qtbot):
    app = QCoreApplication.instance() or QCoreApplication([])
    obs = DummyObservable[int](0)
    bridge = ObservableQtBridge(obs)

    with qtbot.waitSignal(bridge.value_changed, timeout=1000) as blocker:
        obs.set(42)

    assert blocker.args == [42]


