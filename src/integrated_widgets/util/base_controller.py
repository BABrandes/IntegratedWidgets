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

class _Forwarder(QObject):
    trigger = Signal()


class BaseController():

    def __init__(
        self,
        parent: Optional[QObject] = None,
        logger: Optional[Logger] = None,

    ) -> None:
        # Store parent reference for internal use
        self._parent: Optional[QObject] = parent
        
        # Create a QObject to handle Qt parent-child relationships
        self._qt_object = QObject(parent)
        
        # Create forwarder as child of the Qt object for proper cleanup
        self._forwarder = _Forwarder(self._qt_object)
        self._forwarder.trigger.connect(self.invalidate_widgets, Qt.ConnectionType.QueuedConnection)
        
        # Initialize internal state
        self._blocking_objects: set[object] = set()
        self._internal_widget_update: bool = False
        self._is_disposed: bool = False
        self._logger: Optional[Logger] = logger
      
        # Create owner widget as child of the Qt object
        if isinstance(parent, QWidget):
            self._owner_widget = parent
        else:
            # Create a new QWidget as child of the parent (or None if no parent)
            self._owner_widget = QWidget(parent)  # type: ignore[arg-type]

        log_msg(self, f"{self.__class__.__name__} initialized", self._logger, "BaseController initialized")

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
    def invalidate_widgets(self) -> None:
        """
        Invalidate the widgets.

        This method is called automatically by the base controller when component values have been changed and the widgets should be invalidated.
        It automatically wraps the actual implementation in the internal update context.

        **DO NOT OVERRIDE:** Controllers should implement _invalidate_widgets_impl() instead.
        """
        if self._is_disposed:
            return  # Silently return if disposed to avoid errors during cleanup
        
        with self._internal_update():
            self.set_block_signals(self)
            try:
                log_msg(self, "invalidate_widgets", self._logger, f"Invalidating widgets")
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

    @property
    @final
    def owner_widget(self) -> QWidget:
        """
        Get the owner widget of the controlled widgets.
        """
        return self._owner_widget