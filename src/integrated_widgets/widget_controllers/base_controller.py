from __future__ import annotations

from abc import abstractmethod
from typing import Generic, Optional, TypeVar, Callable

from PySide6.QtCore import QObject, Qt, Signal, Slot
from PySide6.QtWidgets import QWidget
from PySide6.QtWidgets import QWidget

from integrated_widgets.util.observable_protocols import ObservableLike
from observables import Observable

O = TypeVar("O", bound=ObservableLike | Observable, covariant=True)

class _Forwarder(QObject):
    trigger = Signal()


class ObservableController(Generic[O]):
    """Base class for non-widget controllers that sync an observable and child widgets.

    Provides the same thread-safe forwarding and blocking semantics as ObservableWidgetMixin
    but without inheriting QWidget.
    """

    def __init__(self, observable: O, parent: Optional[QObject] = None) -> None:
        self._observable: O = observable
        self._parent: Optional[QObject] = parent
        # tie the forwarder to the parent for safe disposal
        self._forwarder = _Forwarder(parent)
        self._forwarder.trigger.connect(self._on_observable_notified, Qt.ConnectionType.QueuedConnection)
        self._blocking_objects: set[object] = set()
        self._internal_widget_update: bool = False
        self._is_disposed: bool = False
        self._observable_callback = self._notify_from_observable
        self._observable.add_listeners(self._observable_callback)
        self._owner_widget = QWidget(parent if isinstance(parent, QWidget) else None)
        # Auto-dispose when parent is destroyed (if QObject parent provided)
        if parent is not None:
            try:
                parent.destroyed.connect(lambda *_: self.dispose())  # type: ignore[attr-defined]
            except Exception:
                pass
        self.initialize_widgets()
        self.update_widgets_from_observable()

    ###########################################################################
    # Hooks
    ###########################################################################

    @abstractmethod
    def initialize_widgets(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def update_widgets_from_observable(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def update_observable_from_widgets(self) -> None:
        raise NotImplementedError
    
    def dispose_before_children(self) -> None:
        """Hook for controllers to disconnect signals before children are deleted."""
        pass

    def dispose_after_children(self) -> None:
        """Hook after children were scheduled for deletion."""
        pass

    ###########################################################################
    # Blocking
    ###########################################################################

    @property
    def is_blocking_signals(self) -> bool:
        return bool(self._blocking_objects)

    def set_block_signals(self, obj: object) -> None:
        self._blocking_objects.add(obj)

    def set_unblock_signals(self, obj: object) -> None:
        if obj in self._blocking_objects:
            self._blocking_objects.remove(obj)

    ###########################################################################
    # Forwarding
    ###########################################################################

    def _notify_from_observable(self) -> None:
        self._forwarder.trigger.emit()

    @Slot()
    def _on_observable_notified(self) -> None:
        if self._blocking_objects:
            return
        self.set_block_signals(self)
        try:
            self.update_widgets_from_observable()
        finally:
            self.set_unblock_signals(self)

    ###########################################################################
    # Internal update guard
    ###########################################################################

    def _internal_update(self):
        class _Ctx:
            def __init__(self, owner: "ObservableController") -> None:
                self._owner = owner
            def __enter__(self) -> None:
                self._owner._internal_widget_update = True
                try:
                    # Mirror flag on the owner QWidget so guarded widgets can detect internal updates
                    setattr(self._owner._owner_widget, "_internal_widget_update", True)
                except Exception:
                    pass
            def __exit__(self, exc_type, exc, tb) -> None:
                self._owner._internal_widget_update = False
                try:
                    setattr(self._owner._owner_widget, "_internal_widget_update", False)
                except Exception:
                    pass
        return _Ctx(self)

    def suspend_updates(self):
        """Public context manager to suspend UI<->model updates temporarily."""
        return self._internal_update()

    ###########################################################################
    # Public
    ###########################################################################

    @property
    def observable(self) -> O:
        return self._observable

    @property
    def parent(self) -> Optional[QObject]:
        return self._parent

    @property
    def owner_widget(self) -> QWidget:
        return self._owner_widget

    def dispose(self) -> None:
        """Disconnect listeners and release resources.

        Subclasses overriding should call super().dispose() at the end.
        """
        if self._is_disposed:
            return
        self._is_disposed = True
        # Allow subclass to disconnect signals first
        try:
            self.dispose_before_children()
        except Exception:
            pass

        # Remove observable listener
        try:
            self._observable.remove_listeners(self._observable_callback)
        except Exception:
            pass

        # Schedule children deletion
        try:
            self._owner_widget.deleteLater()
        except Exception:
            pass

        # Delete forwarder last
        try:
            self._forwarder.deleteLater()
        except Exception:
            pass

        # Post-dispose hook
        try:
            self.dispose_after_children()
        except Exception:
            pass

    def set_or_replace_observable(self, new_observable: ObservableLike | Observable) -> None:
        if new_observable is self._observable:
            return
        try:
            self._observable.remove_listeners(self._observable_callback)
        except Exception:
            pass
        self._observable = new_observable # type: ignore[assignment]
        self._observable.add_listeners(self._observable_callback)
        self.update_widgets_from_observable()


