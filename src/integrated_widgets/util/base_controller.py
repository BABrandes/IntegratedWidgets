from __future__ import annotations

# Standard library imports
from abc import abstractmethod
from contextlib import contextmanager
from typing import Optional, final
from logging import Logger
from PySide6.QtCore import QObject, Qt, Signal
from PySide6.QtWidgets import QWidget

# Local imports
from ..util.resources import log_msg

class _WidgetInvalidationSignal(QObject):
    """Internal QObject used to marshal widget invalidation requests to the Qt event loop.
    
    This ensures that widget updates triggered by the hook system are queued
    rather than executed synchronously, preventing re-entrancy issues and
    ensuring proper event loop processing.
    """
    trigger = Signal()

class BaseController():

    def __init__(
        self,
        parent_of_widgets: Optional[QWidget] = None,
        logger: Optional[Logger] = None,

    ) -> None:
        # Store parent reference for internal use
        self._parent_of_widgets = parent_of_widgets
        
        # Create a QObject to handle Qt parent-child relationships
        self._qt_object = QObject(parent_of_widgets)
        
        # Create signal forwarder for queued widget invalidation
        # This ensures widget updates are processed through the Qt event loop rather than synchronously,
        # preventing re-entrancy issues when the hook system triggers updates
        self._widget_invalidation_signal = _WidgetInvalidationSignal(self._qt_object)
        self._widget_invalidation_signal.trigger.connect(
            self._invalidate_widgets_called_by_hook_system, 
            Qt.ConnectionType.QueuedConnection
        )
        
        # Initialize internal state
        self._blocking_objects: set[object] = set()
        self._internal_widget_update: bool = False
        self._is_disposed: bool = False
        self._logger: Optional[Logger] = logger
      
        # Queue initial widget invalidation (will execute after full initialization completes)
        # This ensures widgets reflect initial values once construction finishes
        self._widget_invalidation_signal.trigger.emit()
        
        log_msg(self, f"{self.__class__.__name__} initialized", self._logger, "BaseController initialized, initial invalidation queued")

    @property
    @final
    def parent_of_widgets(self) -> Optional[QWidget]:
        return self._parent_of_widgets

    @property
    @final
    def logger(self) -> Optional[Logger]:
        return self._logger

    @logger.setter
    @final
    def logger(self, logger: Optional[Logger]) -> None:
        self._logger = logger

    ###########################################################################
    # Abstract Methods - To be implemented by subclasses
    ###########################################################################

    @abstractmethod
    def _initialize_widgets(self) -> None:
        """Create and set up widget instances.
        
        **REQUIRED OVERRIDE:** Controllers must implement this method to create their widgets.
        This is called during initialization before any other operations.
        
        **What to do here:**
        - Create all widget instances (QWidget, QLabel, etc.)
        - Set up widget properties and initial states
        - Connect widget signals to internal handlers
        - Store widgets as instance attributes (e.g., self._label, self._button)
        
        **What NOT to do here:**
        - Don't update widget values from component values (that's handled by invalidate_widgets)
        - Don't set up bindings (base controller handles this)
        - Don't call update methods (base controller calls them automatically)
        - Don't call self._internal_update() (base controller handles this)
        - Don't use block_signals() or unblock_signals() (base controller handles this)
        """
        raise NotImplementedError

    @abstractmethod
    def _invalidate_widgets_impl(self) -> None:
        """
        Invalidate the widgets implementation.

        **REQUIRED OVERRIDE:** Controllers must implement this method to invalidate their widgets.
        This is called automatically by the base controller when the component values have been changed.
        """
        raise NotImplementedError

    ###########################################################################
    # Signal Management and Blocking
    ###########################################################################

    @final
    @property
    def is_blocking_signals(self) -> bool:
        return bool(self._blocking_objects)

    @final
    def set_block_signals(self, obj: object) -> None:
        self._blocking_objects.add(obj)

    @final
    def set_unblock_signals(self, obj: object) -> None:
        if obj in self._blocking_objects:
            self._blocking_objects.remove(obj)

    @final
    @contextmanager
    def _internal_update(self):
        """Context manager for internal widget updates."""
        self._internal_widget_update = True
        try:
            yield
        finally:
            self._internal_widget_update = False

    ###########################################################################
    # Widget Update and Synchronization
    ###########################################################################

    @final
    def _invalidate_widgets_called_by_hook_system(self) -> None:
        """
        Invalidate the widgets.

        This method is called automatically by the base controller when component values have been changed by the hook system and the widgets should be invalidated.
        It automatically wraps the actual implementation in the internal update context.

        **DO NOT OVERRIDE:** Controllers should implement _invalidate_widgets_impl() instead.
        """
        if self._is_disposed:
            return  # Silently return if disposed to avoid errors during cleanup
        
        with self._internal_update():
            self.set_block_signals(self)
            try:
                log_msg(self, "_invalidate_widgets_called_by_hook_system", self._logger, f"Invalidating widgets")
                self._invalidate_widgets_impl()
            finally:
                self.set_unblock_signals(self)

    ###########################################################################
    # Lifecycle Management
    ###########################################################################

    @abstractmethod
    def dispose(self) -> None:
        ...

    def __del__(self) -> None:
        """Ensure proper cleanup when the object is garbage collected."""
        if not self._is_disposed:
            self.dispose()