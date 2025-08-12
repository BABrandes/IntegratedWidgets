"""Bridges between Observables and Qt signals.

Thread-safe signal emission: updates from any thread are marshaled to the Qt
main thread via QObject.signal, ensuring GUI thread safety.
"""

from __future__ import annotations

from typing import Any, Callable, Generic, Optional, Protocol, TypeVar

from PySide6.QtCore import QObject, Qt, Signal, Slot


T = TypeVar("T")


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
        # Optionally emit the initial value synchronously on the Qt thread
        try:
            initial_value = self._observable.value
            # Emit via forward signal to ensure delivery on the object's thread
            self._forward_value.emit(initial_value)
        except Exception:
            pass

    # This method might be called from any thread
    def _on_observable_value(self, value: T) -> None:
        self._forward_value.emit(value)

    @Slot(object)
    def _on_forward_value(self, value: T) -> None:
        # Runs on the QObject's thread; safe to emit to any receivers
        self.value_changed.emit(value)


