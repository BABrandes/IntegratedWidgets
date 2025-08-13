"""Bridges between Observables and Qt signals.

Thread-safe signal emission: updates from any thread are marshaled to the Qt
main thread via QObject.signal, ensuring GUI thread safety.
"""

from __future__ import annotations

from typing import Any, Callable, Generic, Optional, Protocol, TypeVar, List

from PySide6.QtCore import QObject, Qt, Signal, Slot


T = TypeVar("T")
U = TypeVar("U")


class ObservableLike(Generic[T], Protocol):
    value: T

    def subscribe(self, callback: Callable[[T], Any]) -> Any:  # disposable/handle
        ...


class ObservableQtBridge(QObject, Generic[T]):
    """Thread-safe bridge connecting an observable to a Qt `Signal`.

    - Subscribes to the provided observable
    - Emits `value_changed` on the Qt main thread when the observable changes
    - Never creates a QApplication instance itself
    """

    # Public signal that consumers connect to
    value_changed: Signal = Signal(object)
    # Internal signal used to marshal from any thread to the QObject's thread
    _forward_value: Signal = Signal(object)

    def __init__(self, observable: ObservableLike[T], parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self._observable: ObservableLike[T] = observable
        self._forward_value.connect(self._on_forward_value, Qt.ConnectionType.QueuedConnection)
        self._subscription = self._observable.subscribe(self._on_observable_value)
        # Do not emit the initial value automatically; only emit on changes

    # This method might be called from any thread
    def _on_observable_value(self, value: T) -> None:
        self._forward_value.emit(value)

    @Slot(object)
    def _on_forward_value(self, value: T) -> None:
        # Runs on the QObject's thread; safe to emit to any receivers
        self.value_changed.emit(value)


class MappedObservable(Generic[T, U]):
    """Adapter that maps values from a source observable via a selector.

    Useful for composite observables (e.g., dicts) to observe a single component
    without relying on a specific Observables API. The adapter itself conforms
    to `ObservableLike` so it plugs into existing widgets/bridges.
    """

    def __init__(self, source: ObservableLike[T], selector: Callable[[T], U]) -> None:
        self._source: ObservableLike[T] = source
        self._selector: Callable[[T], U] = selector
        self._subscribers: list[Callable[[U], Any]] = []
        # Initialize current value if accessible
        try:
            self.value: U = self._selector(self._source.value)  # type: ignore[assignment]
        except Exception:  # pragma: no cover - optional
            # Delay until first source emission
            self.value = None  # type: ignore[assignment]

        def _on_source_value(v: T) -> None:
            mapped = self._selector(v)
            self.value = mapped
            for cb in list(self._subscribers):
                cb(mapped)

        self._subscription = self._source.subscribe(_on_source_value)

    def subscribe(self, callback: Callable[[U], Any]) -> Any:
        self._subscribers.append(callback)
        return callback


