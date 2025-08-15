from __future__ import annotations

from abc import abstractmethod
from contextlib import contextmanager
from typing import Optional, Callable, Any, Mapping

from PySide6.QtCore import QObject, Qt, Signal, Slot
from PySide6.QtWidgets import QWidget

from observables import BaseObservable, HookLike


class _Forwarder(QObject):
    trigger = Signal()


class BaseObservableController(BaseObservable):
    """Base class for controllers that use hooks for data management.

    Inherits from BaseObservable and provides hook-based data synchronization
    with automatic change notifications and bidirectional bindings.
    """

    def __init__(
            self,
            component_values: dict[str, Any],
            component_hooks: dict[str, HookLike[Any]],
            *,
            parent: Optional[QObject] = None,
            verification_method: Optional[Callable[[Mapping[str, Any]], tuple[bool, str]]] = None,
            component_copy_methods: dict[str, Optional[Callable[[Any], Any]]] = {}
    ) -> None:
        # Initialize BaseObservable with empty component values and hooks
        super().__init__(
            component_values=component_values,
            component_hooks=component_hooks,
            component_copy_methods=component_copy_methods,
            verification_method=verification_method
        )
        
        self._parent: Optional[QObject] = parent
        # tie the forwarder to the parent for safe disposal
        self._forwarder = _Forwarder(parent)
        self._forwarder.trigger.connect(self._on_component_values_changed, Qt.ConnectionType.QueuedConnection)
        self._blocking_objects: set[object] = set()
        self._internal_widget_update: bool = False
        self._is_disposed: bool = False
        
        # Create owner widget before initializing widgets
        self._owner_widget: QWidget = self._parent if isinstance(self._parent, QWidget) else QWidget()
        
        # Auto-dispose when parent is destroyed (if QObject parent provided)
        if parent is not None:
            try:
                parent.destroyed.connect(lambda *_: self.dispose())  # type: ignore[attr-defined]
            except Exception:
                pass
        
        self.initialize_widgets()
        self.update_widgets_from_component_values()

    ###########################################################################
    # Hooks
    ###########################################################################

    @abstractmethod
    def initialize_widgets(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def update_widgets_from_component_values(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def update_component_values_from_widgets(self) -> None:
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

    @contextmanager
    def _internal_update(self):
        """Context manager for internal widget updates."""
        self._internal_widget_update = True
        try:
            yield
        finally:
            self._internal_widget_update = False

    ###########################################################################
    # Forwarding
    ###########################################################################

    @Slot()
    def _on_component_values_changed(self) -> None:
        if self._blocking_objects:
            return
        self.set_block_signals(self)
        try:
            self.update_widgets_from_component_values()
        finally:
            self.set_unblock_signals(self)

    ###########################################################################
    # Lifecycle
    ###########################################################################

    def dispose(self) -> None:
        """Dispose of the controller and clean up resources."""
        if self._is_disposed:
            return
        
        self._is_disposed = True
        
        # Disconnect forwarder
        if hasattr(self, '_forwarder'):
            self._forwarder.trigger.disconnect()
        
        # Call disposal hooks
        self.dispose_before_children()
        self.dispose_after_children()




