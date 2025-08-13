"""Base mixin for Qt widgets bound to Observables (thread-safe).

Moved from `widgets/_base.py`.
"""

from __future__ import annotations

from typing import Any, Callable, Generic, TypeVar

from abc import abstractmethod
from PySide6.QtCore import QObject, Qt, Signal, Slot


O = TypeVar("O")


class _Forwarder(QObject):
    trigger = Signal()


class ObservableWidgetMixin(Generic[O]):
    """Mixin to bind a Qt widget to an observable object."""

    def __init_mixin__(self, observable: O) -> None:
        self._observable: O = observable
        self._forwarder = _Forwarder()  # type: ignore[attr-defined]
        self._forwarder.trigger.connect(self._on_observable_notified, Qt.ConnectionType.QueuedConnection)
        self._blocking_objects: set[object] = set()
        # Register listener to marshal into Qt thread
        self._observable_callback = self._notify_from_observable
        # type: ignore[attr-defined]
        self._observable.add_listeners(self._observable_callback)  # pyright: ignore[reportAttributeAccessIssue]

    # Lifecycle helpers -----------------------------------------------------
    def construction_finished(self) -> None:
        self._internal_update_widget()

    def set_or_replace_observable(self, observable: O) -> None:
        if observable is self._observable:
            return
        # type: ignore[attr-defined]
        self._observable.remove_listeners(self._observable_callback)  # pyright: ignore[reportAttributeAccessIssue]
        self._observable = observable
        # type: ignore[attr-defined]
        self._observable.add_listeners(self._observable_callback)  # pyright: ignore[reportAttributeAccessIssue]
        self._internal_update_widget()

    # Blocking --------------------------------------------------------------
    @property
    def is_blocking_signals(self) -> bool:
        return bool(self._blocking_objects)

    def set_block_signals(self, obj: object) -> None:
        self._blocking_objects.add(obj)

    def set_unblock_signals(self, obj: object) -> None:
        if obj in self._blocking_objects:
            self._blocking_objects.remove(obj)

    def force_unblock_signals(self) -> None:
        self._blocking_objects.clear()

    # Internal plumbing -----------------------------------------------------
    def _notify_from_observable(self) -> None:
        # Called potentially from any thread; forward to Qt thread
        self._forwarder.trigger.emit()

    @Slot()
    def _on_observable_notified(self) -> None:
        self._internal_update_widget()

    def _internal_update_widget(self) -> None:
        if self._blocking_objects:
            return
        self.set_block_signals(self)
        try:
            self.update_widget_from_observable()
        finally:
            self.set_unblock_signals(self)

    def _internal_update_observable(self) -> None:
        if self._blocking_objects:
            return
        self.set_block_signals(self)
        try:
            self.update_observable_from_widget()
        finally:
            self.set_unblock_signals(self)

    @property
    def observable(self) -> O:
        return self._observable

    # Methods for subclasses ------------------------------------------------
    @abstractmethod
    def update_widget_from_observable(self) -> None:  # pragma: no cover - abstract by convention
        raise NotImplementedError

    @abstractmethod
    def update_observable_from_widget(self) -> None:  # pragma: no cover - abstract by convention
        raise NotImplementedError


